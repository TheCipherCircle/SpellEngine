"""Victory scene with M&M-style layout.

Displayed on campaign completion with stats and rating.
"""

from typing import TYPE_CHECKING, Any

from storysmith.engine.game.scenes.base import Scene
from storysmith.engine.game.ui import (
    Colors,
    LAYOUT,
    Typography,
    Panel,
    StatusPanel,
    Menu,
    MenuItem,
    get_fonts,
    draw_double_border_title,
)

if TYPE_CHECKING:
    import pygame
    from storysmith.engine.game.client import GameClient


class VictoryScene(Scene):
    """Victory screen with stats and rating.

    Layout:
    +---------------------------------------------------+
    |                     VICTORY                       |
    |            ═══════════════════════                |
    +-------------------------+-------------------------+
    |   FINAL STATS           |   RATING                |
    |   ══════════════        |   ══════                |
    |   XP: 2,450             |   ****_                 |
    |   Clean: 24/31          |   VICTORIOUS            |
    |   Hints: 7              |                         |
    |   Deaths: 2             |   "Well fought..."      |
    +-------------------------+-------------------------+
    |       [C] Chronicle    [ESC] Exit                 |
    +---------------------------------------------------+
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the victory scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)
        self.total_xp = 0
        self.deaths = 0
        self.achievements: list[str] = []

        # UI components
        self.main_panel: Panel | None = None
        self.stats_panel: StatusPanel | None = None
        self.rating_panel: Panel | None = None
        self.menu: Menu | None = None

        # Assets
        self._xp_icon: "pygame.Surface | None" = None

    def enter(self, **kwargs: Any) -> None:
        """Enter the victory scene.

        Args:
            total_xp: Total XP earned
            deaths: Total death count
        """
        self.total_xp = kwargs.get("total_xp", 0)
        self.deaths = kwargs.get("deaths", 0)
        self.achievements = self.client.adventure_state.state.achievements.copy()

        screen_w, screen_h = self.client.screen_size

        # Play victory fanfare
        if self.client.audio:
            self.client.audio.play_sfx("victory_fanfare")

        # Load XP icon
        self._xp_icon = self.client.assets.get_ui_element(
            self.client.campaign.id, "icon_xp"
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

        # Calculate layout for inner panels
        content = self.main_panel.content_rect
        inner_top = content.y + 120  # Space for title
        panel_height = content.height - 180  # Space for title and menu
        panel_width = (content.width - margin) // 2

        # Create stats panel (left side)
        self.stats_panel = StatusPanel(
            content.x,
            inner_top,
            panel_width,
            panel_height,
            title="FINAL STATS",
        )
        self._populate_stats()

        # Create rating panel (right side)
        self.rating_panel = Panel(
            content.x + panel_width + margin,
            inner_top,
            panel_width,
            panel_height,
            title="RATING",
            major=True,
        )

        # Create menu at bottom
        menu_y = content.y + content.height - 50
        self.menu = Menu(
            content.x,
            menu_y,
            content.width,
            [
                MenuItem("Chronicle", "C", self._on_chronicle, enabled=False),
                MenuItem("Exit", "ESC", self._on_quit),
            ],
            centered=True,
        )

        # Clean up save file on victory
        if (
            self.client.adventure_state.save_path
            and self.client.adventure_state.save_path.exists()
        ):
            self.client.adventure_state.save_path.unlink()

    def _populate_stats(self) -> None:
        """Populate the stats panel with final stats."""
        if not self.stats_panel:
            return

        self.stats_panel.clear_stats()

        state = self.client.adventure_state.state

        # XP
        self.stats_panel.add_stat("Total XP", f"{self.total_xp:,}", Colors.YELLOW)

        # Separator
        self.stats_panel.add_stat("", "")

        # Clean solves
        total_encounters = sum(
            len(ch.encounters) for ch in self.client.campaign.chapters
        )
        clean = state.clean_solves
        self.stats_panel.add_stat(
            "Clean Solves",
            f"{clean}/{total_encounters}",
            Colors.SUCCESS if clean == total_encounters else Colors.TEXT_PRIMARY,
        )

        # Hints used
        self.stats_panel.add_stat("Hints Used", str(state.hints_used), Colors.BLUE)

        # Deaths
        color = Colors.ERROR if self.deaths > 0 else Colors.SUCCESS
        self.stats_panel.add_stat("Deaths", str(self.deaths), color)

        # Separator
        self.stats_panel.add_stat("", "")

        # Achievements
        if self.achievements:
            self.stats_panel.add_stat(
                "Achievements",
                str(len(self.achievements)),
                Colors.TEXT_HEADER,
            )

    def _calculate_rating(self) -> tuple[int, str]:
        """Calculate the rating based on performance.

        Returns:
            Tuple of (stars, title)
        """
        state = self.client.adventure_state.state
        total_encounters = sum(
            len(ch.encounters) for ch in self.client.campaign.chapters
        )

        # Base score
        score = 0

        # XP bonus (up to 2 stars)
        max_xp = sum(
            sum(e.xp_reward for e in ch.encounters)
            for ch in self.client.campaign.chapters
        )
        xp_ratio = self.total_xp / max_xp if max_xp > 0 else 0
        score += int(xp_ratio * 2)

        # Clean solve bonus (up to 2 stars)
        clean_ratio = state.clean_solves / total_encounters if total_encounters > 0 else 0
        score += int(clean_ratio * 2)

        # Deductions
        score -= min(2, self.deaths)  # Up to -2 for deaths
        score -= min(1, state.hints_used // 5)  # -1 for every 5 hints

        # Clamp to 0-5
        stars = max(0, min(5, score + 2))  # Base of 2 stars for completion

        # Title based on stars
        titles = {
            5: "LEGENDARY",
            4: "VICTORIOUS",
            3: "TRIUMPHANT",
            2: "SURVIVOR",
            1: "ESCAPEE",
            0: "BATTERED",
        }

        return stars, titles.get(stars, "COMPLETE")

    def _on_chronicle(self) -> None:
        """Handle chronicle button click."""
        # Not implemented yet
        pass

    def _on_quit(self) -> None:
        """Handle quit button click."""
        self.client.quit()

    def exit(self) -> None:
        """Exit the victory scene."""
        self.main_panel = None
        self.stats_panel = None
        self.rating_panel = None
        self.menu = None
        self._xp_icon = None

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        if self.menu:
            self.menu.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self._on_quit()

    def update(self, dt: float) -> None:
        """Update scene."""
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the victory scene."""
        import pygame

        screen_w, screen_h = self.client.screen_size
        campaign = self.client.campaign

        # Fill with darkest background
        surface.fill(Colors.BG_DARKEST)

        # Draw main panel
        if self.main_panel:
            self.main_panel.draw(surface)

        content = self.main_panel.content_rect if self.main_panel else pygame.Rect(
            20, 20, screen_w - 40, screen_h - 40
        )

        fonts = get_fonts()

        # Draw "VICTORY" title with double-line borders
        title_y = content.y + 10
        draw_double_border_title(
            surface,
            "VICTORY",
            content.x + 100,
            title_y,
            content.width - 200,
        )

        # Draw campaign completion text
        campaign_font = fonts.get_body_font()
        campaign_text = f"{campaign.title} - COMPLETE"
        campaign_surface = campaign_font.render(
            campaign_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
        )
        campaign_x = content.x + (content.width - campaign_surface.get_width()) // 2
        surface.blit(campaign_surface, (campaign_x, title_y + 90))

        # Draw stats panel
        if self.stats_panel:
            self.stats_panel.draw(surface)

        # Draw rating panel
        if self.rating_panel:
            self.rating_panel.draw(surface)

            # Draw rating content
            rating_content = self.rating_panel.content_rect
            stars, title = self._calculate_rating()

            # Draw stars
            star_font = fonts.get_title_font()
            star_str = "*" * stars + "_" * (5 - stars)
            star_surface = star_font.render(
                star_str, Typography.ANTIALIAS, Colors.YELLOW
            )
            star_x = rating_content.x + (rating_content.width - star_surface.get_width()) // 2
            star_y = rating_content.y + 20
            surface.blit(star_surface, (star_x, star_y))

            # Draw rating title
            title_surface = fonts.get_header_font().render(
                title, Typography.ANTIALIAS, Colors.SUCCESS
            )
            title_x = rating_content.x + (rating_content.width - title_surface.get_width()) // 2
            surface.blit(title_surface, (title_x, star_y + star_font.get_height() + 10))

            # Draw flavor text
            flavor_texts = {
                5: '"The Citadel trembles before you."',
                4: '"Well fought, Infiltrator."',
                3: '"A worthy challenger."',
                2: '"You survived. Barely."',
                1: '"The shadows remember your passage."',
                0: '"Return when you are ready."',
            }
            flavor = flavor_texts.get(stars, '"The end is only the beginning."')

            flavor_font = fonts.get_label_font()
            flavor_surface = flavor_font.render(
                flavor, Typography.ANTIALIAS, Colors.TEXT_MUTED
            )
            flavor_x = rating_content.x + (rating_content.width - flavor_surface.get_width()) // 2
            flavor_y = rating_content.y + rating_content.height - 60
            surface.blit(flavor_surface, (flavor_x, flavor_y))

        # Draw achievements if any
        if self.achievements and self.rating_panel:
            achieve_y = self.rating_panel.content_rect.y + 120
            achieve_font = fonts.get_small_font()

            for achievement in self.achievements[:4]:  # Max 4 displayed
                display_name = achievement.replace("_", " ").upper()
                achieve_text = f"* {display_name}"
                achieve_surface = achieve_font.render(
                    achieve_text, Typography.ANTIALIAS, Colors.TEXT_HEADER
                )
                achieve_x = self.rating_panel.content_rect.x + 10
                surface.blit(achieve_surface, (achieve_x, achieve_y))
                achieve_y += achieve_font.get_height() + 4

        # Draw menu
        if self.menu:
            self.menu.draw(surface)

        # Draw outro text if available
        if campaign.outro_text:
            outro_font = fonts.get_label_font()
            outro_y = content.y + content.height - 80

            for line in campaign.outro_text.split("\n")[:2]:
                outro_surface = outro_font.render(
                    line, Typography.ANTIALIAS, Colors.TEXT_MUTED
                )
                outro_x = content.x + (content.width - outro_surface.get_width()) // 2
                surface.blit(outro_surface, (outro_x, outro_y))
                outro_y += outro_font.get_height() + 4
