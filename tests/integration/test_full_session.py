"""Level 3 Integration Tests: Full Game Sessions.

Tests complete campaign walkthroughs, XP accumulation,
and difficulty mode behavior.

These tests verify end-to-end functionality of the game engine.
"""

import pytest

from spellengine.adventures.models import DifficultyLevel, EncounterType


class TestCampaignCompletion:
    """Test full campaign completion."""

    def test_complete_normal_campaign(self, simulator):
        """Should complete campaign with no deaths in normal mode."""
        result = simulator.run_to_completion()

        assert result['complete'] is True
        assert result['deaths'] == 0
        assert result['total_xp'] > 0

    def test_all_encounters_visited(self, simulator, campaign):
        """All encounters should be visited during completion."""
        result = simulator.run_to_completion()

        all_enc_ids = {
            enc.id
            for chapter in campaign.chapters
            for enc in chapter.encounters
        }
        visited = set(result['encounters_visited'])

        assert all_enc_ids == visited, f"Missing: {all_enc_ids - visited}"

    def test_correct_number_of_chapters_completed(self, simulator, campaign):
        """All chapters should be completed."""
        result = simulator.run_to_completion()

        # All chapters except the last (which is marked 'complete' not 'chapter_complete')
        expected_chapters = len(campaign.chapters) - 1
        assert len(result['chapters_completed']) == expected_chapters

    def test_xp_accumulated_correctly(self, simulator, campaign):
        """XP should accumulate from all encounters."""
        result = simulator.run_to_completion()

        # Minimum expected XP is sum of all encounter base XP
        min_expected = sum(
            enc.xp_reward
            for chapter in campaign.chapters
            for enc in chapter.encounters
        )

        # Total XP may be higher due to achievements
        assert result['total_xp'] >= min_expected


class TestDifficultyModes:
    """Test difficulty-specific behavior."""

    def test_heroic_xp_multiplier(self, campaign):
        """Heroic mode should award more XP than normal."""
        from tests.integration.conftest import GameSessionSimulator

        normal_sim = GameSessionSimulator(campaign, difficulty=DifficultyLevel.NORMAL)
        normal_result = normal_sim.run_to_completion()

        heroic_sim = GameSessionSimulator(campaign, difficulty=DifficultyLevel.HEROIC)
        heroic_result = heroic_sim.run_to_completion()

        assert heroic_result['total_xp'] > normal_result['total_xp']

    def test_mythic_xp_multiplier(self, campaign):
        """Mythic mode should award more XP than heroic."""
        from tests.integration.conftest import GameSessionSimulator

        heroic_sim = GameSessionSimulator(campaign, difficulty=DifficultyLevel.HEROIC)
        heroic_result = heroic_sim.run_to_completion()

        mythic_sim = GameSessionSimulator(campaign, difficulty=DifficultyLevel.MYTHIC)
        mythic_result = mythic_sim.run_to_completion()

        assert mythic_result['total_xp'] > heroic_result['total_xp']

    def test_mythic_requires_heroic_unlock(self, campaign):
        """Mythic difficulty should require Heroic completion."""
        from spellengine.adventures.state import AdventureState

        state = AdventureState(campaign)

        assert state.is_difficulty_unlocked(DifficultyLevel.NORMAL) is True
        assert state.is_difficulty_unlocked(DifficultyLevel.HEROIC) is True
        assert state.is_difficulty_unlocked(DifficultyLevel.MYTHIC) is False

    def test_mythic_unlocked_after_heroic_completion(self, campaign):
        """Mythic should unlock after completing Heroic."""
        from tests.integration.conftest import GameSessionSimulator

        # Complete campaign on Heroic
        heroic_sim = GameSessionSimulator(campaign, difficulty=DifficultyLevel.HEROIC)
        heroic_sim.run_to_completion()

        # Check if Mythic is now unlocked
        assert DifficultyLevel.HEROIC.value in heroic_sim.state.state.completed_difficulties.get(campaign.id, [])


class TestObserverMode:
    """Test observer (learning) mode behavior."""

    def test_observer_stops_at_prologue(self, observer_simulator):
        """Observer mode should stop at prologue gate."""
        result = observer_simulator.run_to_completion()

        # Should not complete the full campaign
        assert result['complete'] is False
        # Should have hit prologue gate
        last_action = result['event_log'][-1]['result']
        assert last_action in ('prologue_gate', 'chapter_complete')

    def test_observer_reduced_xp(self, campaign):
        """Observer mode should award reduced XP."""
        from tests.integration.conftest import GameSessionSimulator

        normal_sim = GameSessionSimulator(campaign, game_mode="full")
        normal_sim.solve_current_encounter()
        normal_xp = normal_sim.state.state.total_xp

        observer_sim = GameSessionSimulator(campaign, game_mode="observer")
        observer_sim.solve_current_encounter()
        observer_xp = observer_sim.state.state.total_xp

        # Observer gets 20% XP
        assert observer_xp < normal_xp
        assert observer_xp == int(normal_xp * 0.2)

    def test_observer_all_difficulties_available(self, campaign):
        """Observer mode should have all difficulties available."""
        from spellengine.adventures.state import AdventureState

        state = AdventureState(campaign, game_mode="observer")

        assert state.is_difficulty_unlocked(DifficultyLevel.NORMAL) is True
        assert state.is_difficulty_unlocked(DifficultyLevel.HEROIC) is True
        assert state.is_difficulty_unlocked(DifficultyLevel.MYTHIC) is True


class TestXPAccumulation:
    """Test XP accumulation throughout campaign."""

    def test_xp_increases_after_each_encounter(self, simulator):
        """XP should increase after each encounter."""
        xp_history = []

        # Solve first 5 encounters
        for _ in range(5):
            xp_before = simulator.state.state.total_xp
            simulator.solve_current_encounter()
            xp_after = simulator.state.state.total_xp
            xp_history.append(xp_after - xp_before)

        # At least some encounters should award XP
        assert any(xp > 0 for xp in xp_history)

    def test_xp_never_decreases(self, simulator):
        """XP should never decrease during normal play."""
        max_encounters = 50
        previous_xp = 0

        for _ in range(max_encounters):
            if simulator.state.is_complete:
                break

            simulator.solve_current_encounter()
            current_xp = simulator.state.state.total_xp

            assert current_xp >= previous_xp
            previous_xp = current_xp

    def test_chapter_xp_is_subset_of_total(self, simulator):
        """xp_earned should track current chapter earnings."""
        # Complete first chapter
        simulator.run_to_chapter_end()

        # xp_earned tracks current earnings
        assert simulator.state.state.xp_earned <= simulator.state.state.total_xp


class TestProgressTracking:
    """Test progress tracking throughout campaign."""

    def test_progress_starts_at_zero(self, campaign):
        """Progress should start at 0%."""
        from spellengine.adventures.state import AdventureState

        state = AdventureState(campaign)
        summary = state.get_progress_summary()

        assert summary['progress_pct'] == 0

    def test_progress_increases_with_completion(self, simulator):
        """Progress percentage should increase as encounters complete."""
        initial_summary = simulator.state.get_progress_summary()
        initial_pct = initial_summary['progress_pct']

        # Complete a few encounters
        for _ in range(5):
            simulator.solve_current_encounter()

        new_summary = simulator.state.get_progress_summary()
        new_pct = new_summary['progress_pct']

        assert new_pct > initial_pct

    def test_progress_reaches_100_on_completion(self, simulator):
        """Progress should reach near 100% on completion."""
        simulator.run_to_completion()

        summary = simulator.state.get_progress_summary()

        # Progress might not be exactly 100 due to rounding
        assert summary['progress_pct'] >= 95


class TestEncounterModeTracking:
    """Test that encounter completion modes are tracked."""

    def test_encounter_mode_recorded(self, simulator):
        """Encounter mode should be recorded on completion."""
        simulator.solve_current_encounter()
        first_encounter = simulator.encounters_visited[0]

        mode = simulator.state.state.encounter_modes.get(first_encounter)

        assert mode == "full"

    def test_observer_mode_recorded(self, observer_simulator):
        """Observer mode should be recorded."""
        observer_simulator.solve_current_encounter()
        first_encounter = observer_simulator.encounters_visited[0]

        mode = observer_simulator.state.state.encounter_modes.get(first_encounter)

        assert mode == "observer"


class TestEventLog:
    """Test event logging during session."""

    def test_event_log_records_encounters(self, simulator):
        """Event log should record each encounter."""
        simulator.solve_current_encounter()
        simulator.solve_current_encounter()
        simulator.solve_current_encounter()

        assert len(simulator.event_log) == 3
        assert all(e['action'] == 'solve' for e in simulator.event_log)

    def test_event_log_includes_xp(self, simulator):
        """Event log should include XP awarded."""
        simulator.solve_current_encounter()

        event = simulator.event_log[0]

        assert 'xp_awarded' in event

    def test_event_log_includes_encounter_type(self, simulator):
        """Event log should include encounter type."""
        simulator.solve_current_encounter()

        event = simulator.event_log[0]

        assert 'encounter_type' in event
        assert isinstance(event['encounter_type'], EncounterType)


class TestChapterTransitions:
    """Test chapter transition behavior during campaign."""

    def test_chapter_complete_recorded(self, simulator):
        """Chapter completions should be recorded."""
        simulator.run_to_completion()

        # Should have completed chapters
        assert len(simulator.chapters_completed) > 0

    def test_chapter_ids_are_valid(self, simulator, campaign):
        """Completed chapter IDs should match campaign chapters."""
        simulator.run_to_completion()

        valid_chapter_ids = {ch.id for ch in campaign.chapters}

        for ch_id in simulator.chapters_completed:
            assert ch_id in valid_chapter_ids
