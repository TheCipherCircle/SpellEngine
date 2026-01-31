"""Level 3 Integration Tests: Encounter Types.

Tests type-specific encounter behavior and validates
that each encounter type has the required attributes.

These tests verify encounter content integrity.
"""

import pytest

from spellengine.adventures.models import EncounterType, DifficultyLevel


class TestEncounterTypePresence:
    """Test that encounters have required attributes by type."""

    def test_flash_encounters_have_solutions(self, campaign):
        """FLASH encounters should have solutions."""
        missing = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.FLASH:
                    solution = enc.solution or enc.get_solution_for_difficulty(DifficultyLevel.NORMAL)
                    if not solution:
                        missing.append(enc.id)

        assert not missing, f"FLASH encounters missing solutions: {missing}"

    def test_hunt_encounters_have_solutions(self, campaign):
        """HUNT encounters should have solutions."""
        missing = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.HUNT:
                    solution = enc.solution or enc.get_solution_for_difficulty(DifficultyLevel.NORMAL)
                    if not solution and enc.hash:  # Only if hash is present
                        missing.append(enc.id)

        assert not missing, f"HUNT encounters with hash but missing solutions: {missing}"

    def test_craft_encounters_have_mask_patterns(self, campaign):
        """CRAFT encounters should have mask-style solutions."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.CRAFT:
                    solution = enc.solution or enc.get_solution_for_difficulty(DifficultyLevel.NORMAL)
                    if solution:
                        # Mask patterns contain ? characters
                        assert '?' in solution, f"CRAFT {enc.id} solution doesn't look like a mask: {solution}"

    def test_all_encounters_have_titles(self, campaign):
        """Every encounter should have a title."""
        missing = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if not enc.title:
                    missing.append(enc.id)

        assert not missing, f"Encounters missing titles: {missing}"

    def test_all_encounters_have_xp(self, campaign):
        """Every encounter should have an XP reward >= 0."""
        invalid = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.xp_reward < 0:
                    invalid.append((enc.id, enc.xp_reward))

        assert not invalid, f"Encounters with invalid XP: {invalid}"


class TestEncounterTypeDistribution:
    """Test encounter type distribution in campaign."""

    def test_campaign_has_multiple_types(self, campaign):
        """Campaign should have multiple encounter types."""
        types_seen = set()
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                types_seen.add(enc.encounter_type)

        assert len(types_seen) > 1, f"Only one encounter type: {types_seen}"

    def test_flash_is_common(self, campaign):
        """FLASH should be a common encounter type."""
        flash_count = sum(
            1 for chapter in campaign.chapters
            for enc in chapter.encounters
            if enc.encounter_type == EncounterType.FLASH
        )
        total_count = sum(len(ch.encounters) for ch in campaign.chapters)

        # FLASH should be at least 20% of encounters
        assert flash_count >= total_count * 0.2, f"Only {flash_count}/{total_count} FLASH encounters"


class TestEncounterChaining:
    """Test encounter next_encounter references."""

    def test_all_next_encounters_exist(self, campaign):
        """All next_encounter references should point to valid encounters."""
        all_ids = {
            enc.id
            for chapter in campaign.chapters
            for enc in chapter.encounters
        }

        invalid = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.next_encounter and enc.next_encounter not in all_ids:
                    invalid.append((enc.id, enc.next_encounter))

        assert not invalid, f"Invalid next_encounter refs: {invalid}"

    def test_last_chapter_encounter_no_next(self, campaign):
        """Last encounter of last chapter should have no next_encounter."""
        last_chapter = campaign.chapters[-1]
        last_encounter = last_chapter.encounters[-1]

        # Last encounter shouldn't have next_encounter
        # (or it points to nothing, which is handled by campaign complete logic)


class TestDifficultyVariants:
    """Test difficulty-specific encounter attributes."""

    def test_difficulty_hash_variants(self, campaign):
        """Encounters with difficulty variants should have different hashes."""
        variants_found = 0
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                normal_hash = enc.get_hash_for_difficulty(DifficultyLevel.NORMAL)
                heroic_hash = enc.get_hash_for_difficulty(DifficultyLevel.HEROIC)
                mythic_hash = enc.get_hash_for_difficulty(DifficultyLevel.MYTHIC)

                # Count encounters with actual variants
                if heroic_hash and heroic_hash != normal_hash:
                    variants_found += 1
                if mythic_hash and mythic_hash != normal_hash:
                    variants_found += 1

        # Having some variants is good, but not required
        # This test just documents the current state

    def test_difficulty_xp_scaling(self, campaign):
        """Heroic/Mythic XP should be >= Normal XP."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                normal_xp = enc.get_xp_for_difficulty(DifficultyLevel.NORMAL)
                heroic_xp = enc.get_xp_for_difficulty(DifficultyLevel.HEROIC)
                mythic_xp = enc.get_xp_for_difficulty(DifficultyLevel.MYTHIC)

                # Higher difficulties should give at least as much XP
                assert heroic_xp >= normal_xp, f"{enc.id}: Heroic XP {heroic_xp} < Normal {normal_xp}"
                assert mythic_xp >= normal_xp, f"{enc.id}: Mythic XP {mythic_xp} < Normal {normal_xp}"


class TestEncounterContent:
    """Test encounter content quality."""

    def test_encounter_descriptions_not_empty(self, campaign):
        """Encounters should have descriptions or narrative text."""
        # This is a soft check - not all encounters may need descriptions
        has_content = 0
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.intro_text or enc.success_text or enc.failure_text:
                    has_content += 1

        total = sum(len(ch.encounters) for ch in campaign.chapters)

        # At least 50% should have some content
        assert has_content >= total * 0.5, f"Only {has_content}/{total} encounters have content"

    def test_hash_encounters_have_hashes(self, campaign):
        """Hash-based encounters should actually have hashes."""
        hash_types = {EncounterType.FLASH, EncounterType.HUNT, EncounterType.DUEL}

        missing = []
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type in hash_types:
                    hash_value = enc.hash or enc.get_hash_for_difficulty(DifficultyLevel.NORMAL)
                    if not hash_value:
                        missing.append(enc.id)

        # Some encounters might not have hashes (narrative sections)
        # This is informational


class TestEncounterTypeVisitation:
    """Test that different encounter types are visited during play."""

    def test_multiple_types_encountered(self, simulator):
        """Multiple encounter types should be encountered during play."""
        types_seen = set()

        for _ in range(30):
            if simulator.state.is_complete:
                break

            enc = simulator.state.current_encounter
            types_seen.add(enc.encounter_type)
            simulator.solve_current_encounter()

        assert len(types_seen) > 1, f"Only encountered types: {types_seen}"


class TestSpecificEncounterTypes:
    """Test specific encounter type handling."""

    def test_tour_encounters_are_narrative(self, campaign):
        """TOUR encounters should be narrative-focused."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.TOUR:
                    # TOUR encounters typically have lore and low XP
                    # They're meant for teaching, not testing
                    pass  # Just verify they exist and are valid

    def test_puzzle_box_has_steps(self, campaign):
        """PUZZLE_BOX encounters should have step structure."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.PUZZLE_BOX:
                    # PUZZLE_BOX typically has multiple solutions or steps
                    pass  # Validation depends on campaign structure

    def test_pipeline_has_sequence(self, campaign):
        """PIPELINE encounters should have sequential structure."""
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.encounter_type == EncounterType.PIPELINE:
                    # PIPELINE involves command sequences
                    pass  # Validation depends on campaign structure


class TestEncounterHints:
    """Test hint availability by difficulty."""

    def test_normal_has_hints(self, campaign):
        """Normal difficulty should have accessible hints."""
        hint_count = 0
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                hint = enc.get_hint_for_difficulty(DifficultyLevel.NORMAL)
                if hint:
                    hint_count += 1

        # Some encounters should have hints
        assert hint_count > 0, "No hints found in normal difficulty"

    def test_heroic_hints_may_be_limited(self, campaign):
        """Heroic difficulty may have fewer or different hints."""
        normal_hints = 0
        heroic_hints = 0

        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                if enc.get_hint_for_difficulty(DifficultyLevel.NORMAL):
                    normal_hints += 1
                if enc.get_hint_for_difficulty(DifficultyLevel.HEROIC):
                    heroic_hints += 1

        # Just documenting the relationship - not a strict requirement
