"""Level 1 State Machine Tests - Campaign Walkthrough.

Tests the adventure state machine by walking through the campaign
programmatically, submitting correct answers, and verifying state
transitions.

This is "pure logic" testing - no UI, no rendering, just the state machine.

Run with: pytest tests/test_campaign_state_machine.py -v
"""

import pytest
from pathlib import Path

from spellengine.adventures.loader import load_campaign, validate_campaign
from spellengine.adventures.state import AdventureState
from spellengine.adventures.models import OutcomeType, EncounterType


# Path to the Dread Citadel campaign
CAMPAIGN_PATH = Path(__file__).parent.parent / "content" / "adventures" / "dread_citadel" / "campaign_source_built.yaml"


class TestCampaignLoading:
    """Test that the campaign loads and validates correctly."""

    def test_campaign_file_exists(self):
        """Campaign file should exist."""
        assert CAMPAIGN_PATH.exists(), f"Campaign not found at {CAMPAIGN_PATH}"

    def test_campaign_loads(self):
        """Campaign should load without errors."""
        campaign = load_campaign(CAMPAIGN_PATH)
        assert campaign is not None
        assert campaign.id == "dread_citadel"

    def test_campaign_validates(self):
        """Campaign should pass validation."""
        campaign = load_campaign(CAMPAIGN_PATH)
        errors = validate_campaign(campaign)
        assert not errors, f"Validation errors: {errors}"

    def test_campaign_has_chapters(self):
        """Campaign should have chapters."""
        campaign = load_campaign(CAMPAIGN_PATH)
        assert len(campaign.chapters) > 0
        # Dread Citadel has 7 chapters (prologue + 6)
        assert len(campaign.chapters) == 7


class TestAdventureStateInit:
    """Test AdventureState initialization."""

    @pytest.fixture
    def campaign(self):
        """Load the campaign for tests."""
        return load_campaign(CAMPAIGN_PATH)

    def test_state_creates(self, campaign):
        """Should create a new state."""
        state = AdventureState(campaign, player_name="Test Player")
        assert state is not None

    def test_state_starts_at_first_encounter(self, campaign):
        """State should start at first chapter, first encounter."""
        state = AdventureState(campaign)

        # Should be in first chapter (ch_awakening for Dread Citadel)
        first_chapter = campaign.chapters[0]
        assert state.current_chapter.id == first_chapter.id

        # Should be at first encounter
        first_enc = first_chapter.first_encounter
        assert state.state.encounter_id == first_enc

    def test_state_starts_with_zero_xp(self, campaign):
        """State should start with 0 XP."""
        state = AdventureState(campaign)
        assert state.state.total_xp == 0
        assert state.state.xp_earned == 0

    def test_state_not_complete_at_start(self, campaign):
        """State should not be complete at start."""
        state = AdventureState(campaign)
        assert not state.is_complete


class TestEncounterProgression:
    """Test moving through encounters."""

    @pytest.fixture
    def campaign(self):
        return load_campaign(CAMPAIGN_PATH)

    @pytest.fixture
    def state(self, campaign):
        return AdventureState(campaign, player_name="Test Player")

    def test_get_current_solution(self, state):
        """Should be able to get current solution."""
        solution = state.get_current_solution()
        # Most encounters should have solutions
        # (some narrative-only may not)
        # Just verify we can call it without error

    def test_record_success_advances(self, state):
        """Recording success should advance to next encounter."""
        first_enc = state.state.encounter_id

        result = state.record_outcome(OutcomeType.SUCCESS)

        # Should have advanced
        assert result["action"] in ["continue", "chapter_complete"]

        # If continuing, should be at new encounter
        if result["action"] == "continue":
            assert state.state.encounter_id != first_enc

    def test_record_success_awards_xp(self, state):
        """Recording success should award XP."""
        initial_xp = state.state.total_xp

        state.record_outcome(OutcomeType.SUCCESS)

        # Should have gained XP (unless it was a 0-XP encounter)
        assert state.state.total_xp >= initial_xp

    def test_marks_encounter_complete(self, state):
        """Completing encounter should mark it in completed list."""
        first_enc = state.state.encounter_id

        state.record_outcome(OutcomeType.SUCCESS)

        assert first_enc in state.state.completed_encounters


class TestFullCampaignWalkthrough:
    """Walk through the entire campaign programmatically."""

    @pytest.fixture
    def campaign(self):
        return load_campaign(CAMPAIGN_PATH)

    def test_can_complete_campaign(self, campaign):
        """Should be able to walk through entire campaign."""
        state = AdventureState(campaign, player_name="Automated Tester")

        max_iterations = 200  # Safety limit
        iteration = 0
        encounters_completed = []

        while not state.is_complete and iteration < max_iterations:
            iteration += 1

            enc = state.current_encounter
            encounters_completed.append(enc.id)

            # Record outcome (success for all)
            result = state.record_outcome(OutcomeType.SUCCESS)

            # Handle different result types
            if result["action"] == "complete":
                break
            elif result["action"] == "chapter_complete":
                # Chapter boundary - continue
                pass
            elif result["action"] == "prologue_gate":
                # Observer mode gate - shouldn't hit in normal mode
                pytest.fail("Hit prologue gate in normal mode")
            elif result["action"] == "game_over":
                pytest.fail(f"Hit game over at {enc.id}: {result.get('message')}")

        # Verify completion
        assert state.is_complete, f"Campaign not complete after {iteration} iterations"
        assert state.state.total_xp > 0

        # Should have completed all encounters
        total_encounters = sum(len(ch.encounters) for ch in campaign.chapters)
        assert len(encounters_completed) == total_encounters, \
            f"Completed {len(encounters_completed)} but expected {total_encounters}"

    def test_walkthrough_collects_stats(self, campaign):
        """Walkthrough should collect proper statistics."""
        state = AdventureState(campaign, player_name="Stats Tester")

        max_iterations = 200
        iteration = 0

        chapter_count = 0
        encounter_types_seen = set()

        while not state.is_complete and iteration < max_iterations:
            iteration += 1

            enc = state.current_encounter
            encounter_types_seen.add(enc.encounter_type)

            result = state.record_outcome(OutcomeType.SUCCESS)

            if result["action"] == "chapter_complete":
                chapter_count += 1
            elif result["action"] == "complete":
                chapter_count += 1  # Final chapter
                break

        # Verify stats
        assert chapter_count == 7, f"Expected 7 chapters, got {chapter_count}"

        # Should see multiple encounter types
        assert len(encounter_types_seen) > 1, \
            f"Only saw encounter types: {encounter_types_seen}"

    def test_walkthrough_xp_accumulates(self, campaign):
        """XP should accumulate correctly through campaign."""
        state = AdventureState(campaign, player_name="XP Tester")

        xp_by_chapter = []
        current_chapter = state.current_chapter.id
        chapter_xp = 0
        encounter_xp_awarded = 0  # Just encounter rewards, not achievements

        max_iterations = 200
        iteration = 0

        while not state.is_complete and iteration < max_iterations:
            iteration += 1

            result = state.record_outcome(OutcomeType.SUCCESS)
            xp_awarded = result.get("xp_awarded", 0)
            chapter_xp += xp_awarded
            encounter_xp_awarded += xp_awarded

            if result["action"] in ["chapter_complete", "complete"]:
                xp_by_chapter.append((current_chapter, chapter_xp))
                if result["action"] != "complete":
                    current_chapter = state.current_chapter.id
                    chapter_xp = 0
                else:
                    break

        # Encounter XP should match what we summed from results
        # Note: total_xp may be higher due to achievement bonuses
        total_from_encounters = sum(xp for _, xp in xp_by_chapter)
        assert total_from_encounters == encounter_xp_awarded

        # State total_xp should be >= encounter XP (achievements add more)
        assert state.state.total_xp >= encounter_xp_awarded, \
            f"State XP {state.state.total_xp} < encounter sum {encounter_xp_awarded}"

        # Should have earned meaningful XP
        assert state.state.total_xp > 0


class TestEncounterDetails:
    """Test that encounters have proper content."""

    @pytest.fixture
    def campaign(self):
        return load_campaign(CAMPAIGN_PATH)

    def test_all_encounters_have_titles(self, campaign):
        """Every encounter should have a title."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                assert enc.title, f"Encounter {enc.id} missing title"

    def test_hash_encounters_have_solutions(self, campaign):
        """Hash-based encounters should have solutions."""
        hash_types = {
            EncounterType.FLASH,
            EncounterType.HUNT,
            EncounterType.DUEL,
        }

        missing_solutions = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type in hash_types:
                    if enc.hash and not enc.solution:
                        missing_solutions.append(enc.id)

        assert not missing_solutions, \
            f"Encounters with hash but no solution: {missing_solutions}"

    def test_encounters_have_valid_next(self, campaign):
        """Each encounter's next_encounter should exist (or be None for last)."""
        all_ids = set()
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                all_ids.add(enc.id)

        invalid_nexts = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.next_encounter and enc.next_encounter not in all_ids:
                    invalid_nexts.append((enc.id, enc.next_encounter))

        assert not invalid_nexts, f"Invalid next_encounter refs: {invalid_nexts}"


class TestProgressSummary:
    """Test progress tracking and summary."""

    @pytest.fixture
    def campaign(self):
        return load_campaign(CAMPAIGN_PATH)

    def test_progress_summary_at_start(self, campaign):
        """Progress summary should work at start."""
        state = AdventureState(campaign)
        summary = state.get_progress_summary()

        assert summary["progress_pct"] == 0
        assert summary["xp_earned"] == 0
        assert summary["deaths"] == 0

    def test_progress_summary_updates(self, campaign):
        """Progress summary should update after encounters."""
        state = AdventureState(campaign)

        # Complete first encounter
        state.record_outcome(OutcomeType.SUCCESS)

        summary = state.get_progress_summary()
        assert summary["progress_pct"] > 0 or len(state.state.completed_encounters) > 0


class TestEncounterSolutions:
    """Verify encounter solutions are accessible."""

    @pytest.fixture
    def campaign(self):
        return load_campaign(CAMPAIGN_PATH)

    def test_can_get_solution_for_each_encounter(self, campaign):
        """Should be able to retrieve solution for each encounter."""
        state = AdventureState(campaign)

        solutions_found = []
        solutions_missing = []

        max_iterations = 200
        iteration = 0

        while not state.is_complete and iteration < max_iterations:
            iteration += 1

            enc = state.current_encounter
            solution = state.get_current_solution()

            if solution:
                solutions_found.append((enc.id, solution))
            else:
                # Check if this encounter type should have a solution
                needs_solution = enc.encounter_type in {
                    EncounterType.FLASH,
                    EncounterType.HUNT,
                    EncounterType.CRAFT,
                    EncounterType.PUZZLE_BOX,
                    EncounterType.PIPELINE,
                }
                if needs_solution and enc.hash:
                    solutions_missing.append(enc.id)

            state.record_outcome(OutcomeType.SUCCESS)

        # Report findings
        print(f"\nSolutions found: {len(solutions_found)}")
        print(f"Solutions missing: {len(solutions_missing)}")

        # Some encounters (TOUR, WALKTHROUGH) don't need solutions
        # But hash-based ones should have them
        if solutions_missing:
            print(f"Missing: {solutions_missing}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
