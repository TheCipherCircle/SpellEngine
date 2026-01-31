"""Shared test fixtures for all test levels.

This module provides common fixtures used across:
- Level 1: State machine tests
- Level 2: UI component tests
- Level 3: Integration tests

Run with: pytest tests/ -v
"""

import pytest
from pathlib import Path

from spellengine.adventures.loader import load_campaign
from spellengine.adventures.state import AdventureState
from spellengine.adventures.models import DifficultyLevel


# Path to the Dread Citadel campaign
CAMPAIGN_PATH = (
    Path(__file__).parent.parent
    / "content"
    / "adventures"
    / "dread_citadel"
    / "campaign_source_built.yaml"
)


@pytest.fixture
def campaign():
    """Load the Dread Citadel campaign for testing."""
    return load_campaign(CAMPAIGN_PATH)


@pytest.fixture
def adventure_state(campaign):
    """Create a fresh AdventureState for testing."""
    return AdventureState(campaign, player_name="Test Player")


@pytest.fixture
def heroic_state(campaign):
    """Create an AdventureState at HEROIC difficulty."""
    return AdventureState(
        campaign,
        player_name="Heroic Tester",
        difficulty=DifficultyLevel.HEROIC,
    )


@pytest.fixture
def mythic_state(campaign):
    """Create an AdventureState at MYTHIC difficulty."""
    return AdventureState(
        campaign,
        player_name="Mythic Tester",
        difficulty=DifficultyLevel.MYTHIC,
    )


@pytest.fixture
def observer_state(campaign):
    """Create an AdventureState in observer mode."""
    return AdventureState(
        campaign,
        player_name="Observer",
        game_mode="observer",
    )


@pytest.fixture
def campaign_path():
    """Return the path to the campaign file."""
    return CAMPAIGN_PATH


# Utility functions for tests


def get_all_encounter_ids(campaign) -> set[str]:
    """Get all encounter IDs from the campaign."""
    return {
        enc.id
        for chapter in campaign.chapters
        for enc in chapter.encounters
    }


def count_encounters_by_type(campaign) -> dict:
    """Count encounters by type."""
    from collections import Counter
    return Counter(
        enc.encounter_type
        for chapter in campaign.chapters
        for enc in chapter.encounters
    )
