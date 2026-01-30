"""Visual Effects System for PatternForge.

WoW Blackrock Mountain-inspired visual effects for dramatic gameplay:
- Screen shake on boss encounters and failures
- Flash effects on success/failure
- CRT scanline overlay for terminal
- Text glow animations
- Particle systems (future)

These effects make the dungeon-crawling hash-cracking experience
feel epic and theatrical.
"""

import math
import random
from typing import TYPE_CHECKING

from spellengine.engine.game.ui.theme import Colors

if TYPE_CHECKING:
    import pygame


class ScreenEffect:
    """Base class for visual effects.

    Effects have a lifetime and can be composited over the game surface.
    """

    def __init__(self, duration: float = 0.5):
        """Initialize the effect.

        Args:
            duration: Effect duration in seconds (0 for infinite)
        """
        self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float) -> None:
        """Update the effect state.

        Args:
            dt: Delta time in seconds
        """
        self.elapsed += dt
        if self.duration > 0 and self.elapsed >= self.duration:
            self.active = False

    @property
    def progress(self) -> float:
        """Get effect progress from 0.0 to 1.0."""
        if self.duration <= 0:
            return 0.0
        return min(1.0, self.elapsed / self.duration)

    def apply(self, surface: "pygame.Surface") -> "pygame.Surface":
        """Apply the effect to a surface.

        Args:
            surface: Surface to apply effect to

        Returns:
            Modified surface (may be same surface or new one)
        """
        return surface

    def get_offset(self) -> tuple[int, int]:
        """Get the screen offset for shake effects.

        Returns:
            (x_offset, y_offset) tuple
        """
        return (0, 0)


class ShakeEffect(ScreenEffect):
    """Screen shake effect for dramatic moments.

    Used for:
    - Boss encounter entry
    - Failed crack attempts
    - Critical events
    """

    def __init__(
        self,
        intensity: float = 10.0,
        duration: float = 0.3,
        decay: bool = True,
    ):
        """Initialize shake effect.

        Args:
            intensity: Maximum shake offset in pixels
            duration: Shake duration in seconds
            decay: Whether shake should decay over time
        """
        super().__init__(duration)
        self.intensity = intensity
        self.decay = decay
        self._offset_x = 0.0
        self._offset_y = 0.0

    def update(self, dt: float) -> None:
        """Update shake offset."""
        super().update(dt)

        if not self.active:
            self._offset_x = 0.0
            self._offset_y = 0.0
            return

        # Calculate current intensity (with optional decay)
        current_intensity = self.intensity
        if self.decay:
            current_intensity *= 1.0 - self.progress

        # Random shake offset
        self._offset_x = random.uniform(-current_intensity, current_intensity)
        self._offset_y = random.uniform(-current_intensity, current_intensity)

    def get_offset(self) -> tuple[int, int]:
        """Get current shake offset."""
        return (int(self._offset_x), int(self._offset_y))


class FlashEffect(ScreenEffect):
    """Screen flash effect for success/failure feedback.

    Creates a brief color overlay that fades out.
    """

    def __init__(
        self,
        color: tuple[int, int, int] = (255, 255, 255),
        intensity: float = 0.5,
        duration: float = 0.2,
    ):
        """Initialize flash effect.

        Args:
            color: Flash color (RGB)
            intensity: Maximum opacity (0.0 to 1.0)
            duration: Flash duration in seconds
        """
        super().__init__(duration)
        self.color = color
        self.intensity = intensity
        self._overlay: "pygame.Surface | None" = None

    def apply(self, surface: "pygame.Surface") -> "pygame.Surface":
        """Apply flash overlay to surface."""
        import pygame

        if not self.active:
            return surface

        # Create overlay if needed
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Calculate current alpha (fade out)
        alpha = int(255 * self.intensity * (1.0 - self.progress))

        # Fill overlay with flash color
        self._overlay.fill((*self.color, alpha))

        # Blit overlay onto surface
        surface.blit(self._overlay, (0, 0))

        return surface


class SuccessFlash(FlashEffect):
    """Green flash for successful actions."""

    def __init__(self, intensity: float = 0.3, duration: float = 0.15):
        super().__init__(
            color=Colors.SUCCESS,
            intensity=intensity,
            duration=duration,
        )


class FailureFlash(FlashEffect):
    """Red flash for failed actions."""

    def __init__(self, intensity: float = 0.4, duration: float = 0.2):
        super().__init__(
            color=Colors.ERROR,
            intensity=intensity,
            duration=duration,
        )


class ScanlineOverlay(ScreenEffect):
    """CRT scanline effect for terminal/retro feel.

    Adds horizontal scanlines that subtly animate for
    authentic CRT monitor appearance.
    """

    def __init__(
        self,
        line_spacing: int = 3,
        line_alpha: int = 30,
        animate: bool = True,
    ):
        """Initialize scanline effect.

        Args:
            line_spacing: Pixels between scanlines
            line_alpha: Opacity of scanlines (0-255)
            animate: Whether scanlines should animate
        """
        super().__init__(duration=0)  # Infinite
        self.line_spacing = line_spacing
        self.line_alpha = line_alpha
        self.animate = animate
        self._overlay: "pygame.Surface | None" = None
        self._offset = 0.0

    def update(self, dt: float) -> None:
        """Update scanline animation."""
        super().update(dt)
        if self.animate:
            self._offset += dt * 30  # Scroll speed
            if self._offset >= self.line_spacing:
                self._offset = 0.0

    def apply(self, surface: "pygame.Surface") -> "pygame.Surface":
        """Apply scanline overlay."""
        import pygame

        if not self.active:
            return surface

        width, height = surface.get_size()

        # Create or resize overlay
        if self._overlay is None or self._overlay.get_size() != (width, height):
            self._overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        # Clear overlay
        self._overlay.fill((0, 0, 0, 0))

        # Draw scanlines
        y = int(self._offset)
        while y < height:
            pygame.draw.line(
                self._overlay,
                (0, 0, 0, self.line_alpha),
                (0, y),
                (width, y),
            )
            y += self.line_spacing

        # Apply overlay
        surface.blit(self._overlay, (0, 0))

        return surface


class TextGlowEffect(ScreenEffect):
    """Glowing text animation for emphasis.

    Creates a pulsing glow around text for successful cracks,
    achievements, or important messages.
    """

    def __init__(
        self,
        color: tuple[int, int, int] = Colors.SUCCESS,
        pulse_speed: float = 3.0,
        duration: float = 2.0,
    ):
        """Initialize text glow effect.

        Args:
            color: Glow color (RGB)
            pulse_speed: Pulses per second
            duration: Total glow duration
        """
        super().__init__(duration)
        self.color = color
        self.pulse_speed = pulse_speed

    def get_glow_intensity(self) -> float:
        """Get current glow intensity (0.0 to 1.0).

        Returns:
            Current intensity based on pulse animation
        """
        if not self.active:
            return 0.0

        # Sinusoidal pulse
        pulse = 0.5 + 0.5 * math.sin(self.elapsed * self.pulse_speed * 2 * math.pi)

        # Fade out over duration
        fade = 1.0 - self.progress

        return pulse * fade

    def render_glowing_text(
        self,
        text: str,
        font: "pygame.font.Font",
        base_color: tuple[int, int, int],
        surface: "pygame.Surface",
        pos: tuple[int, int],
    ) -> None:
        """Render text with glow effect.

        Args:
            text: Text to render
            font: Font to use
            base_color: Base text color
            surface: Surface to render on
            pos: Position (x, y) to render at
        """
        import pygame

        intensity = self.get_glow_intensity()

        if intensity > 0.1:
            # Render glow layers (blur simulation)
            glow_color = tuple(
                int(c * intensity) for c in self.color
            )

            for offset in [(0, -2), (0, 2), (-2, 0), (2, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                glow_surface = font.render(text, True, glow_color)
                glow_surface.set_alpha(int(100 * intensity))
                surface.blit(glow_surface, (pos[0] + offset[0], pos[1] + offset[1]))

        # Render base text on top
        text_surface = font.render(text, True, base_color)
        surface.blit(text_surface, pos)


class VignetteEffect(ScreenEffect):
    """Darkened screen edges for cinematic feel.

    Creates the classic "movie theater" look with darker corners,
    focusing attention on the center of the screen.
    """

    def __init__(self, intensity: float = 0.3):
        """Initialize vignette effect.

        Args:
            intensity: Darkness intensity (0.0 to 1.0)
        """
        super().__init__(duration=0)  # Infinite
        self.intensity = intensity
        self._overlay: "pygame.Surface | None" = None

    def apply(self, surface: "pygame.Surface") -> "pygame.Surface":
        """Apply vignette overlay."""
        import pygame

        width, height = surface.get_size()

        # Create or resize overlay
        if self._overlay is None or self._overlay.get_size() != (width, height):
            self._overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            self._create_vignette(width, height)

        surface.blit(self._overlay, (0, 0))
        return surface

    def _create_vignette(self, width: int, height: int) -> None:
        """Create the vignette gradient overlay."""
        import pygame

        self._overlay.fill((0, 0, 0, 0))

        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        # Draw radial gradient (simplified for performance)
        for ring in range(0, int(max_dist), 10):
            # Calculate alpha based on distance from center
            dist_ratio = ring / max_dist
            alpha = int(255 * self.intensity * dist_ratio**2)

            if alpha > 0:
                pygame.draw.circle(
                    self._overlay,
                    (0, 0, 0, min(alpha, 255)),
                    (center_x, center_y),
                    int(max_dist - ring),
                    10,
                )


class EffectManager:
    """Manages active visual effects and composites them.

    Handles multiple simultaneous effects and applies them
    in the correct order to the game surface.
    """

    def __init__(self):
        """Initialize the effect manager."""
        self._effects: list[ScreenEffect] = []
        self._persistent_effects: list[ScreenEffect] = []  # Always-on effects like vignette

    def add_effect(self, effect: ScreenEffect) -> None:
        """Add a temporary effect.

        Args:
            effect: Effect to add
        """
        self._effects.append(effect)

    def add_persistent_effect(self, effect: ScreenEffect) -> None:
        """Add a persistent effect (like vignette or scanlines).

        Args:
            effect: Effect to add
        """
        self._persistent_effects.append(effect)

    def shake(self, intensity: float = 10.0, duration: float = 0.3) -> None:
        """Trigger a screen shake.

        Args:
            intensity: Shake intensity in pixels
            duration: Shake duration in seconds
        """
        self.add_effect(ShakeEffect(intensity, duration))

    def flash_success(self) -> None:
        """Trigger a success flash."""
        self.add_effect(SuccessFlash())

    def flash_failure(self) -> None:
        """Trigger a failure flash."""
        self.add_effect(FailureFlash())

    def flash(self, color: tuple[int, int, int], intensity: float = 0.3) -> None:
        """Trigger a custom flash.

        Args:
            color: Flash color
            intensity: Flash intensity
        """
        self.add_effect(FlashEffect(color, intensity))

    def update(self, dt: float) -> None:
        """Update all effects.

        Args:
            dt: Delta time in seconds
        """
        # Update temporary effects
        for effect in self._effects:
            effect.update(dt)

        # Remove finished effects
        self._effects = [e for e in self._effects if e.active]

        # Update persistent effects
        for effect in self._persistent_effects:
            effect.update(dt)

    def apply(self, surface: "pygame.Surface") -> "pygame.Surface":
        """Apply all effects to a surface.

        Args:
            surface: Surface to modify

        Returns:
            Modified surface
        """
        # Apply persistent effects first
        for effect in self._persistent_effects:
            surface = effect.apply(surface)

        # Apply temporary effects
        for effect in self._effects:
            surface = effect.apply(surface)

        return surface

    def get_offset(self) -> tuple[int, int]:
        """Get combined screen offset from all shake effects.

        Returns:
            (x_offset, y_offset) tuple
        """
        total_x, total_y = 0, 0
        for effect in self._effects:
            ox, oy = effect.get_offset()
            total_x += ox
            total_y += oy
        return (total_x, total_y)

    def clear(self) -> None:
        """Clear all temporary effects."""
        self._effects.clear()

    def clear_all(self) -> None:
        """Clear all effects including persistent ones."""
        self._effects.clear()
        self._persistent_effects.clear()
