"""Level 2 Tests: ExpandablePanel Component.

Tests the expandable panel's toggle behavior, animation, and event handling.

Tests verify behavior (WHAT it does), not implementation (HOW it works).
"""

import pytest
from unittest.mock import Mock

from spellengine.engine.game.ui.expandable_panel import ExpandablePanel


class TestPanelCreation:
    """Test ExpandablePanel initialization."""

    def test_panel_creates_with_dimensions(self, mock_pygame):
        """Panel should initialize with given dimensions."""
        panel = ExpandablePanel(
            x=100,
            y=200,
            width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        assert panel.x == 100
        assert panel.width == 400
        assert panel.collapsed_height == 32
        assert panel.expanded_height == 300

    def test_panel_starts_collapsed(self, mock_pygame):
        """Panel should start in collapsed state."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        assert panel.is_expanded is False
        assert panel._current_height == 32

    def test_panel_stores_callbacks(self, mock_pygame):
        """Panel should store label and callbacks."""
        renderer = Mock()
        on_toggle = Mock()
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            label="TEST",
            toggle_key="T",
            content_renderer=renderer,
            on_toggle=on_toggle,
        )

        assert panel.label == "TEST"
        assert panel.toggle_key == "T"
        assert panel.content_renderer is renderer
        assert panel.on_toggle is on_toggle


class TestPanelToggle:
    """Test expand/collapse behavior."""

    def test_toggle_changes_expanded_state(self, mock_pygame):
        """toggle() should change expanded state."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        panel.toggle()

        assert panel.is_expanded is True

    def test_toggle_twice_returns_to_original(self, mock_pygame):
        """Toggling twice should return to original state."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        panel.toggle()
        panel.toggle()

        assert panel.is_expanded is False

    def test_expand_sets_expanded_state(self, mock_pygame):
        """expand() should set panel to expanded."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        panel.expand()

        assert panel.is_expanded is True

    def test_expand_when_already_expanded_does_nothing(self, mock_pygame):
        """expand() when already expanded should not toggle."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.expand()
        assert panel.is_expanded is True

        panel.expand()  # Call again

        assert panel.is_expanded is True  # Still expanded

    def test_collapse_sets_collapsed_state(self, mock_pygame):
        """collapse() should set panel to collapsed."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.expand()

        panel.collapse()

        assert panel.is_expanded is False

    def test_collapse_when_already_collapsed_does_nothing(self, mock_pygame):
        """collapse() when already collapsed should not toggle."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        assert panel.is_expanded is False

        panel.collapse()

        assert panel.is_expanded is False

    def test_toggle_sets_target_height_expanded(self, mock_pygame):
        """toggle() should set target height to expanded_height."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        panel.toggle()

        assert panel._target_height == 300

    def test_toggle_sets_target_height_collapsed(self, mock_pygame):
        """toggle() from expanded should set target to collapsed_height."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()  # Expand first

        panel.toggle()  # Collapse

        assert panel._target_height == 32

    def test_toggle_calls_callback(self, mock_pygame):
        """toggle() should call on_toggle callback."""
        callback = Mock()
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            on_toggle=callback,
        )

        panel.toggle()

        callback.assert_called_once_with(True)  # Now expanded


class TestPanelAnimation:
    """Test height animation behavior."""

    def test_is_animating_when_height_differs(self, mock_pygame):
        """is_animating should be True when height != target."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()

        assert panel.is_animating is True

    def test_is_animating_false_when_complete(self, mock_pygame):
        """is_animating should be False when at target."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        # Not toggled, at collapsed height
        assert panel.is_animating is False

    def test_animation_progresses_with_dt(self, mock_pygame):
        """update() should progress animation toward target."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()
        initial_height = panel._current_height

        panel.update(0.1)  # 100ms

        assert panel._current_height > initial_height

    def test_animation_completes_at_target(self, mock_pygame):
        """Animation should eventually reach target height."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()

        # Run enough updates to complete animation
        for _ in range(100):
            panel.update(0.016)

        assert panel._current_height == panel.expanded_height

    def test_collapse_animation_reaches_target(self, mock_pygame):
        """Collapse animation should reach collapsed height."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()
        # Run to expanded
        for _ in range(100):
            panel.update(0.016)

        panel.toggle()  # Start collapse
        # Run to collapsed
        for _ in range(100):
            panel.update(0.016)

        assert panel._current_height == panel.collapsed_height

    def test_animation_speed_is_proportional(self, mock_pygame):
        """Animation should progress proportionally to dt."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()

        # Large dt should cause larger height change
        panel.update(0.5)

        # Should have progressed significantly
        assert panel._current_height > 100


class TestPanelEvents:
    """Test event handling."""

    def test_toggle_key_triggers_toggle(self, mock_pygame, make_key_event):
        """Pressing toggle key should toggle panel."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            toggle_key="T",
        )

        result = panel.handle_event(make_key_event(mock_pygame.K_t))

        assert result is True
        assert panel.is_expanded is True

    def test_tab_key_toggles_tab_panel(self, mock_pygame, make_key_event):
        """TAB toggle_key should respond to TAB key."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            toggle_key="TAB",
        )

        result = panel.handle_event(make_key_event(mock_pygame.K_TAB))

        assert result is True
        assert panel.is_expanded is True

    def test_unrelated_key_not_consumed(self, mock_pygame, make_key_event):
        """Unrelated keys should not be consumed."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            toggle_key="T",
        )

        result = panel.handle_event(make_key_event(mock_pygame.K_ESCAPE))

        assert result is False
        assert panel.is_expanded is False

    def test_header_click_toggles(self, mock_pygame, make_click_event):
        """Clicking header area should toggle panel."""
        panel = ExpandablePanel(
            x=100, y=200, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        # Click inside header (panel is bottom-anchored, so y is calculated)
        # Header is at top of current rect
        header_y = panel.rect.y + 10

        result = panel.handle_event(make_click_event(200, header_y))

        assert result is True
        assert panel.is_expanded is True

    def test_non_header_click_not_consumed(self, mock_pygame, make_click_event):
        """Clicking outside header should not toggle."""
        panel = ExpandablePanel(
            x=100, y=200, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        # Click way outside the panel
        result = panel.handle_event(make_click_event(0, 0))

        assert result is False
        assert panel.is_expanded is False


class TestPanelRect:
    """Test rect property calculations."""

    def test_rect_reflects_current_height(self, mock_pygame):
        """rect property should use current height."""
        panel = ExpandablePanel(
            x=100, y=200, width=400,
            collapsed_height=32,
            expanded_height=300,
        )

        rect = panel.rect

        assert rect.width == 400
        assert rect.height == 32  # Collapsed height

    def test_content_rect_excludes_header(self, mock_pygame):
        """content_rect should be inside the header."""
        panel = ExpandablePanel(
            x=100, y=200, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        panel.toggle()
        # Run animation to completion
        for _ in range(100):
            panel.update(0.016)

        content = panel.content_rect

        assert content.y > panel.rect.y  # Below header
        assert content.height < panel.rect.height  # Smaller than full


class TestPanelLabel:
    """Test label management."""

    def test_set_label_updates_label(self, mock_pygame):
        """set_label should update the panel label."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            label="ORIGINAL",
        )

        panel.set_label("NEW LABEL")

        assert panel.label == "NEW LABEL"

    def test_set_content_renderer_updates_renderer(self, mock_pygame):
        """set_content_renderer should update renderer callback."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
        )
        new_renderer = Mock()

        panel.set_content_renderer(new_renderer)

        assert panel.content_renderer is new_renderer


class TestPanelDraw:
    """Test rendering behavior."""

    def test_draw_does_not_crash_collapsed(self, mock_pygame, mock_surface):
        """draw() should complete without error when collapsed."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            label="TEST",
        )

        # Should not raise
        panel.draw(mock_surface)

    def test_draw_does_not_crash_expanded(self, mock_pygame, mock_surface):
        """draw() should complete without error when expanded."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            label="TEST",
        )
        panel.toggle()
        for _ in range(100):
            panel.update(0.016)

        # Should not raise
        panel.draw(mock_surface)

    def test_content_renderer_called_when_expanded(self, mock_pygame, mock_surface):
        """Content renderer should be called when panel is expanded enough."""
        renderer = Mock()
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=32,
            expanded_height=300,
            content_renderer=renderer,
        )
        panel.toggle()
        # Animate to full expansion
        for _ in range(100):
            panel.update(0.016)

        panel.draw(mock_surface)

        renderer.assert_called()

    def test_zero_height_skips_draw(self, mock_pygame, mock_surface):
        """Panel with zero height should skip drawing."""
        panel = ExpandablePanel(
            x=0, y=0, width=400,
            collapsed_height=0,
            expanded_height=300,
        )
        panel._current_height = 0

        # Should not raise even with zero height
        panel.draw(mock_surface)
