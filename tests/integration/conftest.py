"""Integration test fixtures and GameSessionSimulator.

Provides comprehensive fixtures for end-to-end testing of game sessions,
including campaign walking, scene transitions, and encounter behavior.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

from spellengine.adventures.loader import load_campaign
from spellengine.adventures.state import AdventureState
from spellengine.adventures.models import OutcomeType, DifficultyLevel, EncounterType


# Path to the Dread Citadel campaign
CAMPAIGN_PATH = (
    Path(__file__).parent.parent.parent
    / "content"
    / "adventures"
    / "dread_citadel"
    / "campaign_source_built.yaml"
)


@pytest.fixture
def campaign():
    """Load the Dread Citadel campaign for integration testing."""
    return load_campaign(CAMPAIGN_PATH)


class GameSessionSimulator:
    """Simulates game sessions for integration testing.

    Allows walking through campaigns programmatically,
    tracking events, and verifying state transitions.
    """

    def __init__(
        self,
        campaign,
        player_name: str = "TestPlayer",
        difficulty: DifficultyLevel = DifficultyLevel.NORMAL,
        game_mode: str = "full",
    ):
        """Initialize a game session simulator.

        Args:
            campaign: The campaign to play through
            player_name: Name for the test player
            difficulty: Difficulty level
            game_mode: Game mode (full/hashcat/john/observer)
        """
        self.campaign = campaign
        self.state = AdventureState(
            campaign,
            player_name=player_name,
            difficulty=difficulty,
            game_mode=game_mode,
        )
        self.difficulty = difficulty
        self.game_mode = game_mode

        # Tracking
        self.frame_count = 0
        self.event_log: list[dict] = []
        self.encounters_visited: list[str] = []
        self.chapters_completed: list[str] = []

    def solve_current_encounter(self) -> dict | None:
        """Submit correct answer for current encounter.

        Returns:
            Result dict from record_outcome, or None if no solution
        """
        encounter = self.state.current_encounter
        self.encounters_visited.append(encounter.id)

        result = self.state.record_outcome(OutcomeType.SUCCESS)

        self.event_log.append({
            'action': 'solve',
            'encounter_id': encounter.id,
            'encounter_type': encounter.encounter_type,
            'result': result['action'],
            'xp_awarded': result.get('xp_awarded', 0),
            'chapter_id': self.state.state.chapter_id,
        })

        if result['action'] == 'chapter_complete':
            self.chapters_completed.append(result['chapter_completed'])

        return result

    def run_to_completion(self, max_encounters: int = 200) -> dict:
        """Run through entire campaign solving all encounters.

        Args:
            max_encounters: Safety limit to prevent infinite loops

        Returns:
            Summary dict with completion stats
        """
        count = 0
        while not self.state.is_complete and count < max_encounters:
            result = self.solve_current_encounter()
            count += 1

            if result and result['action'] == 'complete':
                break
            if result and result['action'] == 'prologue_gate':
                # Observer mode stops at prologue
                break

        return {
            'complete': self.state.is_complete,
            'encounters_solved': count,
            'encounters_visited': list(self.encounters_visited),
            'chapters_completed': list(self.chapters_completed),
            'total_xp': self.state.state.total_xp,
            'deaths': self.state.state.deaths,
            'event_log': self.event_log,
        }

    def run_to_chapter_end(self) -> dict:
        """Run until the current chapter is complete.

        Returns:
            Summary dict with chapter stats
        """
        chapter_id = self.state.current_chapter.id
        count = 0
        max_encounters = 100

        while count < max_encounters:
            result = self.solve_current_encounter()
            count += 1

            if result['action'] in ('chapter_complete', 'complete', 'prologue_gate'):
                break

        return {
            'chapter_id': chapter_id,
            'encounters_solved': count,
            'xp_earned': self.state.state.xp_earned,
        }

    def get_remaining_encounters(self) -> list[str]:
        """Get IDs of encounters not yet visited."""
        all_ids = {
            enc.id
            for chapter in self.campaign.chapters
            for enc in chapter.encounters
        }
        visited = set(self.encounters_visited)
        return list(all_ids - visited)


@pytest.fixture
def simulator(campaign):
    """Create a GameSessionSimulator with normal difficulty."""
    return GameSessionSimulator(campaign)


@pytest.fixture
def heroic_simulator(campaign):
    """Create a GameSessionSimulator with heroic difficulty."""
    return GameSessionSimulator(campaign, difficulty=DifficultyLevel.HEROIC)


@pytest.fixture
def mythic_simulator(campaign):
    """Create a GameSessionSimulator with mythic difficulty."""
    return GameSessionSimulator(campaign, difficulty=DifficultyLevel.MYTHIC)


@pytest.fixture
def observer_simulator(campaign):
    """Create a GameSessionSimulator in observer mode."""
    return GameSessionSimulator(campaign, game_mode="observer")


# Mock fixtures for pygame and assets


class MockRect:
    """Mock pygame.Rect for integration tests."""

    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.left, self.top = x, y
        self.right = x + w
        self.bottom = y + h

    def collidepoint(self, pos):
        return self.x <= pos[0] < self.right and self.y <= pos[1] < self.bottom


@pytest.fixture
def mock_pygame():
    """Comprehensive pygame mock for integration tests."""
    mock_pg = MagicMock()

    def create_surface(size):
        surface = Mock()
        surface.get_width.return_value = size[0]
        surface.get_height.return_value = size[1]
        surface.get_size.return_value = size
        return surface

    mock_pg.Surface = create_surface
    mock_pg.Rect = MockRect

    # Event constants
    mock_pg.KEYDOWN = 2
    mock_pg.MOUSEBUTTONDOWN = 5
    mock_pg.K_RETURN = 13
    mock_pg.K_SPACE = 32

    # Font mock
    mock_font = Mock()
    mock_font.render.return_value = create_surface((100, 20))
    mock_font.get_height.return_value = 20
    mock_pg.font.Font.return_value = mock_font

    with patch.dict(sys.modules, {'pygame': mock_pg}):
        yield mock_pg


@pytest.fixture
def mock_audio():
    """Mock audio system."""
    audio = Mock()
    audio.play_music = Mock()
    audio.play_sfx = Mock()
    audio.stop_music = Mock()
    audio.fade_out = Mock()
    return audio


@pytest.fixture
def mock_assets():
    """Mock asset loader."""
    def make_surface(w=100, h=100):
        s = Mock()
        s.get_width.return_value = w
        s.get_height.return_value = h
        s.get_size.return_value = (w, h)
        return s

    assets = Mock()
    assets.get_background.return_value = make_surface(1280, 800)
    assets.get_encounter_image.return_value = make_surface(400, 300)
    assets.get_boss_sprite.return_value = make_surface(200, 200)
    assets.get_font.return_value = Mock()
    return assets


# Utility functions


def get_encounter_ids_by_type(campaign, enc_type: EncounterType) -> list[str]:
    """Get all encounter IDs of a specific type."""
    return [
        enc.id
        for chapter in campaign.chapters
        for enc in chapter.encounters
        if enc.encounter_type == enc_type
    ]


def count_encounters_by_chapter(campaign) -> dict[str, int]:
    """Count encounters per chapter."""
    return {
        chapter.id: len(chapter.encounters)
        for chapter in campaign.chapters
    }


def calculate_expected_xp(campaign, difficulty: DifficultyLevel = DifficultyLevel.NORMAL) -> int:
    """Calculate total XP for completing all encounters."""
    multiplier = {
        DifficultyLevel.NORMAL: 1.0,
        DifficultyLevel.HEROIC: 1.5,
        DifficultyLevel.MYTHIC: 2.0,
    }.get(difficulty, 1.0)

    total = sum(
        enc.get_xp_for_difficulty(difficulty)
        for chapter in campaign.chapters
        for enc in chapter.encounters
    )

    return int(total * multiplier)
