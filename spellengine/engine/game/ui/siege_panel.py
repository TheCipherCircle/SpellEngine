"""Siege Panel - Progressive observation UI for SIEGE encounters.

Shows auto-scrolling output that simulates watching SCARAB/analysis work:
- Progressive output lines appear over time
- Pattern discovery highlights appear
- Checkpoints pause for user acknowledgment
- Teaches that analysis takes TIME

Gruvbox-styled with terminal aesthetic.
"""

from typing import TYPE_CHECKING, Callable

from spellengine.engine.game.ui.theme import Colors, SPACING, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


class SiegePanel:
    """Progressive observation panel for SIEGE encounters.

    Displays auto-scrolling output that teaches patience and observation.
    Used for SCARAB analysis, EntropySmith generation, etc.

    Layout:
    +------------------------------------------+
    |  [SCARAB ANALYSIS]                       |
    +------------------------------------------+
    |  > Ingesting corpus...                   |
    |  > Found 1,423 tokens                    |
    |  > Analyzing patterns...                 |
    |  > WORD: 45.2%                          |
    |  > DIGIT: 23.1%                         |
    |  > *** PATTERN DISCOVERED ***           | <- Highlighted
    |  > Most common: word+digits             |
    |  > ...                                   |
    +------------------------------------------+
    |  [SPACE] Continue                        |
    +------------------------------------------+
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        lines: list[str] | None = None,
        line_delay: float = 0.3,
        on_complete: Callable[[], None] | None = None,
    ):
        """Initialize the siege panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            lines: List of output lines to display progressively
            line_delay: Delay between lines in seconds
            on_complete: Callback when all lines are shown
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lines = lines or []
        self.line_delay = line_delay
        self.on_complete = on_complete

        self.rect = pygame.Rect(x, y, width, height)

        # State
        self._visible_lines: list[tuple[str, tuple[int, int, int]]] = []
        self._current_line_index = 0
        self._line_timer = 0.0
        self._complete = False
        self._waiting_for_input = False
        self._checkpoint_message = ""

        # Scroll state
        self._scroll_offset = 0
        self._max_visible_lines = 12

    def add_line(self, text: str, color: tuple[int, int, int] | None = None) -> None:
        """Add a line to the output."""
        if color is None:
            # Auto-detect color based on content
            if "***" in text or "DISCOVERED" in text.upper():
                color = Colors.SUCCESS
            elif "ERROR" in text.upper() or "FAILED" in text.upper():
                color = Colors.ERROR
            elif "WARNING" in text.upper():
                color = Colors.WARNING
            elif text.startswith(">"):
                color = Colors.BLUE
            elif "%" in text:
                color = Colors.YELLOW
            else:
                color = Colors.TEXT_PRIMARY

        self._visible_lines.append((text, color))

        # Auto-scroll to show new line
        if len(self._visible_lines) > self._max_visible_lines:
            self._scroll_offset = len(self._visible_lines) - self._max_visible_lines

    def set_checkpoint(self, message: str = "Press SPACE to continue...") -> None:
        """Pause for user acknowledgment."""
        self._waiting_for_input = True
        self._checkpoint_message = message

    def advance_checkpoint(self) -> None:
        """Continue past a checkpoint."""
        self._waiting_for_input = False
        self._checkpoint_message = ""

    def start(self) -> None:
        """Start the progressive output."""
        self._visible_lines = []
        self._current_line_index = 0
        self._line_timer = 0.0
        self._complete = False
        self._waiting_for_input = False
        self._scroll_offset = 0

    def reset(self, lines: list[str] | None = None) -> None:
        """Reset with optional new lines."""
        if lines is not None:
            self.lines = lines
        self.start()

    @property
    def is_complete(self) -> bool:
        """Check if all lines have been shown."""
        return self._complete

    @property
    def is_waiting(self) -> bool:
        """Check if waiting for user input at checkpoint."""
        return self._waiting_for_input

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle input events.

        Returns True if event was consumed.
        """
        import pygame

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self._waiting_for_input:
                    self.advance_checkpoint()
                    return True
                elif self._complete and self.on_complete:
                    self.on_complete()
                    return True

            # Allow scrolling with arrow keys
            if event.key == pygame.K_UP:
                if self._scroll_offset > 0:
                    self._scroll_offset -= 1
                return True
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self._visible_lines) - self._max_visible_lines)
                if self._scroll_offset < max_scroll:
                    self._scroll_offset += 1
                return True

        return False

    def update(self, dt: float) -> None:
        """Update panel state - add new lines over time."""
        if self._complete or self._waiting_for_input:
            return

        self._line_timer += dt

        # Add next line when timer expires
        while (
            self._line_timer >= self.line_delay
            and self._current_line_index < len(self.lines)
        ):
            line = self.lines[self._current_line_index]

            # Check for checkpoint markers
            if line.startswith("[CHECKPOINT]"):
                checkpoint_msg = line[12:].strip() or "Press SPACE to continue..."
                self.set_checkpoint(checkpoint_msg)
                self._current_line_index += 1
                self._line_timer = 0.0
                return  # Stop until user continues

            # Add the line
            self.add_line(line)
            self._current_line_index += 1
            self._line_timer -= self.line_delay

        # Check if complete
        if self._current_line_index >= len(self.lines) and not self._waiting_for_input:
            self._complete = True

    def render(self, surface: "pygame.Surface") -> None:
        """Render the siege panel."""
        import pygame

        fonts = get_fonts()

        # Panel background
        pygame.draw.rect(surface, Colors.BG_DARKEST, self.rect, border_radius=4)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, width=2, border_radius=4)

        # Title bar
        title_height = 28
        title_rect = pygame.Rect(self.x, self.y, self.width, title_height)
        pygame.draw.rect(surface, Colors.BG_DARK, title_rect)
        pygame.draw.line(
            surface, Colors.BORDER,
            (self.x, self.y + title_height),
            (self.x + self.width, self.y + title_height),
            1
        )

        title_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        title_surface = title_font.render("ANALYSIS OUTPUT", Typography.ANTIALIAS, Colors.TEXT_HEADER)
        surface.blit(title_surface, (self.x + 10, self.y + 6))

        # Content area
        content_y = self.y + title_height + 8
        content_height = self.height - title_height - 40  # Leave room for prompt
        line_height = 18

        # Calculate visible lines
        start_idx = self._scroll_offset
        end_idx = min(start_idx + self._max_visible_lines, len(self._visible_lines))

        # Render visible lines
        line_font = fonts.get_font(Typography.SIZE_SMALL)
        y = content_y

        for i in range(start_idx, end_idx):
            if i < len(self._visible_lines):
                text, color = self._visible_lines[i]
                line_surface = line_font.render(text, Typography.ANTIALIAS, color)

                # Clip to content area
                if y + line_height <= self.y + self.height - 35:
                    surface.blit(line_surface, (self.x + 10, y))
                    y += line_height

        # Scroll indicator
        if len(self._visible_lines) > self._max_visible_lines:
            total_lines = len(self._visible_lines)
            scroll_pct = self._scroll_offset / max(1, total_lines - self._max_visible_lines)

            scroll_bar_height = content_height - 10
            scroll_bar_x = self.x + self.width - 12
            scroll_bar_y = content_y + 5

            # Track
            pygame.draw.rect(
                surface, Colors.BG_DARK,
                (scroll_bar_x, scroll_bar_y, 6, scroll_bar_height),
                border_radius=3
            )

            # Thumb
            thumb_height = max(20, scroll_bar_height * self._max_visible_lines // total_lines)
            thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_height) * scroll_pct)
            pygame.draw.rect(
                surface, Colors.TEXT_MUTED,
                (scroll_bar_x, thumb_y, 6, thumb_height),
                border_radius=3
            )

        # Bottom prompt
        prompt_y = self.y + self.height - 28
        pygame.draw.line(
            surface, Colors.BORDER,
            (self.x, prompt_y - 5),
            (self.x + self.width, prompt_y - 5),
            1
        )

        prompt_font = fonts.get_font(Typography.SIZE_SMALL)
        if self._waiting_for_input:
            prompt_text = self._checkpoint_message
            prompt_color = Colors.YELLOW
        elif self._complete:
            prompt_text = "[SPACE] Analysis Complete - Continue"
            prompt_color = Colors.SUCCESS
        else:
            # Show progress
            pct = (self._current_line_index / max(1, len(self.lines))) * 100
            prompt_text = f"Analyzing... {pct:.0f}%"
            prompt_color = Colors.TEXT_MUTED

        prompt_surface = prompt_font.render(prompt_text, Typography.ANTIALIAS, prompt_color)
        surface.blit(prompt_surface, (self.x + 10, prompt_y))

        # Blinking cursor indicator when waiting
        if self._waiting_for_input or self._complete:
            import math
            blink = int(pygame.time.get_ticks() / 500) % 2
            if blink:
                cursor_x = self.x + self.width - 20
                cursor_surface = prompt_font.render("_", Typography.ANTIALIAS, prompt_color)
                surface.blit(cursor_surface, (cursor_x, prompt_y))
