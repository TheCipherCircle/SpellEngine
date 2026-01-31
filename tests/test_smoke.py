"""Smoke Tests - Catch crashes before they happen.

These tests verify that the game can actually start:
- All modules import without error
- Pygame initializes correctly (headless)
- Fonts load without crashing
- Core systems initialize

Run with: pytest tests/test_smoke.py -v
"""

import pytest
import os
import sys


class TestModuleImports:
    """Verify all game modules import without error.

    Import errors are a common cause of red screens.
    If a module fails to import, the game crashes immediately.
    """

    def test_import_adventures_loader(self):
        """adventures.loader should import."""
        from spellengine.adventures import loader
        assert loader is not None

    def test_import_adventures_state(self):
        """adventures.state should import."""
        from spellengine.adventures import state
        assert state is not None

    def test_import_adventures_models(self):
        """adventures.models should import."""
        from spellengine.adventures import models
        assert models is not None

    def test_import_adventures_achievements(self):
        """adventures.achievements should import."""
        from spellengine.adventures import achievements
        assert achievements is not None

    def test_import_ui_terminal(self):
        """UI terminal module should import."""
        from spellengine.engine.game.ui import terminal
        assert terminal is not None

    def test_import_ui_textbox(self):
        """UI textbox module should import."""
        from spellengine.engine.game.ui import textbox
        assert textbox is not None

    def test_import_ui_expandable_panel(self):
        """UI expandable_panel module should import."""
        from spellengine.engine.game.ui import expandable_panel
        assert expandable_panel is not None

    def test_import_ui_craft_panel(self):
        """UI craft_panel module should import."""
        from spellengine.engine.game.ui import craft_panel
        assert craft_panel is not None

    def test_import_ui_puzzle_panel(self):
        """UI puzzle_panel module should import."""
        from spellengine.engine.game.ui import puzzle_panel
        assert puzzle_panel is not None

    def test_import_ui_siege_panel(self):
        """UI siege_panel module should import."""
        from spellengine.engine.game.ui import siege_panel
        assert siege_panel is not None

    def test_import_ui_theme(self):
        """UI theme module should import."""
        from spellengine.engine.game.ui import theme
        assert theme is not None

    def test_import_ui_widgets(self):
        """UI widgets module should import."""
        from spellengine.engine.game.ui import widgets
        assert widgets is not None


class TestPygameInitialization:
    """Test pygame can initialize in headless mode.

    These tests use SDL_VIDEODRIVER=dummy to run without a display.
    """

    @pytest.fixture(autouse=True)
    def setup_headless(self):
        """Set up headless pygame environment."""
        # Store original values
        original_video = os.environ.get('SDL_VIDEODRIVER')
        original_audio = os.environ.get('SDL_AUDIODRIVER')

        # Set headless drivers
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'

        yield

        # Restore original values
        if original_video is not None:
            os.environ['SDL_VIDEODRIVER'] = original_video
        elif 'SDL_VIDEODRIVER' in os.environ:
            del os.environ['SDL_VIDEODRIVER']

        if original_audio is not None:
            os.environ['SDL_AUDIODRIVER'] = original_audio
        elif 'SDL_AUDIODRIVER' in os.environ:
            del os.environ['SDL_AUDIODRIVER']

    def test_pygame_imports(self):
        """pygame should import."""
        import pygame
        assert pygame is not None

    def test_pygame_init(self):
        """pygame.init() should succeed."""
        import pygame
        result = pygame.init()
        # Returns (successful, failed) tuple
        assert result[1] == 0 or result[0] > 0  # Some success, or no critical failures
        pygame.quit()

    def test_pygame_display_init(self):
        """pygame.display should initialize."""
        import pygame
        pygame.init()
        try:
            # In dummy mode, this should work
            pygame.display.set_mode((100, 100))
        finally:
            pygame.quit()

    def test_pygame_font_init(self):
        """pygame.font should initialize."""
        import pygame
        pygame.init()
        try:
            pygame.font.init()
            assert pygame.font.get_init()
        finally:
            pygame.quit()


class TestFontLoading:
    """Test that fonts can be loaded.

    Font loading failures are a common crash cause.
    """

    @pytest.fixture(autouse=True)
    def setup_headless(self):
        """Set up headless pygame for font tests."""
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'

        import pygame
        pygame.init()
        pygame.font.init()

        yield pygame

        pygame.quit()

    def test_default_font_loads(self, setup_headless):
        """Default system font should load."""
        pygame = setup_headless
        font = pygame.font.Font(None, 24)
        assert font is not None

    def test_sysfont_loads(self, setup_headless):
        """SysFont should load with fallback."""
        pygame = setup_headless
        # This should always work - falls back to default
        font = pygame.font.SysFont('arial,helvetica,sans', 24)
        assert font is not None

    def test_font_renders_text(self, setup_headless):
        """Font should be able to render text."""
        pygame = setup_headless
        font = pygame.font.Font(None, 24)
        surface = font.render("Test", True, (255, 255, 255))
        assert surface is not None
        assert surface.get_width() > 0
        assert surface.get_height() > 0


class TestCoreSystemsInit:
    """Test core game systems can initialize."""

    def test_campaign_loads(self):
        """Campaign should load without error."""
        from pathlib import Path
        from spellengine.adventures.loader import load_campaign

        campaign_path = (
            Path(__file__).parent.parent
            / "content"
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        campaign = load_campaign(campaign_path)
        assert campaign is not None
        assert campaign.id == "dread_citadel"

    def test_adventure_state_creates(self):
        """AdventureState should create without error."""
        from pathlib import Path
        from spellengine.adventures.loader import load_campaign
        from spellengine.adventures.state import AdventureState

        campaign_path = (
            Path(__file__).parent.parent
            / "content"
            / "adventures"
            / "dread_citadel"
            / "campaign_source_built.yaml"
        )

        campaign = load_campaign(campaign_path)
        state = AdventureState(campaign, player_name="Smoke Test")

        assert state is not None
        assert state.current_encounter is not None

    def test_achievement_manager_creates(self):
        """AchievementManager should create without error."""
        from spellengine.adventures.achievements import create_achievement_manager

        manager = create_achievement_manager()
        assert manager is not None
