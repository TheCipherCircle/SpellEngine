"""Settings Scene - Audio and visual preferences.

Allows players to adjust volume, toggle effects, and configure
accessibility options. Settings persist across sessions.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    get_fonts,
)
from spellengine.engine.game.ui.widgets import Slider, Toggle
from spellengine.engine.settings import get_settings, update_settings

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


class SettingsScene(Scene):
    """Settings menu for audio and visual preferences.

    Layout:
    +------------------------------------------+
    |              SETTINGS                     |
    +------------------------------------------+
    |  SFX Volume      [=========>    ] 70%    |
    |  Music Volume    [=====>        ] 50%    |
    |  Ambiance        [====>         ] 40%    |
    |                                          |
    |  Screen Shake    [ON ]                   |
    |  Flash Effects   [ON ]                   |
    |  CRT Scanlines   [OFF]                   |
    |                                          |
    |  Reduce Motion   [OFF]                   |
    |                                          |
    |           [BACK]                         |
    +------------------------------------------+
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize settings scene."""
        super().__init__(client)

        self.panel: Panel | None = None
        self.sliders: list[Slider] = []
        self.toggles: list[Toggle] = []

        # Track where to return
        self._return_scene: str = "title"

    def enter(self, **kwargs: Any) -> None:
        """Enter settings scene."""
        import pygame

        self._return_scene = kwargs.get("return_to", "title")

        screen_w, screen_h = self.client.screen_size
        settings = get_settings()

        # Create main panel (centered, takes most of screen)
        panel_width = min(500, screen_w - 100)
        panel_height = min(450, screen_h - 100)
        panel_x = (screen_w - panel_width) // 2
        panel_y = (screen_h - panel_height) // 2

        self.panel = Panel(
            panel_x, panel_y, panel_width, panel_height,
            title="SETTINGS",
            major=True,
        )

        content = self.panel.content_rect
        widget_width = content.width - 40
        x = content.x + 20
        y = content.y + 20

        self.sliders = []
        self.toggles = []

        # Audio section header
        # (we'll draw this in the render method)
        y += 25

        # SFX Volume
        sfx_slider = Slider(
            x, y, widget_width, "SFX Volume",
            value=settings.sfx_volume,
            on_change=lambda v: self._on_setting_change("sfx_volume", v),
        )
        self.sliders.append(sfx_slider)
        y += 40

        # Music Volume
        music_slider = Slider(
            x, y, widget_width, "Music Volume",
            value=settings.music_volume,
            on_change=lambda v: self._on_setting_change("music_volume", v),
        )
        self.sliders.append(music_slider)
        y += 40

        # Ambiance Volume
        ambiance_slider = Slider(
            x, y, widget_width, "Ambiance",
            value=settings.ambiance_volume,
            on_change=lambda v: self._on_setting_change("ambiance_volume", v),
        )
        self.sliders.append(ambiance_slider)
        y += 50

        # Visual section header
        y += 10

        # Screen Shake
        shake_toggle = Toggle(
            x, y, widget_width, "Screen Shake",
            value=settings.screen_shake,
            on_change=lambda v: self._on_setting_change("screen_shake", v),
        )
        self.toggles.append(shake_toggle)
        y += 35

        # Flash Effects
        flash_toggle = Toggle(
            x, y, widget_width, "Flash Effects",
            value=settings.flash_effects,
            on_change=lambda v: self._on_setting_change("flash_effects", v),
        )
        self.toggles.append(flash_toggle)
        y += 35

        # CRT Scanlines
        crt_toggle = Toggle(
            x, y, widget_width, "CRT Scanlines",
            value=settings.crt_scanlines,
            on_change=lambda v: self._on_setting_change("crt_scanlines", v),
        )
        self.toggles.append(crt_toggle)
        y += 50

        # Accessibility section
        y += 10

        # Reduce Motion
        motion_toggle = Toggle(
            x, y, widget_width, "Reduce Motion",
            value=settings.reduce_motion,
            on_change=lambda v: self._on_setting_change("reduce_motion", v),
        )
        self.toggles.append(motion_toggle)

    def _on_setting_change(self, key: str, value: Any) -> None:
        """Handle setting change - update and save."""
        update_settings(**{key: value})

        # Apply changes immediately where possible
        if key in ("sfx_volume", "music_volume", "ambiance_volume"):
            if self.client.audio:
                settings = get_settings()
                self.client.audio.set_volume(
                    sfx=settings.sfx_volume,
                    music=settings.music_volume,
                )

    def exit(self) -> None:
        """Exit settings scene."""
        self.panel = None
        self.sliders = []
        self.toggles = []

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        # Handle widget events
        for slider in self.sliders:
            if slider.handle_event(event):
                return

        for toggle in self.toggles:
            if toggle.handle_event(event):
                return

        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self._go_back()

    def _go_back(self) -> None:
        """Return to previous scene."""
        if self._return_scene == "title":
            self.change_scene("title", campaign=self.client.campaign, has_save=self.client.has_save())
        else:
            self.change_scene(self._return_scene)

    def update(self, dt: float) -> None:
        """Update settings scene."""
        pass  # No animations needed

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw settings scene."""
        import pygame

        # Background
        surface.fill(Colors.BG_DARKEST)

        # Panel
        if self.panel:
            self.panel.draw(surface)

            content = self.panel.content_rect
            fonts = get_fonts()
            section_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)

            # Section headers
            x = content.x + 20

            # Audio header
            audio_y = content.y + 5
            audio_surface = section_font.render("AUDIO", Typography.ANTIALIAS, Colors.TEXT_MUTED)
            surface.blit(audio_surface, (x, audio_y))

            # Draw separator line
            line_y = audio_y + section_font.get_height() + 2
            pygame.draw.line(surface, Colors.BORDER, (x, line_y), (content.x + content.width - 20, line_y))

            # Visual header (after sliders)
            visual_y = content.y + 170
            visual_surface = section_font.render("VISUAL", Typography.ANTIALIAS, Colors.TEXT_MUTED)
            surface.blit(visual_surface, (x, visual_y))
            line_y = visual_y + section_font.get_height() + 2
            pygame.draw.line(surface, Colors.BORDER, (x, line_y), (content.x + content.width - 20, line_y))

            # Accessibility header
            access_y = content.y + 305
            access_surface = section_font.render("ACCESSIBILITY", Typography.ANTIALIAS, Colors.TEXT_MUTED)
            surface.blit(access_surface, (x, access_y))
            line_y = access_y + section_font.get_height() + 2
            pygame.draw.line(surface, Colors.BORDER, (x, line_y), (content.x + content.width - 20, line_y))

        # Sliders
        for slider in self.sliders:
            slider.render(surface)

        # Toggles
        for toggle in self.toggles:
            toggle.render(surface)

        # Back hint at bottom
        if self.panel:
            fonts = get_fonts()
            hint_font = fonts.get_small_font()
            hint_surface = hint_font.render("[ESC] Back", Typography.ANTIALIAS, Colors.TEXT_DIM)
            hint_x = self.panel.rect.x + (self.panel.rect.width - hint_surface.get_width()) // 2
            hint_y = self.panel.rect.y + self.panel.rect.height - 25
            surface.blit(hint_surface, (hint_x, hint_y))
