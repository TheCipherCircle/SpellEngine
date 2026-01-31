"""Settings widgets - Sliders and Toggles.

UI components for the settings menu.
Gruvbox-styled with clean retro aesthetic.
"""

from typing import TYPE_CHECKING, Callable

from spellengine.engine.game.ui.theme import Colors, SPACING, Typography, get_fonts

if TYPE_CHECKING:
    import pygame


class Slider:
    """Horizontal slider for volume/percentage values.

    Draggable handle on a track, shows current value as percentage.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        label: str,
        value: float = 0.5,
        on_change: Callable[[float], None] | None = None,
    ):
        """Initialize slider.

        Args:
            x: X position
            y: Y position
            width: Total width including label
            label: Label text (e.g., "SFX Volume")
            value: Initial value (0.0-1.0)
            on_change: Callback when value changes
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self._value = max(0.0, min(1.0, value))
        self.on_change = on_change

        # Layout
        self.label_width = 150
        self.track_width = width - self.label_width - 60  # Leave room for percentage
        self.track_height = 8
        self.handle_width = 16
        self.handle_height = 20
        self.height = 30

        # Track position
        self.track_x = x + self.label_width
        self.track_y = y + (self.height - self.track_height) // 2

        # Interaction state
        self._dragging = False
        self._hovered = False

        # Rects for hit testing
        self.rect = pygame.Rect(x, y, width, self.height)
        self._update_handle_rect()

    def _update_handle_rect(self) -> None:
        """Update handle rect based on current value."""
        import pygame

        handle_x = self.track_x + int(self._value * (self.track_width - self.handle_width))
        handle_y = self.y + (self.height - self.handle_height) // 2
        self._handle_rect = pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)

    @property
    def value(self) -> float:
        """Get current value (0.0-1.0)."""
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        """Set value and update handle position."""
        self._value = max(0.0, min(1.0, val))
        self._update_handle_rect()

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle mouse events.

        Returns True if event was consumed.
        """
        import pygame

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._handle_rect.collidepoint(event.pos):
                self._dragging = True
                return True
            elif self._track_rect.collidepoint(event.pos):
                # Click on track - jump to position
                self._set_value_from_x(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False

        elif event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
            if self._dragging:
                self._set_value_from_x(event.pos[0])
                return True

        return False

    def _set_value_from_x(self, mouse_x: int) -> None:
        """Set value based on mouse X position."""
        relative_x = mouse_x - self.track_x
        new_value = relative_x / (self.track_width - self.handle_width)
        new_value = max(0.0, min(1.0, new_value))

        if new_value != self._value:
            self._value = new_value
            self._update_handle_rect()
            if self.on_change:
                self.on_change(self._value)

    @property
    def _track_rect(self) -> "pygame.Rect":
        """Get track rectangle for hit testing."""
        import pygame
        return pygame.Rect(self.track_x, self.track_y - 5, self.track_width, self.track_height + 10)

    def render(self, surface: "pygame.Surface") -> None:
        """Render the slider."""
        import pygame

        fonts = get_fonts()
        label_font = fonts.get_font(Typography.SIZE_BODY)
        value_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)

        # Label
        label_surface = label_font.render(self.label, Typography.ANTIALIAS, Colors.TEXT_PRIMARY)
        surface.blit(label_surface, (self.x, self.y + (self.height - label_surface.get_height()) // 2))

        # Track background
        track_rect = pygame.Rect(self.track_x, self.track_y, self.track_width, self.track_height)
        pygame.draw.rect(surface, Colors.BG_DARKEST, track_rect, border_radius=4)

        # Track fill (up to handle)
        fill_width = int(self._value * self.track_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.track_x, self.track_y, fill_width, self.track_height)
            pygame.draw.rect(surface, Colors.BLUE, fill_rect, border_radius=4)

        # Track border
        pygame.draw.rect(surface, Colors.BORDER, track_rect, width=1, border_radius=4)

        # Handle
        handle_color = Colors.TEXT_HEADER if self._dragging or self._hovered else Colors.TEXT_PRIMARY
        pygame.draw.rect(surface, handle_color, self._handle_rect, border_radius=3)
        pygame.draw.rect(surface, Colors.BORDER, self._handle_rect, width=1, border_radius=3)

        # Percentage value
        pct_text = f"{int(self._value * 100)}%"
        pct_surface = value_font.render(pct_text, Typography.ANTIALIAS, Colors.YELLOW)
        pct_x = self.track_x + self.track_width + 10
        pct_y = self.y + (self.height - pct_surface.get_height()) // 2
        surface.blit(pct_surface, (pct_x, pct_y))


class Toggle:
    """On/Off toggle switch.

    Clickable toggle with label, shows ON/OFF state.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        label: str,
        value: bool = False,
        on_change: Callable[[bool], None] | None = None,
    ):
        """Initialize toggle.

        Args:
            x: X position
            y: Y position
            width: Total width including label
            label: Label text
            value: Initial state
            on_change: Callback when toggled
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self._value = value
        self.on_change = on_change

        # Layout
        self.label_width = 150
        self.toggle_width = 60
        self.toggle_height = 26
        self.height = 30

        # Toggle button position
        self.toggle_x = x + self.label_width
        self.toggle_y = y + (self.height - self.toggle_height) // 2

        # Interaction
        self._hovered = False

        # Rects
        self.rect = pygame.Rect(x, y, width, self.height)
        self._toggle_rect = pygame.Rect(self.toggle_x, self.toggle_y, self.toggle_width, self.toggle_height)

    @property
    def value(self) -> bool:
        """Get current state."""
        return self._value

    @value.setter
    def value(self, val: bool) -> None:
        """Set state."""
        self._value = val

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle mouse events.

        Returns True if event was consumed.
        """
        import pygame

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._toggle_rect.collidepoint(event.pos):
                self._value = not self._value
                if self.on_change:
                    self.on_change(self._value)
                return True

        elif event.type == pygame.MOUSEMOTION:
            self._hovered = self._toggle_rect.collidepoint(event.pos)

        return False

    def render(self, surface: "pygame.Surface") -> None:
        """Render the toggle."""
        import pygame

        fonts = get_fonts()
        label_font = fonts.get_font(Typography.SIZE_BODY)
        toggle_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)

        # Label
        label_surface = label_font.render(self.label, Typography.ANTIALIAS, Colors.TEXT_PRIMARY)
        surface.blit(label_surface, (self.x, self.y + (self.height - label_surface.get_height()) // 2))

        # Toggle background
        bg_color = Colors.SUCCESS if self._value else Colors.BG_DARKEST
        if self._hovered:
            bg_color = tuple(min(255, c + 20) for c in bg_color)
        pygame.draw.rect(surface, bg_color, self._toggle_rect, border_radius=4)
        pygame.draw.rect(surface, Colors.BORDER, self._toggle_rect, width=1, border_radius=4)

        # Toggle text
        toggle_text = "ON" if self._value else "OFF"
        text_color = Colors.BG_DARKEST if self._value else Colors.TEXT_MUTED
        text_surface = toggle_font.render(toggle_text, Typography.ANTIALIAS, text_color)
        text_x = self.toggle_x + (self.toggle_width - text_surface.get_width()) // 2
        text_y = self.toggle_y + (self.toggle_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))


class TimerWidget:
    """Countdown timer widget for RACE encounters.

    Displays a countdown with visual urgency indicators:
    - Green: > 50% time remaining
    - Yellow: 25-50% time remaining
    - Red + pulse: < 25% time remaining
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        duration: float,
        on_expire: Callable[[], None] | None = None,
    ):
        """Initialize timer.

        Args:
            x: X position
            y: Y position
            width: Widget width
            duration: Total duration in seconds
            on_expire: Callback when timer expires
        """
        import pygame

        self.x = x
        self.y = y
        self.width = width
        self.height = 40
        self.duration = duration
        self.remaining = duration
        self.on_expire = on_expire

        self._running = False
        self._expired = False
        self._pulse_timer = 0.0

        self.rect = pygame.Rect(x, y, width, self.height)

    def start(self) -> None:
        """Start the countdown."""
        self._running = True
        self._expired = False
        self.remaining = self.duration

    def stop(self) -> None:
        """Stop the countdown."""
        self._running = False

    def reset(self, duration: float | None = None) -> None:
        """Reset the timer."""
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration
        self._running = False
        self._expired = False

    @property
    def is_running(self) -> bool:
        """Check if timer is running."""
        return self._running

    @property
    def is_expired(self) -> bool:
        """Check if timer has expired."""
        return self._expired

    @property
    def progress(self) -> float:
        """Get progress as 0.0-1.0 (1.0 = full, 0.0 = expired)."""
        return max(0.0, self.remaining / self.duration)

    def update(self, dt: float) -> None:
        """Update timer state."""
        if not self._running or self._expired:
            return

        self.remaining -= dt
        self._pulse_timer += dt

        if self.remaining <= 0:
            self.remaining = 0
            self._running = False
            self._expired = True
            if self.on_expire:
                self.on_expire()

    def render(self, surface: "pygame.Surface") -> None:
        """Render the timer widget."""
        import pygame
        import math

        fonts = get_fonts()

        # Calculate time display
        minutes = int(self.remaining // 60)
        seconds = int(self.remaining % 60)
        time_str = f"{minutes}:{seconds:02d}"

        # Determine color based on remaining time
        progress = self.progress
        if progress > 0.5:
            bar_color = Colors.SUCCESS
            text_color = Colors.SUCCESS
        elif progress > 0.25:
            bar_color = Colors.YELLOW
            text_color = Colors.YELLOW
        else:
            # Red with pulse effect
            pulse = 0.7 + 0.3 * math.sin(self._pulse_timer * 8.0)
            bar_color = (int(255 * pulse), int(50 * pulse), int(50 * pulse))
            text_color = Colors.ERROR

        # Draw background bar
        bar_height = 12
        bar_y = self.y + 24
        bar_rect = pygame.Rect(self.x, bar_y, self.width, bar_height)
        pygame.draw.rect(surface, Colors.BG_DARKEST, bar_rect, border_radius=6)

        # Draw fill
        fill_width = int(self.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=6)

        # Draw border
        pygame.draw.rect(surface, Colors.BORDER, bar_rect, width=1, border_radius=6)

        # Draw time text
        time_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        time_surface = time_font.render(time_str, Typography.ANTIALIAS, text_color)
        time_x = self.x + (self.width - time_surface.get_width()) // 2
        surface.blit(time_surface, (time_x, self.y))

        # Draw "TIME" label if space permits
        if self.width > 100:
            label_font = fonts.get_font(Typography.SIZE_SMALL)
            label_surface = label_font.render("TIME", Typography.ANTIALIAS, Colors.TEXT_MUTED)
            label_x = self.x + 5
            surface.blit(label_surface, (label_x, self.y + 4))
