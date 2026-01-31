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
    "viewport_height": 0.70,     # Top portion for art/status (increased for more narrative text)
    "narrative_height": 0.30,    # Bottom portion for text/input

    # Padding and margins (bumped for breathing room)
    "panel_padding": 16,         # Was 12
    "panel_margin": 8,           # Was 4
    "border_width": 2,
    "border_width_thick": 3,
}

# Spacing system (consistent units)
SPACING = {
    "xs": 4,      # Tight spacing
    "sm": 8,      # Small gaps
    "md": 16,     # Default spacing
    "lg": 24,     # Section gaps
    "xl": 32,     # Major divisions
    "xxl": 48,    # Screen-level spacing
}


# =============================================================================
# COLOR PALETTE (Gruvbox Corrupted)
# =============================================================================

class Colors:
    """Gruvbox Dark color palette with hash accents."""

    # Backgrounds
    BG_DARKEST = (29, 32, 33)        # #1d2021 - deepest shadows, screen bg
    BG_DARK = (40, 40, 40)           # #282828 - main panel fill
    BG_HIGHLIGHT = (50, 48, 47)      # #32302f - hover state, slightly raised
    BG_MEDIUM = (60, 56, 54)         # #3c3836 - slightly raised panels
    BG_LIGHT = (80, 73, 69)          # #504945 - elevated elements

    # Borders
    BORDER = (102, 92, 84)           # #665c54 - panel borders
    BORDER_HIGHLIGHT = (124, 111, 100)  # #7c6f64 - active/focus borders

    # Text colors (WCAG AA contrast optimized - bumped for better visibility)
    TEXT_PRIMARY = (251, 241, 199)   # #fbf1c7 - brighter body text (13:1 contrast)
    TEXT_HEADER = (254, 128, 25)     # #fe8019 - titles, labels (orange)
    TEXT_SECONDARY = (235, 219, 178) # #ebdbb2 - secondary text (10:1 contrast)
    TEXT_MUTED = (189, 174, 147)     # #bdae93 - hints, disabled (6.5:1 contrast)
    TEXT_DIM = (168, 153, 132)       # #a89984 - subtle hints (5.5:1 - bumped from 4.5)

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
    """Typography settings - monospace, chunky, readable.

    UI Rebuild v1.0: Bumped sizes for better readability.
    Anti-aliasing enabled for body text (retro feel preserved in headers).
    """

    # Font sizes (bumped for readability)
    SIZE_TITLE = 52        # Screen titles
    SIZE_HEADER = 32       # Panel headers
    SIZE_SUBHEADER = 26    # Section headers
    SIZE_BODY = 20         # Body text
    SIZE_INTRO = 16        # Intro/narrative text - reduced to fit more content
    SIZE_LABEL = 18        # Labels
    SIZE_SMALL = 16        # Hints, prompts (was 14 - too small)
    SIZE_TINY = 14         # Only for truly minor elements

    # Line heights (multiplier of font size)
    LINE_HEIGHT = 1.5      # Slightly more breathing room

    # Anti-aliasing (enabled for readability, disable for pixel-art headers if wanted)
    ANTIALIAS = True
    ANTIALIAS_HEADERS = False  # Keep headers chunky/retro

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
# CUSTOM FONT PATHS
# =============================================================================

# Custom font files (relative to assets/fonts/)
CUSTOM_FONTS = {
    "title": "PressStart2P-Regular.ttf",  # Classic 8-bit RPG font for titles/headers
    "body": "VT323-Regular.ttf",          # CRT terminal font for body text
    "mono": "SpaceMono-Regular.ttf",      # Clean mono for hash/code display
}


# =============================================================================
# FONT MANAGER
# =============================================================================

class FontManager:
    """Manages font loading and caching with retro fallbacks.

    Supports custom TTF fonts for titles/headers while using system
    monospace for body text and terminal display.
    """

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
        self._title_font_path: str | None = None
        self._body_font_path: str | None = None
        self._mono_font_path: str | None = None

    def _init_fonts(self) -> None:
        """Initialize pygame fonts if not already done."""
        if self._initialized:
            return

        import pygame.font
        from pathlib import Path

        if not pygame.font.get_init():
            pygame.font.init()

        # Find best available system monospace font (ultimate fallback)
        available = pygame.font.get_fonts()
        for font_name in Typography.MONO_FONTS:
            normalized = font_name.lower().replace(" ", "").replace("-", "")
            if normalized in available:
                self._mono_font_name = normalized
                break

        if self._mono_font_name is None:
            # Fallback to any monospace
            self._mono_font_name = "monospace"

        # Locate custom fonts
        def find_font(font_file: str) -> str | None:
            """Find a font file in known locations."""
            font_locations = [
                Path(__file__).parent.parent.parent.parent.parent / "assets" / "fonts" / font_file,
                Path.cwd() / "assets" / "fonts" / font_file,
            ]
            for font_path in font_locations:
                if font_path.exists():
                    return str(font_path)
            return None

        # Load title font (Press Start 2P)
        if CUSTOM_FONTS.get("title"):
            self._title_font_path = find_font(CUSTOM_FONTS["title"])

        # Load body font (VT323)
        if CUSTOM_FONTS.get("body"):
            self._body_font_path = find_font(CUSTOM_FONTS["body"])

        # Load mono font (Space Mono)
        if CUSTOM_FONTS.get("mono"):
            self._mono_font_path = find_font(CUSTOM_FONTS["mono"])

        self._initialized = True

    def get_font(self, size: int, bold: bool = False) -> "pygame.font.Font":
        """Get a monospace font at the specified size (Space Mono or fallback).

        Args:
            size: Font size in points
            bold: Whether to use bold variant (ignored for custom fonts)

        Returns:
            Pygame font object
        """
        import pygame.font

        self._init_fonts()

        key = f"mono:{size}:{bold}"
        if key not in self._fonts:
            # Try custom mono font first (Space Mono)
            if self._mono_font_path:
                try:
                    self._fonts[key] = pygame.font.Font(self._mono_font_path, size)
                except Exception:
                    pass

            # Fallback to system mono
            if key not in self._fonts:
                try:
                    self._fonts[key] = pygame.font.SysFont(
                        self._mono_font_name, size, bold=bold
                    )
                except Exception:
                    # Ultimate fallback
                    self._fonts[key] = pygame.font.Font(None, size)

        return self._fonts[key]

    def get_title_font_at_size(self, size: int) -> "pygame.font.Font":
        """Get the custom title font (ByteBounce) at the specified size.

        Falls back to bold monospace if custom font not available.

        Args:
            size: Font size in points

        Returns:
            Pygame font object
        """
        import pygame.font

        self._init_fonts()

        key = f"title:{size}"
        if key not in self._fonts:
            if self._title_font_path:
                try:
                    self._fonts[key] = pygame.font.Font(self._title_font_path, size)
                except Exception:
                    # Fallback to bold monospace
                    self._fonts[key] = self.get_font(size, bold=True)
            else:
                # No custom font available, use bold monospace
                self._fonts[key] = self.get_font(size, bold=True)

        return self._fonts[key]

    def get_body_font_at_size(self, size: int) -> "pygame.font.Font":
        """Get the custom body font (VT323) at the specified size.

        Falls back to regular monospace if custom font not available.

        Args:
            size: Font size in points

        Returns:
            Pygame font object
        """
        import pygame.font

        self._init_fonts()

        key = f"body:{size}"
        if key not in self._fonts:
            if self._body_font_path:
                try:
                    self._fonts[key] = pygame.font.Font(self._body_font_path, size)
                except Exception:
                    # Fallback to monospace
                    self._fonts[key] = self.get_font(size)
            else:
                # No custom font available, use monospace
                self._fonts[key] = self.get_font(size)

        return self._fonts[key]

    def get_header_font(self) -> "pygame.font.Font":
        """Get the font for headers (ByteBounce or bold monospace)."""
        return self.get_title_font_at_size(Typography.SIZE_HEADER)

    def get_title_font(self) -> "pygame.font.Font":
        """Get the font for screen titles (ByteBounce or bold monospace)."""
        return self.get_title_font_at_size(Typography.SIZE_TITLE)

    def get_body_font(self) -> "pygame.font.Font":
        """Get the font for body text (VT323 or monospace)."""
        return self.get_body_font_at_size(Typography.SIZE_BODY)

    def get_label_font(self) -> "pygame.font.Font":
        """Get the font for labels (VT323 or monospace)."""
        return self.get_body_font_at_size(Typography.SIZE_LABEL)

    def get_small_font(self) -> "pygame.font.Font":
        """Get the font for hints and prompts (VT323 or monospace)."""
        return self.get_body_font_at_size(Typography.SIZE_SMALL)

    def get_intro_font(self) -> "pygame.font.Font":
        """Get the font for intro/narrative text (VT323 or monospace)."""
        return self.get_body_font_at_size(Typography.SIZE_INTRO)


# Convenience function
def get_fonts() -> FontManager:
    """Get the global FontManager instance."""
    return FontManager.get_instance()
