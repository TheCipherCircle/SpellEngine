"""Scribe - Knowledge Base Curator Agent.

A data steward agent that bridges PatternForge observations to the Hashtopia
knowledge base. Scribe proposes changes but NEVER writes without explicit
authorization.

Design Principles:
- Read freely, write never (without approval)
- All changes go through staging and review
- Qualify data sources (test vs real-world)
- Maintain knowledge base accuracy and currency
- Support dynamic sample hash rotation
- Understand Obsidian graph structure for intelligent proposals
- Collect personal input corpus for individual language modeling
"""

import json
import hashlib
import re
import yaml
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


class ChangeType(Enum):
    """Types of knowledge base changes."""
    UPDATE = "update"           # Modify existing content
    ENRICH = "enrich"           # Add new data to existing page
    CORRECT = "correct"         # Fix inaccurate information
    DEPRECATE = "deprecate"     # Mark outdated information
    CREATE = "create"           # New page/section
    ROTATE = "rotate"           # Rotate sample data
    PROMOTE = "promote"         # Promote from staging to production


class DataQualification(Enum):
    """Qualification of data source."""
    PRODUCTION = "production"       # Real-world data
    CONTROLLED_TEST = "controlled"  # Controlled test environment
    SYNTHETIC = "synthetic"         # Generated/synthetic data
    MIXED = "mixed"                 # Combination of sources
    UNKNOWN = "unknown"             # Source not determined


class ApprovalStatus(Enum):
    """Status of change approval."""
    STAGED = "staged"           # Awaiting review
    APPROVED = "approved"       # Approved, ready to write
    REJECTED = "rejected"       # Rejected, will not write
    APPLIED = "applied"         # Successfully written
    FAILED = "failed"           # Write attempted but failed


@dataclass
class ChangeReport:
    """A proposed change to the knowledge base."""
    report_id: str
    created_at: str
    change_type: str
    target_file: str
    target_section: str | None
    current_content: str
    proposed_content: str
    rationale: str
    data_sources: list[str]
    data_qualification: str
    supporting_evidence: dict
    status: str = "staged"
    reviewed_at: str | None = None
    reviewed_by: str | None = None
    decision_notes: str = ""
    applied_at: str | None = None


@dataclass
class SampleHashSet:
    """A set of sample hashes for training."""
    hash_type: str
    hash_mode: int
    display_name: str
    description: str
    hashes: list[dict]  # Each has 'hash', 'plaintext' (optional), 'metadata'
    created_at: str
    source: str
    qualification: str


@dataclass
class DiscrepancyRecord:
    """A detected discrepancy between observed and documented data."""
    discrepancy_id: str
    detected_at: str
    target_file: str
    documented_claim: str
    observed_value: str
    difference: str
    significance: str  # low, medium, high, critical
    data_source: str
    qualification: str
    resolved: bool = False
    resolution: str = ""


# =============================================================================
# OBSIDIAN KNOWLEDGE GRAPH STRUCTURES
# =============================================================================

@dataclass
class ObsidianPage:
    """A parsed Obsidian page with metadata."""
    path: str
    title: str
    content: str
    frontmatter: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    wikilinks: list[str] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)
    word_count: int = 0


@dataclass
class KnowledgeGraph:
    """The full knowledge graph of a vault."""
    pages: dict[str, ObsidianPage] = field(default_factory=dict)
    forward_links: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    backlinks: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    tag_index: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


@dataclass
class TagAnalysis:
    """Analysis of a tag's usage."""
    tag: str
    count: int
    pages: list[str]
    similar_tags: list[str] = field(default_factory=list)
    suggested_hierarchy: str | None = None


@dataclass
class ConnectionProposal:
    """A proposed connection between pages."""
    source_page: str
    target_page: str
    reason: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class GraphAnalysis:
    """Full analysis of a knowledge graph."""
    total_pages: int
    total_tags: int
    total_links: int
    orphan_pages: list[str]
    most_connected: list[tuple[str, int]]
    least_connected: list[tuple[str, int]]
    tag_frequency: dict[str, int]
    clusters: list[list[str]]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# PERSONAL CORPUS STRUCTURES
# =============================================================================

@dataclass
class CorpusEntry:
    """A single input entry in the personal corpus."""
    timestamp: str
    session_id: str
    raw_text: str
    words: list[str]
    word_count: int
    potential_errors: list[dict]  # {'word': str, 'position': int, 'candidates': list}


@dataclass
class ErrorPattern:
    """A detected typing error pattern."""
    error_type: str  # transposition, adjacent_key, omission, doubling, phonetic
    original: str
    likely_intended: str
    frequency: int
    examples: list[str]


@dataclass
class CorpusAnalysis:
    """Analysis of the personal corpus."""
    total_entries: int
    total_words: int
    unique_words: int
    vocabulary_richness: float  # unique/total ratio
    word_frequency: dict[str, int]
    top_bigrams: list[tuple[str, int]]
    top_trigrams: list[tuple[str, int]]
    error_patterns: list[ErrorPattern]
    typing_velocity_proxy: float  # words per entry average
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ObservationSource(Protocol):
    """Protocol for observation sources (Cosmic, MVA)."""

    def get_observations(self, filter_tags: list[str] | None = None) -> list[dict]:
        """Get observations, optionally filtered by tags."""
        ...


class Scribe:
    """Scribe - The Knowledge Base Curator Agent.

    Watches PatternForge observations and proposes updates to the
    Hashtopia knowledge base. All writes require explicit approval.
    """

    def __init__(
        self,
        hashtopia_path: Path | str,
        data_dir: Path | str = "scribe",
        auto_save: bool = True,
        production_path: Path | str | None = None,
    ):
        """Initialize Scribe.

        Args:
            hashtopia_path: Path to the Hashtopia knowledge base (staging)
            data_dir: Directory for Scribe's working data
            auto_save: Whether to auto-save state changes
            production_path: Optional path to production vault for promotions
        """
        self.hashtopia_path = Path(hashtopia_path)
        self.data_dir = Path(data_dir)
        self.auto_save = auto_save
        self.production_path: Path | None = Path(production_path) if production_path else None

        # Verify Hashtopia exists
        if not self.hashtopia_path.exists():
            raise ValueError(f"Hashtopia path does not exist: {self.hashtopia_path}")

        # Verify production path if provided
        if self.production_path and not self.production_path.exists():
            raise ValueError(f"Production path does not exist: {self.production_path}")

        # In-memory state
        self.change_reports: dict[str, ChangeReport] = {}
        self.sample_hash_sets: dict[str, SampleHashSet] = {}
        self.discrepancies: dict[str, DiscrepancyRecord] = {}

        # Connected observation sources
        self.observation_sources: dict[str, ObservationSource] = {}

        # Counters
        self._report_count = 0
        self._discrepancy_count = 0

        # Load existing state
        self._load_state()

    def _load_state(self) -> None:
        """Load existing state from disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load change reports
        reports_file = self.data_dir / "change_reports.json"
        if reports_file.exists():
            with open(reports_file) as f:
                data = json.load(f)
            for rid, rdata in data.items():
                self.change_reports[rid] = ChangeReport(**rdata)
            if self.change_reports:
                self._report_count = max(
                    int(r.split("_")[1]) for r in self.change_reports.keys()
                ) + 1

        # Load sample hash sets
        samples_file = self.data_dir / "sample_hash_sets.json"
        if samples_file.exists():
            with open(samples_file) as f:
                data = json.load(f)
            for sid, sdata in data.items():
                self.sample_hash_sets[sid] = SampleHashSet(**sdata)

        # Load discrepancies
        discrepancies_file = self.data_dir / "discrepancies.json"
        if discrepancies_file.exists():
            with open(discrepancies_file) as f:
                data = json.load(f)
            for did, ddata in data.items():
                self.discrepancies[did] = DiscrepancyRecord(**ddata)
            if self.discrepancies:
                self._discrepancy_count = max(
                    int(d.split("_")[1]) for d in self.discrepancies.keys()
                ) + 1

    def _save_state(self) -> None:
        """Save current state to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Save change reports
        reports_file = self.data_dir / "change_reports.json"
        with open(reports_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.change_reports.items()}, f, indent=2)

        # Save sample hash sets
        samples_file = self.data_dir / "sample_hash_sets.json"
        with open(samples_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.sample_hash_sets.items()}, f, indent=2)

        # Save discrepancies
        discrepancies_file = self.data_dir / "discrepancies.json"
        with open(discrepancies_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.discrepancies.items()}, f, indent=2)

    # =========================================================================
    # OBSERVATION SOURCE MANAGEMENT
    # =========================================================================

    def register_source(self, name: str, source: ObservationSource) -> None:
        """Register an observation source (e.g., Cosmic, MVA).

        Args:
            name: Source name
            source: Source instance implementing ObservationSource protocol
        """
        self.observation_sources[name] = source

    # =========================================================================
    # HASHTOPIA READING (Always Allowed)
    # =========================================================================

    def read_page(self, relative_path: str) -> str | None:
        """Read a page from Hashtopia.

        Args:
            relative_path: Path relative to Hashtopia root

        Returns:
            Page content, or None if not found
        """
        full_path = self.hashtopia_path / relative_path
        if full_path.exists():
            return full_path.read_text()
        return None

    def find_pages(self, pattern: str) -> list[Path]:
        """Find pages matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.md")

        Returns:
            List of matching paths relative to Hashtopia root
        """
        matches = list(self.hashtopia_path.glob(pattern))
        return [p.relative_to(self.hashtopia_path) for p in matches]

    def search_content(self, query: str, file_pattern: str = "**/*.md") -> list[tuple[Path, list[str]]]:
        """Search for content across Hashtopia pages.

        Args:
            query: Text to search for (case-insensitive)
            file_pattern: Glob pattern for files to search

        Returns:
            List of (path, matching_lines) tuples
        """
        results = []
        query_lower = query.lower()

        for path in self.hashtopia_path.glob(file_pattern):
            if path.is_file():
                try:
                    content = path.read_text()
                    matches = [
                        line.strip()
                        for line in content.split("\n")
                        if query_lower in line.lower()
                    ]
                    if matches:
                        rel_path = path.relative_to(self.hashtopia_path)
                        results.append((rel_path, matches))
                except Exception:
                    pass

        return results

    def get_page_structure(self, relative_path: str) -> dict | None:
        """Parse a markdown page's structure.

        Args:
            relative_path: Path relative to Hashtopia root

        Returns:
            Dict with sections and their content
        """
        content = self.read_page(relative_path)
        if content is None:
            return None

        structure = {
            "path": relative_path,
            "title": None,
            "sections": [],
        }

        current_section = None
        current_content = []

        for line in content.split("\n"):
            # Check for headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                # Save previous section
                if current_section:
                    structure["sections"].append({
                        "level": current_section["level"],
                        "title": current_section["title"],
                        "content": "\n".join(current_content).strip(),
                    })

                level = len(header_match.group(1))
                title = header_match.group(2)

                if level == 1 and structure["title"] is None:
                    structure["title"] = title

                current_section = {"level": level, "title": title}
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_section:
            structure["sections"].append({
                "level": current_section["level"],
                "title": current_section["title"],
                "content": "\n".join(current_content).strip(),
            })

        return structure

    # =========================================================================
    # CHANGE PROPOSAL (Staging)
    # =========================================================================

    def propose_change(
        self,
        change_type: ChangeType | str,
        target_file: str,
        current_content: str,
        proposed_content: str,
        rationale: str,
        data_sources: list[str],
        data_qualification: DataQualification | str,
        supporting_evidence: dict | None = None,
        target_section: str | None = None,
    ) -> ChangeReport:
        """Propose a change to a Hashtopia page (stages for review).

        Args:
            change_type: Type of change
            target_file: Path relative to Hashtopia root
            current_content: What currently exists
            proposed_content: What should replace it
            rationale: Why this change is proposed
            data_sources: Where the data came from
            data_qualification: Quality/source of data
            supporting_evidence: Additional evidence dict
            target_section: Specific section being changed

        Returns:
            The staged ChangeReport
        """
        report_id = f"change_{self._report_count}"
        self._report_count += 1

        if isinstance(change_type, ChangeType):
            change_type = change_type.value
        if isinstance(data_qualification, DataQualification):
            data_qualification = data_qualification.value

        report = ChangeReport(
            report_id=report_id,
            created_at=datetime.now().isoformat(),
            change_type=change_type,
            target_file=target_file,
            target_section=target_section,
            current_content=current_content,
            proposed_content=proposed_content,
            rationale=rationale,
            data_sources=data_sources,
            data_qualification=data_qualification,
            supporting_evidence=supporting_evidence or {},
            status="staged",
        )

        self.change_reports[report_id] = report

        if self.auto_save:
            self._save_state()

        return report

    def get_staged_changes(self) -> list[ChangeReport]:
        """Get all changes awaiting review.

        Returns:
            List of staged ChangeReports
        """
        return [r for r in self.change_reports.values() if r.status == "staged"]

    def get_change_report(self, report_id: str) -> ChangeReport | None:
        """Get a specific change report.

        Args:
            report_id: The report ID

        Returns:
            The ChangeReport, or None if not found
        """
        return self.change_reports.get(report_id)

    # =========================================================================
    # REVIEW AND AUTHORIZATION
    # =========================================================================

    def diff(self, report_id: str, context_lines: int = 3) -> str:
        """Show a unified diff for a change report.

        Args:
            report_id: The change report to diff
            context_lines: Number of context lines around changes

        Returns:
            Unified diff string, or error message if not found
        """
        import difflib

        report = self.change_reports.get(report_id)
        if not report:
            return f"Change report '{report_id}' not found."

        current_lines = report.current_content.splitlines(keepends=True)
        proposed_lines = report.proposed_content.splitlines(keepends=True)

        # Add newlines if missing
        if current_lines and not current_lines[-1].endswith('\n'):
            current_lines[-1] += '\n'
        if proposed_lines and not proposed_lines[-1].endswith('\n'):
            proposed_lines[-1] += '\n'

        diff = difflib.unified_diff(
            current_lines,
            proposed_lines,
            fromfile=f"current: {report.target_file}",
            tofile=f"proposed: {report.target_file}",
            n=context_lines,
        )

        diff_text = ''.join(diff)

        if not diff_text:
            return "No differences (files are identical)."

        # Build output with header
        lines = [
            "=" * 60,
            f"DIFF: {report.report_id}",
            f"Target: {report.target_file}",
            f"Type: {report.change_type}",
            f"Rationale: {report.rationale}",
            "=" * 60,
            "",
            diff_text,
        ]

        return '\n'.join(lines)

    def review_change(
        self,
        report_id: str,
        approved: bool,
        confirm: str | None = None,
        reviewer: str = "user",
        notes: str = "",
    ) -> ChangeReport | None:
        """Review a staged change.

        IMPORTANT: Approval requires explicit confirmation.

        Args:
            report_id: The report to review
            approved: Whether to approve the change
            confirm: Must be "yes" to approve (safety check)
            reviewer: Who is reviewing
            notes: Decision notes

        Returns:
            Updated ChangeReport, or None if not found

        Raises:
            ValueError: If approving without confirm="yes"
        """
        if report_id not in self.change_reports:
            return None

        report = self.change_reports[report_id]

        if report.status != "staged":
            return report  # Already reviewed

        # Safety check: require explicit confirmation for approval
        if approved and confirm != "yes":
            raise ValueError(
                f"Approval requires confirm='yes'. "
                f"Review the diff first with: scribe.diff('{report_id}')"
            )

        report.status = "approved" if approved else "rejected"
        report.reviewed_at = datetime.now().isoformat()
        report.reviewed_by = reviewer
        report.decision_notes = notes

        if self.auto_save:
            self._save_state()

        return report

    def apply_approved_changes(self) -> list[tuple[str, bool, str]]:
        """Apply all approved changes to Hashtopia.

        Returns:
            List of (report_id, success, message) tuples
        """
        results = []

        approved = [r for r in self.change_reports.values() if r.status == "approved"]

        for report in approved:
            try:
                target_path = self.hashtopia_path / report.target_file

                # Ensure parent directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)

                if report.change_type == "create":
                    # Create new file
                    target_path.write_text(report.proposed_content)
                else:
                    # Update existing file
                    if target_path.exists():
                        current = target_path.read_text()

                        # If section-specific, replace just that section
                        if report.target_section and report.current_content in current:
                            new_content = current.replace(
                                report.current_content,
                                report.proposed_content
                            )
                            target_path.write_text(new_content)
                        elif report.current_content == current:
                            # Full file replacement
                            target_path.write_text(report.proposed_content)
                        else:
                            # Content changed since proposal
                            report.status = "failed"
                            report.decision_notes += " | Content changed since proposal"
                            results.append((
                                report.report_id,
                                False,
                                "Target content changed since proposal was created"
                            ))
                            continue
                    else:
                        # File doesn't exist, create it
                        target_path.write_text(report.proposed_content)

                report.status = "applied"
                report.applied_at = datetime.now().isoformat()
                results.append((report.report_id, True, "Applied successfully"))

            except Exception as e:
                report.status = "failed"
                report.decision_notes += f" | Error: {e}"
                results.append((report.report_id, False, str(e)))

        if self.auto_save:
            self._save_state()

        return results

    # =========================================================================
    # PROMOTION (Staging → Production)
    # =========================================================================

    def set_production_path(self, path: Path | str) -> None:
        """Set or update the production vault path.

        Args:
            path: Path to the production Hashtopia vault
        """
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Production path does not exist: {path}")
        self.production_path = path

    def promote_to_production(
        self,
        file_path: str,
        rationale: str = "",
    ) -> ChangeReport:
        """Propose promoting a file from staging to production vault.

        Reads the file from the staging vault (hashtopia_path) and creates
        a change proposal to write it to the production vault. Still requires
        approval before the write happens.

        Args:
            file_path: Path relative to vault root (e.g., "15. Misc/Example Hashes.md")
            rationale: Why this promotion is being proposed

        Returns:
            Staged ChangeReport for the promotion

        Raises:
            ValueError: If production path not configured or file doesn't exist
        """
        if not self.production_path:
            raise ValueError(
                "Production path not configured. Use set_production_path() first."
            )

        # Read from staging
        staging_content = self.read_page(file_path)
        if staging_content is None:
            raise ValueError(f"File not found in staging vault: {file_path}")

        # Read current production content (if exists)
        production_file = self.production_path / file_path
        if production_file.exists():
            production_content = production_file.read_text()
        else:
            production_content = ""

        # Create promotion proposal
        report_id = f"change_{self._report_count}"
        self._report_count += 1

        report = ChangeReport(
            report_id=report_id,
            created_at=datetime.now().isoformat(),
            change_type=ChangeType.PROMOTE.value,
            target_file=file_path,
            target_section=None,
            current_content=production_content,
            proposed_content=staging_content,
            rationale=rationale or f"Promote {file_path} from staging to production",
            data_sources=["staging_vault"],
            data_qualification=DataQualification.PRODUCTION.value,
            supporting_evidence={
                "staging_vault": str(self.hashtopia_path),
                "production_vault": str(self.production_path),
                "staging_size": len(staging_content),
                "production_size": len(production_content),
            },
            status="staged",
        )

        self.change_reports[report_id] = report

        if self.auto_save:
            self._save_state()

        return report

    def apply_promotions(self) -> list[tuple[str, bool, str]]:
        """Apply all approved promotion changes to the production vault.

        This specifically handles PROMOTE type changes, writing to
        production_path instead of hashtopia_path.

        Returns:
            List of (report_id, success, message) tuples
        """
        if not self.production_path:
            return [("", False, "Production path not configured")]

        results = []

        promotions = [
            r for r in self.change_reports.values()
            if r.status == "approved" and r.change_type == "promote"
        ]

        for report in promotions:
            try:
                target_path = self.production_path / report.target_file

                # Ensure parent directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Write to production
                target_path.write_text(report.proposed_content)

                report.status = "applied"
                report.applied_at = datetime.now().isoformat()
                results.append((
                    report.report_id,
                    True,
                    f"Promoted to {self.production_path.name}/{report.target_file}"
                ))

            except Exception as e:
                report.status = "failed"
                report.decision_notes += f" | Error: {e}"
                results.append((report.report_id, False, str(e)))

        if self.auto_save:
            self._save_state()

        return results

    def list_promotable_files(self) -> list[dict]:
        """List files in staging that differ from production.

        Returns:
            List of dicts with file info and diff status
        """
        if not self.production_path:
            return []

        promotable = []

        for staging_file in self.hashtopia_path.rglob("*.md"):
            if staging_file.name.startswith("."):
                continue

            rel_path = staging_file.relative_to(self.hashtopia_path)
            production_file = self.production_path / rel_path

            staging_content = staging_file.read_text()

            if production_file.exists():
                production_content = production_file.read_text()
                if staging_content != production_content:
                    promotable.append({
                        "file": str(rel_path),
                        "status": "modified",
                        "staging_size": len(staging_content),
                        "production_size": len(production_content),
                    })
            else:
                promotable.append({
                    "file": str(rel_path),
                    "status": "new",
                    "staging_size": len(staging_content),
                    "production_size": 0,
                })

        return promotable

    def promote(self, name: str, rationale: str = "") -> ChangeReport:
        """Promote a file by partial name match (convenience method).

        Args:
            name: Partial filename to match (e.g., "Example Hashes")
            rationale: Optional rationale

        Returns:
            Staged ChangeReport

        Raises:
            ValueError: If no match or multiple matches found
        """
        promotable = self.list_promotable_files()
        matches = [p for p in promotable if name.lower() in p["file"].lower()]

        if not matches:
            raise ValueError(f"No promotable file matching '{name}'")
        if len(matches) > 1:
            files = ", ".join(m["file"] for m in matches)
            raise ValueError(f"Multiple matches for '{name}': {files}")

        return self.promote_to_production(matches[0]["file"], rationale)

    def push(self, rationale: str = "Batch promotion") -> list[ChangeReport]:
        """Promote all modified/new files (convenience method).

        Args:
            rationale: Rationale for all promotions

        Returns:
            List of staged ChangeReports
        """
        promotable = self.list_promotable_files()
        reports = []

        for p in promotable:
            report = self.promote_to_production(p["file"], rationale)
            reports.append(report)

        return reports

    # =========================================================================
    # DISCREPANCY DETECTION
    # =========================================================================

    def record_discrepancy(
        self,
        target_file: str,
        documented_claim: str,
        observed_value: str,
        difference: str,
        significance: str,
        data_source: str,
        qualification: DataQualification | str,
    ) -> DiscrepancyRecord:
        """Record a discrepancy between documented and observed data.

        Args:
            target_file: File containing the claim
            documented_claim: What the documentation says
            observed_value: What was actually observed
            difference: Description of the difference
            significance: low, medium, high, critical
            data_source: Where observation came from
            qualification: Data quality

        Returns:
            The recorded discrepancy
        """
        discrepancy_id = f"discrepancy_{self._discrepancy_count}"
        self._discrepancy_count += 1

        if isinstance(qualification, DataQualification):
            qualification = qualification.value

        record = DiscrepancyRecord(
            discrepancy_id=discrepancy_id,
            detected_at=datetime.now().isoformat(),
            target_file=target_file,
            documented_claim=documented_claim,
            observed_value=observed_value,
            difference=difference,
            significance=significance,
            data_source=data_source,
            qualification=qualification,
        )

        self.discrepancies[discrepancy_id] = record

        if self.auto_save:
            self._save_state()

        return record

    def get_unresolved_discrepancies(self) -> list[DiscrepancyRecord]:
        """Get all unresolved discrepancies.

        Returns:
            List of unresolved DiscrepancyRecords
        """
        return [d for d in self.discrepancies.values() if not d.resolved]

    def resolve_discrepancy(
        self,
        discrepancy_id: str,
        resolution: str,
    ) -> DiscrepancyRecord | None:
        """Mark a discrepancy as resolved.

        Args:
            discrepancy_id: The discrepancy to resolve
            resolution: How it was resolved

        Returns:
            Updated record, or None if not found
        """
        if discrepancy_id not in self.discrepancies:
            return None

        record = self.discrepancies[discrepancy_id]
        record.resolved = True
        record.resolution = resolution

        if self.auto_save:
            self._save_state()

        return record

    # =========================================================================
    # SAMPLE HASH MANAGEMENT
    # =========================================================================

    def register_sample_set(
        self,
        hash_type: str,
        hash_mode: int,
        display_name: str,
        description: str,
        hashes: list[dict],
        source: str,
        qualification: DataQualification | str,
    ) -> SampleHashSet:
        """Register a set of sample hashes.

        Args:
            hash_type: Hash type identifier (e.g., "md5", "ntlmv2")
            hash_mode: Hashcat mode number
            display_name: Human-readable name
            description: Description of the hash set
            hashes: List of hash dicts with 'hash', optional 'plaintext', 'metadata'
            source: Where hashes came from
            qualification: Data quality

        Returns:
            The registered SampleHashSet
        """
        if isinstance(qualification, DataQualification):
            qualification = qualification.value

        sample_set = SampleHashSet(
            hash_type=hash_type,
            hash_mode=hash_mode,
            display_name=display_name,
            description=description,
            hashes=hashes,
            created_at=datetime.now().isoformat(),
            source=source,
            qualification=qualification,
        )

        self.sample_hash_sets[hash_type] = sample_set

        if self.auto_save:
            self._save_state()

        return sample_set

    def get_sample_set(self, hash_type: str) -> SampleHashSet | None:
        """Get a registered sample set.

        Args:
            hash_type: The hash type

        Returns:
            SampleHashSet, or None if not found
        """
        return self.sample_hash_sets.get(hash_type)

    def list_sample_sets(self) -> list[str]:
        """List all registered sample hash types.

        Returns:
            List of hash type identifiers
        """
        return list(self.sample_hash_sets.keys())

    def generate_sample_page(
        self,
        hash_types: list[str] | None = None,
        samples_per_type: int = 10,
        include_plaintexts: bool = False,
    ) -> str:
        """Generate markdown content for sample hash page.

        Args:
            hash_types: Which types to include (None = all)
            samples_per_type: How many samples per type
            include_plaintexts: Whether to include plaintext passwords

        Returns:
            Markdown content for the page
        """
        if hash_types is None:
            hash_types = list(self.sample_hash_sets.keys())

        lines = [
            "# Sample Hash Types",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "These sample hashes are provided for training and testing purposes.",
            "",
        ]

        for hash_type in hash_types:
            sample_set = self.sample_hash_sets.get(hash_type)
            if not sample_set:
                continue

            lines.extend([
                f"## {sample_set.display_name}",
                "",
                f"**Hashcat Mode:** {sample_set.hash_mode}",
                f"**Source:** {sample_set.source}",
                f"**Data Quality:** {sample_set.qualification}",
                "",
                sample_set.description,
                "",
                "```",
            ])

            # Select samples
            samples = sample_set.hashes[:samples_per_type]

            for sample in samples:
                if include_plaintexts and sample.get("plaintext"):
                    lines.append(f"{sample['hash']}  # {sample['plaintext']}")
                else:
                    lines.append(sample["hash"])

            lines.extend([
                "```",
                "",
            ])

        return "\n".join(lines)

    def propose_sample_page_update(
        self,
        target_file: str = "sample_hash_types.md",
        hash_types: list[str] | None = None,
        samples_per_type: int = 10,
    ) -> ChangeReport:
        """Propose an update to the sample hash page.

        Args:
            target_file: Target file path
            hash_types: Which types to include
            samples_per_type: Samples per type

        Returns:
            Staged ChangeReport
        """
        current = self.read_page(target_file) or ""
        proposed = self.generate_sample_page(hash_types, samples_per_type)

        return self.propose_change(
            change_type=ChangeType.ROTATE if current else ChangeType.CREATE,
            target_file=target_file,
            current_content=current,
            proposed_content=proposed,
            rationale="Update sample hash page with current registered hash sets",
            data_sources=list(self.sample_hash_sets.keys()),
            data_qualification=DataQualification.SYNTHETIC,
            supporting_evidence={"sample_counts": {
                k: len(v.hashes) for k, v in self.sample_hash_sets.items()
            }},
        )

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_status_report(self) -> str:
        """Generate a status report.

        Returns:
            Formatted report string
        """
        staged = len([r for r in self.change_reports.values() if r.status == "staged"])
        approved = len([r for r in self.change_reports.values() if r.status == "approved"])
        applied = len([r for r in self.change_reports.values() if r.status == "applied"])
        rejected = len([r for r in self.change_reports.values() if r.status == "rejected"])

        unresolved = len(self.get_unresolved_discrepancies())

        lines = [
            "=" * 70,
            "SCRIBE STATUS REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
            "",
            "CHANGE REPORTS",
            "-" * 40,
            f"  Staged (awaiting review): {staged}",
            f"  Approved (ready to apply): {approved}",
            f"  Applied: {applied}",
            f"  Rejected: {rejected}",
            "",
            "DISCREPANCIES",
            "-" * 40,
            f"  Unresolved: {unresolved}",
            f"  Total recorded: {len(self.discrepancies)}",
            "",
            "SAMPLE HASH SETS",
            "-" * 40,
        ]

        for hash_type, sample_set in self.sample_hash_sets.items():
            lines.append(f"  {sample_set.display_name}: {len(sample_set.hashes)} samples")

        if not self.sample_hash_sets:
            lines.append("  No sample sets registered")

        lines.extend([
            "",
            "OBSERVATION SOURCES",
            "-" * 40,
            f"  Registered: {list(self.observation_sources.keys()) or 'None'}",
            "",
            "=" * 70,
        ])

        return "\n".join(lines)

    def generate_change_review_report(self) -> str:
        """Generate a detailed report of staged changes for review.

        Returns:
            Formatted review report
        """
        staged = self.get_staged_changes()

        if not staged:
            return "No changes staged for review."

        lines = [
            "=" * 70,
            "SCRIBE CHANGE REVIEW",
            f"Generated: {datetime.now().isoformat()}",
            f"Changes awaiting review: {len(staged)}",
            "=" * 70,
        ]

        for report in staged:
            lines.extend([
                "",
                f"[{report.report_id}] {report.change_type.upper()}",
                "-" * 40,
                f"Target: {report.target_file}",
                f"Section: {report.target_section or 'Full file'}",
                f"Data Quality: {report.data_qualification}",
                f"Sources: {', '.join(report.data_sources)}",
                "",
                "RATIONALE:",
                report.rationale,
                "",
                "CURRENT CONTENT:",
                "```",
                report.current_content[:500] + ("..." if len(report.current_content) > 500 else ""),
                "```",
                "",
                "PROPOSED CONTENT:",
                "```",
                report.proposed_content[:500] + ("..." if len(report.proposed_content) > 500 else ""),
                "```",
            ])

        lines.extend([
            "",
            "=" * 70,
            "To approve: scribe.review_change(report_id, approved=True)",
            "To reject:  scribe.review_change(report_id, approved=False)",
            "=" * 70,
        ])

        return "\n".join(lines)

    # =========================================================================
    # CROSS-AGENT COMMUNICATION
    # =========================================================================

    def answer_query(self, question: str, context: dict | None = None) -> str:
        """Answer a query from another agent.

        Args:
            question: The question being asked
            context: Optional context

        Returns:
            Response string
        """
        question_lower = question.lower()

        if "status" in question_lower:
            staged = len(self.get_staged_changes())
            unresolved = len(self.get_unresolved_discrepancies())
            samples = len(self.sample_hash_sets)

            return (
                f"Scribe Status: {staged} changes staged for review, "
                f"{unresolved} unresolved discrepancies, "
                f"{samples} sample hash sets registered. "
                f"Hashtopia path: {self.hashtopia_path}"
            )

        if "staged" in question_lower or "pending" in question_lower:
            staged = self.get_staged_changes()
            if not staged:
                return "No changes currently staged for review."
            return f"{len(staged)} changes staged: " + ", ".join(
                f"{r.report_id} ({r.change_type})" for r in staged
            )

        if "discrepanc" in question_lower:
            unresolved = self.get_unresolved_discrepancies()
            if not unresolved:
                return "No unresolved discrepancies."
            return f"{len(unresolved)} unresolved discrepancies: " + ", ".join(
                f"{d.discrepancy_id} ({d.significance})" for d in unresolved
            )

        if "sample" in question_lower or "hash" in question_lower:
            if not self.sample_hash_sets:
                return "No sample hash sets registered."
            return "Registered sample sets: " + ", ".join(
                f"{s.display_name} ({len(s.hashes)} hashes)"
                for s in self.sample_hash_sets.values()
            )

        if "promot" in question_lower or "production" in question_lower:
            if not self.production_path:
                return "Production vault not configured. Use set_production_path() to enable promotions."
            promotable = self.list_promotable_files()
            if not promotable:
                return f"No files differ between staging and production ({self.production_path.name})."
            return f"{len(promotable)} files ready for promotion to {self.production_path.name}: " + ", ".join(
                f"{p['file']} ({p['status']})" for p in promotable[:5]
            ) + ("..." if len(promotable) > 5 else "")

        return (
            "I am Scribe, the knowledge base curator. "
            "I propose changes to Hashtopia but never write without approval. "
            "Ask me about: status, staged changes, discrepancies, sample hashes, or promotions."
        )

    # =========================================================================
    # PERSONAL CORPUS COLLECTION
    # =========================================================================

    def _init_corpus(self) -> None:
        """Initialize personal corpus storage."""
        self._corpus_entries: list[CorpusEntry] = []
        self._word_frequency: dict[str, int] = defaultdict(int)
        self._bigrams: dict[tuple[str, str], int] = defaultdict(int)
        self._trigrams: dict[tuple[str, str, str], int] = defaultdict(int)
        self._error_candidates: list[dict] = []
        self._corpus_loaded = False

    def _ensure_corpus_loaded(self) -> None:
        """Lazy-load corpus data."""
        if not hasattr(self, '_corpus_loaded') or not self._corpus_loaded:
            self._init_corpus()
            self._load_corpus()
            self._corpus_loaded = True

    def _load_corpus(self) -> None:
        """Load existing corpus from disk."""
        corpus_dir = self._get_corpus_dir()
        if not corpus_dir.exists():
            return

        # Load entries
        entries_file = corpus_dir / "entries.jsonl"
        if entries_file.exists():
            with open(entries_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self._corpus_entries.append(CorpusEntry(**data))

        # Load word frequency
        freq_file = corpus_dir / "word_frequency.json"
        if freq_file.exists():
            with open(freq_file) as f:
                self._word_frequency = defaultdict(int, json.load(f))

        # Load bigrams
        bigrams_file = corpus_dir / "bigrams.json"
        if bigrams_file.exists():
            with open(bigrams_file) as f:
                data = json.load(f)
                self._bigrams = defaultdict(int, {tuple(k.split("|")): v for k, v in data.items()})

        # Load trigrams
        trigrams_file = corpus_dir / "trigrams.json"
        if trigrams_file.exists():
            with open(trigrams_file) as f:
                data = json.load(f)
                self._trigrams = defaultdict(int, {tuple(k.split("|")): v for k, v in data.items()})

        # Load error candidates
        errors_file = corpus_dir / "error_candidates.jsonl"
        if errors_file.exists():
            with open(errors_file) as f:
                for line in f:
                    if line.strip():
                        self._error_candidates.append(json.loads(line))

    def _save_corpus(self) -> None:
        """Save corpus to disk."""
        corpus_dir = self._get_corpus_dir()
        corpus_dir.mkdir(parents=True, exist_ok=True)

        # Save entries (append mode for efficiency)
        entries_file = corpus_dir / "entries.jsonl"
        with open(entries_file, "w") as f:
            for entry in self._corpus_entries:
                f.write(json.dumps(asdict(entry)) + "\n")

        # Save word frequency
        freq_file = corpus_dir / "word_frequency.json"
        with open(freq_file, "w") as f:
            json.dump(dict(self._word_frequency), f, indent=2)

        # Save bigrams
        bigrams_file = corpus_dir / "bigrams.json"
        with open(bigrams_file, "w") as f:
            json.dump({"|".join(k): v for k, v in self._bigrams.items()}, f, indent=2)

        # Save trigrams
        trigrams_file = corpus_dir / "trigrams.json"
        with open(trigrams_file, "w") as f:
            json.dump({"|".join(k): v for k, v in self._trigrams.items()}, f, indent=2)

        # Save error candidates
        errors_file = corpus_dir / "error_candidates.jsonl"
        with open(errors_file, "w") as f:
            for error in self._error_candidates:
                f.write(json.dumps(error) + "\n")

    def _get_corpus_dir(self) -> Path:
        """Get the corpus directory path (in production vault if set)."""
        base = self.production_path if self.production_path else self.hashtopia_path
        return base / ".research" / "personal_corpus"

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words, preserving original form (including errors).

        Args:
            text: Raw input text

        Returns:
            List of words (lowercase, preserving misspellings)
        """
        # Split on whitespace and punctuation, keep words
        words = re.findall(r"[a-zA-Z']+", text.lower())
        return words

    def _detect_potential_errors(self, word: str) -> list[str]:
        """Detect if a word might be a typo.

        Uses simple heuristics - not spell checking, just pattern detection:
        - Repeated characters (tthe → the)
        - Common transpositions (teh → the)
        - Adjacent key errors (adn → and)
        - Missing vowels

        Args:
            word: The word to check

        Returns:
            List of possible correct forms (empty if word looks fine)
        """
        candidates = []

        # Too short to analyze
        if len(word) < 3:
            return []

        # Common known errors (expand this over time from observations)
        known_errors = {
            "teh": "the",
            "adn": "and",
            "tht": "that",
            "waht": "what",
            "wiht": "with",
            "ahve": "have",
            "taht": "that",
            "jsut": "just",
            "hte": "the",
            "yuo": "you",
            "cna": "can",
            "dont": "don't",
            "wont": "won't",
            "cant": "can't",
            "didnt": "didn't",
            "doesnt": "doesn't",
            "isnt": "isn't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "havent": "haven't",
            "hasnt": "hasn't",
            "wouldnt": "wouldn't",
            "shouldnt": "shouldn't",
            "couldnt": "couldn't",
            "thier": "their",
            "recieve": "receive",
            "beleive": "believe",
            "occured": "occurred",
            "seperate": "separate",
            "definately": "definitely",
            "occassion": "occasion",
            "accomodate": "accommodate",
            "untill": "until",
            "begining": "beginning",
            "occuring": "occurring",
            "refering": "referring",
            "arguement": "argument",
            "independant": "independent",
            "knowlege": "knowledge",
            "necesary": "necessary",
            "reasearch": "research",
            "represntative": "representative",
            "potnetially": "potentially",
            "misspellings": "misspellings",  # meta!
        }

        if word in known_errors:
            candidates.append(known_errors[word])

        # Check for doubled letters that might be errors
        doubled = re.sub(r'(.)\1+', r'\1', word)
        if doubled != word and len(doubled) >= 3:
            candidates.append(doubled)

        # Check for transpositions (swap adjacent letters)
        for i in range(len(word) - 1):
            swapped = word[:i] + word[i+1] + word[i] + word[i+2:]
            # Check against known words and personal vocabulary
            word_freq = getattr(self, '_word_frequency', {})
            if swapped in known_errors.values() or swapped in word_freq:
                candidates.append(swapped)

        return list(set(candidates))

    def _classify_error(self, original: str, corrected: str) -> str:
        """Classify the type of typing error.

        Args:
            original: The misspelled word
            corrected: The likely intended word

        Returns:
            Error type classification
        """
        if len(original) == len(corrected):
            # Same length - could be transposition or substitution
            diffs = sum(1 for a, b in zip(original, corrected) if a != b)
            if diffs == 2:
                # Check if it's a transposition
                for i in range(len(original) - 1):
                    if original[i] == corrected[i+1] and original[i+1] == corrected[i]:
                        return "transposition"
            return "substitution"

        if len(original) > len(corrected):
            # Extra character - could be doubling or insertion
            if re.sub(r'(.)\1+', r'\1', original) == corrected:
                return "doubling"
            return "insertion"

        # Missing character
        return "omission"

    def collect_input(self, text: str, session_id: str = "default") -> CorpusEntry:
        """Collect user input into the personal corpus.

        Args:
            text: Raw user input text
            session_id: Optional session identifier

        Returns:
            The created CorpusEntry
        """
        self._ensure_corpus_loaded()

        words = self._tokenize(text)
        potential_errors = []

        for i, word in enumerate(words):
            candidates = self._detect_potential_errors(word)
            if candidates:
                error_info = {
                    "word": word,
                    "position": i,
                    "candidates": candidates,
                    "context": " ".join(words[max(0, i-2):i+3]),
                }
                potential_errors.append(error_info)
                self._error_candidates.append({
                    **error_info,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                })

        entry = CorpusEntry(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            raw_text=text,
            words=words,
            word_count=len(words),
            potential_errors=potential_errors,
        )

        self._corpus_entries.append(entry)

        # Update frequency counts
        for word in words:
            self._word_frequency[word] += 1

        # Update n-grams
        for i in range(len(words) - 1):
            self._bigrams[(words[i], words[i+1])] += 1

        for i in range(len(words) - 2):
            self._trigrams[(words[i], words[i+1], words[i+2])] += 1

        if self.auto_save:
            self._save_corpus()

        return entry

    def collect_session(self, inputs: list[str], session_id: str | None = None) -> list[CorpusEntry]:
        """Collect multiple inputs from a session.

        Args:
            inputs: List of user input strings
            session_id: Optional session identifier (auto-generated if None)

        Returns:
            List of created CorpusEntries
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        entries = []
        for text in inputs:
            if text.strip():
                entries.append(self.collect_input(text, session_id))

        return entries

    def get_word_frequency(self, top_n: int = 100) -> list[tuple[str, int]]:
        """Get word frequency distribution.

        Args:
            top_n: Number of top words to return

        Returns:
            List of (word, count) tuples, sorted by frequency
        """
        self._ensure_corpus_loaded()
        sorted_words = sorted(
            self._word_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_words[:top_n]

    def get_bigrams(self, top_n: int = 50) -> list[tuple[tuple[str, str], int]]:
        """Get most common bigrams.

        Args:
            top_n: Number of top bigrams to return

        Returns:
            List of ((word1, word2), count) tuples
        """
        self._ensure_corpus_loaded()
        sorted_bigrams = sorted(
            self._bigrams.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_bigrams[:top_n]

    def get_trigrams(self, top_n: int = 50) -> list[tuple[tuple[str, str, str], int]]:
        """Get most common trigrams.

        Args:
            top_n: Number of top trigrams to return

        Returns:
            List of ((word1, word2, word3), count) tuples
        """
        self._ensure_corpus_loaded()
        sorted_trigrams = sorted(
            self._trigrams.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_trigrams[:top_n]

    def get_error_patterns(self) -> list[ErrorPattern]:
        """Analyze and categorize detected errors.

        Returns:
            List of ErrorPattern objects
        """
        self._ensure_corpus_loaded()

        # Group errors by (original, likely_intended)
        error_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)

        for error in self._error_candidates:
            word = error["word"]
            for candidate in error.get("candidates", []):
                error_groups[(word, candidate)].append(error)

        patterns = []
        for (original, corrected), instances in error_groups.items():
            error_type = self._classify_error(original, corrected)
            patterns.append(ErrorPattern(
                error_type=error_type,
                original=original,
                likely_intended=corrected,
                frequency=len(instances),
                examples=[e.get("context", "") for e in instances[:5]],
            ))

        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def analyze_corpus(self) -> CorpusAnalysis:
        """Run full analysis on the collected corpus.

        Returns:
            CorpusAnalysis with all metrics
        """
        self._ensure_corpus_loaded()

        total_words = sum(self._word_frequency.values())
        unique_words = len(self._word_frequency)

        analysis = CorpusAnalysis(
            total_entries=len(self._corpus_entries),
            total_words=total_words,
            unique_words=unique_words,
            vocabulary_richness=unique_words / total_words if total_words > 0 else 0,
            word_frequency=dict(self._word_frequency),
            top_bigrams=[(f"{b[0]} {b[1]}", c) for (b, c) in self.get_bigrams(30)],
            top_trigrams=[(f"{t[0]} {t[1]} {t[2]}", c) for (t, c) in self.get_trigrams(20)],
            error_patterns=self.get_error_patterns(),
            typing_velocity_proxy=(
                total_words / len(self._corpus_entries)
                if self._corpus_entries else 0
            ),
        )

        return analysis

    def generate_corpus_report(self) -> str:
        """Generate a human-readable corpus analysis report.

        Returns:
            Formatted report string
        """
        analysis = self.analyze_corpus()

        lines = [
            "=" * 70,
            "PERSONAL CORPUS ANALYSIS",
            f"Generated: {analysis.generated_at}",
            "=" * 70,
            "",
            "OVERVIEW",
            "-" * 40,
            f"  Total entries collected: {analysis.total_entries}",
            f"  Total words: {analysis.total_words:,}",
            f"  Unique words: {analysis.unique_words:,}",
            f"  Vocabulary richness: {analysis.vocabulary_richness:.4f}",
            f"  Avg words per entry: {analysis.typing_velocity_proxy:.1f}",
            "",
            "TOP 20 WORDS",
            "-" * 40,
        ]

        for word, count in self.get_word_frequency(20):
            pct = (count / analysis.total_words * 100) if analysis.total_words > 0 else 0
            lines.append(f"  {word:20} {count:6,} ({pct:5.2f}%)")

        lines.extend([
            "",
            "TOP 10 BIGRAMS (word pairs)",
            "-" * 40,
        ])

        for bigram, count in analysis.top_bigrams[:10]:
            lines.append(f"  {bigram:30} {count:5,}")

        lines.extend([
            "",
            "TOP 10 TRIGRAMS (word triplets)",
            "-" * 40,
        ])

        for trigram, count in analysis.top_trigrams[:10]:
            lines.append(f"  {trigram:40} {count:4,}")

        if analysis.error_patterns:
            lines.extend([
                "",
                "ERROR PATTERNS DETECTED",
                "-" * 40,
            ])

            for pattern in analysis.error_patterns[:15]:
                lines.append(
                    f"  [{pattern.error_type:12}] {pattern.original:15} → "
                    f"{pattern.likely_intended:15} (×{pattern.frequency})"
                )
                if pattern.examples:
                    lines.append(f"    Example: \"{pattern.examples[0]}\"")

        lines.extend([
            "",
            "=" * 70,
            "This corpus represents YOUR unique language patterns.",
            "Errors are signal, not noise - they reveal cognitive/motor patterns.",
            "=" * 70,
        ])

        return "\n".join(lines)

    def save_corpus_to_vault(self) -> str:
        """Save corpus analysis as a private file in the vault.

        Creates/updates .research/personal_corpus/analysis.md

        Returns:
            Path to the saved file
        """
        self._ensure_corpus_loaded()

        corpus_dir = self._get_corpus_dir()
        corpus_dir.mkdir(parents=True, exist_ok=True)

        # Generate the report
        report = self.generate_corpus_report()

        # Save as markdown
        analysis_file = corpus_dir / "analysis.md"
        content = [
            "---",
            "private: true",
            "type: research",
            f"generated: {datetime.now().isoformat()}",
            "---",
            "",
            report,
        ]

        analysis_file.write_text("\n".join(content))

        # Also save raw data
        self._save_corpus()

        return str(analysis_file)

    def get_corpus_stats(self) -> dict:
        """Get quick corpus statistics.

        Returns:
            Dict with basic stats
        """
        self._ensure_corpus_loaded()

        return {
            "entries": len(self._corpus_entries),
            "total_words": sum(self._word_frequency.values()),
            "unique_words": len(self._word_frequency),
            "error_candidates": len(self._error_candidates),
            "bigrams": len(self._bigrams),
            "trigrams": len(self._trigrams),
            "corpus_path": str(self._get_corpus_dir()),
        }

    def get_personal_vocabulary(self) -> set[str]:
        """Get the set of all words in the personal corpus.

        Useful for password candidate generation - these are YOUR words.

        Returns:
            Set of unique words
        """
        self._ensure_corpus_loaded()
        return set(self._word_frequency.keys())

    def export_for_scarab(self) -> list[str]:
        """Export corpus entries for SCARAB analysis.

        Returns:
            List of raw text entries (can be fed to SCARAB as a corpus)
        """
        self._ensure_corpus_loaded()
        return [entry.raw_text for entry in self._corpus_entries]

    def query_corpus(self, query: str, context: dict | None = None) -> str:
        """Answer corpus-related queries from other agents.

        Args:
            query: The question
            context: Optional context

        Returns:
            Response string
        """
        self._ensure_corpus_loaded()

        query_lower = query.lower()
        stats = self.get_corpus_stats()

        if "stats" in query_lower or "status" in query_lower:
            return (
                f"Corpus stats: {stats['entries']} entries, "
                f"{stats['total_words']:,} total words, "
                f"{stats['unique_words']:,} unique words, "
                f"{stats['error_candidates']} potential errors detected."
            )

        if "error" in query_lower or "mistake" in query_lower:
            patterns = self.get_error_patterns()[:5]
            if not patterns:
                return "No error patterns detected yet."
            return "Top error patterns: " + ", ".join(
                f"{p.original}→{p.likely_intended} (×{p.frequency})"
                for p in patterns
            )

        if "word" in query_lower or "frequent" in query_lower:
            top = self.get_word_frequency(10)
            return "Top words: " + ", ".join(f"{w}({c})" for w, c in top)

        if "bigram" in query_lower or "pair" in query_lower:
            top = self.get_bigrams(5)
            return "Top bigrams: " + ", ".join(f"'{b[0]} {b[1]}'({c})" for b, c in top)

        if "vocab" in query_lower or "unique" in query_lower:
            return f"Vocabulary size: {stats['unique_words']:,} unique words"

        return (
            f"Personal corpus: {stats['entries']} entries, "
            f"{stats['total_words']:,} words. "
            "Query about: stats, errors, words, bigrams, vocabulary."
        )

    def end_session(
        self,
        session_inputs: list[str],
        session_id: str | None = None,
        commit_message: str | None = None,
    ) -> dict:
        """End a session by collecting all inputs and saving corpus.

        Call this at the end of each session to:
        1. Collect all user inputs from the session
        2. Update word frequency and n-gram statistics
        3. Detect and log potential typing errors
        4. Save corpus data to the vault
        5. Generate analysis report

        Args:
            session_inputs: List of all user input strings from the session
            session_id: Optional session identifier (auto-generated if None)
            commit_message: Optional message for git commit

        Returns:
            Dict with session summary including:
            - entries_added: Number of new entries
            - words_collected: Total words from this session
            - errors_detected: Potential typos found
            - corpus_stats: Updated corpus statistics
            - analysis_path: Path to saved analysis file
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Collect all inputs
        entries = self.collect_session(session_inputs, session_id)

        # Calculate session stats
        session_words = sum(e.word_count for e in entries)
        session_errors = sum(len(e.potential_errors) for e in entries)

        # Save corpus to vault
        analysis_path = self.save_corpus_to_vault()

        # Get updated stats
        corpus_stats = self.get_corpus_stats()

        return {
            "session_id": session_id,
            "entries_added": len(entries),
            "words_collected": session_words,
            "errors_detected": session_errors,
            "corpus_stats": corpus_stats,
            "analysis_path": analysis_path,
            "commit_message": commit_message or f"Corpus update: session {session_id}",
        }
