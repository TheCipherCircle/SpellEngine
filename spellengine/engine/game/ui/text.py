"""Text rendering utilities with retro styling.

Anti-aliased body text for readability, chunky headers for retro feel.
Corrupted SNES aesthetic with monospace fonts and ALL CAPS headers.
"""

from typing import TYPE_CHECKING

from spellengine.engine.game.ui.theme import Colors, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


class TextRenderer:
    """Utility class for rendering styled text without anti-aliasing."""

    @staticmethod
    def render_title(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render a screen title (ALL CAPS, large, bold, chunky).

        Args:
            text: Text to render
            color: Text color (default: TEXT_HEADER)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_title_font()
        color = color or Colors.TEXT_HEADER
        # Headers use chunky rendering (no anti-alias) for retro feel
        return font.render(text.upper(), Typography.ANTIALIAS_HEADERS, color)

    @staticmethod
    def render_header(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render a panel header (ALL CAPS, medium, bold, chunky).

        Args:
            text: Text to render
            color: Text color (default: TEXT_HEADER)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_header_font()
        color = color or Colors.TEXT_HEADER
        # Headers use chunky rendering (no anti-alias) for retro feel
        return font.render(text.upper(), Typography.ANTIALIAS_HEADERS, color)

    @staticmethod
    def render_body(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render body text.

        Args:
            text: Text to render
            color: Text color (default: TEXT_PRIMARY)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_body_font()
        color = color or Colors.TEXT_PRIMARY
        return font.render(text, Typography.ANTIALIAS, color)

    @staticmethod
    def render_label(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render a label (ALL CAPS, small, muted, chunky).

        Args:
            text: Text to render
            color: Text color (default: TEXT_MUTED)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_label_font()
        color = color or Colors.TEXT_MUTED
        # Labels use chunky rendering for retro feel
        return font.render(text.upper(), Typography.ANTIALIAS_HEADERS, color)

    @staticmethod
    def render_prompt(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render a prompt with brackets (e.g., "[H] Hint").

        Args:
            text: Text to render
            color: Text color (default: TEXT_MUTED)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_small_font()
        color = color or Colors.TEXT_MUTED
        return font.render(text, Typography.ANTIALIAS, color)

    @staticmethod
    def render_value(text: str, color: tuple[int, int, int] | None = None) -> "pygame.Surface":
        """Render a value (mixed case, primary).

        Args:
            text: Text to render
            color: Text color (default: TEXT_PRIMARY)

        Returns:
            Rendered text surface
        """
        font = get_fonts().get_body_font()
        color = color or Colors.TEXT_PRIMARY
        return font.render(text, Typography.ANTIALIAS, color)

    @staticmethod
    def wrap_text(
        text: str,
        font: "pygame.font.Font",
        max_width: int,
        color: tuple[int, int, int] | None = None,
    ) -> list[tuple["pygame.Surface", int]]:
        """Wrap text to fit within max width and render each line.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
            color: Text color (default: TEXT_PRIMARY)

        Returns:
            List of (surface, y_offset) tuples
        """
        color = color or Colors.TEXT_PRIMARY
        lines: list[tuple["pygame.Surface", int]] = []
        y = 0
        line_height = int(font.get_height() * Typography.LINE_HEIGHT)

        for paragraph in text.split("\n"):
            if not paragraph.strip():
                y += line_height
                continue

            words = paragraph.split()
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surface = font.render(test_line, Typography.ANTIALIAS, color)

                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        surface = font.render(current_line, Typography.ANTIALIAS, color)
                        lines.append((surface, y))
                        y += line_height
                    current_line = word

            if current_line:
                surface = font.render(current_line, Typography.ANTIALIAS, color)
                lines.append((surface, y))
                y += line_height

        return lines


class TypewriterText:
    """Animated text display with typewriter effect.

    Text appears character by character for dramatic effect.
    """

    def __init__(
        self,
        text: str,
        color: tuple[int, int, int] | None = None,
        speed: float = 0.03,
        font_size: int | None = None,
    ) -> None:
        """Initialize typewriter text.

        Args:
            text: Full text to display
            color: Text color (default: TEXT_PRIMARY)
            speed: Seconds per character
            font_size: Font size (default: SIZE_BODY)
        """
        self.full_text = text
        self.color = color or Colors.TEXT_PRIMARY
        self.speed = speed
        self.font_size = font_size or Typography.SIZE_BODY

        self.displayed_text = ""
        self.char_index = 0
        self.timer = 0.0
        self.complete = False

        self._font = get_fonts().get_font(self.font_size)

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
        return self._font.render(self.displayed_text, Typography.ANTIALIAS, self.color)

    def render_wrapped(
        self, max_width: int, line_height: int | None = None
    ) -> list[tuple["pygame.Surface", int]]:
        """Render with word wrapping.

        Args:
            max_width: Maximum line width in pixels
            line_height: Height per line (default: calculated from font)

        Returns:
            List of (surface, y_offset) tuples
        """
        if line_height is None:
            line_height = int(self._font.get_height() * Typography.LINE_HEIGHT)

        return TextRenderer.wrap_text(
            self.displayed_text,
            self._font,
            max_width,
            self.color,
        )


def draw_double_border_title(
    surface: "pygame.Surface",
    text: str,
    x: int,
    y: int,
    width: int,
) -> int:
    """Draw a title with double-line borders above and below.

    Like: ═══════════════
              TITLE
          ═══════════════

    Args:
        surface: Surface to draw on
        text: Title text (will be centered, ALL CAPS)
        x: X position
        y: Y position
        width: Total width
        color: Text color

    Returns:
        Total height used
    """
    import pygame

    font = get_fonts().get_header_font()
    line_char_width = 12  # Approximate width of ═ character

    # Calculate how many line characters we need
    num_chars = width // line_char_width

    # Create the border line
    border_line = "\u2550" * num_chars  # ═

    # Render border lines (chunky for retro feel)
    border_surface = font.render(border_line, Typography.ANTIALIAS_HEADERS, Colors.TEXT_HEADER)

    # Render title (chunky for retro feel)
    title_surface = font.render(text.upper(), Typography.ANTIALIAS_HEADERS, Colors.TEXT_HEADER)
    title_x = x + (width - title_surface.get_width()) // 2

    line_height = font.get_height()

    # Draw top border
    surface.blit(border_surface, (x, y))

    # Draw title
    surface.blit(title_surface, (title_x, y + line_height))

    # Draw bottom border
    surface.blit(border_surface, (x, y + line_height * 2))

    return line_height * 3
