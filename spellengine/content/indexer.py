"""
Content Indexer for SpellEngine

Manages discovery and indexing of adventures and trainings at scale.
Flat structure + queryable index for thousands of content items.

PROPRIETARY - All Rights Reserved
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# Default content root relative to project
CONTENT_ROOT = Path(__file__).parent.parent.parent / "content"
INDEX_FILE = "index.json"
MANIFEST_FILE = "manifest.yaml"
CONTENT_TYPES = ("adventures", "trainings")


class ContentIndexer:
    """Indexes and queries SpellEngine content."""

    def __init__(self, content_root: Path | None = None):
        self.content_root = Path(content_root) if content_root else CONTENT_ROOT
        self.index_path = self.content_root / INDEX_FILE
        self._index: dict[str, Any] | None = None

    @property
    def index(self) -> dict[str, Any]:
        """Lazy-load index from disk."""
        if self._index is None:
            self._index = self._load_index()
        return self._index

    def _load_index(self) -> dict[str, Any]:
        """Load existing index or return empty structure."""
        if self.index_path.exists():
            with open(self.index_path) as f:
                return json.load(f)
        return self._empty_index()

    def _empty_index(self) -> dict[str, Any]:
        """Return empty index structure."""
        return {
            "version": "1.0.0",
            "generated": None,
            "schema_version": "1.0.0",
            "adventures": [],
            "trainings": [],
        }

    def rebuild(self) -> dict[str, Any]:
        """Rebuild index from all manifest files."""
        index = self._empty_index()
        index["generated"] = datetime.now(timezone.utc).isoformat()

        for content_type in CONTENT_TYPES:
            type_dir = self.content_root / content_type
            if not type_dir.exists():
                continue

            items = []
            for item_dir in sorted(type_dir.iterdir()):
                if not item_dir.is_dir():
                    continue

                manifest_path = item_dir / MANIFEST_FILE
                if not manifest_path.exists():
                    continue

                try:
                    manifest = self._load_manifest(manifest_path)
                    items.append(self._manifest_to_index_entry(manifest, item_dir))
                except Exception as e:
                    print(f"Warning: Failed to index {item_dir.name}: {e}")

            index[content_type] = items

        # Save index
        self._save_index(index)
        self._index = index
        return index

    def _load_manifest(self, path: Path) -> dict[str, Any]:
        """Load and parse a manifest file."""
        with open(path) as f:
            return yaml.safe_load(f)

    def _manifest_to_index_entry(
        self, manifest: dict[str, Any], item_dir: Path
    ) -> dict[str, Any]:
        """Convert manifest to index entry (subset of fields for fast queries)."""
        content_type = manifest.get("type", "adventure")
        relative_path = item_dir.relative_to(self.content_root)

        entry = {
            "id": manifest.get("id", item_dir.name),
            "type": content_type,
            "path": str(relative_path),
            "title": manifest.get("title", item_dir.name),
            "version": manifest.get("version", "0.0.0"),
            "engine": manifest.get("engine", ">=1.0.0"),
            # Discovery fields
            "difficulty": manifest.get("difficulty"),
            "duration_minutes": manifest.get("duration_minutes"),
            "tags": manifest.get("tags", []),
            "hash_types": manifest.get("hash_types", []),
            "tools": manifest.get("tools", []),
            # Metadata
            "author": manifest.get("author"),
            "description": manifest.get("description"),
        }

        # Type-specific fields
        if content_type == "adventure":
            entry["chapters"] = manifest.get("chapters")
            entry["encounters"] = manifest.get("encounters")
        elif content_type == "training":
            entry["modules"] = manifest.get("modules")
            entry["lessons"] = manifest.get("lessons")

        return entry

    def _save_index(self, index: dict[str, Any]) -> None:
        """Save index to disk."""
        with open(self.index_path, "w") as f:
            json.dump(index, f, indent=2)

    def find(
        self,
        content_type: str | None = None,
        difficulty: str | None = None,
        tags: list[str] | None = None,
        hash_types: list[str] | None = None,
        max_duration: int | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find content matching filters."""
        results = []

        # Determine which types to search
        types_to_search = [content_type] if content_type else list(CONTENT_TYPES)

        for ctype in types_to_search:
            items = self.index.get(ctype, [])
            for item in items:
                if self._matches_filters(
                    item, difficulty, tags, hash_types, max_duration, search
                ):
                    results.append(item)

        return results

    def _matches_filters(
        self,
        item: dict[str, Any],
        difficulty: str | None,
        tags: list[str] | None,
        hash_types: list[str] | None,
        max_duration: int | None,
        search: str | None,
    ) -> bool:
        """Check if item matches all provided filters."""
        if difficulty and item.get("difficulty") != difficulty:
            return False

        if tags:
            item_tags = set(item.get("tags", []))
            if not all(tag in item_tags for tag in tags):
                return False

        if hash_types:
            item_hashes = set(item.get("hash_types", []))
            if not any(ht in item_hashes for ht in hash_types):
                return False

        if max_duration:
            item_duration = item.get("duration_minutes")
            if item_duration and item_duration > max_duration:
                return False

        if search:
            search_lower = search.lower()
            searchable = (
                item.get("title", "").lower()
                + " "
                + item.get("description", "").lower()
                + " "
                + " ".join(item.get("tags", []))
            )
            if search_lower not in searchable:
                return False

        return True

    def get(self, content_id: str) -> dict[str, Any] | None:
        """Get a specific content item by ID."""
        for content_type in CONTENT_TYPES:
            for item in self.index.get(content_type, []):
                if item.get("id") == content_id:
                    return item
        return None

    def validate(self) -> list[dict[str, Any]]:
        """Validate all content manifests. Returns list of issues."""
        issues = []

        for content_type in CONTENT_TYPES:
            type_dir = self.content_root / content_type
            if not type_dir.exists():
                continue

            for item_dir in type_dir.iterdir():
                if not item_dir.is_dir():
                    continue

                manifest_path = item_dir / MANIFEST_FILE
                item_issues = self._validate_manifest(item_dir, manifest_path)
                issues.extend(item_issues)

        return issues

    def _validate_manifest(
        self, item_dir: Path, manifest_path: Path
    ) -> list[dict[str, Any]]:
        """Validate a single manifest file."""
        issues = []
        item_name = item_dir.name

        if not manifest_path.exists():
            issues.append(
                {
                    "item": item_name,
                    "severity": "error",
                    "message": "Missing manifest.yaml",
                }
            )
            return issues

        try:
            manifest = self._load_manifest(manifest_path)
        except Exception as e:
            issues.append(
                {
                    "item": item_name,
                    "severity": "error",
                    "message": f"Invalid YAML: {e}",
                }
            )
            return issues

        # Required fields
        required = ["id", "type", "title", "version", "engine"]
        for field in required:
            if field not in manifest:
                issues.append(
                    {
                        "item": item_name,
                        "severity": "error",
                        "message": f"Missing required field: {field}",
                    }
                )

        # Type validation
        if manifest.get("type") not in ("adventure", "training"):
            issues.append(
                {
                    "item": item_name,
                    "severity": "error",
                    "message": f"Invalid type: {manifest.get('type')}",
                }
            )

        # ID should match directory name
        if manifest.get("id") != item_name:
            issues.append(
                {
                    "item": item_name,
                    "severity": "warning",
                    "message": f"ID '{manifest.get('id')}' doesn't match directory name",
                }
            )

        # Recommended fields
        recommended = ["difficulty", "duration_minutes", "tags", "description"]
        for field in recommended:
            if field not in manifest:
                issues.append(
                    {
                        "item": item_name,
                        "severity": "info",
                        "message": f"Missing recommended field: {field}",
                    }
                )

        return issues

    def stats(self) -> dict[str, Any]:
        """Return statistics about indexed content."""
        stats = {
            "total": 0,
            "by_type": {},
            "by_difficulty": {},
            "by_tag": {},
            "by_hash_type": {},
        }

        for content_type in CONTENT_TYPES:
            items = self.index.get(content_type, [])
            count = len(items)
            stats["by_type"][content_type] = count
            stats["total"] += count

            for item in items:
                # Difficulty
                diff = item.get("difficulty", "unknown")
                stats["by_difficulty"][diff] = stats["by_difficulty"].get(diff, 0) + 1

                # Tags
                for tag in item.get("tags", []):
                    stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1

                # Hash types
                for ht in item.get("hash_types", []):
                    stats["by_hash_type"][ht] = stats["by_hash_type"].get(ht, 0) + 1

        return stats


# Convenience functions
def rebuild_index(content_root: Path | None = None) -> dict[str, Any]:
    """Rebuild the content index."""
    indexer = ContentIndexer(content_root)
    return indexer.rebuild()


def validate_content(content_root: Path | None = None) -> list[dict[str, Any]]:
    """Validate all content manifests."""
    indexer = ContentIndexer(content_root)
    return indexer.validate()


def find_content(
    content_root: Path | None = None, **filters: Any
) -> list[dict[str, Any]]:
    """Find content matching filters."""
    indexer = ContentIndexer(content_root)
    return indexer.find(**filters)
