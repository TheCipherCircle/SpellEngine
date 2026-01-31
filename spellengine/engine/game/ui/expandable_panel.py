"""Expandable panel component - slides up/down with context-aware content.

Used for:
- Terminal output (hash cracking encounters)
- Step tracker (PUZZLE_BOX, PIPELINE)
- Learn More (TOUR, WALKTHROUGH)
- Consequences (FORK choices)
"""

from typing import TYPE_CHECKING, Callable, Any

from spellengine.engine.game.ui.theme import Colors, Typography, SPACING, LAYOUT, get_fonts

if TYPE_CHECKING:
    import pygame


class ExpandablePanel:
    """A panel that can expand/collapse from a header bar.

    When collapsed: Shows just a clickable header bar with label and toggle hint
    When expanded: Slides up to show full content area

    Supports different content types via content_renderer callback.
    """

    # Animation settings
    EXPAND_SPEED = 1200  # pixels per second

    # Header bar height when collapsed
    HEADER_HEIGHT = 32

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        collapsed_height: int,
        expanded_height: int,
        label: str = "PANEL",
        toggle_key: str = "T",
        content_renderer: Callable[["pygame.Surface", "pygame.Rect"], None] | None = None,
        on_toggle: Callable[[bool], None] | None = None,
    ) -> None:
        """Initialize the expandable panel.

        Args:
            x: X position (left edge)
            y: Y position when fully expanded (top of expanded panel)
            width: Panel width
            collapsed_height: Height when collapsed (usually just header)
            expanded_height: Height when fully expanded
            label: Label shown in header bar (e.g., "TERMINAL", "STEPS")
            toggle_key: Key hint shown in header (e.g., "T")
            content_renderer: Callback to render content area
            on_toggle: Callback when panel is toggled (receives is_expanded)
        """
        import pygame

        self.x = x
        self.width = width
        self.collapsed_height = collapsed_height
        self.expanded_height = expanded_height
        self.label = label
        self.toggle_key = toggle_key
        self.content_renderer = content_renderer
        self.on_toggle = on_toggle

        # State
        self._expanded = False
        self._current_height = float(collapsed_height)
        self._target_height = float(collapsed_height)

        # The y position is the BOTTOM of the panel (anchored to bottom of screen area)
        self._bottom_y = y + expanded_height

        # Cached rect
        self._rect: pygame.Rect | None = None
        self._content_rect: pygame.Rect | None = None

    @property
    def is_expanded(self) -> bool:
        """Whether the panel is currently expanded."""
        return self._expanded

    @property
    def is_animating(self) -> bool:
        """Whether the panel is currently animating."""
        return abs(self._current_height - self._target_height) > 1

    @property
    def rect(self) -> "pygame.Rect":
        """Get the current panel rect."""
        import pygame

        current_y = int(self._bottom_y - self._current_height)
        return pygame.Rect(self.x, current_y, self.width, int(self._current_height))

    @property
    def content_rect(self) -> "pygame.Rect":
        """Get the content area rect (excludes header)."""
        import pygame

        r = self.rect
        return pygame.Rect(
            r.x + SPACING["sm"],
            r.y + self.HEADER_HEIGHT + SPACING["xs"],
            r.width - SPACING["sm"] * 2,
            r.height - self.HEADER_HEIGHT - SPACING["sm"]
        )

    def set_label(self, label: str) -> None:
        """Update the panel label."""
        self.label = label

    def set_content_renderer(self, renderer: Callable[["pygame.Surface", "pygame.Rect"], None]) -> None:
        """Set the content renderer callback."""
        self.content_renderer = renderer

    def toggle(self) -> None:
        """Toggle between expanded and collapsed states."""
        self._expanded = not self._expanded
        self._target_height = float(
            self.expanded_height if self._expanded else self.collapsed_height
        )

        if self.on_toggle:
            self.on_toggle(self._expanded)

    def expand(self) -> None:
        """Expand the panel."""
        if not self._expanded:
            self.toggle()

    def collapse(self) -> None:
        """Collapse the panel."""
        if self._expanded:
            self.toggle()

    def update(self, dt: float) -> None:
        """Update animation state.

        Args:
            dt: Delta time in seconds
        """
        if self.is_animating:
            # Animate towards target height
            diff = self._target_height - self._current_height
            step = self.EXPAND_SPEED * dt

            if abs(diff) <= step:
                self._current_height = self._target_height
            elif diff > 0:
                self._current_height += step
            else:
                self._current_height -= step

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed
        """
        import pygame

        # Check for toggle key
        if event.type == pygame.KEYDOWN:
            # Handle special key names
            key_map = {
                "TAB": pygame.K_TAB,
                "`": pygame.K_BACKQUOTE,
                "BACKQUOTE": pygame.K_BACKQUOTE,
            }
            expected_key = key_map.get(self.toggle_key.upper(),
                                       getattr(pygame, f"K_{self.toggle_key.lower()}", None))
            if event.key == expected_key:
                self.toggle()
                return True

        # Check for click on header bar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            header_rect = self._get_header_rect()
            if header_rect.collidepoint(event.pos):
                self.toggle()
                return True

        return False

    def _get_header_rect(self) -> "pygame.Rect":
        """Get the header bar rect."""
        import pygame

        r = self.rect
        return pygame.Rect(r.x, r.y, r.width, self.HEADER_HEIGHT)

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the panel.

        Args:
            surface: Surface to draw on
        """
        import pygame

        # Don't draw anything if completely collapsed (height 0)
        if self._current_height < 1:
            return

        r = self.rect
        fonts = get_fonts()

        # Background
        pygame.draw.rect(surface, Colors.BG_DARK, r)

        # Border
        pygame.draw.rect(surface, Colors.BORDER, r, LAYOUT["border_width"])

        # Only draw header content if we have enough height
        if self._current_height >= self.HEADER_HEIGHT:
            # Header bar
            header_rect = self._get_header_rect()
            pygame.draw.rect(surface, Colors.BG_MEDIUM, header_rect)
            pygame.draw.line(
                surface,
                Colors.BORDER,
                (header_rect.x, header_rect.bottom),
                (header_rect.right, header_rect.bottom),
                1
            )

            # Toggle arrow
            arrow = "▼" if self._expanded else "▲"
            arrow_font = fonts.get_font(Typography.SIZE_SMALL)
            arrow_surface = arrow_font.render(arrow, True, Colors.TEXT_MUTED)
            arrow_x = header_rect.x + SPACING["sm"]
            arrow_y = header_rect.centery - arrow_surface.get_height() // 2
            surface.blit(arrow_surface, (arrow_x, arrow_y))

            # Label
            label_font = fonts.get_font(Typography.SIZE_SMALL, bold=True)
            label_surface = label_font.render(self.label.upper(), True, Colors.TEXT_HEADER)
            label_x = arrow_x + arrow_surface.get_width() + SPACING["sm"]
            label_y = header_rect.centery - label_surface.get_height() // 2
            surface.blit(label_surface, (label_x, label_y))

            # Toggle hint on right side
            hint_text = f"[{self.toggle_key.upper()}] {'Hide' if self._expanded else 'Show'}"
            hint_font = fonts.get_font(Typography.SIZE_TINY)
            hint_surface = hint_font.render(hint_text, True, Colors.TEXT_DIM)
            hint_x = header_rect.right - hint_surface.get_width() - SPACING["sm"]
            hint_y = header_rect.centery - hint_surface.get_height() // 2
            surface.blit(hint_surface, (hint_x, hint_y))

        # Content area (only if expanded enough to show)
        if self._current_height > self.HEADER_HEIGHT + SPACING["md"]:
            content_rect = self.content_rect

            # Clip content to panel bounds
            surface.set_clip(content_rect)

            if self.content_renderer:
                self.content_renderer(surface, content_rect)

            surface.set_clip(None)


class StepTracker:
    """Content renderer for PUZZLE_BOX/PIPELINE step tracking.

    Shows steps with completion status and explanations.
    """

    def __init__(self) -> None:
        """Initialize the step tracker."""
        self._steps: list[tuple[str, str, str, bool]] = []  # (id, label, explanation, completed)
        self._tip: str = ""

    def set_steps(self, steps: list[tuple[str, str, str]]) -> None:
        """Set the steps to track.

        Args:
            steps: List of (id, label, explanation) tuples
        """
        self._steps = [(s[0], s[1], s[2], False) for s in steps]

    def complete_step(self, step_id: str) -> None:
        """Mark a step as completed.

        Args:
            step_id: ID of the step to complete
        """
        self._steps = [
            (sid, label, exp, True if sid == step_id else completed)
            for sid, label, exp, completed in self._steps
        ]

    def set_tip(self, tip: str) -> None:
        """Set the bottom tip text.

        Args:
            tip: Tip text to display
        """
        self._tip = tip

    def render(self, surface: "pygame.Surface", content_rect: "pygame.Rect") -> None:
        """Render the step tracker content.

        Args:
            surface: Surface to draw on
            content_rect: Content area rectangle
        """
        import pygame

        fonts = get_fonts()
        step_font = fonts.get_font(Typography.SIZE_SMALL, bold=True)
        exp_font = fonts.get_font(Typography.SIZE_TINY)

        y = content_rect.y
        line_height = step_font.get_height() + exp_font.get_height() + SPACING["sm"]

        for step_id, label, explanation, completed in self._steps:
            # Status icon
            icon = "✓" if completed else "○"
            icon_color = Colors.SUCCESS if completed else Colors.TEXT_MUTED
            icon_surface = step_font.render(icon, True, icon_color)
            surface.blit(icon_surface, (content_rect.x, y))

            # Label
            label_color = Colors.TEXT_PRIMARY if completed else Colors.TEXT_SECONDARY
            label_surface = step_font.render(label, True, label_color)
            surface.blit(label_surface, (content_rect.x + 25, y))

            # Explanation (indented)
            exp_surface = exp_font.render(f"→ {explanation}", True, Colors.TEXT_DIM)
            surface.blit(exp_surface, (content_rect.x + 30, y + step_font.get_height() + 2))

            y += line_height

        # Tip at bottom
        if self._tip:
            tip_y = content_rect.bottom - exp_font.get_height() - SPACING["xs"]
            tip_surface = exp_font.render(f"💡 {self._tip}", True, Colors.AQUA)
            surface.blit(tip_surface, (content_rect.x, tip_y))


class LearnMoreContent:
    """Content renderer for TOUR/WALKTHROUGH educational content.

    Shows extended explanations, lore, and learning material.
    """

    def __init__(self) -> None:
        """Initialize learn more content."""
        self._title: str = ""
        self._paragraphs: list[str] = []
        self._highlight: str = ""

    def set_content(self, title: str, paragraphs: list[str], highlight: str = "") -> None:
        """Set the learn more content.

        Args:
            title: Section title
            paragraphs: List of paragraph strings
            highlight: Optional highlighted takeaway
        """
        self._title = title
        self._paragraphs = paragraphs
        self._highlight = highlight

    def render(self, surface: "pygame.Surface", content_rect: "pygame.Rect") -> None:
        """Render the learn more content.

        Args:
            surface: Surface to draw on
            content_rect: Content area rectangle
        """
        import pygame

        fonts = get_fonts()
        title_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        body_font = fonts.get_font(Typography.SIZE_TINY)

        y = content_rect.y

        # Title
        if self._title:
            title_surface = title_font.render(self._title, True, Colors.TEXT_HEADER)
            surface.blit(title_surface, (content_rect.x, y))
            y += title_font.get_height() + SPACING["sm"]

        # Paragraphs
        for para in self._paragraphs:
            # Simple word wrap
            words = para.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_surface = body_font.render(test_line, True, Colors.TEXT_SECONDARY)
                if test_surface.get_width() > content_rect.width - 10:
                    # Render current line and start new one
                    if line:
                        line_surface = body_font.render(line, True, Colors.TEXT_SECONDARY)
                        surface.blit(line_surface, (content_rect.x, y))
                        y += body_font.get_height() + 2
                    line = word
                else:
                    line = test_line

            # Render remaining line
            if line:
                line_surface = body_font.render(line, True, Colors.TEXT_SECONDARY)
                surface.blit(line_surface, (content_rect.x, y))
                y += body_font.get_height() + SPACING["xs"]

            y += SPACING["xs"]  # Paragraph spacing

        # Highlight box at bottom
        if self._highlight:
            highlight_y = content_rect.bottom - body_font.get_height() * 2 - SPACING["sm"]

            # Background box
            highlight_rect = pygame.Rect(
                content_rect.x,
                highlight_y - SPACING["xs"],
                content_rect.width,
                body_font.get_height() * 2 + SPACING["sm"]
            )
            pygame.draw.rect(surface, Colors.BG_HIGHLIGHT, highlight_rect, border_radius=4)
            pygame.draw.rect(surface, Colors.AQUA, highlight_rect, 1, border_radius=4)

            # Text
            highlight_surface = body_font.render(f"✦ {self._highlight}", True, Colors.AQUA)
            surface.blit(highlight_surface, (content_rect.x + SPACING["xs"], highlight_y))
