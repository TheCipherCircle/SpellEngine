"""Level 2 Tests: PuzzlePanel Component.

Tests the multi-step verification UI for PUZZLE_BOX and PIPELINE encounters,
including step verification, navigation, and completion tracking.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.puzzle_panel import PuzzlePanel, PuzzleStep


class TestPuzzlePanelCreation:
    """Test PuzzlePanel initialization."""

    def test_panel_creates_with_dimensions(self, mock_pygame):
        """Panel should initialize with given dimensions."""
        panel = PuzzlePanel(x=100, y=100, width=400, height=350)

        assert panel.x == 100
        assert panel.y == 100
        assert panel.width == 400
        assert panel.height == 350

    def test_panel_creates_steps(self, mock_pygame):
        """Panel should create steps from input."""
        steps = [
            ("KEY 1", "answer1", "hint1"),
            ("KEY 2", "answer2", "hint2"),
            ("KEY 3", "answer3", "hint3"),
        ]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        assert len(panel.steps) == 3
        assert panel.steps[0].label == "KEY 1"
        assert panel.steps[0].expected == "answer1"
        assert panel.steps[0].hint == "hint1"

    def test_panel_starts_at_first_step(self, mock_pygame):
        """Panel should start at first step."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        assert panel.current_step == 0

    def test_panel_starts_not_complete(self, mock_pygame):
        """Panel should start incomplete."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        assert panel.is_complete is False

    def test_panel_stores_title(self, mock_pygame):
        """Panel should store custom title."""
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, title="LOCK BOX")

        assert panel.title == "LOCK BOX"


class TestStepInput:
    """Test input handling for puzzle steps."""

    def test_printable_char_adds_to_step(self, mock_pygame, make_key_event):
        """Printable characters should add to current step."""
        steps = [("KEY 1", "test", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        result = panel.handle_event(make_key_event(ord('a'), 'a'))

        assert result is True
        assert panel.steps[0].value == "a"

    def test_backspace_removes_char(self, mock_pygame, make_key_event):
        """Backspace should remove last character."""
        steps = [("KEY 1", "test", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "abc"

        panel.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert panel.steps[0].value == "ab"

    def test_backspace_on_verified_does_nothing(self, mock_pygame, make_key_event):
        """Backspace should not affect verified steps."""
        steps = [("KEY 1", "test", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "test"
        panel.steps[0].verified = True

        panel.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert panel.steps[0].value == "test"

    def test_verified_step_ignores_input(self, mock_pygame, make_key_event):
        """Verified steps should ignore new input."""
        steps = [("KEY 1", "test", ""), ("KEY 2", "next", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].verified = True

        panel.handle_event(make_key_event(ord('a'), 'a'))

        assert panel.steps[0].value == ""  # Didn't change


class TestStepNavigation:
    """Test navigation between steps."""

    def test_tab_moves_to_next_step(self, mock_pygame, make_key_event):
        """Tab should move to next step."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", ""), ("KEY 3", "c", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        panel.handle_event(make_key_event(mock_pygame.K_TAB))

        assert panel.current_step == 1

    def test_tab_wraps_around(self, mock_pygame, make_key_event):
        """Tab at last step should wrap to first."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.current_step = 1

        panel.handle_event(make_key_event(mock_pygame.K_TAB))

        assert panel.current_step == 0

    def test_up_arrow_moves_up(self, mock_pygame, make_key_event):
        """Up arrow should move to previous step."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.current_step = 1

        panel.handle_event(make_key_event(mock_pygame.K_UP))

        assert panel.current_step == 0

    def test_down_arrow_moves_down(self, mock_pygame, make_key_event):
        """Down arrow should move to next step."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        panel.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert panel.current_step == 1

    def test_up_at_top_stays(self, mock_pygame, make_key_event):
        """Up arrow at first step should stay at first."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        panel.handle_event(make_key_event(mock_pygame.K_UP))

        assert panel.current_step == 0

    def test_down_at_bottom_stays(self, mock_pygame, make_key_event):
        """Down arrow at last step should stay at last."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.current_step = 1

        panel.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert panel.current_step == 1


class TestStepVerification:
    """Test step verification logic."""

    def test_correct_answer_verifies_step(self, mock_pygame):
        """Correct answer should verify the step."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "answer"

        result = panel.verify_current()

        assert result is True
        assert panel.steps[0].verified is True

    def test_case_insensitive_matching(self, mock_pygame):
        """Verification should be case-insensitive."""
        steps = [("KEY 1", "Answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "ANSWER"

        result = panel.verify_current()

        assert result is True
        assert panel.steps[0].verified is True

    def test_whitespace_trimmed(self, mock_pygame):
        """Verification should trim whitespace."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "  answer  "

        result = panel.verify_current()

        assert result is True

    def test_wrong_answer_sets_error(self, mock_pygame):
        """Wrong answer should set error state."""
        steps = [("KEY 1", "correct", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "wrong"

        result = panel.verify_current()

        assert result is False
        assert panel.steps[0].error is True
        assert panel.steps[0].verified is False

    def test_verify_already_verified_returns_true(self, mock_pygame):
        """Verifying already verified step returns True."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].verified = True

        result = panel.verify_current()

        assert result is True

    def test_enter_key_verifies(self, mock_pygame, make_key_event):
        """Enter key should verify current step."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "answer"

        result = panel.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result is True
        assert panel.steps[0].verified is True


class TestStepAdvancement:
    """Test automatic advancement after verification."""

    def test_verify_advances_to_next_unverified(self, mock_pygame):
        """Verification should advance to next unverified step."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", ""), ("KEY 3", "c", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "a"

        panel.verify_current()

        assert panel.current_step == 1

    def test_verify_skips_already_verified(self, mock_pygame):
        """Advancement should skip verified steps."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", ""), ("KEY 3", "c", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[1].verified = True  # Middle step already done
        panel.steps[0].value = "a"

        panel.verify_current()

        assert panel.current_step == 2  # Skipped to step 3


class TestCompletion:
    """Test puzzle completion detection."""

    def test_all_verified_sets_complete(self, mock_pygame):
        """All steps verified should set complete state."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "a"
        panel.verify_current()
        panel.steps[1].value = "b"

        panel.verify_current()

        assert panel.is_complete is True

    def test_partial_not_complete(self, mock_pygame):
        """Partial verification should not complete."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "a"
        panel.verify_current()

        assert panel.is_complete is False

    def test_unlock_calls_callback(self, mock_pygame):
        """unlock() when complete should call on_complete."""
        callback = Mock()
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps, on_complete=callback)
        panel.steps[0].value = "a"
        panel.verify_current()

        panel.unlock()

        callback.assert_called_once()

    def test_unlock_incomplete_does_nothing(self, mock_pygame):
        """unlock() when incomplete should not call callback."""
        callback = Mock()
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps, on_complete=callback)

        panel.unlock()

        callback.assert_not_called()

    def test_enter_when_complete_calls_unlock(self, mock_pygame, make_key_event):
        """Enter when all complete should call unlock."""
        callback = Mock()
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps, on_complete=callback)
        panel.steps[0].value = "a"
        panel.verify_current()

        panel.handle_event(make_key_event(mock_pygame.K_RETURN))

        callback.assert_called_once()


class TestInputHelpers:
    """Test input helper methods."""

    def test_get_current_input(self, mock_pygame):
        """get_current_input should return current step's value."""
        steps = [("KEY 1", "a", ""), ("KEY 2", "b", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "test"

        assert panel.get_current_input() == "test"

    def test_set_current_input(self, mock_pygame):
        """set_current_input should set current step's value."""
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        panel.set_current_input("test")

        assert panel.steps[0].value == "test"

    def test_add_char_appends(self, mock_pygame):
        """add_char should append to current step."""
        steps = [("KEY 1", "test", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "ab"

        panel.add_char("c")

        assert panel.steps[0].value == "abc"

    def test_backspace_method(self, mock_pygame):
        """backspace should remove last char from current step."""
        steps = [("KEY 1", "test", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "abc"

        panel.backspace()

        assert panel.steps[0].value == "ab"


class TestFeedback:
    """Test feedback message behavior."""

    def test_verify_success_shows_feedback(self, mock_pygame):
        """Successful verification should show feedback."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "answer"

        panel.verify_current()

        assert "VERIFIED" in panel._feedback_message

    def test_verify_failure_shows_feedback(self, mock_pygame):
        """Failed verification should show feedback."""
        steps = [("KEY 1", "correct", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "wrong"

        panel.verify_current()

        assert "Incorrect" in panel._feedback_message

    def test_feedback_decays(self, mock_pygame):
        """Feedback should decay over time."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel._feedback_message = "Test"
        panel._feedback_timer = 1.0

        panel.update(1.5)

        assert panel._feedback_message == ""


class TestCursorBlink:
    """Test cursor blink behavior."""

    def test_cursor_starts_visible(self, mock_pygame):
        """Cursor should start visible."""
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        assert panel._cursor_visible is True

    def test_cursor_blinks(self, mock_pygame):
        """Cursor should toggle after 0.5 seconds."""
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        initial = panel._cursor_visible

        panel.update(0.5)

        assert panel._cursor_visible != initial


class TestPuzzlePanelRender:
    """Test rendering behavior."""

    def test_render_does_not_crash(self, mock_pygame, mock_surface):
        """render should complete without error."""
        steps = [("KEY 1", "answer", "hint")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)

        # Should not raise
        panel.render(mock_surface)

    def test_render_with_verified_step(self, mock_pygame, mock_surface):
        """render should handle verified steps."""
        steps = [("KEY 1", "answer", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "answer"
        panel.verify_current()

        # Should not raise
        panel.render(mock_surface)

    def test_render_with_error_step(self, mock_pygame, mock_surface):
        """render should handle error state."""
        steps = [("KEY 1", "correct", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "wrong"
        panel.verify_current()

        # Should not raise
        panel.render(mock_surface)

    def test_render_complete(self, mock_pygame, mock_surface):
        """render should handle complete state."""
        steps = [("KEY 1", "a", "")]
        panel = PuzzlePanel(x=0, y=0, width=400, height=350, steps=steps)
        panel.steps[0].value = "a"
        panel.verify_current()

        # Should not raise
        panel.render(mock_surface)
