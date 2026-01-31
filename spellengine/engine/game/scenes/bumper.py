"""Studio bumper scene - displays Cipher Circle production logo at startup.

Shows a professional studio splash before the title screen.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    Typography,
    get_fonts,
)

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


# ASCII art logo for Cipher Circle
CIPHER_CIRCLE_LOGO = [
    "     ╔═══════════════════════════════════╗",
    "     ║                                   ║",
    "     ║       ◈  CIPHER CIRCLE  ◈        ║",
    "     ║                                   ║",
    "     ╚═══════════════════════════════════╝",
]

PRODUCTION_TEXT = "A CIPHER CIRCLE PRODUCTION"


class BumperScene(Scene):
    """Studio bumper splash screen.

    Flow:
    - Fade in (0.5s)
    - Hold (2.0s)
    - Fade out (0.5s)
    - Auto-advance to title scene

    Can be skipped with any key press.
    """

    # Timing constants
    FADE_IN_DURATION = 0.5
    HOLD_DURATION = 2.0
    FADE_OUT_DURATION = 0.5

    def __init__(self, client: "GameClient") -> None:
        """Initialize the bumper scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)

        # Animation state
        self._timer: float = 0.0
        self._alpha: float = 0.0
        self._phase: str = "fade_in"  # fade_in, hold, fade_out, done
        self._skipped: bool = False

    def enter(self, **kwargs: Any) -> None:
        """Enter the bumper scene."""
        self._timer = 0.0
        self._alpha = 0.0
        self._phase = "fade_in"
        self._skipped = False

    def exit(self) -> None:
        """Exit the bumper scene."""
        pass

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events - any key skips the bumper."""
        import pygame

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self._skip_to_title()

    def _skip_to_title(self) -> None:
        """Skip directly to title scene."""
        if not self._skipped:
            self._skipped = True
            self.change_scene("title", campaign=self.client.campaign, has_save=self.client.has_save())

    def update(self, dt: float) -> None:
        """Update animation state."""
        if self._skipped:
            return

        self._timer += dt

        if self._phase == "fade_in":
            # Fade in over FADE_IN_DURATION seconds
            progress = min(1.0, self._timer / self.FADE_IN_DURATION)
            self._alpha = progress * 255

            if self._timer >= self.FADE_IN_DURATION:
                self._timer = 0.0
                self._phase = "hold"
                self._alpha = 255

        elif self._phase == "hold":
            # Hold at full opacity
            self._alpha = 255

            if self._timer >= self.HOLD_DURATION:
                self._timer = 0.0
                self._phase = "fade_out"

        elif self._phase == "fade_out":
            # Fade out over FADE_OUT_DURATION seconds
            progress = min(1.0, self._timer / self.FADE_OUT_DURATION)
            self._alpha = (1.0 - progress) * 255

            if self._timer >= self.FADE_OUT_DURATION:
                self._phase = "done"
                self._skip_to_title()

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the bumper screen."""
        import pygame

        screen_w, screen_h = self.client.screen_size

        # Fill with darkest background
        surface.fill(Colors.BG_DARKEST)

        # Create a surface for the logo content with alpha
        content_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

        fonts = get_fonts()

        # Draw ASCII logo centered
        logo_font = fonts.get_font(Typography.SIZE_BODY)
        logo_height = len(CIPHER_CIRCLE_LOGO) * logo_font.get_height()
        logo_start_y = screen_h // 2 - logo_height // 2 - 30

        for i, line in enumerate(CIPHER_CIRCLE_LOGO):
            text_surface = logo_font.render(
                line, Typography.ANTIALIAS, Colors.TEXT_HEADER
            )
            text_x = screen_w // 2 - text_surface.get_width() // 2
            text_y = logo_start_y + i * logo_font.get_height()
            content_surface.blit(text_surface, (text_x, text_y))

        # Draw production text below logo
        production_font = fonts.get_font(Typography.SIZE_SMALL)
        production_surface = production_font.render(
            PRODUCTION_TEXT, Typography.ANTIALIAS, Colors.TEXT_MUTED
        )
        production_x = screen_w // 2 - production_surface.get_width() // 2
        production_y = logo_start_y + logo_height + 40
        content_surface.blit(production_surface, (production_x, production_y))

        # Apply alpha to the content surface
        content_surface.set_alpha(int(self._alpha))

        # Blit content to main surface
        surface.blit(content_surface, (0, 0))
