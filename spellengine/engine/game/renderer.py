"""Rendering utilities for the game client.

This module provides backward-compatible rendering utilities while
integrating with the new UI theme system.
"""

from typing import TYPE_CHECKING

# Import colors from the new theme for backward compatibility
from spellengine.engine.game.ui.theme import Colors, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


# Legacy Gruvbox color palette (for backward compatibility)
# These map to the new Colors class
GRUVBOX = {
    # Backgrounds
    "bg_dark": Colors.BG_DARK,
    "bg_medium": Colors.BG_MEDIUM,
    "bg_light": Colors.BG_LIGHT,

    # Foregrounds
    "fg": Colors.TEXT_PRIMARY,
    "fg_dim": Colors.TEXT_MUTED,

    # Accents
    "red": Colors.RED,
    "green": Colors.GREEN,
    "yellow": Colors.YELLOW,
    "blue": Colors.BLUE,
    "purple": Colors.PURPLE,
    "aqua": Colors.AQUA,
    "orange": Colors.ORANGE,
}


class TypewriterText:
    """Animated text display with typewriter effect.

    Legacy wrapper around the new TypewriterText from ui.text.
    """

    def __init__(
        self,
        text: str,
        font: "pygame.font.Font",
        color: tuple[int, int, int] = Colors.TEXT_PRIMARY,
        speed: float = 0.03,
    ) -> None:
        """Initialize typewriter text.

        Args:
            text: Full text to display
            font: Pygame font to use
            color: Text color
            speed: Seconds per character
        """
        self.full_text = text
        self.font = font
        self.color = color
        self.speed = speed

        self.displayed_text = ""
        self.char_index = 0
        self.timer = 0.0
        self.complete = False

    def update(self, dt: float) -> None:
        """Update the typewriter animation.

        Args:
            dt: Delta time in seconds
        """
        if self.complete:
            return

        self.timer += dt
        while self.timer >= self.speed and self.char_index < len(self.full_text):
            self.timer -= self.speed
            self.char_index += 1
            self.displayed_text = self.full_text[: self.char_index]

        if self.char_index >= len(self.full_text):
            self.complete = True

    def skip(self) -> None:
        """Skip to end of text."""
        self.displayed_text = self.full_text
        self.char_index = len(self.full_text)
        self.complete = True

    def reset(self, new_text: str | None = None) -> None:
        """Reset the typewriter.

        Args:
            new_text: Optional new text to display
        """
        if new_text is not None:
            self.full_text = new_text
        self.displayed_text = ""
        self.char_index = 0
        self.timer = 0.0
        self.complete = False

    def render(self) -> "pygame.Surface":
        """Render the current text state.

        Returns:
            Surface with rendered text
        """
        return self.font.render(self.displayed_text, Typography.ANTIALIAS, self.color)

    def render_wrapped(
        self, max_width: int, line_height: int | None = None
    ) -> list[tuple["pygame.Surface", int]]:
        """Render with word wrapping.

        Args:
            max_width: Maximum line width in pixels
            line_height: Height per line (default: font height + 4)

        Returns:
            List of (surface, y_offset) tuples
        """
        if line_height is None:
            line_height = self.font.get_height() + 4

        lines = []
        y = 0

        for paragraph in self.displayed_text.split("\n"):
            if not paragraph.strip():
                y += line_height
                continue

            words = paragraph.split()
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surface = self.font.render(test_line, Typography.ANTIALIAS, self.color)

                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        surface = self.font.render(current_line, Typography.ANTIALIAS, self.color)
                        lines.append((surface, y))
                        y += line_height
                    current_line = word

            if current_line:
                surface = self.font.render(current_line, Typography.ANTIALIAS, self.color)
                lines.append((surface, y))
                y += line_height

        return lines


def draw_panel(
    surface: "pygame.Surface",
    rect: "pygame.Rect",
    bg_color: tuple[int, int, int] = Colors.BG_MEDIUM,
    border_color: tuple[int, int, int] = Colors.BG_LIGHT,
    border_width: int = 2,
) -> None:
    """Draw a panel with border.

    Legacy function - prefer using Panel class from ui.panel.

    Args:
        surface: Surface to draw on
        rect: Panel rectangle
        bg_color: Background color
        border_color: Border color
        border_width: Border width in pixels
    """
    import pygame

    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width)


def draw_progress_bar(
    surface: "pygame.Surface",
    rect: "pygame.Rect",
    progress: float,
    fg_color: tuple[int, int, int] = Colors.GREEN,
    bg_color: tuple[int, int, int] = Colors.BG_DARK,
    border_color: tuple[int, int, int] = Colors.BG_LIGHT,
) -> None:
    """Draw a progress bar.

    Args:
        surface: Surface to draw on
        rect: Bar rectangle
        progress: Progress value 0.0-1.0
        fg_color: Fill color
        bg_color: Background color
        border_color: Border color
    """
    import pygame

    progress = max(0.0, min(1.0, progress))

    # Background
    pygame.draw.rect(surface, bg_color, rect)

    # Fill
    fill_rect = pygame.Rect(
        rect.x + 2, rect.y + 2, int((rect.width - 4) * progress), rect.height - 4
    )
    if fill_rect.width > 0:
        pygame.draw.rect(surface, fg_color, fill_rect)

    # Border
    pygame.draw.rect(surface, border_color, rect, 2)
