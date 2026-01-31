"""Puzzle Panel - Multi-step verification UI for PUZZLE_BOX encounters.

Provides an interface for completing multi-step challenges:
- Multiple verification steps (KEY 1, KEY 2, KEY 3)
- Each step has input + VERIFY button
- Progress through steps sequentially
- Final UNLOCK when all complete

Also handles PIPELINE encounters:
- Multiple command input fields
- Step-by-step execution display
- Validation at each step

Gruvbox-styled with retro game aesthetic.
"""

from typing import TYPE_CHECKING, Callable

from spellengine.engine.game.ui.theme import Colors, SPACING, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


class PuzzleStep:
    """A single step in a puzzle box."""

    def __init__(
        self,
        index: int,
        label: str,
        expected: str,
        hint: str = "",
    ):
        """Initialize a puzzle step.

        Args:
            index: Step index (0-based)
            label: Display label (e.g., "KEY 1")
            expected: Expected answer
            hint: Hint text
        """
        self.index = index
        self.label = label
        self.expected = expected
        self.hint = hint
        self.value = ""
        self.verified = False
        self.error = False


class PuzzlePanel:
    """Multi-step verification panel for PUZZLE_BOX and PIPELINE encounters.

    Layout:
    +------------------------------------------+
    |  PUZZLE BOX                              |
    +------------------------------------------+
    |  KEY 1: [________] [VERIFY] [CHECK]      |
    |  KEY 2: [________] [VERIFY] [ ]          |
    |  KEY 3: [________] [VERIFY] [ ]          |
    +------------------------------------------+
    |  Progress: 1/3                           |
    +------------------------------------------+
    |  [UNLOCK]                                |
    +------------------------------------------+
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        steps: list[tuple[str, str, str]] | None = None,
        title: str = "PUZZLE BOX",
        on_complete: Callable[[], None] | None = None,
    ):
        """Initialize the puzzle panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            steps: List of (label, expected, hint) tuples
            title: Panel title
            on_complete: Callback when all steps verified
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.on_complete = on_complete

        self.rect = pygame.Rect(x, y, width, height)

        # Create steps
        self.steps: list[PuzzleStep] = []
        if steps:
            for i, (label, expected, hint) in enumerate(steps):
                self.steps.append(PuzzleStep(i, label, expected, hint))

        # State
        self.current_step = 0
        self._feedback_message = ""
        self._feedback_color = Colors.TEXT_PRIMARY
        self._feedback_timer = 0.0
        self._all_verified = False

        # Input state
        self._input_active = True
        self._cursor_visible = True
        self._cursor_timer = 0.0

    @property
    def is_complete(self) -> bool:
        """Check if all steps are verified."""
        return self._all_verified

    def get_current_input(self) -> str:
        """Get the current step's input value."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step].value
        return ""

    def set_current_input(self, value: str) -> None:
        """Set the current step's input value."""
        if 0 <= self.current_step < len(self.steps):
            self.steps[self.current_step].value = value

    def add_char(self, char: str) -> None:
        """Add a character to current input."""
        if 0 <= self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            if not step.verified:
                step.value += char

    def backspace(self) -> None:
        """Remove last character from current input."""
        if 0 <= self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            if not step.verified and step.value:
                step.value = step.value[:-1]

    def verify_current(self) -> bool:
        """Verify the current step.

        Returns True if verified correctly.
        """
        if not (0 <= self.current_step < len(self.steps)):
            return False

        step = self.steps[self.current_step]
        if step.verified:
            return True

        # Compare (case-insensitive, trimmed)
        if step.value.lower().strip() == step.expected.lower().strip():
            step.verified = True
            step.error = False

            self._feedback_message = f"{step.label} VERIFIED!"
            self._feedback_color = Colors.SUCCESS
            self._feedback_timer = 1.5

            # Move to next unverified step
            self._advance_to_next()

            # Check if all complete
            if all(s.verified for s in self.steps):
                self._all_verified = True
                self._feedback_message = "ALL KEYS VERIFIED!"
                self._feedback_color = Colors.SUCCESS
                self._feedback_timer = 2.0

            return True
        else:
            step.error = True
            self._feedback_message = f"Incorrect {step.label}"
            self._feedback_color = Colors.ERROR
            self._feedback_timer = 2.0
            return False

    def _advance_to_next(self) -> None:
        """Advance to next unverified step."""
        for i in range(len(self.steps)):
            if not self.steps[i].verified:
                self.current_step = i
                return
        # All verified
        self.current_step = len(self.steps) - 1

    def unlock(self) -> None:
        """Attempt to unlock (complete) the puzzle."""
        if self._all_verified and self.on_complete:
            self.on_complete()

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle input events.

        Returns True if event was consumed.
        """
        import pygame

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self._all_verified:
                    self.unlock()
                else:
                    self.verify_current()
                return True

            elif event.key == pygame.K_BACKSPACE:
                self.backspace()
                return True

            elif event.key == pygame.K_TAB:
                # Move to next step
                self.current_step = (self.current_step + 1) % len(self.steps)
                return True

            elif event.key == pygame.K_UP:
                if self.current_step > 0:
                    self.current_step -= 1
                return True

            elif event.key == pygame.K_DOWN:
                if self.current_step < len(self.steps) - 1:
                    self.current_step += 1
                return True

            elif event.unicode and event.unicode.isprintable():
                self.add_char(event.unicode)
                return True

        return False

    def update(self, dt: float) -> None:
        """Update panel state."""
        # Cursor blink
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

        # Feedback timer
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._feedback_message = ""

    def render(self, surface: "pygame.Surface") -> None:
        """Render the puzzle panel."""
        import pygame

        fonts = get_fonts()

        # Panel background
        pygame.draw.rect(surface, Colors.BG_DARK, self.rect, border_radius=8)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, width=2, border_radius=8)

        # Title
        title_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        title_surface = title_font.render(self.title, Typography.ANTIALIAS, Colors.TEXT_HEADER)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, self.y + 15))

        # Steps
        step_y = self.y + 55
        step_height = 45
        input_width = 180
        label_width = 80

        for i, step in enumerate(self.steps):
            is_current = (i == self.current_step)

            # Label
            label_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
            label_color = Colors.SUCCESS if step.verified else (
                Colors.YELLOW if is_current else Colors.TEXT_MUTED
            )
            label_surface = label_font.render(step.label, Typography.ANTIALIAS, label_color)
            surface.blit(label_surface, (self.x + 15, step_y + 10))

            # Input box
            input_x = self.x + 15 + label_width
            input_rect = pygame.Rect(input_x, step_y + 5, input_width, 30)

            # Input background
            if step.verified:
                bg_color = Colors.SUCCESS
            elif step.error:
                bg_color = (80, 40, 40)  # Dark red
            elif is_current:
                bg_color = Colors.BG_HIGHLIGHT
            else:
                bg_color = Colors.BG_DARKEST

            pygame.draw.rect(surface, bg_color, input_rect, border_radius=4)

            border_color = Colors.SUCCESS if step.verified else (
                Colors.ERROR if step.error else (
                    Colors.BORDER_HIGHLIGHT if is_current else Colors.BORDER
                )
            )
            pygame.draw.rect(surface, border_color, input_rect, width=2, border_radius=4)

            # Input text
            input_font = fonts.get_font(Typography.SIZE_BODY)
            display_text = step.value
            if step.verified:
                display_text = step.expected  # Show correct answer when verified

            text_surface = input_font.render(display_text, Typography.ANTIALIAS,
                Colors.BG_DARKEST if step.verified else Colors.TEXT_PRIMARY)
            text_x = input_x + 8
            text_y = step_y + 10
            surface.blit(text_surface, (text_x, text_y))

            # Cursor for current step
            if is_current and not step.verified and self._cursor_visible:
                cursor_x = text_x + text_surface.get_width() + 2
                cursor_surface = input_font.render("|", Typography.ANTIALIAS, Colors.CURSOR)
                surface.blit(cursor_surface, (cursor_x, text_y))

            # Verify indicator
            indicator_x = input_x + input_width + 15
            indicator_size = 20
            indicator_rect = pygame.Rect(indicator_x, step_y + 10, indicator_size, indicator_size)

            if step.verified:
                pygame.draw.rect(surface, Colors.SUCCESS, indicator_rect, border_radius=3)
                check_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
                check_surface = check_font.render("✓", Typography.ANTIALIAS, Colors.BG_DARKEST)
                check_x = indicator_x + (indicator_size - check_surface.get_width()) // 2
                check_y = step_y + 10 + (indicator_size - check_surface.get_height()) // 2
                surface.blit(check_surface, (check_x, check_y))
            else:
                pygame.draw.rect(surface, Colors.BG_DARKEST, indicator_rect, border_radius=3)
                pygame.draw.rect(surface, Colors.BORDER, indicator_rect, width=1, border_radius=3)

            step_y += step_height

        # Progress
        verified_count = sum(1 for s in self.steps if s.verified)
        progress_font = fonts.get_font(Typography.SIZE_LABEL)
        progress_text = f"Progress: {verified_count}/{len(self.steps)}"
        progress_surface = progress_font.render(progress_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        surface.blit(progress_surface, (self.x + 15, self.y + self.height - 70))

        # Unlock button (only when all verified)
        button_y = self.y + self.height - 45
        button_width = 120
        button_height = 32
        button_x = self.x + (self.width - button_width) // 2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        if self._all_verified:
            pygame.draw.rect(surface, Colors.SUCCESS, button_rect, border_radius=4)
            button_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
            button_text = "UNLOCK"
            button_color = Colors.BG_DARKEST
        else:
            pygame.draw.rect(surface, Colors.BG_DARKEST, button_rect, border_radius=4)
            pygame.draw.rect(surface, Colors.BORDER, button_rect, width=1, border_radius=4)
            button_font = fonts.get_font(Typography.SIZE_LABEL)
            button_text = "LOCKED"
            button_color = Colors.TEXT_MUTED

        button_surface = button_font.render(button_text, Typography.ANTIALIAS, button_color)
        button_text_x = button_x + (button_width - button_surface.get_width()) // 2
        button_text_y = button_y + (button_height - button_surface.get_height()) // 2
        surface.blit(button_surface, (button_text_x, button_text_y))

        # Feedback message
        if self._feedback_message:
            feedback_font = fonts.get_font(Typography.SIZE_BODY)
            feedback_surface = feedback_font.render(
                self._feedback_message, Typography.ANTIALIAS, self._feedback_color
            )
            feedback_x = self.x + (self.width - feedback_surface.get_width()) // 2
            feedback_y = self.y + self.height - 95
            surface.blit(feedback_surface, (feedback_x, feedback_y))

        # Hint for current step
        if not self._all_verified and 0 <= self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            if step.hint and not step.verified:
                hint_font = fonts.get_font(Typography.SIZE_SMALL)
                hint_text = f"Hint: {step.hint}"
                hint_surface = hint_font.render(hint_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
                hint_x = self.x + 15
                hint_y = self.y + 55 + len(self.steps) * 45 + 10
                surface.blit(hint_surface, (hint_x, hint_y))
