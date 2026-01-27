"""Button UI component for game client.

Styled with Gruvbox colors, square corners, thick borders.
Corrupted SNES aesthetic.
"""

from typing import Callable, TYPE_CHECKING

from patternforge.game.ui.theme import Colors, Typography, get_fonts, LAYOUT

if TYPE_CHECKING:
    import pygame


class Button:
    """A clickable button widget.

    Features:
    - Gruvbox themed with hover/press states
    - Square corners (no rounding)
    - Thick borders
    - No anti-aliasing for retro feel
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable[[], None] | None = None,
        font_size: int | None = None,
    ) -> None:
        """Initialize the button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button label
            callback: Function to call on click
            font_size: Font size (default: SIZE_BODY)
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

        self.hovered = False
        self.pressed = False
        self.enabled = True

        self._font_size = font_size or Typography.SIZE_BODY
        self._font = get_fonts().get_font(self._font_size)

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            True if button was clicked
        """
        import pygame

        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
                    return True

        return False

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the button.

        Args:
            surface: Surface to draw on
        """
        import pygame

        # Determine colors based on state
        if not self.enabled:
            bg_color = Colors.BG_DARK
            border_color = Colors.BORDER
            text_color = Colors.TEXT_DIM
        elif self.pressed:
            bg_color = Colors.BG_DARK
            border_color = Colors.TEXT_HEADER
            text_color = Colors.TEXT_HEADER
        elif self.hovered:
            bg_color = Colors.BG_LIGHT
            border_color = Colors.TEXT_HEADER
            text_color = Colors.TEXT_HEADER
        else:
            bg_color = Colors.BG_MEDIUM
            border_color = Colors.BORDER
            text_color = Colors.TEXT_PRIMARY

        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)

        # Draw border (thicker when hovered/pressed)
        border_width = LAYOUT["border_width"] if (self.hovered or self.pressed) else 1
        pygame.draw.rect(surface, border_color, self.rect, border_width)

        # Draw text
        text_surface = self._font.render(self.text, Typography.ANTIALIAS, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def set_position(self, x: int, y: int) -> None:
        """Set button position.

        Args:
            x: New X position
            y: New Y position
        """
        self.rect.x = x
        self.rect.y = y
