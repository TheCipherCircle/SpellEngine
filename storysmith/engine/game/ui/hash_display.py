"""Hash display component with type-specific styling.

Displays hashes with color-coded type indicators and state management.
"""

from typing import TYPE_CHECKING

from storysmith.engine.game.ui.theme import Colors, Typography, get_fonts, LAYOUT

if TYPE_CHECKING:
    import pygame


class HashDisplay:
    """Component for displaying hash values with type indicators.

    States:
    - locked: Hash is obscured (shown as block characters)
    - revealed: Hash is visible
    - cracked: Hash has been solved (green checkmark)

    Colors based on hash type:
    - MD5: Tarnished amber
    - SHA1: Toxic cyan
    - SHA256: Corrupt purple
    - BCRYPT: Blood red
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        hash_value: str = "",
        hash_type: str = "MD5",
    ) -> None:
        """Initialize the hash display.

        Args:
            x: X position
            y: Y position
            width: Display width
            hash_value: The hash string to display
            hash_type: Hash algorithm (MD5, SHA1, SHA256, BCRYPT)
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, 0)  # Height calculated dynamically
        self.hash_value = hash_value
        self.hash_type = hash_type.upper()

        # State
        self.state = "revealed"  # locked, revealed, cracked

        # Get type-specific color
        self.type_color = Colors.get_hash_color(self.hash_type)

        # Calculate display properties
        self._font = get_fonts().get_font(Typography.SIZE_LABEL)
        self._type_font = get_fonts().get_font(Typography.SIZE_SMALL, bold=True)

        # Calculate height based on content
        self._update_height()

    def _update_height(self) -> None:
        """Calculate height based on hash length and wrapping."""
        # Type label + hash lines + padding
        type_height = self._type_font.get_height()
        chars_per_line = (self.rect.width - LAYOUT["panel_padding"] * 2) // (
            self._font.size("0")[0]
        )
        if chars_per_line < 1:
            chars_per_line = 16

        hash_lines = (len(self.hash_value) + chars_per_line - 1) // chars_per_line
        hash_lines = max(hash_lines, 2)  # At least 2 lines for appearance

        hash_height = hash_lines * int(
            self._font.get_height() * Typography.LINE_HEIGHT
        )

        self.rect.height = type_height + hash_height + LAYOUT["panel_padding"] * 2

    def set_hash(self, hash_value: str, hash_type: str | None = None) -> None:
        """Set the hash value and optionally the type.

        Args:
            hash_value: New hash value
            hash_type: New hash type (optional)
        """
        self.hash_value = hash_value
        if hash_type:
            self.hash_type = hash_type.upper()
            self.type_color = Colors.get_hash_color(self.hash_type)
        self._update_height()

    def set_state(self, state: str) -> None:
        """Set the display state.

        Args:
            state: One of 'locked', 'revealed', 'cracked'
        """
        if state in ("locked", "revealed", "cracked"):
            self.state = state

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the hash display.

        Args:
            surface: Surface to draw on
        """
        import pygame

        pad = LAYOUT["panel_padding"]
        x = self.rect.x + pad
        y = self.rect.y

        # Draw type label with icon-like bracket
        type_label = f"[{self.hash_type}]"
        type_surface = self._type_font.render(
            type_label, Typography.ANTIALIAS, self.type_color
        )
        surface.blit(type_surface, (x, y))

        # Separator line
        y += self._type_font.get_height() + 4
        pygame.draw.line(
            surface,
            Colors.BORDER,
            (x, y),
            (x + self.rect.width - pad * 2, y),
            1,
        )
        y += 6

        # Calculate hash display
        chars_per_line = (self.rect.width - pad * 2) // (self._font.size("0")[0])
        if chars_per_line < 1:
            chars_per_line = 16

        # Determine what to display based on state
        if self.state == "locked":
            # Show block characters
            display_hash = "\u2591" * len(self.hash_value)  # ░
            hash_color = Colors.TEXT_DIM
        elif self.state == "cracked":
            # Show hash with checkmark
            display_hash = self.hash_value
            hash_color = Colors.SUCCESS
        else:
            # Revealed - show hash normally
            display_hash = self.hash_value
            hash_color = self.type_color

        # Wrap and draw hash
        line_height = int(self._font.get_height() * Typography.LINE_HEIGHT)

        for i in range(0, len(display_hash), chars_per_line):
            line = display_hash[i : i + chars_per_line]
            line_surface = self._font.render(line, Typography.ANTIALIAS, hash_color)
            surface.blit(line_surface, (x, y))
            y += line_height

        # Draw checkmark for cracked state
        if self.state == "cracked":
            check_surface = self._font.render(
                " \u2713", Typography.ANTIALIAS, Colors.SUCCESS  # checkmark
            )
            surface.blit(check_surface, (x + self.rect.width - pad * 2 - 20, self.rect.y))


class HashInputPanel:
    """Combined hash display and input field panel.

    Used in the bottom-right area of the encounter screen.
    Shows the target hash and provides input for password guessing.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        hash_value: str = "",
        hash_type: str = "MD5",
    ) -> None:
        """Initialize the hash input panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            hash_value: The target hash
            hash_type: Hash algorithm type
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, height)
        self.hash_value = hash_value
        self.hash_type = hash_type

        # Components
        self.hash_display = HashDisplay(
            x + LAYOUT["panel_padding"],
            y + LAYOUT["panel_padding"],
            width - LAYOUT["panel_padding"] * 2,
            hash_value,
            hash_type,
        )

        # Input state
        self.input_text = ""
        self.input_active = True
        self.cursor_visible = True
        self.cursor_timer = 0.0

        # Fonts
        self._input_font = get_fonts().get_font(Typography.SIZE_BODY)
        self._prompt_font = get_fonts().get_font(Typography.SIZE_SMALL)

    def set_hash(self, hash_value: str, hash_type: str) -> None:
        """Set the target hash.

        Args:
            hash_value: Hash string
            hash_type: Hash algorithm type
        """
        self.hash_value = hash_value
        self.hash_type = hash_type
        self.hash_display.set_hash(hash_value, hash_type)

    def handle_event(self, event: "pygame.event.Event") -> str | None:
        """Handle input events.

        Args:
            event: Pygame event

        Returns:
            Submitted text if Enter was pressed, None otherwise
        """
        import pygame

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                submitted = self.input_text
                self.input_text = ""
                return submitted

            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_ESCAPE:
                self.input_text = ""

            elif event.unicode and event.unicode.isprintable():
                if len(self.input_text) < 50:  # Max length
                    self.input_text += event.unicode

        return None

    def update(self, dt: float) -> None:
        """Update cursor blink.

        Args:
            dt: Delta time in seconds
        """
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the hash input panel.

        Args:
            surface: Surface to draw on
        """
        import pygame

        pad = LAYOUT["panel_padding"]
        bw = LAYOUT["border_width"]

        # Panel background
        pygame.draw.rect(surface, Colors.BG_MEDIUM, self.rect)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, bw)

        # Title
        title_font = get_fonts().get_font(Typography.SIZE_SUBHEADER, bold=True)
        title_surface = title_font.render(
            "TARGET HASH", Typography.ANTIALIAS, Colors.TEXT_HEADER
        )
        surface.blit(title_surface, (self.rect.x + pad, self.rect.y + pad))

        # Title underline
        line_y = self.rect.y + pad + title_font.get_height() + 4
        pygame.draw.line(
            surface,
            Colors.BORDER,
            (self.rect.x + pad, line_y),
            (self.rect.x + self.rect.width - pad, line_y),
            1,
        )

        # Hash display
        hash_y = line_y + 8
        self.hash_display.rect.x = self.rect.x + pad
        self.hash_display.rect.y = hash_y
        self.hash_display.draw(surface)

        # Input field
        input_height = self._input_font.get_height() + 12
        input_y = self.rect.y + self.rect.height - input_height - pad

        # Input background
        input_rect = pygame.Rect(
            self.rect.x + pad,
            input_y,
            self.rect.width - pad * 2,
            input_height,
        )
        pygame.draw.rect(surface, Colors.BG_DARK, input_rect)
        pygame.draw.rect(
            surface,
            Colors.CURSOR if self.input_active else Colors.BORDER,
            input_rect,
            1,
        )

        # Input prompt and text
        prompt = "> "
        text = prompt + self.input_text
        if self.input_active and self.cursor_visible:
            text += "_"

        input_surface = self._input_font.render(
            text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
        )
        surface.blit(input_surface, (input_rect.x + 8, input_rect.y + 6))

    def clear(self) -> None:
        """Clear the input text."""
        self.input_text = ""

    def flash_error(self) -> None:
        """Flash the input to indicate error (sets cracked state briefly)."""
        # Could add animation here
        pass

    def flash_success(self) -> None:
        """Flash the input to indicate success."""
        self.hash_display.set_state("cracked")
