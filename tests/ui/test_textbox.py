"""Level 2 Tests: TextBox Component.

Tests the text input box for password guessing, including input handling,
focus management, and flash effects.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.textbox import TextBox


class TestTextBoxCreation:
    """Test TextBox initialization."""

    def test_textbox_creates_with_dimensions(self, mock_pygame):
        """TextBox should initialize with given dimensions."""
        textbox = TextBox(x=100, y=200, width=300, height=40)

        assert textbox.rect.x == 100
        assert textbox.rect.y == 200
        assert textbox.rect.width == 300
        assert textbox.rect.height == 40

    def test_textbox_starts_with_placeholder(self, mock_pygame):
        """TextBox should have placeholder text."""
        textbox = TextBox(x=0, y=0, width=300, height=40, placeholder="Enter text...")

        assert textbox.placeholder == "Enter text..."

    def test_textbox_starts_inactive(self, mock_pygame):
        """TextBox should start inactive."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        assert textbox.active is False

    def test_textbox_starts_with_empty_text(self, mock_pygame):
        """TextBox should start with empty text."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        assert textbox.text == ""

    def test_textbox_stores_callbacks(self, mock_pygame):
        """TextBox should store callbacks."""
        on_submit = Mock()
        on_keystroke = Mock()
        textbox = TextBox(
            x=0, y=0, width=300, height=40,
            on_submit=on_submit,
            on_keystroke=on_keystroke,
        )

        assert textbox.on_submit is on_submit
        assert textbox.on_keystroke is on_keystroke


class TestTextBoxFocus:
    """Test focus behavior."""

    def test_click_inside_activates(self, mock_pygame, make_click_event):
        """Clicking inside textbox should activate it."""
        textbox = TextBox(x=100, y=100, width=300, height=40)

        textbox.handle_event(make_click_event(150, 120))

        assert textbox.active is True

    def test_click_outside_deactivates(self, mock_pygame, make_click_event):
        """Clicking outside textbox should deactivate it."""
        textbox = TextBox(x=100, y=100, width=300, height=40)
        textbox.active = True

        textbox.handle_event(make_click_event(50, 50))

        assert textbox.active is False

    def test_focus_method_activates(self, mock_pygame):
        """focus() should activate textbox."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        textbox.focus()

        assert textbox.active is True
        assert textbox.cursor_visible is True

    def test_blur_method_deactivates(self, mock_pygame):
        """blur() should deactivate textbox."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True

        textbox.blur()

        assert textbox.active is False


class TestTextBoxInput:
    """Test keyboard input handling."""

    def test_printable_char_appends(self, mock_pygame, make_key_event):
        """Printable characters should append to text."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True

        textbox.handle_event(make_key_event(ord('a'), 'a'))

        assert textbox.text == "a"

    def test_multiple_chars_build_string(self, mock_pygame, make_key_event):
        """Multiple characters should build a string."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True

        textbox.handle_event(make_key_event(ord('t'), 't'))
        textbox.handle_event(make_key_event(ord('e'), 'e'))
        textbox.handle_event(make_key_event(ord('s'), 's'))
        textbox.handle_event(make_key_event(ord('t'), 't'))

        assert textbox.text == "test"

    def test_backspace_removes_last_char(self, mock_pygame, make_key_event):
        """Backspace should remove last character."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True
        textbox.text = "test"

        textbox.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert textbox.text == "tes"

    def test_backspace_on_empty_does_nothing(self, mock_pygame, make_key_event):
        """Backspace on empty text should do nothing."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True

        textbox.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert textbox.text == ""

    def test_enter_submits(self, mock_pygame, make_key_event):
        """Enter should submit text."""
        on_submit = Mock()
        textbox = TextBox(x=0, y=0, width=300, height=40, on_submit=on_submit)
        textbox.active = True
        textbox.text = "password123"

        result = textbox.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result is True
        on_submit.assert_called_once_with("password123")
        assert textbox.text == ""  # Cleared after submit

    def test_enter_without_text_does_not_submit(self, mock_pygame, make_key_event):
        """Enter with empty text should not call submit."""
        on_submit = Mock()
        textbox = TextBox(x=0, y=0, width=300, height=40, on_submit=on_submit)
        textbox.active = True

        result = textbox.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result is False
        on_submit.assert_not_called()

    def test_escape_clears_and_deactivates(self, mock_pygame, make_key_event):
        """Escape should clear text and deactivate."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True
        textbox.text = "some text"

        textbox.handle_event(make_key_event(mock_pygame.K_ESCAPE))

        assert textbox.text == ""
        assert textbox.active is False

    def test_inactive_ignores_input(self, mock_pygame, make_key_event):
        """Inactive textbox should ignore keyboard input."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        # Not active

        textbox.handle_event(make_key_event(ord('a'), 'a'))

        assert textbox.text == ""

    def test_max_length_enforced(self, mock_pygame, make_key_event):
        """Text should not exceed max_length."""
        textbox = TextBox(x=0, y=0, width=300, height=40, max_length=5)
        textbox.active = True
        textbox.text = "12345"

        textbox.handle_event(make_key_event(ord('6'), '6'))

        assert textbox.text == "12345"
        assert len(textbox.text) == 5

    def test_keystroke_callback_called(self, mock_pygame, make_key_event):
        """on_keystroke should be called when typing."""
        on_keystroke = Mock()
        textbox = TextBox(x=0, y=0, width=300, height=40, on_keystroke=on_keystroke)
        textbox.active = True

        textbox.handle_event(make_key_event(ord('a'), 'a'))

        on_keystroke.assert_called_once()


class TestTextBoxCursor:
    """Test cursor blink behavior."""

    def test_cursor_starts_visible(self, mock_pygame):
        """Cursor should start visible."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        assert textbox.cursor_visible is True

    def test_cursor_blinks_on_update(self, mock_pygame):
        """Cursor should toggle visibility after 0.5 seconds."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        initial = textbox.cursor_visible

        textbox.update(0.5)

        assert textbox.cursor_visible != initial

    def test_cursor_timer_resets_on_focus(self, mock_pygame):
        """Focusing should reset cursor timer."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.cursor_timer = 0.4

        textbox.focus()

        assert textbox.cursor_timer == 0


class TestTextBoxFlash:
    """Test error and success flash effects."""

    def test_flash_error_sets_state(self, mock_pygame):
        """flash_error should set error state."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        textbox.flash_error(duration=0.5)

        assert textbox._error_flash is True
        assert textbox._error_timer == 0.5

    def test_error_flash_decays(self, mock_pygame):
        """Error flash should decay over time."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.flash_error(duration=0.5)

        textbox.update(0.5)

        assert textbox._error_flash is False

    def test_flash_success_sets_state(self, mock_pygame):
        """flash_success should set success state."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        textbox.flash_success(duration=0.5)

        assert textbox._success_flash is True
        assert textbox._success_timer == 0.5

    def test_success_flash_decays(self, mock_pygame):
        """Success flash should decay over time."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.flash_success(duration=0.5)

        textbox.update(0.5)

        assert textbox._success_flash is False


class TestTextBoxMethods:
    """Test utility methods."""

    def test_clear_removes_text(self, mock_pygame):
        """clear() should remove all text."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.text = "some text"

        textbox.clear()

        assert textbox.text == ""

    def test_set_text_replaces_text(self, mock_pygame):
        """set_text should replace current text."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.text = "old"

        textbox.set_text("new text")

        assert textbox.text == "new text"

    def test_set_text_respects_max_length(self, mock_pygame):
        """set_text should truncate to max_length."""
        textbox = TextBox(x=0, y=0, width=300, height=40, max_length=5)

        textbox.set_text("this is too long")

        assert len(textbox.text) == 5
        assert textbox.text == "this "

    def test_set_placeholder_updates(self, mock_pygame):
        """set_placeholder should update placeholder text."""
        textbox = TextBox(x=0, y=0, width=300, height=40, placeholder="old")

        textbox.set_placeholder("Enter new...")

        assert textbox.placeholder == "Enter new..."


class TestTextBoxDraw:
    """Test rendering behavior."""

    def test_draw_does_not_crash_inactive(self, mock_pygame, mock_surface):
        """draw() should complete without error when inactive."""
        textbox = TextBox(x=0, y=0, width=300, height=40)

        # Should not raise
        textbox.draw(mock_surface)

    def test_draw_does_not_crash_active(self, mock_pygame, mock_surface):
        """draw() should complete without error when active."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.active = True
        textbox.text = "some text"

        # Should not raise
        textbox.draw(mock_surface)

    def test_draw_with_error_flash(self, mock_pygame, mock_surface):
        """draw() should handle error flash state."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.flash_error()

        # Should not raise
        textbox.draw(mock_surface)

    def test_draw_with_success_flash(self, mock_pygame, mock_surface):
        """draw() should handle success flash state."""
        textbox = TextBox(x=0, y=0, width=300, height=40)
        textbox.flash_success()

        # Should not raise
        textbox.draw(mock_surface)
