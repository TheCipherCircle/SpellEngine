"""Level 2 Tests: SiegePanel Component.

Tests the progressive observation UI for SIEGE encounters,
including auto-scrolling output, checkpoints, and completion.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.siege_panel import SiegePanel


class TestSiegePanelCreation:
    """Test SiegePanel initialization."""

    def test_panel_creates_with_dimensions(self, mock_pygame):
        """Panel should initialize with given dimensions."""
        panel = SiegePanel(x=100, y=100, width=500, height=400)

        assert panel.x == 100
        assert panel.y == 100
        assert panel.width == 500
        assert panel.height == 400

    def test_panel_stores_lines(self, mock_pygame):
        """Panel should store provided lines."""
        lines = ["Line 1", "Line 2", "Line 3"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines)

        assert panel.lines == lines

    def test_panel_default_line_delay(self, mock_pygame):
        """Panel should have default line delay."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        assert panel.line_delay == 0.3

    def test_panel_custom_line_delay(self, mock_pygame):
        """Panel should accept custom line delay."""
        panel = SiegePanel(x=0, y=0, width=500, height=400, line_delay=0.5)

        assert panel.line_delay == 0.5

    def test_panel_starts_not_complete(self, mock_pygame):
        """Panel should start not complete."""
        lines = ["Line 1", "Line 2"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines)

        assert panel.is_complete is False

    def test_panel_starts_not_waiting(self, mock_pygame):
        """Panel should start not waiting for input."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        assert panel.is_waiting is False


class TestProgressiveOutput:
    """Test progressive line display."""

    def test_start_clears_visible_lines(self, mock_pygame):
        """start() should clear visible lines."""
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=["Test"])
        panel._visible_lines = [("Old line", (255, 255, 255))]

        panel.start()

        assert len(panel._visible_lines) == 0

    def test_update_adds_line_after_delay(self, mock_pygame):
        """update() should add line after line_delay."""
        lines = ["Line 1", "Line 2"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.3)
        panel.start()

        panel.update(0.3)

        assert len(panel._visible_lines) == 1
        assert panel._visible_lines[0][0] == "Line 1"

    def test_update_adds_multiple_lines(self, mock_pygame):
        """Long update should add multiple lines."""
        lines = ["Line 1", "Line 2", "Line 3"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()

        panel.update(0.35)  # Enough for 3 lines

        assert len(panel._visible_lines) == 3

    def test_complete_when_all_lines_shown(self, mock_pygame):
        """Panel should be complete when all lines shown."""
        lines = ["Line 1"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()

        panel.update(0.2)

        assert panel.is_complete is True

    def test_no_lines_completes_immediately(self, mock_pygame):
        """Empty lines list should complete immediately."""
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=[])
        panel.start()

        panel.update(0.1)

        assert panel.is_complete is True


class TestAddLine:
    """Test direct line addition."""

    def test_add_line_appends(self, mock_pygame):
        """add_line should append to visible lines."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        panel.add_line("Test line")

        assert len(panel._visible_lines) == 1
        assert panel._visible_lines[0][0] == "Test line"

    def test_add_line_with_custom_color(self, mock_pygame):
        """add_line should accept custom color."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        custom_color = (255, 0, 0)

        panel.add_line("Red line", color=custom_color)

        assert panel._visible_lines[0][1] == custom_color

    def test_add_line_auto_detects_success_color(self, mock_pygame):
        """Lines with *** should get success color."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        panel.add_line("*** DISCOVERED ***")

        # Should be success color (green-ish)
        assert panel._visible_lines[0][1][1] > 100  # Green channel

    def test_add_line_auto_detects_error_color(self, mock_pygame):
        """Lines with ERROR should get error color."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        panel.add_line("ERROR: Something failed")

        # Should be error color (red-ish)
        assert panel._visible_lines[0][1][0] > 200  # Red channel

    def test_add_line_auto_scrolls(self, mock_pygame):
        """Adding many lines should auto-scroll."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._max_visible_lines = 5

        for i in range(10):
            panel.add_line(f"Line {i}")

        assert panel._scroll_offset == 5  # Should scroll to show last lines


class TestCheckpoints:
    """Test checkpoint behavior."""

    def test_checkpoint_pauses_output(self, mock_pygame):
        """Checkpoint should pause output."""
        lines = ["Line 1", "[CHECKPOINT]", "Line 2"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()

        # Run past first line and checkpoint
        panel.update(0.25)

        assert panel.is_waiting is True
        # Line 2 should not be visible yet
        assert len(panel._visible_lines) == 1

    def test_checkpoint_with_message(self, mock_pygame):
        """Checkpoint should display custom message."""
        lines = ["[CHECKPOINT]Custom message"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()

        panel.update(0.15)

        assert panel._checkpoint_message == "Custom message"

    def test_advance_checkpoint_resumes(self, mock_pygame):
        """advance_checkpoint should resume output."""
        lines = ["Line 1", "[CHECKPOINT]", "Line 2"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()
        panel.update(0.25)  # Hit checkpoint

        panel.advance_checkpoint()

        assert panel.is_waiting is False

    def test_space_key_advances_checkpoint(self, mock_pygame, make_key_event):
        """Space key should advance past checkpoint."""
        lines = ["[CHECKPOINT]"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()
        panel.update(0.15)  # Hit checkpoint

        result = panel.handle_event(make_key_event(mock_pygame.K_SPACE))

        assert result is True
        assert panel.is_waiting is False


class TestScrolling:
    """Test scroll behavior."""

    def test_scroll_offset_starts_at_zero(self, mock_pygame):
        """Scroll offset should start at zero."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        assert panel._scroll_offset == 0

    def test_up_arrow_scrolls_up(self, mock_pygame, make_key_event):
        """Up arrow should scroll up."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._max_visible_lines = 5
        for i in range(10):
            panel.add_line(f"Line {i}")

        panel.handle_event(make_key_event(mock_pygame.K_UP))

        assert panel._scroll_offset == 4  # One less than max

    def test_down_arrow_scrolls_down(self, mock_pygame, make_key_event):
        """Down arrow should scroll down."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._max_visible_lines = 5
        for i in range(10):
            panel.add_line(f"Line {i}")
        panel._scroll_offset = 3

        panel.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert panel._scroll_offset == 4

    def test_scroll_bounded_at_top(self, mock_pygame, make_key_event):
        """Scroll should not go below zero."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._scroll_offset = 0

        panel.handle_event(make_key_event(mock_pygame.K_UP))

        assert panel._scroll_offset == 0

    def test_scroll_bounded_at_bottom(self, mock_pygame, make_key_event):
        """Scroll should not exceed max."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._max_visible_lines = 5
        for i in range(10):
            panel.add_line(f"Line {i}")
        # Already at max scroll
        max_scroll = len(panel._visible_lines) - panel._max_visible_lines

        panel.handle_event(make_key_event(mock_pygame.K_DOWN))

        assert panel._scroll_offset == max_scroll


class TestCompletion:
    """Test completion behavior."""

    def test_space_when_complete_calls_callback(self, mock_pygame, make_key_event):
        """Space when complete should call on_complete."""
        callback = Mock()
        lines = ["Line 1"]
        panel = SiegePanel(
            x=0, y=0, width=500, height=400,
            lines=lines, line_delay=0.1,
            on_complete=callback
        )
        panel.start()
        panel.update(0.2)  # Complete

        panel.handle_event(make_key_event(mock_pygame.K_SPACE))

        callback.assert_called_once()

    def test_space_incomplete_not_at_checkpoint(self, mock_pygame, make_key_event):
        """Space when incomplete and not at checkpoint does nothing."""
        callback = Mock()
        lines = ["Line 1", "Line 2"]
        panel = SiegePanel(
            x=0, y=0, width=500, height=400,
            lines=lines, line_delay=0.5,
            on_complete=callback
        )
        panel.start()
        panel.update(0.1)  # Still running

        result = panel.handle_event(make_key_event(mock_pygame.K_SPACE))

        assert result is False
        callback.assert_not_called()


class TestReset:
    """Test reset functionality."""

    def test_reset_clears_state(self, mock_pygame):
        """reset() should clear all state."""
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=["Line 1"])
        panel.start()
        panel.update(0.5)  # Complete

        panel.reset()

        assert len(panel._visible_lines) == 0
        assert panel._current_line_index == 0
        assert panel.is_complete is False

    def test_reset_with_new_lines(self, mock_pygame):
        """reset() with new lines should replace lines."""
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=["Old"])

        panel.reset(lines=["New 1", "New 2"])

        assert panel.lines == ["New 1", "New 2"]


class TestNoUpdateWhenPaused:
    """Test that update doesn't progress when paused."""

    def test_update_paused_at_complete(self, mock_pygame):
        """update should not change state when complete."""
        lines = ["Line 1"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()
        panel.update(0.2)  # Complete
        line_count = len(panel._visible_lines)

        panel.update(1.0)  # More time passes

        assert len(panel._visible_lines) == line_count

    def test_update_paused_at_checkpoint(self, mock_pygame):
        """update should not add lines when waiting at checkpoint."""
        lines = ["Line 1", "[CHECKPOINT]", "Line 2"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()
        panel.update(0.25)  # Hit checkpoint
        line_count = len(panel._visible_lines)

        panel.update(1.0)

        assert len(panel._visible_lines) == line_count


class TestSiegePanelRender:
    """Test rendering behavior."""

    def test_render_does_not_crash_empty(self, mock_pygame, mock_surface):
        """render should complete without error when empty."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)

        # Should not raise
        panel.render(mock_surface)

    def test_render_with_lines(self, mock_pygame, mock_surface):
        """render should handle lines."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel.add_line("Test line 1")
        panel.add_line("Test line 2")

        # Should not raise
        panel.render(mock_surface)

    def test_render_at_checkpoint(self, mock_pygame, mock_surface):
        """render should handle checkpoint state."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel.set_checkpoint("Press SPACE to continue")

        # Should not raise
        panel.render(mock_surface)

    def test_render_complete(self, mock_pygame, mock_surface):
        """render should handle complete state."""
        lines = ["Line 1"]
        panel = SiegePanel(x=0, y=0, width=500, height=400, lines=lines, line_delay=0.1)
        panel.start()
        panel.update(0.2)  # Complete

        # Should not raise
        panel.render(mock_surface)

    def test_render_with_scroll(self, mock_pygame, mock_surface):
        """render should handle scrolled state."""
        panel = SiegePanel(x=0, y=0, width=500, height=400)
        panel._max_visible_lines = 5
        for i in range(10):
            panel.add_line(f"Line {i}")
        panel._scroll_offset = 3

        # Should not raise
        panel.render(mock_surface)
