"""Victory scene with M&M-style layout.

Displayed on campaign completion with stats and rating.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    StatusPanel,
    Menu,
    MenuItem,
    get_fonts,
    draw_double_border_title,
)
from spellengine.adventures.models import DifficultyLevel

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


# Campaign-specific artifacts
CAMPAIGN_ARTIFACTS = {
    "dread_citadel": {
        "name": "Skeleton Key",
        "fragments": {
            DifficultyLevel.NORMAL: {
                "id": "skeleton_key_fragment_normal",
                "name": "Skeleton Key Fragment (Normal)",
                "description": "A shard of the shattered Skeleton Key. It pulses with faint power.",
            },
            DifficultyLevel.HEROIC: {
                "id": "skeleton_key_fragment_heroic",
                "name": "Skeleton Key Fragment (Heroic)",
                "description": "A glowing fragment of the Skeleton Key. Its power is unmistakable.",
            },
            DifficultyLevel.MYTHIC: {
                "id": "skeleton_key_fragment_mythic",
                "name": "Skeleton Key Fragment (Mythic)",
                "description": "A blazing shard of the Skeleton Key. It burns with ancient secrets.",
            },
        },
        "complete_artifact": {
            "id": "skeleton_key_restored",
            "name": "THE SKELETON KEY (RESTORED)",
            "description": "All three fragments united. The Skeleton Key is whole once more.",
        },
    },
}


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

        # Artifact state
        self._awarded_fragment: dict | None = None
        self._has_complete_artifact: bool = False
        self._owned_fragments: list[str] = []
        self._celebration_timer: float = 0.0
        self._show_key_celebration: bool = False

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

        # Finalize test session with stats
        state = self.client.adventure_state.state
        self.client.finalize_test_session({
            "total_xp": self.total_xp,
            "deaths": self.deaths,
            "clean_solves": state.clean_solves,
            "hints_used": state.hints_used,
            "result": "VICTORY",
        })

        # Play victory fanfare
        if self.client.audio:
            self.client.audio.play_sfx("victory_fanfare")

        # Load XP icon
        self._xp_icon = self.client.assets.get_ui_element(
            self.client.campaign.id, "icon_xp"
        )

        # Award campaign artifact fragment
        self._award_artifact_fragment()

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
                MenuItem("Credits", "R", self._on_credits),
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

    def _award_artifact_fragment(self) -> None:
        """Award the campaign artifact fragment for the completed difficulty."""
        campaign_id = self.client.campaign.id
        difficulty = self.client.adventure_state.difficulty
        state = self.client.adventure_state.state

        # Check if this campaign has artifacts
        artifact_config = CAMPAIGN_ARTIFACTS.get(campaign_id)
        if not artifact_config:
            return

        # Get the fragment for this difficulty
        fragments = artifact_config.get("fragments", {})
        fragment_info = fragments.get(difficulty)
        if not fragment_info:
            return

        fragment_id = fragment_info["id"]

        # Initialize artifacts dict for this campaign if needed
        if campaign_id not in state.artifacts:
            state.artifacts[campaign_id] = []

        # Award fragment if not already owned
        if fragment_id not in state.artifacts[campaign_id]:
            state.artifacts[campaign_id].append(fragment_id)
            self._awarded_fragment = fragment_info

            # Play artifact sound
            if self.client.audio:
                self.client.audio.play_sfx("artifact_acquired")

        # Track owned fragments
        self._owned_fragments = state.artifacts.get(campaign_id, [])

        # Check if all three fragments are now owned
        all_fragment_ids = [f["id"] for f in fragments.values()]
        if all(fid in self._owned_fragments for fid in all_fragment_ids):
            self._has_complete_artifact = True
            self._show_key_celebration = True

            # Add the complete artifact achievement
            complete_artifact = artifact_config.get("complete_artifact", {})
            if complete_artifact.get("id") and complete_artifact["id"] not in state.achievements:
                state.achievements.append(complete_artifact["id"])

            # Play special celebration sound
            if self.client.audio:
                self.client.audio.play_sfx("legendary_unlock")

        # Save the updated state
        self.client.adventure_state.save()

    def _get_fragment_display_info(self) -> list[tuple[str, bool, str]]:
        """Get display info for all fragments.

        Returns:
            List of (fragment_name, is_owned, difficulty_color) tuples
        """
        campaign_id = self.client.campaign.id
        artifact_config = CAMPAIGN_ARTIFACTS.get(campaign_id)
        if not artifact_config:
            return []

        fragments = artifact_config.get("fragments", {})
        result = []

        difficulty_colors = {
            DifficultyLevel.NORMAL: Colors.SUCCESS,
            DifficultyLevel.HEROIC: Colors.BLUE,
            DifficultyLevel.MYTHIC: Colors.PURPLE,
        }

        for diff in [DifficultyLevel.NORMAL, DifficultyLevel.HEROIC, DifficultyLevel.MYTHIC]:
            frag = fragments.get(diff)
            if frag:
                is_owned = frag["id"] in self._owned_fragments
                color = difficulty_colors.get(diff, Colors.TEXT_MUTED)
                result.append((diff.value.upper(), is_owned, color))

        return result

    def _draw_artifact_section(
        self,
        surface: "pygame.Surface",
        fonts: Any,
        content: "pygame.Rect",
    ) -> None:
        """Draw the artifact fragment section.

        Args:
            surface: Surface to draw on
            fonts: Font manager
            content: Content rect from main panel
        """
        import pygame
        import math

        campaign_id = self.client.campaign.id
        artifact_config = CAMPAIGN_ARTIFACTS.get(campaign_id)
        if not artifact_config:
            return

        # Position artifact display in the stats panel area (bottom section)
        if not self.stats_panel:
            return

        stats_content = self.stats_panel.content_rect
        artifact_y = stats_content.y + stats_content.height - 140

        # Draw artifact header
        header_font = fonts.get_font(Typography.SIZE_SMALL, bold=True)
        artifact_name = artifact_config.get("name", "Artifact")

        # Check if showing special celebration
        if self._show_key_celebration:
            self._draw_key_celebration(surface, fonts, content)
            return

        # Draw "SKELETON KEY FRAGMENTS" header
        header_text = f"{artifact_name.upper()} FRAGMENTS"
        header_surface = header_font.render(
            header_text, Typography.ANTIALIAS, Colors.TEXT_HEADER
        )
        header_x = stats_content.x + 10
        surface.blit(header_surface, (header_x, artifact_y))

        # Draw fragment slots
        fragment_info = self._get_fragment_display_info()
        slot_y = artifact_y + 25
        slot_font = fonts.get_font(Typography.SIZE_SMALL)

        for diff_name, is_owned, color in fragment_info:
            # Draw slot indicator
            if is_owned:
                # Filled slot with pulsing glow
                pulse = 0.7 + 0.3 * math.sin(self._celebration_timer * 3)
                glow_color = (
                    int(color[0] * pulse),
                    int(color[1] * pulse),
                    int(color[2] * pulse),
                )
                indicator = "◆"
                slot_surface = slot_font.render(
                    f"{indicator} {diff_name}", Typography.ANTIALIAS, glow_color
                )
            else:
                # Empty slot
                indicator = "◇"
                slot_surface = slot_font.render(
                    f"{indicator} {diff_name}", Typography.ANTIALIAS, Colors.TEXT_MUTED
                )

            surface.blit(slot_surface, (header_x + 10, slot_y))
            slot_y += slot_font.get_height() + 4

        # Draw awarded fragment notification if just earned
        if self._awarded_fragment:
            notif_y = slot_y + 10
            notif_font = fonts.get_font(Typography.SIZE_SMALL, bold=True)

            # Pulsing "FRAGMENT ACQUIRED" text
            pulse = 0.6 + 0.4 * math.sin(self._celebration_timer * 5)
            notif_color = (
                int(Colors.YELLOW[0] * pulse),
                int(Colors.YELLOW[1] * pulse),
                int(Colors.YELLOW[2] * pulse),
            )

            notif_text = "+ FRAGMENT ACQUIRED!"
            notif_surface = notif_font.render(
                notif_text, Typography.ANTIALIAS, notif_color
            )
            surface.blit(notif_surface, (header_x, notif_y))

    def _draw_key_celebration(
        self,
        surface: "pygame.Surface",
        fonts: Any,
        content: "pygame.Rect",
    ) -> None:
        """Draw the special Skeleton Key restoration celebration.

        Args:
            surface: Surface to draw on
            fonts: Font manager
            content: Content rect from main panel
        """
        import pygame
        import math

        screen_w, screen_h = self.client.screen_size
        center_x = screen_w // 2

        campaign_id = self.client.campaign.id
        artifact_config = CAMPAIGN_ARTIFACTS.get(campaign_id)
        if not artifact_config:
            return

        complete_artifact = artifact_config.get("complete_artifact", {})

        # Draw celebration overlay (semi-transparent darkening)
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        # Pulsing golden glow effect
        pulse = 0.5 + 0.5 * math.sin(self._celebration_timer * 2)
        glow_intensity = int(50 * pulse)

        # Draw golden border glow
        glow_rect = pygame.Rect(
            center_x - 250 - glow_intensity,
            200 - glow_intensity,
            500 + glow_intensity * 2,
            250 + glow_intensity * 2,
        )
        pygame.draw.rect(surface, Colors.YELLOW, glow_rect, 3)

        # Draw inner celebration box
        box_rect = pygame.Rect(center_x - 240, 210, 480, 230)
        pygame.draw.rect(surface, Colors.BG_DARK, box_rect)
        pygame.draw.rect(surface, Colors.YELLOW, box_rect, 2)

        # Draw "THE SKELETON KEY" title with shimmer
        title_font = fonts.get_font(Typography.SIZE_HEADER, bold=True)
        shimmer = 0.8 + 0.2 * math.sin(self._celebration_timer * 4)
        title_color = (
            int(255 * shimmer),
            int(215 * shimmer),
            int(0 * shimmer + 50),
        )
        title_text = complete_artifact.get("name", "ARTIFACT RESTORED")
        title_surface = title_font.render(
            title_text, Typography.ANTIALIAS, title_color
        )
        title_x = center_x - title_surface.get_width() // 2
        surface.blit(title_surface, (title_x, 230))

        # Draw decorative line
        line_y = 280
        pygame.draw.line(
            surface,
            Colors.YELLOW,
            (center_x - 180, line_y),
            (center_x + 180, line_y),
            2,
        )

        # Draw "RESTORED" subtitle
        subtitle_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        subtitle_surface = subtitle_font.render(
            "★ RESTORED ★", Typography.ANTIALIAS, Colors.SUCCESS
        )
        subtitle_x = center_x - subtitle_surface.get_width() // 2
        surface.blit(subtitle_surface, (subtitle_x, 295))

        # Draw description
        desc_font = fonts.get_font(Typography.SIZE_BODY)
        desc_text = complete_artifact.get(
            "description", "All fragments united."
        )
        # Word wrap if needed
        words = desc_text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if desc_font.size(test_line)[0] > 420:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(" ".join(current_line))

        desc_y = 335
        for line in lines[:3]:  # Max 3 lines
            desc_surface = desc_font.render(
                line, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
            )
            desc_x = center_x - desc_surface.get_width() // 2
            surface.blit(desc_surface, (desc_x, desc_y))
            desc_y += desc_font.get_height() + 2

        # Draw fragment completion indicators
        frag_y = 395
        frag_font = fonts.get_font(Typography.SIZE_SMALL)
        frag_text = "◆ NORMAL  ◆ HEROIC  ◆ MYTHIC"
        frag_surface = frag_font.render(
            frag_text, Typography.ANTIALIAS, Colors.YELLOW
        )
        frag_x = center_x - frag_surface.get_width() // 2
        surface.blit(frag_surface, (frag_x, frag_y))

    def _on_credits(self) -> None:
        """View credits roll."""
        self.change_scene("credits", from_victory=True)

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
        self._celebration_timer += dt

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

            # Draw rating title (chunky for retro feel)
            title_surface = fonts.get_header_font().render(
                title, Typography.ANTIALIAS_HEADERS, Colors.SUCCESS
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

        # Draw artifact fragment display
        self._draw_artifact_section(surface, fonts, content)
