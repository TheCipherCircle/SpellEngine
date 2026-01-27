"""UI components for the PatternForge game client.

Styled with Gruvbox Dark palette and corrupted SNES aesthetic.
Layout based on Might and Magic (Genesis, 1991).

Components:
- Theme: Colors, layout constants, typography
- Panel: Bordered panels with optional titles
- Text: Text rendering utilities, typewriter effect
- TextBox: Password input field
- Button: Clickable buttons
- Menu: Keyboard-navigable menus
- HashDisplay: Hash value display with type indicators
"""

# Theme and constants
from patternforge.game.ui.theme import (
    Colors,
    LAYOUT,
    Typography,
    BorderChars,
    FontManager,
    get_fonts,
)

# Components
from patternforge.game.ui.button import Button
from patternforge.game.ui.textbox import TextBox
from patternforge.game.ui.panel import Panel, StatusPanel
from patternforge.game.ui.text import TextRenderer, TypewriterText, draw_double_border_title
from patternforge.game.ui.menu import Menu, MenuItem, PromptBar
from patternforge.game.ui.hash_display import HashDisplay, HashInputPanel

__all__ = [
    # Theme
    "Colors",
    "LAYOUT",
    "Typography",
    "BorderChars",
    "FontManager",
    "get_fonts",
    # Components
    "Button",
    "TextBox",
    "Panel",
    "StatusPanel",
    "TextRenderer",
    "TypewriterText",
    "draw_double_border_title",
    "Menu",
    "MenuItem",
    "PromptBar",
    "HashDisplay",
    "HashInputPanel",
]
