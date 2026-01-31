"""Chapter Complete Scene - Celebration screen between chapters.

Shows chapter completion with:
- Chapter title + completion message
- XP BONUS display
- ACHIEVEMENT UNLOCKED notification (if any)
- NEW ABILITY announcement (if any)
- Null Cipher narrative quote
- Continue prompt

Gruvbox-styled with celebratory aesthetics.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import Colors, SPACING, Typography, get_fonts

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


class ChapterCompleteScene(Scene):
    """Celebration screen between chapters.

    Displays chapter completion stats and narrative before continuing.
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the chapter complete scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)

        # Chapter info
        self.chapter_title = ""
        self.chapter_number = 1
        self.total_chapters = 6
        self.xp_bonus = 0
        self.achievement = ""
        self.new_ability = ""
        self.narrative_quote = ""

        # Animation state
        self._timer = 0.0
        self._phase = 0  # 0=fade_in, 1=title, 2=stats, 3=narrative, 4=waiting
        self._pulse_timer = 0.0

    def enter(self, **kwargs: Any) -> None:
        """Enter the chapter complete scene.

        Kwargs:
            chapter_title: Title of completed chapter
            chapter_number: Chapter index (1-based)
            total_chapters: Total number of chapters
            xp_bonus: Bonus XP for chapter completion
            achievement: Achievement unlocked (if any)
            new_ability: New ability unlocked (if any)
            narrative_quote: Quote from the Null Cipher
        """
        self.chapter_title = kwargs.get("chapter_title", "Chapter Complete")
        self.chapter_number = kwargs.get("chapter_number", 1)
        self.total_chapters = kwargs.get("total_chapters", 6)
        self.xp_bonus = kwargs.get("xp_bonus", 100)
        self.achievement = kwargs.get("achievement", "")
        self.new_ability = kwargs.get("new_ability", "")
        self.narrative_quote = kwargs.get("narrative_quote", "")

        # Default quotes per chapter
        if not self.narrative_quote:
            quotes = {
                1: "The first gate falls. Many more remain.",
                2: "Masks reveal more than they hide.",
                3: "Rules transform the obvious into the obscure.",
                4: "Analysis illuminates the path forward.",
                5: "Creation and destruction are two sides of one coin.",
                6: "The Citadel falls. A new Infiltrator rises.",
            }
            self.narrative_quote = quotes.get(self.chapter_number, "Onward, Infiltrator.")

        self._timer = 0.0
        self._phase = 0
        self._pulse_timer = 0.0

        # Play celebration music/sound
        if self.client.audio:
            self.client.audio.play_sfx("chapter_complete")

    def exit(self) -> None:
        """Exit the chapter complete scene."""
        pass

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        if event.type == pygame.KEYDOWN:
            if self._phase >= 3:  # Can continue after narrative
                # Any key continues
                self._continue_to_next()
            elif event.key == pygame.K_SPACE:
                # Skip animation
                self._phase = 4

    def _continue_to_next(self) -> None:
        """Continue to next chapter or victory."""
        if self.chapter_number >= self.total_chapters:
            # Final chapter - go to victory
            state = self.client.adventure_state
            self.change_scene(
                "victory",
                total_xp=state.state.xp_earned,
                deaths=state.state.deaths,
            )
        else:
            # Continue to next chapter
            self.change_scene("encounter")

    def update(self, dt: float) -> None:
        """Update scene state."""
        self._timer += dt
        self._pulse_timer += dt

        # Phase progression
        if self._phase == 0 and self._timer >= 0.5:
            self._phase = 1
        elif self._phase == 1 and self._timer >= 1.5:
            self._phase = 2
        elif self._phase == 2 and self._timer >= 3.0:
            self._phase = 3
        elif self._phase == 3 and self._timer >= 5.0:
            self._phase = 4

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the chapter complete screen."""
        import pygame
        import math

        screen_w, screen_h = self.client.screen_size
        fonts = get_fonts()

        # Background - dark with gradient
        surface.fill(Colors.BG_DARKEST)

        # Subtle vignette effect
        center_x, center_y = screen_w // 2, screen_h // 2

        # Chapter complete banner
        if self._phase >= 1:
            # "CHAPTER X COMPLETE"
            banner_font = fonts.get_font(Typography.SIZE_HEADER, bold=True)
            banner_text = f"CHAPTER {self.chapter_number} COMPLETE"
            banner_surface = banner_font.render(banner_text, Typography.ANTIALIAS, Colors.SUCCESS)
            banner_x = (screen_w - banner_surface.get_width()) // 2
            banner_y = 80
            surface.blit(banner_surface, (banner_x, banner_y))

            # Chapter title
            title_font = fonts.get_font(Typography.SIZE_SUBHEADER)
            title_surface = title_font.render(self.chapter_title.upper(), Typography.ANTIALIAS, Colors.TEXT_HEADER)
            title_x = (screen_w - title_surface.get_width()) // 2
            title_y = banner_y + 50
            surface.blit(title_surface, (title_x, title_y))

        # Stats section
        if self._phase >= 2:
            stats_y = 200

            # XP Bonus with pulsing effect
            pulse = 0.8 + 0.2 * math.sin(self._pulse_timer * 4)
            xp_font = fonts.get_font(Typography.SIZE_HEADER, bold=True)
            xp_text = f"+{self.xp_bonus} XP BONUS"
            xp_color = (
                int(Colors.YELLOW[0] * pulse),
                int(Colors.YELLOW[1] * pulse),
                int(Colors.YELLOW[2] * pulse),
            )
            xp_surface = xp_font.render(xp_text, Typography.ANTIALIAS, xp_color)
            xp_x = (screen_w - xp_surface.get_width()) // 2
            surface.blit(xp_surface, (xp_x, stats_y))

            stats_y += 60

            # Achievement (if any)
            if self.achievement:
                achieve_font = fonts.get_font(Typography.SIZE_BODY, bold=True)
                achieve_text = f"ACHIEVEMENT UNLOCKED: {self.achievement}"
                achieve_surface = achieve_font.render(achieve_text, Typography.ANTIALIAS, Colors.PURPLE)
                achieve_x = (screen_w - achieve_surface.get_width()) // 2
                surface.blit(achieve_surface, (achieve_x, stats_y))
                stats_y += 40

            # New ability (if any)
            if self.new_ability:
                ability_font = fonts.get_font(Typography.SIZE_BODY, bold=True)
                ability_text = f"NEW ABILITY: {self.new_ability}"
                ability_surface = ability_font.render(ability_text, Typography.ANTIALIAS, Colors.BLUE)
                ability_x = (screen_w - ability_surface.get_width()) // 2
                surface.blit(ability_surface, (ability_x, stats_y))

        # Narrative quote
        if self._phase >= 3:
            quote_y = screen_h - 180

            # Quote box
            quote_width = min(600, screen_w - 100)
            quote_x = (screen_w - quote_width) // 2

            # Decorative border
            pygame.draw.line(
                surface, Colors.BORDER_HIGHLIGHT,
                (quote_x, quote_y - 20),
                (quote_x + quote_width, quote_y - 20),
                1
            )

            # Quote text
            quote_font = fonts.get_font(Typography.SIZE_BODY)
            quote_text = f'"{self.narrative_quote}"'
            quote_surface = quote_font.render(quote_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY)
            surface.blit(quote_surface, (quote_x + 20, quote_y))

            # Attribution
            attr_font = fonts.get_font(Typography.SIZE_SMALL)
            attr_surface = attr_font.render("— The Null Cipher", Typography.ANTIALIAS, Colors.TEXT_MUTED)
            attr_x = quote_x + quote_width - attr_surface.get_width() - 20
            surface.blit(attr_surface, (attr_x, quote_y + 30))

            pygame.draw.line(
                surface, Colors.BORDER_HIGHLIGHT,
                (quote_x, quote_y + 55),
                (quote_x + quote_width, quote_y + 55),
                1
            )

        # Continue prompt
        if self._phase >= 4:
            prompt_font = fonts.get_font(Typography.SIZE_BODY)
            pulse = 0.6 + 0.4 * math.sin(self._pulse_timer * 3)
            prompt_color = (
                int(Colors.TEXT_PRIMARY[0] * pulse),
                int(Colors.TEXT_PRIMARY[1] * pulse),
                int(Colors.TEXT_PRIMARY[2] * pulse),
            )
            prompt_text = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt_text, Typography.ANTIALIAS, prompt_color)
            prompt_x = (screen_w - prompt_surface.get_width()) // 2
            prompt_y = screen_h - 50
            surface.blit(prompt_surface, (prompt_x, prompt_y))

        # Progress indicator
        progress_font = fonts.get_font(Typography.SIZE_SMALL)
        progress_text = f"Chapter {self.chapter_number} of {self.total_chapters}"
        progress_surface = progress_font.render(progress_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        progress_x = (screen_w - progress_surface.get_width()) // 2
        surface.blit(progress_surface, (progress_x, screen_h - 25))
