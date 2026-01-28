"""PatternForge UI Theme - Gruvbox Dark + Corrupted SNES aesthetic.

Central theme module with all colors, layout ratios, and typography settings.
Based on the locked UI Style Guide.

Layout Source: Might and Magic (Genesis, 1991)
Visual Source: Corrupted SNES aesthetic
Colors: Gruvbox Dark + hash accents
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame


# =============================================================================
# LAYOUT RATIOS (Sacred - from M&M)
# =============================================================================

LAYOUT = {
    # Main split ratios
    "viewport_width": 0.60,      # Left side - encounter art
    "status_width": 0.40,        # Right side - status panel

    # Vertical splits
    "viewport_height": 0.65,     # Top portion for art/status
    "narrative_height": 0.35,    # Bottom portion for text/input

    # Padding and margins
    "panel_padding": 12,
    "panel_margin": 4,
    "border_width": 2,
    "border_width_thick": 3,
}


# =============================================================================
# COLOR PALETTE (Gruvbox Corrupted)
# =============================================================================

class Colors:
    """Gruvbox Dark color palette with hash accents."""

    # Backgrounds
    BG_DARKEST = (29, 32, 33)        # #1d2021 - deepest shadows, screen bg
    BG_DARK = (40, 40, 40)           # #282828 - main panel fill
    BG_MEDIUM = (60, 56, 54)         # #3c3836 - slightly raised panels
    BG_LIGHT = (80, 73, 69)          # #504945 - elevated elements

    # Borders
    BORDER = (102, 92, 84)           # #665c54 - panel borders
    BORDER_HIGHLIGHT = (124, 111, 100)  # #7c6f64 - active/focus borders

    # Text colors
    TEXT_PRIMARY = (235, 219, 178)   # #ebdbb2 - body text, values
    TEXT_HEADER = (254, 128, 25)     # #fe8019 - titles, labels (orange)
    TEXT_MUTED = (146, 131, 116)     # #928374 - hints, disabled
    TEXT_DIM = (102, 92, 84)         # #665c54 - very subtle hints

    # Status colors
    SUCCESS = (184, 187, 38)         # #b8bb26 - clean solves, wins (green)
    ERROR = (251, 73, 52)            # #fb4934 - failures, deaths (red)
    WARNING = (250, 189, 47)         # #fabd2f - caution states (yellow)

    # Accent colors
    RED = (251, 73, 52)              # #fb4934
    GREEN = (184, 187, 38)           # #b8bb26
    YELLOW = (250, 189, 47)          # #fabd2f
    BLUE = (131, 165, 152)           # #83a598
    PURPLE = (211, 134, 155)         # #d3869b
    AQUA = (142, 192, 124)           # #8ec07c
    ORANGE = (254, 128, 25)          # #fe8019
    GOLD = (215, 153, 33)            # #d79921 - observer mode answers

    # Hash type accents
    HASH_MD5 = (215, 153, 33)        # #d79921 - tarnished amber
    HASH_SHA1 = (104, 157, 106)      # #689d6a - toxic cyan/green
    HASH_SHA256 = (177, 98, 134)     # #b16286 - corrupt purple
    HASH_BCRYPT = (204, 36, 29)      # #cc241d - blood red

    # Selection indicator
    SELECTION = (251, 73, 52)        # #fb4934 - red arrow/highlight

    # Cursor
    CURSOR = (254, 128, 25)          # #fe8019 - orange cursor

    @classmethod
    def get_hash_color(cls, hash_type: str) -> tuple[int, int, int]:
        """Get the accent color for a hash type.

        Args:
            hash_type: Hash algorithm name (MD5, SHA1, SHA256, BCRYPT, etc.)

        Returns:
            RGB color tuple
        """
        hash_colors = {
            "MD5": cls.HASH_MD5,
            "SHA1": cls.HASH_SHA1,
            "SHA-1": cls.HASH_SHA1,
            "SHA256": cls.HASH_SHA256,
            "SHA-256": cls.HASH_SHA256,
            "BCRYPT": cls.HASH_BCRYPT,
        }
        return hash_colors.get(hash_type.upper(), cls.TEXT_MUTED)


# =============================================================================
# TYPOGRAPHY
# =============================================================================

class Typography:
    """Typography settings - monospace, chunky, no anti-aliasing."""

    # Font sizes
    SIZE_TITLE = 48        # Screen titles
    SIZE_HEADER = 28       # Panel headers
    SIZE_SUBHEADER = 22    # Section headers
    SIZE_BODY = 18         # Body text
    SIZE_LABEL = 16        # Labels
    SIZE_SMALL = 14        # Hints, prompts

    # Line heights (multiplier of font size)
    LINE_HEIGHT = 1.4

    # Anti-aliasing (DISABLED for retro feel)
    ANTIALIAS = False

    # Preferred fonts (in order of preference)
    MONO_FONTS = [
        "Courier New",
        "Consolas",
        "Monaco",
        "DejaVu Sans Mono",
        "Liberation Mono",
        "monospace",
    ]


# =============================================================================
# BORDER CHARACTERS (for ASCII-style borders)
# =============================================================================

class BorderChars:
    """Unicode box-drawing characters for panel borders."""

    # Double-line (major panels)
    DOUBLE_TOP_LEFT = "\u2554"      # ╔
    DOUBLE_TOP_RIGHT = "\u2557"     # ╗
    DOUBLE_BOTTOM_LEFT = "\u255a"   # ╚
    DOUBLE_BOTTOM_RIGHT = "\u255d"  # ╝
    DOUBLE_HORIZONTAL = "\u2550"    # ═
    DOUBLE_VERTICAL = "\u2551"      # ║

    # Single-line (sub-panels)
    SINGLE_TOP_LEFT = "\u250c"      # ┌
    SINGLE_TOP_RIGHT = "\u2510"     # ┐
    SINGLE_BOTTOM_LEFT = "\u2514"   # └
    SINGLE_BOTTOM_RIGHT = "\u2518"  # ┘
    SINGLE_HORIZONTAL = "\u2500"    # ─
    SINGLE_VERTICAL = "\u2502"      # │

    # Connectors
    T_DOWN = "\u252c"               # ┬
    T_UP = "\u2534"                 # ┴
    T_RIGHT = "\u251c"              # ├
    T_LEFT = "\u2524"               # ┤
    CROSS = "\u253c"                # ┼


# =============================================================================
# FONT MANAGER
# =============================================================================

class FontManager:
    """Manages font loading and caching with retro fallbacks."""

    _instance: "FontManager | None" = None
    _fonts: dict[str, "pygame.font.Font"] = {}
    _initialized: bool = False

    @classmethod
    def get_instance(cls) -> "FontManager":
        """Get or create the singleton FontManager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the font manager."""
        self._fonts = {}
        self._initialized = False
        self._mono_font_name: str | None = None

    def _init_fonts(self) -> None:
        """Initialize pygame fonts if not already done."""
        if self._initialized:
            return

        import pygame.font

        if not pygame.font.get_init():
            pygame.font.init()

        # Find best available monospace font
        available = pygame.font.get_fonts()
        for font_name in Typography.MONO_FONTS:
            normalized = font_name.lower().replace(" ", "").replace("-", "")
            if normalized in available:
                self._mono_font_name = normalized
                break

        if self._mono_font_name is None:
            # Fallback to any monospace
            self._mono_font_name = "monospace"

        self._initialized = True

    def get_font(self, size: int, bold: bool = False) -> "pygame.font.Font":
        """Get a monospace font at the specified size.

        Args:
            size: Font size in points
            bold: Whether to use bold variant

        Returns:
            Pygame font object
        """
        import pygame.font

        self._init_fonts()

        key = f"{size}:{bold}"
        if key not in self._fonts:
            try:
                self._fonts[key] = pygame.font.SysFont(
                    self._mono_font_name, size, bold=bold
                )
            except Exception:
                # Ultimate fallback
                self._fonts[key] = pygame.font.Font(None, size)

        return self._fonts[key]

    def get_header_font(self) -> "pygame.font.Font":
        """Get the font for headers (bold, large)."""
        return self.get_font(Typography.SIZE_HEADER, bold=True)

    def get_title_font(self) -> "pygame.font.Font":
        """Get the font for screen titles (bold, extra large)."""
        return self.get_font(Typography.SIZE_TITLE, bold=True)

    def get_body_font(self) -> "pygame.font.Font":
        """Get the font for body text."""
        return self.get_font(Typography.SIZE_BODY)

    def get_label_font(self) -> "pygame.font.Font":
        """Get the font for labels."""
        return self.get_font(Typography.SIZE_LABEL)

    def get_small_font(self) -> "pygame.font.Font":
        """Get the font for hints and prompts."""
        return self.get_font(Typography.SIZE_SMALL)


# Convenience function
def get_fonts() -> FontManager:
    """Get the global FontManager instance."""
    return FontManager.get_instance()
