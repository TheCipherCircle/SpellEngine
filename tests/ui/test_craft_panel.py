"""Level 2 Tests: CraftPanel Component.

Tests the mask/rule building UI for CRAFT encounters, including
slot selection, pattern building, and keyboard shortcuts.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.craft_panel import CraftPanel, MASK_CHARSETS


class TestCraftPanelCreation:
    """Test CraftPanel initialization."""

    def test_panel_creates_with_dimensions(self, mock_pygame):
        """Panel should initialize with given dimensions."""
        panel = CraftPanel(x=100, y=100, width=500, height=300)

        assert panel.x == 100
        assert panel.y == 100
        assert panel.width == 500
        assert panel.height == 300

    def test_panel_creates_slots(self, mock_pygame):
        """Panel should create max_slots slots."""
        panel = CraftPanel(x=0, y=0, width=500, height=300, max_slots=8)

        assert len(panel.slots) == 8

    def test_first_slot_is_selected(self, mock_pygame):
        """First slot should be selected initially."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        assert panel.selected_slot == 0
        assert panel.slots[0]._selected is True

    def test_panel_creates_charset_buttons(self, mock_pygame):
        """Panel should create charset buttons."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        assert len(panel.charset_buttons) == len(MASK_CHARSETS)

    def test_panel_stores_expected_pattern(self, mock_pygame):
        """Panel should store expected pattern."""
        panel = CraftPanel(x=0, y=0, width=500, height=300, expected_pattern="?l?l?d?d")

        assert panel.expected_pattern == "?l?l?d?d"


class TestSlotSelection:
    """Test slot selection behavior."""

    def test_click_selects_slot(self, mock_pygame, make_click_event):
        """Clicking a slot should select it."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        # Get position of slot 1 (second slot)
        slot = panel.slots[1]
        click_x = slot.x + slot.size // 2
        click_y = slot.y + slot.size // 2

        result = panel.handle_event(make_click_event(click_x, click_y))

        assert result is True
        assert panel.selected_slot == 1
        assert panel.slots[1]._selected is True
        assert panel.slots[0]._selected is False

    def test_left_arrow_moves_selection_left(self, mock_pygame, make_key_event):
        """Left arrow should move selection left."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel._select_slot(3)  # Start at slot 3

        result = panel.handle_event(make_key_event(mock_pygame.K_LEFT))

        assert result is True
        assert panel.selected_slot == 2

    def test_right_arrow_moves_selection_right(self, mock_pygame, make_key_event):
        """Right arrow should move selection right."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        # Start at slot 0

        result = panel.handle_event(make_key_event(mock_pygame.K_RIGHT))

        assert result is True
        assert panel.selected_slot == 1

    def test_left_at_start_stays_at_start(self, mock_pygame, make_key_event):
        """Left arrow at first slot should stay at first slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        panel.handle_event(make_key_event(mock_pygame.K_LEFT))

        assert panel.selected_slot == 0

    def test_right_at_end_stays_at_end(self, mock_pygame, make_key_event):
        """Right arrow at last slot should stay at last slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300, max_slots=8)
        panel._select_slot(7)  # Last slot

        panel.handle_event(make_key_event(mock_pygame.K_RIGHT))

        assert panel.selected_slot == 7


class TestPatternBuilding:
    """Test mask pattern construction."""

    def test_set_slot_value_sets_value(self, mock_pygame):
        """set_slot_value should set the slot value."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        panel.set_slot_value(0, "?l")

        assert panel.slots[0].value == "?l"

    def test_set_slot_advances_selection(self, mock_pygame):
        """Setting a slot value should advance to next empty slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        panel.set_slot_value(0, "?l")

        assert panel.selected_slot == 1

    def test_get_pattern_joins_slot_values(self, mock_pygame):
        """get_pattern should join all slot values."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?u")
        panel.slots[1].set_value("?l")
        panel.slots[2].set_value("?d")

        pattern = panel.get_pattern()

        assert pattern == "?u?l?d"

    def test_get_pattern_empty_slots_ignored(self, mock_pygame):
        """get_pattern should ignore empty slots."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        # Slot 1 is empty
        panel.slots[2].set_value("?d")

        pattern = panel.get_pattern()

        assert pattern == "?l?d"

    def test_get_preview_generates_example(self, mock_pygame):
        """get_preview should generate example characters."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        panel.slots[1].set_value("?u")

        preview = panel.get_preview()

        # Should contain example characters (order may vary)
        assert len(preview) == 2
        assert preview[0].islower()  # ?l gives lowercase
        assert preview[1].isupper()  # ?u gives uppercase

    def test_get_preview_empty_returns_ellipsis(self, mock_pygame):
        """get_preview with no slots should return '...'."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        preview = panel.get_preview()

        assert preview == "..."


class TestKeyboardShortcuts:
    """Test charset keyboard shortcuts."""

    def test_l_key_sets_lowercase(self, mock_pygame, make_key_event):
        """'L' key should set ?l charset."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        result = panel.handle_event(make_key_event(mock_pygame.K_l, 'l'))

        assert result is True
        assert panel.slots[0].value == "?l"

    def test_u_key_sets_uppercase(self, mock_pygame, make_key_event):
        """'U' key should set ?u charset."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        result = panel.handle_event(make_key_event(mock_pygame.K_u, 'u'))

        assert result is True
        assert panel.slots[0].value == "?u"

    def test_d_key_sets_digit(self, mock_pygame, make_key_event):
        """'D' key should set ?d charset."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        result = panel.handle_event(make_key_event(mock_pygame.K_d, 'd'))

        assert result is True
        assert panel.slots[0].value == "?d"

    def test_s_key_sets_special(self, mock_pygame, make_key_event):
        """'S' key should set ?s charset."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        result = panel.handle_event(make_key_event(mock_pygame.K_s, 's'))

        assert result is True
        assert panel.slots[0].value == "?s"

    def test_a_key_sets_all(self, mock_pygame, make_key_event):
        """'A' key should set ?a charset."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        result = panel.handle_event(make_key_event(mock_pygame.K_a, 'a'))

        assert result is True
        assert panel.slots[0].value == "?a"

    def test_backspace_clears_current_slot(self, mock_pygame, make_key_event):
        """Backspace should clear current slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[1].set_value("?l")
        panel._select_slot(1)

        result = panel.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert result is True
        assert panel.slots[1].value == ""

    def test_backspace_moves_back_when_empty(self, mock_pygame, make_key_event):
        """Backspace on empty slot should move to previous slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        panel._select_slot(1)  # Empty slot

        panel.handle_event(make_key_event(mock_pygame.K_BACKSPACE))

        assert panel.selected_slot == 0

    def test_escape_clears_all(self, mock_pygame, make_key_event):
        """Escape should clear all slots."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        panel.slots[1].set_value("?u")
        panel.slots[2].set_value("?d")

        result = panel.handle_event(make_key_event(mock_pygame.K_ESCAPE))

        assert result is True
        assert all(slot.value == "" for slot in panel.slots)
        assert panel.selected_slot == 0


class TestCharsetButtons:
    """Test charset button interaction."""

    def test_charset_button_click_sets_value(self, mock_pygame, make_click_event):
        """Clicking a charset button should set slot value."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        # Get first charset button (?l)
        btn = panel.charset_buttons[0]
        click_x = btn.x + btn.width // 2
        click_y = btn.y + btn.height // 2

        result = panel.handle_event(make_click_event(click_x, click_y))

        assert result is True
        assert panel.slots[0].value == "?l"


class TestClearAndSubmit:
    """Test clear and submit functionality."""

    def test_clear_all_clears_slots(self, mock_pygame):
        """clear_all should clear all slot values."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        panel.slots[1].set_value("?u")

        panel.clear_all()

        assert all(slot.value == "" for slot in panel.slots)

    def test_clear_all_resets_selection(self, mock_pygame):
        """clear_all should reset selection to first slot."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel._select_slot(5)

        panel.clear_all()

        assert panel.selected_slot == 0

    def test_submit_calls_callback(self, mock_pygame):
        """submit should call on_submit with pattern."""
        callback = Mock()
        panel = CraftPanel(x=0, y=0, width=500, height=300, on_submit=callback)
        panel.slots[0].set_value("?l")
        panel.slots[1].set_value("?d")

        panel.submit()

        callback.assert_called_once_with("?l?d")

    def test_submit_empty_shows_feedback(self, mock_pygame):
        """submit with no pattern should show feedback message."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)

        panel.submit()

        assert panel._feedback_message != ""

    def test_enter_key_submits(self, mock_pygame, make_key_event):
        """Enter key should submit pattern."""
        callback = Mock()
        panel = CraftPanel(x=0, y=0, width=500, height=300, on_submit=callback)
        panel.slots[0].set_value("?l")

        result = panel.handle_event(make_key_event(mock_pygame.K_RETURN))

        assert result is True
        callback.assert_called_once()

    def test_clear_button_click(self, mock_pygame, make_click_event):
        """Clicking clear button should clear all slots."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")
        rect = panel.clear_button_rect

        result = panel.handle_event(make_click_event(
            rect.x + rect.width // 2,
            rect.y + rect.height // 2
        ))

        assert result is True
        assert panel.slots[0].value == ""


class TestCraftPanelUpdate:
    """Test panel update behavior."""

    def test_feedback_timer_decays(self, mock_pygame):
        """Feedback message should decay over time."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel._feedback_message = "Test message"
        panel._feedback_timer = 1.0

        panel.update(1.0)

        assert panel._feedback_message == ""


class TestCraftPanelRender:
    """Test rendering behavior."""

    def test_render_does_not_crash(self, mock_pygame, mock_surface):
        """render should complete without error."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0].set_value("?l")

        # Should not raise
        panel.render(mock_surface)

    def test_render_with_feedback(self, mock_pygame, mock_surface):
        """render should handle feedback message."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel._feedback_message = "Test feedback"
        panel._feedback_timer = 1.0

        # Should not raise
        panel.render(mock_surface)


class TestHoverStates:
    """Test hover state management."""

    def test_motion_updates_slot_hover(self, mock_pygame, make_motion_event):
        """Mouse motion should update slot hover states."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        slot = panel.slots[0]

        # Move over the slot
        panel.handle_event(make_motion_event(
            slot.x + slot.size // 2,
            slot.y + slot.size // 2
        ))

        assert slot._hovered is True

    def test_motion_clears_other_hovers(self, mock_pygame, make_motion_event):
        """Mouse motion should clear hovers on other slots."""
        panel = CraftPanel(x=0, y=0, width=500, height=300)
        panel.slots[0]._hovered = True
        slot1 = panel.slots[1]

        # Move to slot 1
        panel.handle_event(make_motion_event(
            slot1.x + slot1.size // 2,
            slot1.y + slot1.size // 2
        ))

        assert panel.slots[0]._hovered is False
        assert slot1._hovered is True
