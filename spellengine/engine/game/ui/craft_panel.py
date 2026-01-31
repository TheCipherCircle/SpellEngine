"""Craft Panel - Mask/Rule building UI for CRAFT encounters.

Provides an interactive interface for building masks and rules:
- Grid of input slots for pattern building
- Charset palette for selecting mask characters
- Live preview showing example output
- Submit button with validation

Gruvbox-styled with retro game aesthetic.
"""

from typing import TYPE_CHECKING, Callable

from spellengine.engine.game.ui.theme import Colors, SPACING, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


# Mask charset options
MASK_CHARSETS = [
    ("?l", "a-z", "lowercase letter"),
    ("?u", "A-Z", "uppercase letter"),
    ("?d", "0-9", "digit"),
    ("?s", "!@#$", "special char"),
    ("?a", "all", "any printable"),
]

# Example characters for preview
CHARSET_EXAMPLES = {
    "?l": "abcd",
    "?u": "ABCD",
    "?d": "1234",
    "?s": "!@#$",
    "?a": "aB1!",
}


class MaskSlot:
    """A single slot in the mask builder grid."""

    def __init__(self, x: int, y: int, size: int, index: int):
        """Initialize a mask slot.

        Args:
            x: X position
            y: Y position
            size: Slot size (width and height)
            index: Slot index in the pattern
        """
        import pygame

        self.x = x
        self.y = y
        self.size = size
        self.index = index
        self.value: str = ""  # Empty, or mask charset like "?l"
        self.rect = pygame.Rect(x, y, size, size)
        self._hovered = False
        self._selected = False

    def set_value(self, value: str) -> None:
        """Set the slot value."""
        self.value = value

    def clear(self) -> None:
        """Clear the slot."""
        self.value = ""

    def render(self, surface: "pygame.Surface") -> None:
        """Render the slot."""
        import pygame

        fonts = get_fonts()

        # Background
        if self._selected:
            bg_color = Colors.BLUE
        elif self._hovered:
            bg_color = Colors.BG_HIGHLIGHT
        else:
            bg_color = Colors.BG_DARK

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)

        # Border
        border_color = Colors.BORDER_HIGHLIGHT if self._selected else Colors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=4)

        # Value text
        if self.value:
            value_font = fonts.get_font(Typography.SIZE_BODY, bold=True)
            # Color-code by charset type
            if self.value == "?l":
                text_color = Colors.SUCCESS
            elif self.value == "?u":
                text_color = Colors.BLUE
            elif self.value == "?d":
                text_color = Colors.YELLOW
            elif self.value == "?s":
                text_color = Colors.PURPLE
            else:
                text_color = Colors.TEXT_PRIMARY

            text_surface = value_font.render(self.value, Typography.ANTIALIAS, text_color)
            text_x = self.x + (self.size - text_surface.get_width()) // 2
            text_y = self.y + (self.size - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        else:
            # Empty slot indicator
            index_font = fonts.get_font(Typography.SIZE_SMALL)
            index_text = str(self.index + 1)
            index_surface = index_font.render(index_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
            index_x = self.x + (self.size - index_surface.get_width()) // 2
            index_y = self.y + (self.size - index_surface.get_height()) // 2
            surface.blit(index_surface, (index_x, index_y))


class CharsetButton:
    """A button for selecting a charset."""

    def __init__(self, x: int, y: int, width: int, height: int, charset: str, label: str, description: str):
        """Initialize a charset button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            charset: The mask charset (e.g., "?l")
            label: Short label (e.g., "a-z")
            description: Full description
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.charset = charset
        self.label = label
        self.description = description
        self.rect = pygame.Rect(x, y, width, height)
        self._hovered = False
        self._pressed = False

    def render(self, surface: "pygame.Surface") -> None:
        """Render the charset button."""
        import pygame

        fonts = get_fonts()

        # Background
        if self._pressed:
            bg_color = Colors.BLUE
        elif self._hovered:
            bg_color = Colors.BG_HIGHLIGHT
        else:
            bg_color = Colors.BG_DARK

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, width=1, border_radius=4)

        # Charset text
        charset_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        # Color-code
        if self.charset == "?l":
            text_color = Colors.SUCCESS
        elif self.charset == "?u":
            text_color = Colors.BLUE
        elif self.charset == "?d":
            text_color = Colors.YELLOW
        elif self.charset == "?s":
            text_color = Colors.PURPLE
        else:
            text_color = Colors.TEXT_PRIMARY

        charset_surface = charset_font.render(self.charset, Typography.ANTIALIAS, text_color)
        charset_x = self.x + 8
        charset_y = self.y + (self.height - charset_surface.get_height()) // 2
        surface.blit(charset_surface, (charset_x, charset_y))

        # Label
        label_font = fonts.get_font(Typography.SIZE_SMALL)
        label_surface = label_font.render(self.label, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        label_x = self.x + 40
        label_y = self.y + (self.height - label_surface.get_height()) // 2
        surface.blit(label_surface, (label_x, label_y))


class CraftPanel:
    """Mask/Rule building panel for CRAFT encounters.

    Layout:
    +------------------------------------------+
    |  BUILD YOUR MASK                         |
    +------------------------------------------+
    |  [?l] [?u] [  ] [  ] [  ] [  ] [  ] [  ] |  <- Slots
    +------------------------------------------+
    |  CHARSET PALETTE:                        |
    |  [?l a-z] [?u A-Z] [?d 0-9] [?s !@#]    |
    +------------------------------------------+
    |  PREVIEW: aaaa12                         |
    +------------------------------------------+
    |  [CLEAR]                    [SUBMIT]     |
    +------------------------------------------+
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        max_slots: int = 8,
        expected_pattern: str | None = None,
        on_submit: Callable[[str], None] | None = None,
    ):
        """Initialize the craft panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            max_slots: Maximum number of slots (default 8)
            expected_pattern: Expected mask pattern for validation
            on_submit: Callback when pattern is submitted
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_slots = max_slots
        self.expected_pattern = expected_pattern
        self.on_submit = on_submit

        self.rect = pygame.Rect(x, y, width, height)

        # State
        self.selected_slot = 0
        self._feedback_message = ""
        self._feedback_color = Colors.TEXT_PRIMARY
        self._feedback_timer = 0.0

        # Create slots
        self.slots: list[MaskSlot] = []
        slot_size = 44
        slot_spacing = 8
        total_slots_width = max_slots * slot_size + (max_slots - 1) * slot_spacing
        slots_x = x + (width - total_slots_width) // 2
        slots_y = y + 50

        for i in range(max_slots):
            slot_x = slots_x + i * (slot_size + slot_spacing)
            slot = MaskSlot(slot_x, slots_y, slot_size, i)
            self.slots.append(slot)

        # Mark first slot as selected
        if self.slots:
            self.slots[0]._selected = True

        # Create charset buttons
        self.charset_buttons: list[CharsetButton] = []
        button_width = 80
        button_height = 32
        button_spacing = 10
        buttons_y = slots_y + slot_size + 30

        for i, (charset, label, desc) in enumerate(MASK_CHARSETS):
            btn_x = x + 20 + i * (button_width + button_spacing)
            btn = CharsetButton(btn_x, buttons_y, button_width, button_height, charset, label, desc)
            self.charset_buttons.append(btn)

        # Clear and submit button positions
        self.clear_button_rect = pygame.Rect(x + 20, y + height - 50, 80, 36)
        self.submit_button_rect = pygame.Rect(x + width - 100, y + height - 50, 80, 36)

        # Preview area
        self.preview_y = buttons_y + button_height + 30

    def get_pattern(self) -> str:
        """Get the current mask pattern from slots."""
        return "".join(slot.value for slot in self.slots if slot.value)

    def get_preview(self) -> str:
        """Generate an example output for the current pattern."""
        preview = ""
        for slot in self.slots:
            if slot.value in CHARSET_EXAMPLES:
                # Get a character from the example set
                examples = CHARSET_EXAMPLES[slot.value]
                char_idx = len(preview) % len(examples)
                preview += examples[char_idx]
        return preview or "..."

    def set_slot_value(self, index: int, value: str) -> None:
        """Set a slot value and advance to next slot."""
        if 0 <= index < len(self.slots):
            self.slots[index].set_value(value)
            # Advance to next empty slot
            self._advance_selection()

    def _advance_selection(self) -> None:
        """Advance selection to next empty slot or stay at end."""
        # Deselect current
        if 0 <= self.selected_slot < len(self.slots):
            self.slots[self.selected_slot]._selected = False

        # Find next empty slot
        for i in range(self.selected_slot + 1, len(self.slots)):
            if not self.slots[i].value:
                self.selected_slot = i
                self.slots[i]._selected = True
                return

        # If no empty slots, select last filled slot
        self.selected_slot = min(self.selected_slot + 1, len(self.slots) - 1)
        if self.selected_slot < len(self.slots):
            self.slots[self.selected_slot]._selected = True

    def _select_slot(self, index: int) -> None:
        """Select a specific slot."""
        if 0 <= index < len(self.slots):
            # Deselect current
            if 0 <= self.selected_slot < len(self.slots):
                self.slots[self.selected_slot]._selected = False
            # Select new
            self.selected_slot = index
            self.slots[index]._selected = True

    def clear_all(self) -> None:
        """Clear all slots."""
        for slot in self.slots:
            slot.clear()
        self._select_slot(0)

    def submit(self) -> None:
        """Submit the current pattern."""
        pattern = self.get_pattern()

        if not pattern:
            self._feedback_message = "Build a pattern first!"
            self._feedback_color = Colors.WARNING
            self._feedback_timer = 2.0
            return

        if self.on_submit:
            self.on_submit(pattern)

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle input events.

        Returns True if event was consumed.
        """
        import pygame

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos

            # Update slot hover states
            for slot in self.slots:
                slot._hovered = slot.rect.collidepoint(pos)

            # Update button hover states
            for btn in self.charset_buttons:
                btn._hovered = btn.rect.collidepoint(pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check slot clicks
            for i, slot in enumerate(self.slots):
                if slot.rect.collidepoint(pos):
                    self._select_slot(i)
                    return True

            # Check charset button clicks
            for btn in self.charset_buttons:
                if btn.rect.collidepoint(pos):
                    self.set_slot_value(self.selected_slot, btn.charset)
                    return True

            # Check clear button
            if self.clear_button_rect.collidepoint(pos):
                self.clear_all()
                return True

            # Check submit button
            if self.submit_button_rect.collidepoint(pos):
                self.submit()
                return True

        elif event.type == pygame.KEYDOWN:
            # Keyboard shortcuts for charsets
            if event.key == pygame.K_l:
                self.set_slot_value(self.selected_slot, "?l")
                return True
            elif event.key == pygame.K_u:
                self.set_slot_value(self.selected_slot, "?u")
                return True
            elif event.key == pygame.K_d:
                self.set_slot_value(self.selected_slot, "?d")
                return True
            elif event.key == pygame.K_s:
                self.set_slot_value(self.selected_slot, "?s")
                return True
            elif event.key == pygame.K_a:
                self.set_slot_value(self.selected_slot, "?a")
                return True
            elif event.key == pygame.K_BACKSPACE:
                # Clear current slot and go back
                if self.selected_slot > 0:
                    if not self.slots[self.selected_slot].value:
                        self._select_slot(self.selected_slot - 1)
                    self.slots[self.selected_slot].clear()
                return True
            elif event.key == pygame.K_LEFT:
                if self.selected_slot > 0:
                    self._select_slot(self.selected_slot - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                if self.selected_slot < len(self.slots) - 1:
                    self._select_slot(self.selected_slot + 1)
                return True
            elif event.key == pygame.K_RETURN:
                self.submit()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.clear_all()
                return True

        return False

    def update(self, dt: float) -> None:
        """Update panel state."""
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._feedback_message = ""

    def render(self, surface: "pygame.Surface") -> None:
        """Render the craft panel."""
        import pygame

        fonts = get_fonts()

        # Panel background
        pygame.draw.rect(surface, Colors.BG_DARK, self.rect, border_radius=8)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, width=2, border_radius=8)

        # Title
        title_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        title_surface = title_font.render("BUILD YOUR MASK", Typography.ANTIALIAS, Colors.TEXT_HEADER)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, self.y + 15))

        # Render slots
        for slot in self.slots:
            slot.render(surface)

        # Charset palette label
        label_font = fonts.get_font(Typography.SIZE_LABEL)
        label_surface = label_font.render("CHARSET PALETTE:", Typography.ANTIALIAS, Colors.TEXT_MUTED)
        surface.blit(label_surface, (self.x + 20, self.slots[0].y + self.slots[0].size + 12))

        # Render charset buttons
        for btn in self.charset_buttons:
            btn.render(surface)

        # Keyboard shortcuts hint
        hint_font = fonts.get_font(Typography.SIZE_SMALL)
        hint_text = "Keys: [L]ower [U]pper [D]igit [S]ymbol [A]ll"
        hint_surface = hint_font.render(hint_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        hint_x = self.x + (self.width - hint_surface.get_width()) // 2
        hint_y = self.charset_buttons[0].y + self.charset_buttons[0].height + 8
        surface.blit(hint_surface, (hint_x, hint_y))

        # Preview
        preview_label_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        preview_label = preview_label_font.render("PREVIEW:", Typography.ANTIALIAS, Colors.TEXT_PRIMARY)
        surface.blit(preview_label, (self.x + 20, self.preview_y))

        pattern = self.get_pattern()
        preview_text = self.get_preview()

        preview_font = fonts.get_font(Typography.SIZE_BODY, bold=True)
        pattern_surface = preview_font.render(f"{pattern} → {preview_text}", Typography.ANTIALIAS, Colors.YELLOW)
        surface.blit(pattern_surface, (self.x + 100, self.preview_y))

        # Clear button
        clear_hovered = self.clear_button_rect.collidepoint(pygame.mouse.get_pos())
        clear_bg = Colors.BG_HIGHLIGHT if clear_hovered else Colors.BG_DARK
        pygame.draw.rect(surface, clear_bg, self.clear_button_rect, border_radius=4)
        pygame.draw.rect(surface, Colors.BORDER, self.clear_button_rect, width=1, border_radius=4)

        clear_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        clear_surface = clear_font.render("CLEAR", Typography.ANTIALIAS, Colors.TEXT_MUTED)
        clear_x = self.clear_button_rect.x + (self.clear_button_rect.width - clear_surface.get_width()) // 2
        clear_y = self.clear_button_rect.y + (self.clear_button_rect.height - clear_surface.get_height()) // 2
        surface.blit(clear_surface, (clear_x, clear_y))

        # Submit button
        submit_hovered = self.submit_button_rect.collidepoint(pygame.mouse.get_pos())
        submit_bg = Colors.SUCCESS if submit_hovered else Colors.BG_HIGHLIGHT
        pygame.draw.rect(surface, submit_bg, self.submit_button_rect, border_radius=4)
        pygame.draw.rect(surface, Colors.BORDER, self.submit_button_rect, width=1, border_radius=4)

        submit_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        submit_color = Colors.BG_DARKEST if submit_hovered else Colors.SUCCESS
        submit_surface = submit_font.render("SUBMIT", Typography.ANTIALIAS, submit_color)
        submit_x = self.submit_button_rect.x + (self.submit_button_rect.width - submit_surface.get_width()) // 2
        submit_y = self.submit_button_rect.y + (self.submit_button_rect.height - submit_surface.get_height()) // 2
        surface.blit(submit_surface, (submit_x, submit_y))

        # Feedback message
        if self._feedback_message:
            feedback_font = fonts.get_font(Typography.SIZE_BODY)
            feedback_surface = feedback_font.render(self._feedback_message, Typography.ANTIALIAS, self._feedback_color)
            feedback_x = self.x + (self.width - feedback_surface.get_width()) // 2
            feedback_y = self.submit_button_rect.y - 30
            surface.blit(feedback_surface, (feedback_x, feedback_y))
