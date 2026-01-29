"""Text input box for password guessing.

Styled with Gruvbox colors, blinking cursor, monospace font.
Anti-aliased text for readability while typing.
"""

from typing import Callable, TYPE_CHECKING

from spellengine.engine.game.ui.theme import Colors, Typography, get_fonts, LAYOUT, SPACING

if TYPE_CHECKING:
    import pygame


class TextBox:
    """A text input field for password guessing.

    Features:
    - Monospace font for terminal feel
    - Blinking cursor with > prefix
    - Orange cursor when active
    - Anti-aliased text for readability
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        placeholder: str = "Enter password...",
        on_submit: Callable[[str], None] | None = None,
        on_keystroke: Callable[[], None] | None = None,
        font_size: int | None = None,
        max_length: int = 50,
    ) -> None:
        """Initialize the text box.

        Args:
            x: X position
            y: Y position
            width: Box width
            height: Box height
            placeholder: Placeholder text
            on_submit: Callback when Enter pressed
            on_keystroke: Callback when a key is typed (for sound effects)
            font_size: Font size (default: SIZE_BODY)
            max_length: Maximum input length
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.on_submit = on_submit
        self.on_keystroke = on_keystroke
        self.max_length = max_length

        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0

        # Error flash state
        self._error_flash = False
        self._error_timer = 0.0

        # Success flash state
        self._success_flash = False
        self._success_timer = 0.0

        # Font
        self._font_size = font_size or Typography.SIZE_BODY
        self._font = get_fonts().get_font(self._font_size)

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            True if text was submitted
        """
        import pygame

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.text and self.on_submit:
                    self.on_submit(self.text)
                    self.text = ""
                    return True

            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.text = ""

            elif event.unicode and len(self.text) < self.max_length:
                # Filter to printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode
                    # Trigger keystroke callback for sound effects
                    if self.on_keystroke:
                        self.on_keystroke()

        return False

    def update(self, dt: float) -> None:
        """Update cursor blink and flash effects.

        Args:
            dt: Delta time in seconds
        """
        # Cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        # Error flash decay
        if self._error_flash:
            self._error_timer -= dt
            if self._error_timer <= 0:
                self._error_flash = False

        # Success flash decay
        if self._success_flash:
            self._success_timer -= dt
            if self._success_timer <= 0:
                self._success_flash = False

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the text box.

        Args:
            surface: Surface to draw on
        """
        import pygame

        # Determine colors based on state
        if self._error_flash:
            bg_color = Colors.BG_DARK
            border_color = Colors.ERROR
            text_color = Colors.ERROR
        elif self._success_flash:
            bg_color = Colors.BG_DARK
            border_color = Colors.SUCCESS
            text_color = Colors.SUCCESS
        elif self.active:
            bg_color = Colors.BG_MEDIUM
            border_color = Colors.CURSOR  # Orange when active
            text_color = Colors.TEXT_PRIMARY
        else:
            bg_color = Colors.BG_DARK
            border_color = Colors.BORDER
            text_color = Colors.TEXT_PRIMARY

        # Background
        pygame.draw.rect(surface, bg_color, self.rect)

        # Border (2px for active, 1px for inactive)
        border_width = LAYOUT["border_width"] if self.active else 1
        pygame.draw.rect(surface, border_color, self.rect, border_width)

        # Build display text with > prefix
        if self.text:
            display_text = f"> {self.text}"
        elif self.active:
            display_text = "> "
        else:
            display_text = self.placeholder

        # Add cursor if active
        if self.active and self.cursor_visible:
            display_text += "_"

        # Choose color for placeholder vs actual text
        if not self.text and not self.active:
            render_color = Colors.TEXT_DIM
        else:
            render_color = text_color

        # Render text
        text_surface = self._font.render(
            display_text, Typography.ANTIALIAS, render_color
        )

        # Position text with padding
        text_y = self.rect.centery - text_surface.get_height() // 2
        text_x = self.rect.x + LAYOUT["panel_padding"]

        # Clip to box
        clip_rect = self.rect.inflate(-LAYOUT["panel_padding"] * 2, -4)
        surface.set_clip(clip_rect)
        surface.blit(text_surface, (text_x, text_y))
        surface.set_clip(None)

    def clear(self) -> None:
        """Clear the text input."""
        self.text = ""

    def set_text(self, text: str) -> None:
        """Set the text content.

        Args:
            text: New text content
        """
        self.text = text[: self.max_length]

    def focus(self) -> None:
        """Set focus to this text box."""
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0

    def blur(self) -> None:
        """Remove focus from this text box."""
        self.active = False

    def flash_error(self, duration: float = 0.5) -> None:
        """Flash the text box to indicate an error.

        Args:
            duration: Flash duration in seconds
        """
        self._error_flash = True
        self._error_timer = duration

    def flash_success(self, duration: float = 0.5) -> None:
        """Flash the text box to indicate success.

        Args:
            duration: Flash duration in seconds
        """
        self._success_flash = True
        self._success_timer = duration
