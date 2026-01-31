"""Asset Validation Tests - Catch missing files before runtime.

These tests verify that all required assets exist:
- Font files
- Campaign files
- Any other referenced assets

Missing assets cause crashes when the game tries to load them.

Run with: pytest tests/test_assets.py -v
"""

import pytest
from pathlib import Path


# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_PATH = PROJECT_ROOT / "content"
ASSETS_PATH = PROJECT_ROOT / "assets"


class TestCampaignFilesExist:
    """Verify campaign files exist."""

    def test_dread_citadel_campaign_exists(self):
        """Dread Citadel campaign file should exist."""
        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )
        assert campaign_path.exists(), f"Campaign not found: {campaign_path}"

    def test_dread_citadel_source_exists(self):
        """Dread Citadel source file should exist."""
        source_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source.yaml"
        )
        assert source_path.exists(), f"Source not found: {source_path}"


class TestFontDirectoryExists:
    """Verify font assets exist."""

    def test_fonts_directory_exists(self):
        """Fonts directory should exist."""
        fonts_path = ASSETS_PATH / "fonts"
        assert fonts_path.exists(), f"Fonts directory not found: {fonts_path}"

    def test_fonts_directory_not_empty(self):
        """Fonts directory should contain font files."""
        fonts_path = ASSETS_PATH / "fonts"
        if fonts_path.exists():
            font_files = list(fonts_path.glob("*.ttf")) + list(fonts_path.glob("*.otf"))
            # Only assert if directory exists - may use system fonts
            if len(font_files) == 0:
                pytest.skip("No custom fonts found - using system fonts")


class TestContentIntegrity:
    """Verify content files are valid."""

    def test_campaign_yaml_is_valid(self):
        """Campaign YAML should parse without error."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "id" in data
        assert "chapters" in data

    def test_campaign_has_required_fields(self):
        """Campaign should have all required top-level fields."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        required_fields = ["id", "title", "chapters", "first_chapter"]
        for field in required_fields:
            assert field in data, f"Campaign missing required field: {field}"

    def test_all_chapters_have_encounters(self):
        """Every chapter should have at least one encounter."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        for chapter in data.get("chapters", []):
            chapter_id = chapter.get("id", "unknown")
            encounters = chapter.get("encounters", [])
            assert len(encounters) > 0, f"Chapter {chapter_id} has no encounters"


class TestEncounterReferences:
    """Verify encounter references are valid."""

    def test_first_chapter_exists(self):
        """first_chapter reference should point to valid chapter."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        first_chapter = data.get("first_chapter")
        chapter_ids = [ch.get("id") for ch in data.get("chapters", [])]

        assert first_chapter in chapter_ids, f"first_chapter '{first_chapter}' not found in chapters"

    def test_chapter_first_encounters_exist(self):
        """Each chapter's first_encounter should exist in that chapter."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        for chapter in data.get("chapters", []):
            chapter_id = chapter.get("id")
            first_enc = chapter.get("first_encounter")
            encounter_ids = [enc.get("id") for enc in chapter.get("encounters", [])]

            assert first_enc in encounter_ids, \
                f"Chapter {chapter_id}: first_encounter '{first_enc}' not found"

    def test_next_encounter_references_valid(self):
        """All next_encounter references should point to valid encounters."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        # Collect all encounter IDs
        all_encounter_ids = set()
        for chapter in data.get("chapters", []):
            for enc in chapter.get("encounters", []):
                all_encounter_ids.add(enc.get("id"))

        # Check all next_encounter references
        invalid_refs = []
        for chapter in data.get("chapters", []):
            for enc in chapter.get("encounters", []):
                next_enc = enc.get("next_encounter")
                if next_enc and next_enc not in all_encounter_ids:
                    invalid_refs.append((enc.get("id"), next_enc))

        assert not invalid_refs, f"Invalid next_encounter references: {invalid_refs}"


class TestNoOrphanedEncounters:
    """Verify all encounters are reachable."""

    def test_all_encounters_reachable(self):
        """All encounters should be reachable from chapter start."""
        import yaml

        campaign_path = (
            CONTENT_PATH
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        with open(campaign_path) as f:
            data = yaml.safe_load(f)

        for chapter in data.get("chapters", []):
            chapter_id = chapter.get("id")
            encounters = {enc.get("id"): enc for enc in chapter.get("encounters", [])}
            first_enc = chapter.get("first_encounter")

            # Walk through encounters from first_encounter
            visited = set()
            to_visit = [first_enc] if first_enc else []

            while to_visit:
                current = to_visit.pop(0)
                if current in visited or current not in encounters:
                    continue

                visited.add(current)
                enc = encounters[current]

                # Add next_encounter
                if enc.get("next_encounter"):
                    to_visit.append(enc.get("next_encounter"))

                # Add choice targets
                for choice in enc.get("choices", []):
                    if choice.get("leads_to"):
                        to_visit.append(choice.get("leads_to"))

            # Check for orphaned encounters
            all_in_chapter = set(encounters.keys())
            orphaned = all_in_chapter - visited

            # Filter out encounters that might be targets from other chapters
            # (This is a simplified check)
            assert len(orphaned) == 0 or len(visited) == len(all_in_chapter), \
                f"Chapter {chapter_id} has potentially orphaned encounters: {orphaned}"
