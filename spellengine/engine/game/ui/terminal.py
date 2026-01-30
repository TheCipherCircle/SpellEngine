"""Embedded Terminal Panel for PatternForge.

A theatrical terminal interface for hash cracking with WoW Blackrock Mountain
dungeon vibes - epic, dark, and immersive.

Features:
- Command line input with blinking cursor
- Scrollable output history
- PatternForge integration
- Theatrical cracking animations
- CRT scanline effect (optional)
"""

from typing import TYPE_CHECKING, Callable
from collections import deque

from spellengine.engine.game.ui.theme import (
    Colors,
    SPACING,
    Typography,
    get_fonts,
)

if TYPE_CHECKING:
    import pygame


# Terminal color scheme (enhanced Gruvbox for dungeon feel)
class TerminalColors:
    """Terminal-specific colors for the embedded console."""

    BG = (20, 22, 23)  # Slightly darker than main BG
    BORDER = (80, 73, 69)
    BORDER_ACTIVE = (254, 128, 25)  # Orange glow when focused

    # Text colors
    PROMPT = (254, 128, 25)  # Orange prompt
    INPUT = (251, 241, 199)  # Bright input text
    OUTPUT = (189, 174, 147)  # Muted output
    SUCCESS = (184, 187, 38)  # Green for success
    ERROR = (251, 73, 52)  # Red for errors
    INFO = (131, 165, 152)  # Blue for info
    SYSTEM = (250, 189, 47)  # Yellow for system messages

    # Progress colors (theatrical cracking)
    CRACK_PROGRESS = (142, 192, 124)  # Aqua/teal
    CRACK_REVEAL = (215, 153, 33)  # Gold for revealed chars


class TerminalLine:
    """A single line of terminal output."""

    def __init__(self, text: str, color: tuple = TerminalColors.OUTPUT):
        self.text = text
        self.color = color
        self.timestamp = 0.0  # For animation timing


class TerminalPanel:
    """Embedded terminal panel for command-line interaction.

    Provides a theatrical cracking experience with command input,
    scrollable output, and PatternForge integration.
    """

    def __init__(
        self,
        rect: "pygame.Rect",
        on_command: Callable[[str], None] | None = None,
        max_history: int = 100,
    ) -> None:
        """Initialize the terminal panel.

        Args:
            rect: Panel rectangle (position and size)
            on_command: Callback for command execution
            max_history: Maximum lines to keep in output history
        """
        import pygame

        self.rect = rect
        self.on_command = on_command
        self.max_history = max_history

        # Input state
        self._input_buffer: str = ""
        self._cursor_pos: int = 0
        self._cursor_visible: bool = True
        self._cursor_timer: float = 0.0
        self._cursor_blink_rate: float = 0.5

        # Output history
        self._output: deque[TerminalLine] = deque(maxlen=max_history)
        self._scroll_offset: int = 0

        # Focus state
        self._focused: bool = False

        # Command history (up/down navigation)
        self._command_history: list[str] = []
        self._history_index: int = -1

        # Animation state
        self._cracking: bool = False
        self._crack_timer: float = 0.0
        self._crack_progress: str = ""

        # Font cache
        self._font: "pygame.font.Font | None" = None
        self._line_height: int = 0

    def _get_font(self) -> "pygame.font.Font":
        """Get the terminal font (cached)."""
        if self._font is None:
            fonts = get_fonts()
            self._font = fonts.get_font(Typography.SIZE_LABEL)
            self._line_height = int(self._font.get_height() * 1.3)
        return self._font

    @property
    def content_rect(self) -> "pygame.Rect":
        """Get the content area inside the border."""
        import pygame
        padding = SPACING["sm"]
        return pygame.Rect(
            self.rect.x + padding,
            self.rect.y + padding,
            self.rect.width - padding * 2,
            self.rect.height - padding * 2,
        )

    def focus(self) -> None:
        """Focus the terminal for input."""
        self._focused = True

    def unfocus(self) -> None:
        """Remove focus from terminal."""
        self._focused = False

    def clear(self) -> None:
        """Clear the terminal output."""
        self._output.clear()
        self._scroll_offset = 0

    def add_output(
        self,
        text: str,
        color: tuple = TerminalColors.OUTPUT,
    ) -> None:
        """Add a line of output to the terminal.

        Args:
            text: Text to display
            color: Text color
        """
        # Handle multi-line text
        for line in text.split("\n"):
            self._output.append(TerminalLine(line, color))

        # Auto-scroll to bottom
        self._scroll_to_bottom()

    def add_system_message(self, text: str) -> None:
        """Add a system message (yellow)."""
        self.add_output(f"[SYSTEM] {text}", TerminalColors.SYSTEM)

    def add_error(self, text: str) -> None:
        """Add an error message (red)."""
        self.add_output(f"[ERROR] {text}", TerminalColors.ERROR)

    def add_success(self, text: str) -> None:
        """Add a success message (green)."""
        self.add_output(f"[SUCCESS] {text}", TerminalColors.SUCCESS)

    def add_info(self, text: str) -> None:
        """Add an info message (blue)."""
        self.add_output(text, TerminalColors.INFO)

    def _scroll_to_bottom(self) -> None:
        """Scroll to show the latest output."""
        font = self._get_font()
        content = self.content_rect
        visible_lines = (content.height - 30) // self._line_height  # Reserve space for input

        if len(self._output) > visible_lines:
            self._scroll_offset = len(self._output) - visible_lines
        else:
            self._scroll_offset = 0

    def set_input(self, text: str) -> None:
        """Set the input buffer content.

        Args:
            text: Text to put in input buffer
        """
        self._input_buffer = text
        self._cursor_pos = len(text)

    def handle_event(self, event: "pygame.event.Event") -> str | None:
        """Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            Command string if Enter pressed, None otherwise
        """
        import pygame

        if not self._focused:
            return None

        if event.type == pygame.KEYDOWN:
            # Enter - submit command
            if event.key == pygame.K_RETURN:
                command = self._input_buffer.strip()
                if command:
                    # Add to history
                    self._command_history.append(command)
                    self._history_index = len(self._command_history)

                    # Echo command to output
                    self.add_output(f"> {command}", TerminalColors.PROMPT)

                    # Clear input
                    self._input_buffer = ""
                    self._cursor_pos = 0

                    # Execute callback
                    if self.on_command:
                        self.on_command(command)

                    return command
                return None

            # Backspace
            elif event.key == pygame.K_BACKSPACE:
                if self._cursor_pos > 0:
                    self._input_buffer = (
                        self._input_buffer[: self._cursor_pos - 1]
                        + self._input_buffer[self._cursor_pos:]
                    )
                    self._cursor_pos -= 1

            # Delete
            elif event.key == pygame.K_DELETE:
                if self._cursor_pos < len(self._input_buffer):
                    self._input_buffer = (
                        self._input_buffer[: self._cursor_pos]
                        + self._input_buffer[self._cursor_pos + 1:]
                    )

            # Arrow keys - cursor movement
            elif event.key == pygame.K_LEFT:
                self._cursor_pos = max(0, self._cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self._cursor_pos = min(len(self._input_buffer), self._cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self._cursor_pos = 0
            elif event.key == pygame.K_END:
                self._cursor_pos = len(self._input_buffer)

            # Command history navigation
            elif event.key == pygame.K_UP:
                if self._command_history and self._history_index > 0:
                    self._history_index -= 1
                    self._input_buffer = self._command_history[self._history_index]
                    self._cursor_pos = len(self._input_buffer)
            elif event.key == pygame.K_DOWN:
                if self._history_index < len(self._command_history) - 1:
                    self._history_index += 1
                    self._input_buffer = self._command_history[self._history_index]
                    self._cursor_pos = len(self._input_buffer)
                elif self._history_index == len(self._command_history) - 1:
                    self._history_index = len(self._command_history)
                    self._input_buffer = ""
                    self._cursor_pos = 0

            # Page up/down - scroll
            elif event.key == pygame.K_PAGEUP:
                content = self.content_rect
                visible_lines = (content.height - 30) // self._line_height
                self._scroll_offset = max(0, self._scroll_offset - visible_lines)
            elif event.key == pygame.K_PAGEDOWN:
                self._scroll_to_bottom()

            # Regular character input
            elif event.unicode and event.unicode.isprintable():
                self._input_buffer = (
                    self._input_buffer[: self._cursor_pos]
                    + event.unicode
                    + self._input_buffer[self._cursor_pos:]
                )
                self._cursor_pos += 1

        return None

    def update(self, dt: float) -> None:
        """Update terminal state.

        Args:
            dt: Delta time in seconds
        """
        # Cursor blink
        self._cursor_timer += dt
        if self._cursor_timer >= self._cursor_blink_rate:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

        # Cracking animation
        if self._cracking:
            self._crack_timer += dt

    def render(self, surface: "pygame.Surface") -> None:
        """Render the terminal panel.

        Args:
            surface: Surface to render on
        """
        import pygame

        font = self._get_font()
        content = self.content_rect

        # Background
        pygame.draw.rect(surface, TerminalColors.BG, self.rect)

        # Border (glows orange when focused)
        border_color = TerminalColors.BORDER_ACTIVE if self._focused else TerminalColors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Title bar
        title_font = get_fonts().get_font(Typography.SIZE_SMALL, bold=True)
        title_text = "TERMINAL"
        title_surface = title_font.render(title_text, Typography.ANTIALIAS, TerminalColors.PROMPT)
        title_x = self.rect.x + (self.rect.width - title_surface.get_width()) // 2
        title_y = self.rect.y + 3
        surface.blit(title_surface, (title_x, title_y))

        # Separator line under title
        sep_y = title_y + title_font.get_height() + 2
        pygame.draw.line(
            surface,
            TerminalColors.BORDER,
            (self.rect.x + SPACING["xs"], sep_y),
            (self.rect.x + self.rect.width - SPACING["xs"], sep_y),
        )

        # Output area (above input line)
        output_y_start = sep_y + SPACING["xs"]
        input_height = self._line_height + SPACING["sm"]
        output_y_end = self.rect.y + self.rect.height - input_height - SPACING["xs"]
        visible_lines = (output_y_end - output_y_start) // self._line_height

        # Render output lines
        y = output_y_start
        start_idx = self._scroll_offset
        end_idx = min(start_idx + visible_lines, len(self._output))

        for i in range(start_idx, end_idx):
            line = self._output[i]
            # Truncate long lines
            text = line.text
            max_chars = (content.width - SPACING["sm"]) // font.size("M")[0]
            if len(text) > max_chars:
                text = text[: max_chars - 3] + "..."

            line_surface = font.render(text, Typography.ANTIALIAS, line.color)
            surface.blit(line_surface, (content.x, y))
            y += self._line_height

        # Scroll indicator
        if len(self._output) > visible_lines:
            scroll_pct = self._scroll_offset / max(1, len(self._output) - visible_lines)
            scroll_bar_height = max(20, int((visible_lines / len(self._output)) * (output_y_end - output_y_start)))
            scroll_bar_y = output_y_start + int(scroll_pct * (output_y_end - output_y_start - scroll_bar_height))
            scroll_bar_x = self.rect.x + self.rect.width - 6

            pygame.draw.rect(
                surface,
                TerminalColors.BORDER,
                (scroll_bar_x, scroll_bar_y, 4, scroll_bar_height),
                border_radius=2,
            )

        # Input separator
        input_sep_y = output_y_end + 2
        pygame.draw.line(
            surface,
            TerminalColors.BORDER,
            (self.rect.x + SPACING["xs"], input_sep_y),
            (self.rect.x + self.rect.width - SPACING["xs"], input_sep_y),
        )

        # Input line
        input_y = input_sep_y + SPACING["xs"]
        prompt = "> "
        prompt_surface = font.render(prompt, Typography.ANTIALIAS, TerminalColors.PROMPT)
        surface.blit(prompt_surface, (content.x, input_y))

        # Input text
        input_x = content.x + prompt_surface.get_width()
        input_surface = font.render(self._input_buffer, Typography.ANTIALIAS, TerminalColors.INPUT)
        surface.blit(input_surface, (input_x, input_y))

        # Cursor
        if self._focused and self._cursor_visible:
            cursor_x = input_x + font.size(self._input_buffer[: self._cursor_pos])[0]
            cursor_rect = pygame.Rect(cursor_x, input_y, 2, font.get_height())
            pygame.draw.rect(surface, TerminalColors.PROMPT, cursor_rect)

    def start_cracking_animation(self, target: str) -> None:
        """Start the theatrical cracking animation.

        Args:
            target: The target being cracked (for display)
        """
        self._cracking = True
        self._crack_timer = 0.0
        self._crack_progress = ""
        self.add_system_message(f"Initiating crack sequence for: {target[:16]}...")

    def update_cracking_progress(self, progress: str, pct: float) -> None:
        """Update the cracking progress display.

        Args:
            progress: Progress text to show
            pct: Percentage complete (0.0 to 1.0)
        """
        self._crack_progress = progress
        # Could add progress bar here

    def end_cracking_animation(self, success: bool, result: str = "") -> None:
        """End the cracking animation.

        Args:
            success: Whether crack was successful
            result: The cracked result (if successful)
        """
        self._cracking = False
        self._crack_timer = 0.0
        self._crack_progress = ""

        if success:
            self.add_success(f"CRACKED: {result}")
        else:
            self.add_error("Crack failed - hash not in wordlist")


class TheatricalCracker:
    """Manages theatrical cracking animation with suspenseful reveal.

    Creates a WoW boss encounter feel with dramatic timing and effects.
    The cleartext is only revealed at the very end for maximum impact.
    """

    # Hash type to hashcat mode mapping
    HASHCAT_MODES = {
        "md5": 0,
        "sha1": 100,
        "sha256": 1400,
        "sha512": 1700,
        "ntlm": 1000,
        "bcrypt": 3200,
    }

    def __init__(self, terminal: TerminalPanel):
        self.terminal = terminal
        self._solution: str = ""
        self._hash: str = ""
        self._hash_type: str = "md5"
        self._timer: float = 0.0
        self._phase: int = 0  # 0=idle, 1=analyzing, 2=command, 3=cracking, 4=done
        self._crack_duration: float = 2.5  # Total cracking phase duration
        self._last_progress: int = -1  # Track last shown progress %
        self._show_syntax: bool = True  # Show tool syntax by default

    def start(
        self,
        solution: str,
        hash_value: str = "",
        hash_type: str = "md5",
        show_syntax: bool = True,
    ) -> None:
        """Start theatrical crack of the given solution.

        Args:
            solution: The solution to theatrically reveal
            hash_value: The hash being cracked (for syntax display)
            hash_type: Hash type (md5, sha1, etc.)
            show_syntax: Whether to show equivalent tool commands
        """
        self._solution = solution
        self._hash = hash_value
        self._hash_type = hash_type.lower()
        self._show_syntax = show_syntax
        self._timer = 0.0
        self._phase = 1
        self._last_progress = -1
        self.terminal.add_system_message("Initiating crack sequence...")

    def update(self, dt: float) -> bool:
        """Update the theatrical crack animation.

        Args:
            dt: Delta time in seconds

        Returns:
            True when cracking is complete
        """
        if self._phase == 0:
            return False

        self._timer += dt

        # Phase 1: Analyzing hash type (1.0 seconds)
        if self._phase == 1:
            if self._timer >= 1.0:
                hash_len = len(self._hash) if self._hash else 32
                self.terminal.add_info(f"Hash type: {self._hash_type.upper()} ({hash_len} chars)")
                self._timer = 0.0
                self._phase = 2

        # Phase 2: Show equivalent tool syntax (1.5 seconds)
        elif self._phase == 2:
            if self._timer >= 1.5:
                self.terminal.add_info("Loading wordlist: rockyou.txt")

                # Show equivalent tool commands if enabled
                if self._show_syntax and self._hash:
                    self.terminal.add_output("")
                    self.terminal.add_output("Equivalent commands:", TerminalColors.SYSTEM)
                    mode = self.HASHCAT_MODES.get(self._hash_type, 0)
                    short_hash = self._hash[:16] + "..." if len(self._hash) > 16 else self._hash
                    self.terminal.add_output(
                        f"  hashcat -m {mode} {short_hash} rockyou.txt",
                        TerminalColors.INFO
                    )
                    self.terminal.add_output(
                        f"  john --format={self._hash_type} --wordlist=rockyou.txt hash.txt",
                        TerminalColors.INFO
                    )
                    self.terminal.add_output("")

                self._timer = 0.0
                self._phase = 3

        # Phase 3: Cracking progress (no cleartext reveal until done)
        elif self._phase == 3:
            progress = min(int((self._timer / self._crack_duration) * 100), 100)

            # Show progress updates at 25%, 50%, 75%
            if progress >= 25 and self._last_progress < 25:
                self.terminal.add_output("Scanning wordlist...", TerminalColors.CRACK_PROGRESS)
                self._last_progress = 25
            elif progress >= 50 and self._last_progress < 50:
                self.terminal.add_output("Testing candidates...", TerminalColors.CRACK_PROGRESS)
                self._last_progress = 50
            elif progress >= 75 and self._last_progress < 75:
                self.terminal.add_output("Match found! Verifying...", TerminalColors.CRACK_PROGRESS)
                self._last_progress = 75

            # Complete when timer exceeds duration
            if self._timer >= self._crack_duration:
                self._phase = 4
                self.terminal.add_output("")
                self.terminal.add_success(f"CRACKED: {self._solution}")
                self.terminal.add_output("")
                return True

        return False

    @property
    def is_active(self) -> bool:
        """Check if theatrical crack is in progress."""
        return self._phase > 0 and self._phase < 4

    @property
    def result(self) -> str:
        """Get the cracked solution."""
        return self._solution if self._phase == 4 else ""
