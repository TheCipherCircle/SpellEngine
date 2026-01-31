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
from spellengine.engine.game.ui.theme import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    BorderChars,
    FontManager,
    get_fonts,
)

# Components
from spellengine.engine.game.ui.button import Button
from spellengine.engine.game.ui.textbox import TextBox
from spellengine.engine.game.ui.panel import Panel, StatusPanel
from spellengine.engine.game.ui.text import TextRenderer, TypewriterText, draw_double_border_title
from spellengine.engine.game.ui.menu import Menu, MenuItem, PromptBar
from spellengine.engine.game.ui.hash_display import HashDisplay, HashInputPanel
from spellengine.engine.game.ui.validator import TextValidator, UIAuditLog
from spellengine.engine.game.ui.terminal import TerminalPanel, TerminalColors, TheatricalCracker
from spellengine.engine.game.ui.effects import (
    ScreenEffect,
    ShakeEffect,
    FlashEffect,
    SuccessFlash,
    FailureFlash,
    ScanlineOverlay,
    TextGlowEffect,
    VignetteEffect,
    EffectManager,
)
from spellengine.engine.game.ui.widgets import Slider, Toggle, TimerWidget
from spellengine.engine.game.ui.craft_panel import CraftPanel
from spellengine.engine.game.ui.siege_panel import SiegePanel
from spellengine.engine.game.ui.puzzle_panel import PuzzlePanel
from spellengine.engine.game.ui.expandable_panel import (
    ExpandablePanel,
    StepTracker,
    LearnMoreContent,
)

__all__ = [
    # Theme
    "Colors",
    "LAYOUT",
    "SPACING",
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
    # QA/Validation
    "TextValidator",
    "UIAuditLog",
    # Terminal
    "TerminalPanel",
    "TerminalColors",
    "TheatricalCracker",
    # Visual Effects
    "ScreenEffect",
    "ShakeEffect",
    "FlashEffect",
    "SuccessFlash",
    "FailureFlash",
    "ScanlineOverlay",
    "TextGlowEffect",
    "VignetteEffect",
    "EffectManager",
    # Settings widgets
    "Slider",
    "Toggle",
    "TimerWidget",
    # Encounter panels
    "CraftPanel",
    "SiegePanel",
    "PuzzlePanel",
    # Expandable panel
    "ExpandablePanel",
    "StepTracker",
    "LearnMoreContent",
]
