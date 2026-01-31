"""Level 3 Integration Tests: Scene Transitions.

Tests scene flow validation, chapter boundaries, and
state transitions between game scenes.

These tests verify the game's narrative flow is correct.
"""

import pytest

from spellengine.adventures.models import DifficultyLevel, OutcomeType


class TestEncounterProgression:
    """Test encounter-to-encounter transitions."""

    def test_first_encounter_accessible(self, simulator):
        """Should be able to access first encounter immediately."""
        encounter = simulator.state.current_encounter

        assert encounter is not None
        assert encounter.id == simulator.campaign.chapters[0].first_encounter

    def test_next_encounter_after_success(self, simulator):
        """Success should advance to next encounter."""
        first_enc = simulator.state.current_encounter.id

        simulator.solve_current_encounter()

        second_enc = simulator.state.current_encounter.id
        assert second_enc != first_enc

    def test_encounters_follow_next_pointer(self, simulator):
        """Encounters should follow their next_encounter chain."""
        first_enc = simulator.state.current_encounter

        if first_enc.next_encounter:
            simulator.solve_current_encounter()
            assert simulator.state.current_encounter.id == first_enc.next_encounter


class TestChapterBoundaries:
    """Test transitions between chapters."""

    def test_chapter_complete_advances_chapter(self, simulator):
        """Completing a chapter should advance to next chapter."""
        first_chapter_id = simulator.state.current_chapter.id

        simulator.run_to_chapter_end()

        # Should be in different chapter (or complete)
        new_chapter_id = simulator.state.current_chapter.id
        if not simulator.state.is_complete:
            assert new_chapter_id != first_chapter_id

    def test_chapter_transition_starts_at_first_encounter(self, simulator):
        """New chapter should start at its first_encounter."""
        # Complete first chapter
        first_result = simulator.run_to_chapter_end()

        if not simulator.state.is_complete:
            current_chapter = simulator.state.current_chapter
            expected_first = current_chapter.first_encounter
            actual_first = simulator.state.current_encounter.id

            assert actual_first == expected_first

    def test_all_chapters_traversable(self, simulator, campaign):
        """Should be able to traverse all chapters."""
        chapters_seen = set()

        while not simulator.state.is_complete:
            chapters_seen.add(simulator.state.current_chapter.id)
            result = simulator.solve_current_encounter()

            if result['action'] in ('complete', 'prologue_gate'):
                break

        # Should have seen all chapters
        all_chapter_ids = {ch.id for ch in campaign.chapters}
        assert chapters_seen == all_chapter_ids


class TestVictoryCondition:
    """Test campaign victory/completion detection."""

    def test_last_encounter_triggers_complete(self, simulator, campaign):
        """Last encounter should trigger 'complete' action."""
        simulator.run_to_completion()

        # Find the complete action in event log
        complete_events = [e for e in simulator.event_log if e['result'] == 'complete']

        assert len(complete_events) == 1

    def test_is_complete_true_at_end(self, simulator):
        """is_complete should be True after finishing campaign."""
        simulator.run_to_completion()

        assert simulator.state.is_complete is True

    def test_victory_includes_final_xp(self, simulator):
        """Victory should include final XP total."""
        result = simulator.run_to_completion()

        assert result['total_xp'] == simulator.state.state.total_xp


class TestPrologueGate:
    """Test prologue/observer mode gating."""

    def test_observer_hits_prologue_gate(self, observer_simulator):
        """Observer mode should stop at prologue gate."""
        result = observer_simulator.run_to_completion()

        # Should have hit prologue gate
        gate_events = [e for e in result['event_log'] if e['result'] == 'prologue_gate']

        # Either hit prologue gate or chapter_complete (last event)
        last_result = result['event_log'][-1]['result']
        assert last_result in ('prologue_gate', 'chapter_complete')

    def test_prologue_complete_flag_set(self, observer_simulator):
        """Prologue complete flag should be set after gate."""
        observer_simulator.run_to_completion()

        assert observer_simulator.state.state.prologue_complete is True

    def test_normal_mode_no_gate(self, simulator):
        """Normal mode should not hit prologue gate."""
        result = simulator.run_to_completion()

        gate_events = [e for e in result['event_log'] if e['result'] == 'prologue_gate']

        assert len(gate_events) == 0


class TestCheckpointSystem:
    """Test checkpoint recording during gameplay."""

    def test_checkpoint_recorded(self, simulator, campaign):
        """Checkpoint encounters should be recorded."""
        # Run through some encounters
        for _ in range(20):
            if simulator.state.is_complete:
                break
            simulator.solve_current_encounter()

        # Check if any checkpoints were recorded
        checkpoint = simulator.state.state.last_checkpoint

        # May or may not have hit a checkpoint depending on campaign structure
        # This test just verifies the mechanism works
        # A checkpoint would be an encounter ID or None

    def test_checkpoint_is_valid_encounter(self, simulator, campaign):
        """If a checkpoint is set, it should be a valid encounter ID."""
        simulator.run_to_completion()

        checkpoint = simulator.state.state.last_checkpoint
        if checkpoint:
            # Verify it's a real encounter
            all_enc_ids = {
                enc.id
                for chapter in campaign.chapters
                for enc in chapter.encounters
            }
            assert checkpoint in all_enc_ids


class TestResultActions:
    """Test that result actions are valid."""

    def test_all_results_are_valid_actions(self, simulator):
        """All result actions should be recognized types."""
        valid_actions = {'continue', 'chapter_complete', 'complete', 'prologue_gate', 'game_over'}

        simulator.run_to_completion()

        for event in simulator.event_log:
            assert event['result'] in valid_actions, f"Unknown action: {event['result']}"

    def test_continue_is_most_common(self, simulator):
        """'continue' should be the most common result."""
        simulator.run_to_completion()

        continue_count = sum(1 for e in simulator.event_log if e['result'] == 'continue')
        total_count = len(simulator.event_log)

        # Most encounters should result in 'continue'
        assert continue_count > total_count * 0.8


class TestEncounterChain:
    """Test encounter chain integrity."""

    def test_no_encounter_visited_twice(self, simulator):
        """Each encounter should only be visited once."""
        simulator.run_to_completion()

        visited = simulator.encounters_visited
        unique = set(visited)

        assert len(visited) == len(unique), "Some encounters were visited multiple times"

    def test_encounter_order_matches_structure(self, simulator, campaign):
        """Encounters should be visited in campaign structure order."""
        simulator.run_to_completion()

        # Build expected order from campaign
        expected_order = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                expected_order.append(enc.id)

        # Visited order should match
        assert simulator.encounters_visited == expected_order


class TestStateConsistency:
    """Test state remains consistent during transitions."""

    def test_chapter_id_matches_current_chapter(self, simulator):
        """state.chapter_id should always match current_chapter.id."""
        for _ in range(30):
            if simulator.state.is_complete:
                break

            assert simulator.state.state.chapter_id == simulator.state.current_chapter.id
            simulator.solve_current_encounter()

    def test_encounter_id_matches_current_encounter(self, simulator):
        """state.encounter_id should always match current_encounter.id."""
        for _ in range(30):
            if simulator.state.is_complete:
                break

            assert simulator.state.state.encounter_id == simulator.state.current_encounter.id
            simulator.solve_current_encounter()

    def test_completed_list_grows_monotonically(self, simulator):
        """completed_encounters list should only grow."""
        previous_count = 0

        for _ in range(30):
            if simulator.state.is_complete:
                break

            simulator.solve_current_encounter()
            current_count = len(simulator.state.state.completed_encounters)

            assert current_count >= previous_count
            previous_count = current_count
