"""Pygame mocks and fixtures for UI component testing.

Provides comprehensive pygame mocks that allow testing UI components
without an actual display. Includes event factories for simulating
user input.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys


class MockRect:
    """A mock pygame.Rect with real geometric behavior."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self._update_computed()

    def _update_computed(self):
        """Update computed properties."""
        self.left = self.x
        self.top = self.y
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        self.centerx = self.x + self.width // 2
        self.centery = self.y + self.height // 2
        self.center = (self.centerx, self.centery)
        self.topleft = (self.left, self.top)
        self.topright = (self.right, self.top)
        self.bottomleft = (self.left, self.bottom)
        self.bottomright = (self.right, self.bottom)

    def collidepoint(self, pos):
        """Check if a point is inside the rect."""
        x, y = pos
        return self.x <= x < self.right and self.y <= y < self.bottom

    def inflate(self, x, y):
        """Return a new rect inflated by x, y."""
        return MockRect(
            self.x - x // 2,
            self.y - y // 2,
            self.width + x,
            self.height + y,
        )

    def copy(self):
        """Return a copy of this rect."""
        return MockRect(self.x, self.y, self.width, self.height)

    def __repr__(self):
        return f"MockRect({self.x}, {self.y}, {self.width}, {self.height})"


def create_mock_surface(size):
    """Create a mock pygame Surface with proper dimensions."""
    surface = Mock()
    surface.get_width.return_value = size[0]
    surface.get_height.return_value = size[1]
    surface.get_size.return_value = size
    surface.blit = Mock()
    surface.fill = Mock()
    surface.set_clip = Mock()
    surface.get_clip = Mock(return_value=MockRect(0, 0, size[0], size[1]))
    return surface


@pytest.fixture(autouse=True)
def mock_pygame():
    """Mock pygame for headless UI testing.

    This fixture automatically applies to all tests in the ui/ directory.
    It provides a comprehensive mock of pygame functionality needed for
    testing UI components without a display.
    """
    mock_pg = MagicMock()

    # Mock display (no actual window)
    mock_pg.display.set_mode.return_value = create_mock_surface((1280, 800))
    mock_pg.display.flip = Mock()
    mock_pg.display.get_surface.return_value = create_mock_surface((1280, 800))

    # Mock Surface creation
    mock_pg.Surface = lambda size: create_mock_surface(size)

    # Mock Rect with real behavior
    mock_pg.Rect = MockRect

    # Event types
    mock_pg.KEYDOWN = 2
    mock_pg.KEYUP = 3
    mock_pg.MOUSEBUTTONDOWN = 5
    mock_pg.MOUSEBUTTONUP = 6
    mock_pg.MOUSEMOTION = 4

    # Key constants
    mock_pg.K_RETURN = 13
    mock_pg.K_ESCAPE = 27
    mock_pg.K_BACKSPACE = 8
    mock_pg.K_DELETE = 127
    mock_pg.K_TAB = 9
    mock_pg.K_SPACE = 32
    mock_pg.K_UP = 273
    mock_pg.K_DOWN = 274
    mock_pg.K_LEFT = 276
    mock_pg.K_RIGHT = 275
    mock_pg.K_HOME = 278
    mock_pg.K_END = 279
    mock_pg.K_PAGEUP = 280
    mock_pg.K_PAGEDOWN = 281
    mock_pg.K_BACKQUOTE = 96
    mock_pg.K_a = ord('a')
    mock_pg.K_d = ord('d')
    mock_pg.K_l = ord('l')
    mock_pg.K_s = ord('s')
    mock_pg.K_t = ord('t')
    mock_pg.K_u = ord('u')

    # Mouse button constants
    mock_pg.BUTTON_LEFT = 1
    mock_pg.BUTTON_MIDDLE = 2
    mock_pg.BUTTON_RIGHT = 3

    # Mock mouse
    mock_pg.mouse.get_pos.return_value = (0, 0)

    # Mock time
    mock_pg.time.get_ticks.return_value = 0

    # Mock fonts
    mock_font = Mock()
    mock_font.render.return_value = create_mock_surface((100, 20))
    mock_font.get_height.return_value = 20
    mock_font.size.return_value = (100, 20)
    mock_pg.font.Font.return_value = mock_font
    mock_pg.font.SysFont.return_value = mock_font
    mock_pg.font.init = Mock()

    # Mock draw functions
    mock_pg.draw.rect = Mock()
    mock_pg.draw.line = Mock()
    mock_pg.draw.circle = Mock()

    with patch.dict(sys.modules, {'pygame': mock_pg}):
        yield mock_pg


@pytest.fixture
def make_key_event(mock_pygame):
    """Factory for creating keyboard events."""
    def _make(key, unicode_char='', mods=0):
        event = Mock()
        event.type = mock_pygame.KEYDOWN
        event.key = key
        event.unicode = unicode_char
        event.mod = mods
        return event
    return _make


@pytest.fixture
def make_click_event(mock_pygame):
    """Factory for creating mouse click events."""
    def _make(x, y, button=1):
        event = Mock()
        event.type = mock_pygame.MOUSEBUTTONDOWN
        event.pos = (x, y)
        event.button = button
        return event
    return _make


@pytest.fixture
def make_motion_event(mock_pygame):
    """Factory for creating mouse motion events."""
    def _make(x, y, rel=(0, 0), buttons=(0, 0, 0)):
        event = Mock()
        event.type = mock_pygame.MOUSEMOTION
        event.pos = (x, y)
        event.rel = rel
        event.buttons = buttons
        return event
    return _make


@pytest.fixture
def mock_surface(mock_pygame):
    """Create a mock surface for rendering tests."""
    return create_mock_surface((800, 600))


# Mock the theme module to avoid pygame font initialization issues
@pytest.fixture(autouse=True)
def mock_theme():
    """Mock the theme module for testing."""
    mock_fonts = Mock()
    mock_font_obj = Mock()
    mock_font_obj.render.return_value = create_mock_surface((100, 20))
    mock_font_obj.get_height.return_value = 20
    mock_font_obj.size.return_value = (100, 20)
    mock_fonts.get_font.return_value = mock_font_obj

    with patch('spellengine.engine.game.ui.theme.get_fonts', return_value=mock_fonts):
        yield mock_fonts
