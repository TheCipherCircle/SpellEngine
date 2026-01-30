"""Prologue gate scene for Observer mode.

Displayed when Observer mode completes the prologue (Chapter 1).
Blocks progression until tools are installed.
"""

import subprocess
import sys
from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
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


class PrologueGateScene(Scene):
    """Prologue complete gate screen.

    Shows when Observer mode finishes Chapter 1 (Prologue).
    Offers options to install tools or save and quit.
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the prologue gate scene."""
        super().__init__(client)
        self.message = ""
        self.xp_earned = 0

        # UI components
        self.main_panel: Panel | None = None
        self.menu: Menu | None = None

        # State
        self._show_why = False

    def enter(self, **kwargs: Any) -> None:
        """Enter the prologue gate scene."""
        self.message = kwargs.get("message", "")
        self.xp_earned = kwargs.get("xp_earned", 0)
        self._show_why = False

        screen_w, screen_h = self.client.screen_size

        # Play a completion sound
        if self.client.audio:
            self.client.audio.play_sfx("chapter_complete")

        margin = LAYOUT["panel_margin"]

        # Create main panel
        self.main_panel = Panel(
            margin,
            margin,
            screen_w - margin * 2,
            screen_h - margin * 2,
            major=True,
        )

        self._create_menu()

    def _create_menu(self) -> None:
        """Create menu with options."""
        if not self.main_panel:
            return

        content = self.main_panel.content_rect

        items = [
            MenuItem("Install Tools", "I", self._on_install),
            MenuItem("Save & Quit", "S", self._on_save_quit),
            MenuItem("Why do I need tools?", "?", self._on_show_why),
        ]

        menu_y = content.y + content.height - 100
        self.menu = Menu(
            content.x,
            menu_y,
            content.width,
            items,
            centered=True,
        )

    def _on_install(self) -> None:
        """Handle install option - run patternforge install."""
        # Check if PatternForge is available
        try:
            result = subprocess.run(
                [sys.executable, "-m", "patternforge", "install"],
                check=False,
            )

            # Re-check tools after install
            from spellengine.cli import check_cracking_tools, determine_game_mode

            tools = check_cracking_tools()
            new_mode = determine_game_mode(tools)

            if new_mode != "observer":
                # Tools installed! Update game mode and continue
                self.client.game_mode = new_mode
                self.client.tools = tools

                # Update adventure state game mode
                if self.client.adventure_state:
                    self.client.adventure_state.game_mode = new_mode
                    self.client.adventure_state.state.game_mode = new_mode
                    self.client.adventure_state.save()

                # Continue to next chapter
                self.change_scene("encounter")
            else:
                # Still no tools
                self._show_why = False

        except Exception:
            # PatternForge not available, show manual instructions
            self._show_why = True

    def _on_save_quit(self) -> None:
        """Handle save and quit."""
        if self.client.adventure_state:
            self.client.adventure_state.save()
        self.client.quit()

    def _on_show_why(self) -> None:
        """Toggle why explanation."""
        self._show_why = not self._show_why

    def exit(self) -> None:
        """Exit the scene."""
        self.main_panel = None
        self.menu = None

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        if self.menu:
            self.menu.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_save_quit()

    def update(self, dt: float) -> None:
        """Update scene."""
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the prologue gate scene."""
        import pygame

        screen_w, screen_h = self.client.screen_size

        # Fill background
        surface.fill(Colors.BG_DARKEST)

        # Draw main panel
        if self.main_panel:
            self.main_panel.draw(surface)

        content = self.main_panel.content_rect if self.main_panel else pygame.Rect(
            20, 20, screen_w - 40, screen_h - 40
        )

        fonts = get_fonts()

        # Draw "PROLOGUE COMPLETE" title
        title_y = content.y + 40
        draw_double_border_title(
            surface,
            "PROLOGUE COMPLETE",
            content.x + 80,
            title_y,
            content.width - 160,
        )

        # Draw main message
        y = title_y + 120

        messages = [
            "You've learned the ways of the cipher.",
            "The Null Cipher has taught you well.",
            "",
            "But Observer mode can take you no further.",
            "The Citadel's true challenges require real tools.",
        ]

        body_font = fonts.get_body_font()
        for line in messages:
            if line:
                text_surface = body_font.render(
                    line, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
                )
                text_x = content.x + (content.width - text_surface.get_width()) // 2
                surface.blit(text_surface, (text_x, y))
            y += 30

        # Draw XP earned
        y += 20
        xp_font = fonts.get_font(Typography.SIZE_SUBHEADER)
        xp_text = f"XP Earned: {self.xp_earned}"
        xp_surface = xp_font.render(xp_text, Typography.ANTIALIAS, Colors.SUCCESS)
        xp_x = content.x + (content.width - xp_surface.get_width()) // 2
        surface.blit(xp_surface, (xp_x, y))

        # Draw "why" explanation if showing
        if self._show_why:
            y += 60
            why_lines = [
                "The Dread Citadel teaches real hash cracking skills.",
                "To crack hashes, you need tools like hashcat or john.",
                "PatternForge connects to these tools and does the work.",
                "",
                "Install with: pip install patternforge",
                "Then run: patternforge install",
            ]

            small_font = fonts.get_small_font()
            for line in why_lines:
                if line:
                    text_surface = small_font.render(
                        line, Typography.ANTIALIAS, Colors.TEXT_MUTED
                    )
                    text_x = content.x + (content.width - text_surface.get_width()) // 2
                    surface.blit(text_surface, (text_x, y))
                y += 22

        # Draw menu
        if self.menu:
            self.menu.draw(surface)

        # Draw save note at bottom
        note_font = fonts.get_small_font()
        note_text = "Your progress has been saved. Return anytime."
        note_surface = note_font.render(
            note_text, Typography.ANTIALIAS, Colors.TEXT_DIM
        )
        note_x = content.x + (content.width - note_surface.get_width()) // 2
        note_y = content.y + content.height - 30
        surface.blit(note_surface, (note_x, note_y))
