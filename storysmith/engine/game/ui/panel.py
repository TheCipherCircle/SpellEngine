"""Panel component with M&M-style borders.

Supports both thick drawn borders and optional ASCII-style title headers.
Square corners, no rounding - corrupted SNES aesthetic.
"""

from typing import TYPE_CHECKING

from storysmith.engine.game.ui.theme import Colors, LAYOUT, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


class Panel:
    """A bordered panel with optional title header.

    Draws thick borders (2-3px), square corners, with title in orange ALL CAPS.
    Major panels use double-line visual style, sub-panels use single-line.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str | None = None,
        major: bool = True,
        bg_color: tuple[int, int, int] | None = None,
        border_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Initialize the panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            title: Optional title (displayed in ALL CAPS)
            major: Whether this is a major panel (thicker border)
            bg_color: Background color (default: BG_MEDIUM)
            border_color: Border color (default: BORDER)
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, height)
        self.title = title.upper() if title else None
        self.major = major
        self.bg_color = bg_color or Colors.BG_MEDIUM
        self.border_color = border_color or Colors.BORDER

        self._border_width = (
            LAYOUT["border_width_thick"] if major else LAYOUT["border_width"]
        )

        # Calculate content area (inside borders and title)
        self._content_rect: pygame.Rect | None = None
        self._title_height = 0

        if self.title:
            font = get_fonts().get_font(Typography.SIZE_SUBHEADER, bold=True)
            self._title_height = font.get_height() + LAYOUT["panel_padding"]

    @property
    def content_rect(self) -> "pygame.Rect":
        """Get the content area inside the panel (excludes border and title)."""
        import pygame

        if self._content_rect is None:
            pad = LAYOUT["panel_padding"]
            bw = self._border_width

            self._content_rect = pygame.Rect(
                self.rect.x + bw + pad,
                self.rect.y + bw + self._title_height + pad,
                self.rect.width - (bw + pad) * 2,
                self.rect.height - bw * 2 - self._title_height - pad * 2,
            )

        return self._content_rect

    def set_position(self, x: int, y: int) -> None:
        """Set panel position.

        Args:
            x: New X position
            y: New Y position
        """
        self.rect.x = x
        self.rect.y = y
        self._content_rect = None  # Invalidate cache

    def set_size(self, width: int, height: int) -> None:
        """Set panel size.

        Args:
            width: New width
            height: New height
        """
        self.rect.width = width
        self.rect.height = height
        self._content_rect = None  # Invalidate cache

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the panel with border and optional title.

        Args:
            surface: Surface to draw on
        """
        import pygame

        bw = self._border_width

        # Background fill
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Outer border
        pygame.draw.rect(surface, self.border_color, self.rect, bw)

        # For major panels, draw an inner border line for double-line effect
        if self.major and bw >= 2:
            inner_rect = pygame.Rect(
                self.rect.x + bw + 1,
                self.rect.y + bw + 1,
                self.rect.width - (bw + 1) * 2,
                self.rect.height - (bw + 1) * 2,
            )
            pygame.draw.rect(surface, Colors.BORDER_HIGHLIGHT, inner_rect, 1)

        # Title bar
        if self.title:
            font = get_fonts().get_font(Typography.SIZE_SUBHEADER, bold=True)

            # Title background strip
            title_rect = pygame.Rect(
                self.rect.x + bw,
                self.rect.y + bw,
                self.rect.width - bw * 2,
                self._title_height,
            )
            pygame.draw.rect(surface, Colors.BG_DARK, title_rect)

            # Title underline
            line_y = self.rect.y + bw + self._title_height
            pygame.draw.line(
                surface,
                self.border_color,
                (self.rect.x + bw, line_y),
                (self.rect.x + self.rect.width - bw, line_y),
                1,
            )

            # Title text
            title_surface = font.render(
                self.title, Typography.ANTIALIAS, Colors.TEXT_HEADER
            )
            title_x = self.rect.x + bw + LAYOUT["panel_padding"]
            title_y = self.rect.y + bw + (self._title_height - font.get_height()) // 2
            surface.blit(title_surface, (title_x, title_y))


class StatusPanel(Panel):
    """A status panel that displays key-value pairs.

    Used for the right-side status area showing chapter, XP, hints, etc.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str | None = None,
    ) -> None:
        """Initialize the status panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            title: Optional title
        """
        super().__init__(x, y, width, height, title, major=True)
        self._stats: list[tuple[str, str, tuple[int, int, int] | None]] = []

    def set_stats(
        self, stats: list[tuple[str, str, tuple[int, int, int] | None]]
    ) -> None:
        """Set the stats to display.

        Args:
            stats: List of (label, value, color) tuples. Color can be None for default.
        """
        self._stats = stats

    def add_stat(
        self,
        label: str,
        value: str,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """Add a stat to display.

        Args:
            label: Stat label (displayed in muted)
            value: Stat value
            color: Optional value color (default: TEXT_PRIMARY)
        """
        self._stats.append((label, value, color))

    def clear_stats(self) -> None:
        """Clear all stats."""
        self._stats = []

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the status panel with stats.

        Args:
            surface: Surface to draw on
        """
        # Draw base panel
        super().draw(surface)

        if not self._stats:
            return

        fonts = get_fonts()
        label_font = fonts.get_label_font()
        value_font = fonts.get_body_font()

        content = self.content_rect
        y = content.y
        line_height = int(Typography.SIZE_BODY * Typography.LINE_HEIGHT) + 4

        for label, value, color in self._stats:
            if color is None:
                color = Colors.TEXT_PRIMARY

            # Check for separator (empty label/value)
            if not label and not value:
                # Draw a separator line
                sep_y = y + line_height // 2
                pygame.draw.line(
                    surface,
                    Colors.BORDER,
                    (content.x, sep_y),
                    (content.x + content.width, sep_y),
                    1,
                )
                y += line_height
                continue

            # Draw label (ALL CAPS, muted)
            label_surface = label_font.render(
                label.upper() + ":", Typography.ANTIALIAS, Colors.TEXT_MUTED
            )
            surface.blit(label_surface, (content.x, y))

            # Draw value (right-aligned or after label)
            value_surface = value_font.render(value, Typography.ANTIALIAS, color)
            value_x = content.x + content.width - value_surface.get_width()
            surface.blit(value_surface, (value_x, y))

            y += line_height


# Import pygame at module level for type hints only
import pygame
