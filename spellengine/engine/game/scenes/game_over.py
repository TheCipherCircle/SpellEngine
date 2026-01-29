"""Game over scene with M&M-style layout.

Displayed on player death with retry options.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    Menu,
    MenuItem,
    get_fonts,
    draw_double_border_title,
)

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


class GameOverScene(Scene):
    """Game over screen with retry options.

    Layout:
    +---------------------------------------------------+
    |                      DEFEATED                     |
    |            ═══════════════════════                |
    |                                                   |
    |           The Citadel claims another.             |
    |                                                   |
    |           Deaths: X    XP Lost: XXX               |
    |                                                   |
    +---------------------------------------------------+
    |         [R] Retry    [ESC] Abandon                |
    +---------------------------------------------------+
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the game over scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)
        self.message = ""
        self.deaths = 0
        self.options: list[str] = []

        # UI components
        self.main_panel: Panel | None = None
        self.menu: Menu | None = None

        # Assets
        self._failure_panel: "pygame.Surface | None" = None

    def enter(self, **kwargs: Any) -> None:
        """Enter the game over scene.

        Args:
            message: Death message
            options: List of retry option IDs
            deaths: Total death count
        """
        self.message = kwargs.get("message", "You have failed.")
        self.options = kwargs.get("options", ["start_over", "leave"])
        self.deaths = kwargs.get("deaths", 0)

        screen_w, screen_h = self.client.screen_size

        # Finalize test session with stats
        state = self.client.adventure_state.state
        self.client.finalize_test_session({
            "total_xp": state.xp_earned,
            "deaths": self.deaths,
            "clean_solves": state.clean_solves,
            "hints_used": state.hints_used,
            "result": "GAME_OVER",
        })

        # Play defeat sound
        if self.client.audio:
            self.client.audio.play_sfx("defeat_sting")

        # Load failure panel
        self._failure_panel = self.client.assets.get_ui_element(
            self.client.campaign.id, "panel_failure"
        )

        margin = LAYOUT["panel_margin"]

        # Create main panel (full screen with border)
        self.main_panel = Panel(
            margin,
            margin,
            screen_w - margin * 2,
            screen_h - margin * 2,
            major=True,
        )

        # Create menu with retry options
        self._create_menu()

    def _create_menu(self) -> None:
        """Create menu with retry options."""
        if not self.main_panel:
            return

        content = self.main_panel.content_rect

        option_labels = {
            "retry_checkpoint": ("Return to Checkpoint", "C"),
            "retry_fork": ("Return to Last Fork", "F"),
            "start_over": ("Restart Chapter", "R"),
            "leave": ("Abandon", "ESC"),
        }

        items = []
        for option in self.options:
            label, key = option_labels.get(option, (option, "?"))
            items.append(
                MenuItem(label, key, lambda opt=option: self._on_option_select(opt))
            )

        menu_y = content.y + content.height - 80
        self.menu = Menu(
            content.x,
            menu_y,
            content.width,
            items,
            centered=True,
        )

    def _on_option_select(self, option: str) -> None:
        """Handle option selection."""
        state = self.client.adventure_state

        if option == "retry_checkpoint":
            state.retry_from_checkpoint()
            state.save()
            self.change_scene("encounter")

        elif option == "retry_fork":
            state.retry_from_fork()
            state.save()
            self.change_scene("encounter")

        elif option == "start_over":
            state.start_over()
            state.save()
            self.change_scene("encounter")

        elif option == "leave":
            state.save()
            self.client.quit()

    def exit(self) -> None:
        """Exit the game over scene."""
        self.main_panel = None
        self.menu = None
        self._failure_panel = None

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        if self.menu:
            self.menu.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_option_select("leave")

    def update(self, dt: float) -> None:
        """Update scene."""
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the game over scene."""
        import pygame

        screen_w, screen_h = self.client.screen_size

        # Fill with darkest background
        surface.fill(Colors.BG_DARKEST)

        # Draw main panel
        if self.main_panel:
            self.main_panel.draw(surface)

        content = self.main_panel.content_rect if self.main_panel else pygame.Rect(
            20, 20, screen_w - 40, screen_h - 40
        )

        fonts = get_fonts()

        # Draw failure panel image at top if available
        panel_bottom = content.y + 20
        if self._failure_panel:
            panel_img = self._failure_panel
            panel_w, panel_h = panel_img.get_size()

            # Scale to reasonable size (max 150px width)
            max_panel_w = 150
            if panel_w > max_panel_w:
                scale = max_panel_w / panel_w
                new_w, new_h = int(panel_w * scale), int(panel_h * scale)
                panel_img = pygame.transform.scale(panel_img, (new_w, new_h))
                panel_w, panel_h = new_w, new_h

            # Center panel
            panel_x = content.x + (content.width - panel_w) // 2
            panel_y = content.y + 20
            panel_bottom = panel_y + panel_h + 20
            surface.blit(panel_img, (panel_x, panel_y))

        # Draw "DEFEATED" title with double-line borders
        title_y = panel_bottom + 10
        draw_double_border_title(
            surface,
            "DEFEATED",
            content.x + 100,
            title_y,
            content.width - 200,
        )

        # Draw death message
        message_font = fonts.get_body_font()
        message_surface = message_font.render(
            self.message, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
        )
        message_x = content.x + (content.width - message_surface.get_width()) // 2
        message_y = title_y + 110
        surface.blit(message_surface, (message_x, message_y))

        # Draw flavor text
        flavor_texts = [
            "The Citadel claims another.",
            "The shadows consume you.",
            "Your secrets die with you.",
            "The Circle will not remember you.",
        ]
        # Pick flavor based on deaths count
        flavor = flavor_texts[self.deaths % len(flavor_texts)]

        flavor_font = fonts.get_label_font()
        flavor_surface = flavor_font.render(
            flavor, Typography.ANTIALIAS, Colors.TEXT_MUTED
        )
        flavor_x = content.x + (content.width - flavor_surface.get_width()) // 2
        flavor_y = message_y + 40
        surface.blit(flavor_surface, (flavor_x, flavor_y))

        # Draw death count
        stats_y = flavor_y + 60
        stats_font = fonts.get_font(Typography.SIZE_SUBHEADER)

        death_text = f"Deaths: {self.deaths}"
        death_surface = stats_font.render(
            death_text, Typography.ANTIALIAS, Colors.ERROR
        )
        death_x = content.x + (content.width - death_surface.get_width()) // 2
        surface.blit(death_surface, (death_x, stats_y))

        # Draw menu
        if self.menu:
            self.menu.draw(surface)

        # Draw instruction at bottom
        inst_font = fonts.get_small_font()
        inst_text = "Select an option to continue"
        inst_surface = inst_font.render(
            inst_text, Typography.ANTIALIAS, Colors.TEXT_DIM
        )
        inst_x = content.x + (content.width - inst_surface.get_width()) // 2
        inst_y = content.y + content.height - 30
        surface.blit(inst_surface, (inst_x, inst_y))
