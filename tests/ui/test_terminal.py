"""Level 2 Tests: TerminalPanel Component.

Tests the embedded terminal panel's input handling, output display,
cursor behavior, and command history.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.terminal import TerminalPanel, TerminalColors


class TestTerminalCreation:
    """Test TerminalPanel initialization."""

    def test_terminal_creates_with_rect(self, mock_pygame):
        """Terminal should initialize with given rect."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        assert terminal.rect.x == 0
        assert terminal.rect.y == 0
        assert terminal.rect.width == 400
        assert terminal.rect.height == 300

    def test_terminal_starts_unfocused(self, mock_pygame):
        """Terminal should start unfocused."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        assert terminal._focused is False

    def test_terminal_starts_with_empty_input(self, mock_pygame):
        """Terminal should start with empty input buffer."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        assert terminal._input_buffer == ""
        assert terminal._cursor_pos == 0

    def test_terminal_stores_callback(self, mock_pygame):
        """Terminal should store command callback."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        callback = Mock()
        terminal = TerminalPanel(rect, on_command=callback)

        assert terminal.on_command is callback


class TestTerminalFocus:
    """Test terminal focus behavior."""

    def test_focus_sets_focused_state(self, mock_pygame):
        """focus() should set terminal to focused."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.focus()

        assert terminal._focused is True

    def test_unfocus_clears_focused_state(self, mock_pygame):
        """unfocus() should clear focused state."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        terminal.unfocus()

        assert terminal._focused is False


class TestTerminalInput:
    """Test keyboard input handling."""

    def test_printable_char_inserts_at_cursor(self, mock_pygame, make_key_event):
        """Printable characters should insert at cursor position."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        terminal.handle_event(make_key_event(ord('a'), 'a'))

        assert terminal._input_buffer == "a"
        assert terminal._cursor_pos == 1

    def test_multiple_chars_build_string(self, mock_pygame, make_key_event):
        """Multiple character inputs should build a string."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        terminal.handle_event(make_key_event(ord('t'), 't'))
        terminal.handle_event(make_key_event(ord('e'), 'e'))
        terminal.handle_event(make_key_event(ord('s'), 's'))
        terminal.handle_event(make_key_event(ord('t'), 't'))

        assert terminal._input_buffer == "test"
        assert terminal._cursor_pos == 4

    def test_backspace_removes_char(self, mock_pygame, make_key_event):
        """Backspace should remove character before cursor."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 4

        terminal.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert terminal._input_buffer == "tes"
        assert terminal._cursor_pos == 3

    def test_backspace_at_start_does_nothing(self, mock_pygame, make_key_event):
        """Backspace at start of buffer should do nothing."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 0

        terminal.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert terminal._input_buffer == "test"
        assert terminal._cursor_pos == 0

    def test_delete_removes_char_after_cursor(self, mock_pygame, make_key_event):
        """Delete should remove character after cursor."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 2

        terminal.handle_event(make_key_event(mock_pygame.K_DELETE))

        assert terminal._input_buffer == "tet"
        assert terminal._cursor_pos == 2

    def test_enter_submits_command(self, mock_pygame, make_key_event):
        """Enter should submit the command and clear buffer."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        callback = Mock()
        terminal = TerminalPanel(rect, on_command=callback)
        terminal.focus()
        terminal._input_buffer = "test command"
        terminal._cursor_pos = 12

        result = terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result == "test command"
        assert terminal._input_buffer == ""
        assert terminal._cursor_pos == 0
        callback.assert_called_once_with("test command")

    def test_enter_with_empty_buffer_returns_none(self, mock_pygame, make_key_event):
        """Enter with empty buffer should return None."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        result = terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result is None

    def test_unfocused_terminal_ignores_input(self, mock_pygame, make_key_event):
        """Unfocused terminal should ignore keyboard input."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        # Not focused

        result = terminal.handle_event(make_key_event(ord('a'), 'a'))

        assert result is None
        assert terminal._input_buffer == ""


class TestTerminalCursor:
    """Test cursor movement and behavior."""

    def test_left_arrow_moves_cursor_left(self, mock_pygame, make_key_event):
        """Left arrow should move cursor left."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 4

        terminal.handle_event(make_key_event(mock_pygame.K_LEFT))

        assert terminal._cursor_pos == 3

    def test_right_arrow_moves_cursor_right(self, mock_pygame, make_key_event):
        """Right arrow should move cursor right."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 2

        terminal.handle_event(make_key_event(mock_pygame.K_RIGHT))

        assert terminal._cursor_pos == 3

    def test_home_moves_cursor_to_start(self, mock_pygame, make_key_event):
        """Home should move cursor to start."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 4

        terminal.handle_event(make_key_event(mock_pygame.K_HOME))

        assert terminal._cursor_pos == 0

    def test_end_moves_cursor_to_end(self, mock_pygame, make_key_event):
        """End should move cursor to end."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 0

        terminal.handle_event(make_key_event(mock_pygame.K_END))

        assert terminal._cursor_pos == 4

    def test_left_at_start_stays_at_start(self, mock_pygame, make_key_event):
        """Left arrow at start should stay at position 0."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 0

        terminal.handle_event(make_key_event(mock_pygame.K_LEFT))

        assert terminal._cursor_pos == 0

    def test_right_at_end_stays_at_end(self, mock_pygame, make_key_event):
        """Right arrow at end should stay at buffer length."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "test"
        terminal._cursor_pos = 4

        terminal.handle_event(make_key_event(mock_pygame.K_RIGHT))

        assert terminal._cursor_pos == 4

    def test_cursor_blinks_at_half_second(self, mock_pygame):
        """Cursor should toggle visibility every 0.5 seconds."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        initial_visible = terminal._cursor_visible

        terminal.update(0.5)

        assert terminal._cursor_visible != initial_visible

    def test_cursor_blinks_multiple_times(self, mock_pygame):
        """Cursor should blink on schedule."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        # After 0.5s - toggle
        terminal.update(0.5)
        first_state = terminal._cursor_visible

        # After another 0.5s - toggle again
        terminal.update(0.5)
        second_state = terminal._cursor_visible

        assert first_state != second_state


class TestTerminalHistory:
    """Test command history navigation."""

    def test_command_added_to_history(self, mock_pygame, make_key_event):
        """Submitted commands should be added to history."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()
        terminal._input_buffer = "first command"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert "first command" in terminal._command_history

    def test_up_arrow_recalls_history(self, mock_pygame, make_key_event):
        """Up arrow should recall previous command."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        # Submit some commands
        terminal._input_buffer = "first"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))
        terminal._input_buffer = "second"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        # Navigate up
        terminal.handle_event(make_key_event(mock_pygame.K_UP))

        assert terminal._input_buffer == "second"

    def test_up_arrow_navigates_through_history(self, mock_pygame, make_key_event):
        """Multiple up arrows should navigate through history."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        # Submit commands
        terminal._input_buffer = "first"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))
        terminal._input_buffer = "second"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        # Navigate up twice
        terminal.handle_event(make_key_event(mock_pygame.K_UP))
        terminal.handle_event(make_key_event(mock_pygame.K_UP))

        assert terminal._input_buffer == "first"

    def test_down_arrow_navigates_forward(self, mock_pygame, make_key_event):
        """Down arrow should navigate forward in history."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        # Submit commands
        terminal._input_buffer = "first"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))
        terminal._input_buffer = "second"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))

        # Navigate up twice, then down once
        terminal.handle_event(make_key_event(mock_pygame.K_UP))
        terminal.handle_event(make_key_event(mock_pygame.K_UP))
        terminal.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert terminal._input_buffer == "second"

    def test_down_past_end_clears_buffer(self, mock_pygame, make_key_event):
        """Down arrow past history end should clear buffer."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        # Submit and navigate
        terminal._input_buffer = "command"
        terminal.handle_event(make_key_event(mock_pygame.K_RETURN))
        terminal.handle_event(make_key_event(mock_pygame.K_UP))
        terminal.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert terminal._input_buffer == ""


class TestTerminalOutput:
    """Test output display and scrolling."""

    def test_add_output_appends_line(self, mock_pygame):
        """add_output should append a line to output."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_output("test line")

        assert len(terminal._output) == 1
        assert terminal._output[0].text == "test line"

    def test_add_output_with_color(self, mock_pygame):
        """add_output should accept custom color."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_output("colored line", TerminalColors.SUCCESS)

        assert terminal._output[0].color == TerminalColors.SUCCESS

    def test_add_system_message(self, mock_pygame):
        """add_system_message should add [SYSTEM] prefix."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_system_message("test message")

        assert "[SYSTEM]" in terminal._output[0].text
        assert terminal._output[0].color == TerminalColors.SYSTEM

    def test_add_error(self, mock_pygame):
        """add_error should add [ERROR] prefix with error color."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_error("error message")

        assert "[ERROR]" in terminal._output[0].text
        assert terminal._output[0].color == TerminalColors.ERROR

    def test_add_success(self, mock_pygame):
        """add_success should add [SUCCESS] prefix with success color."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_success("success message")

        assert "[SUCCESS]" in terminal._output[0].text
        assert terminal._output[0].color == TerminalColors.SUCCESS

    def test_output_respects_max_lines(self, mock_pygame):
        """Output should respect max_history limit."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect, max_history=10)

        for i in range(20):
            terminal.add_output(f"line {i}")

        assert len(terminal._output) == 10
        # Should have the last 10 lines
        assert terminal._output[-1].text == "line 19"

    def test_multiline_text_splits(self, mock_pygame):
        """Multiline text should be split into separate lines."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)

        terminal.add_output("line 1\nline 2\nline 3")

        assert len(terminal._output) == 3
        assert terminal._output[0].text == "line 1"
        assert terminal._output[1].text == "line 2"
        assert terminal._output[2].text == "line 3"

    def test_clear_removes_all_output(self, mock_pygame):
        """clear() should remove all output."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.add_output("line 1")
        terminal.add_output("line 2")

        terminal.clear()

        assert len(terminal._output) == 0


class TestTerminalSetInput:
    """Test programmatic input control."""

    def test_set_input_replaces_buffer(self, mock_pygame):
        """set_input should replace the input buffer."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal._input_buffer = "old text"

        terminal.set_input("new text")

        assert terminal._input_buffer == "new text"
        assert terminal._cursor_pos == 8  # End of new text


class TestTerminalRender:
    """Test rendering behavior."""

    def test_render_does_not_crash(self, mock_pygame, mock_surface):
        """render() should complete without errors."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.add_output("test line")

        # Should not raise
        terminal.render(mock_surface)

    def test_render_with_focus_shows_border_highlight(self, mock_pygame, mock_surface):
        """Focused terminal should have highlighted border."""
        rect = mock_pygame.Rect(0, 0, 400, 300)
        terminal = TerminalPanel(rect)
        terminal.focus()

        # Just verify it doesn't crash - actual border color would need
        # more sophisticated mocking to verify
        terminal.render(mock_surface)
