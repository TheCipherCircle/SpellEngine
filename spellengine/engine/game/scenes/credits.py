"""Credits scene with scrolling credits display.

Shows the Cipher Circle team and all contributors.
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
    Typography,
    Panel,
    get_fonts,
    draw_double_border_title,
)

if TYPE_CHECKING:
    import pygame
    from spellengine.engine.game.client import GameClient


# Credits data - The Cipher Circle
CREDITS_DATA = {
    "header": "THE CIPHER CIRCLE",
    "sections": [
        {
            "title": "FOUNDERS",
            "entries": [
                ("Executive Producer", "pitl0rd"),
                ("Producer", "Solace"),
            ],
        },
        {
            "title": "FOUNDING AGENTS",
            "entries": [
                ("Lead Engineer", "Forge"),
                ("Lead Designer", "Mirth"),
                ("Lead Writer", "Loreth"),
                ("QA Lead", "Anvil"),
                ("Art Director", "Fraz"),
                ("Data Architect", "Prism"),
                ("Creative Director", "Vex"),
                ("AI Systems", "Jinx"),
            ],
        },
        {
            "title": "BUG HUNTERS",
            "entries": [
                ("", "bluscreenofjeff"),
                ("", "Colossus"),
                ("", "Inceptor"),
            ],
        },
        {
            "title": "SPECIAL THANKS",
            "entries": [
                ("", "The Cipher Circle Discord Community"),
                ("", "All who dared enter the Citadel"),
            ],
        },
    ],
    "footer": '"The Circle is unbroken."',
}


class CreditsScene(Scene):
    """Credits screen with scrolling display.

    Layout:
    +---------------------------------------------------+
    |              THE CIPHER CIRCLE                    |
    |            ═══════════════════════                |
    |                                                   |
    |              [Scrolling Credits]                  |
    |                                                   |
    +---------------------------------------------------+
    |              [ESC] Return                         |
    +---------------------------------------------------+
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the credits scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)

        # UI components
        self.main_panel: Panel | None = None

        # Scroll state
        self._scroll_offset: float = 0.0
        self._scroll_speed: float = 30.0  # Pixels per second
        self._auto_scroll: bool = True
        self._content_height: float = 0.0

    def enter(self, **kwargs: Any) -> None:
        """Enter the credits scene."""
        screen_w, screen_h = self.client.screen_size

        margin = LAYOUT["panel_margin"]

        # Create main panel (full screen with border)
        self.main_panel = Panel(
            margin,
            margin,
            screen_w - margin * 2,
            screen_h - margin * 2,
            major=True,
        )

        # Reset scroll state
        self._scroll_offset = 0.0
        self._auto_scroll = True

        # Calculate content height
        self._calculate_content_height()

    def _calculate_content_height(self) -> None:
        """Calculate the total height of credits content."""
        fonts = get_fonts()
        header_font = fonts.get_header_font()
        title_font = fonts.get_body_font()
        entry_font = fonts.get_label_font()

        height = 100  # Initial padding

        # Header
        height += header_font.get_height() + 40

        # Sections
        for section in CREDITS_DATA["sections"]:
            height += title_font.get_height() + 30  # Section title
            for _ in section["entries"]:
                height += entry_font.get_height() + 8
            height += 40  # Section padding

        # Footer
        height += 60 + entry_font.get_height()

        self._content_height = height

    def exit(self) -> None:
        """Exit the credits scene."""
        self.main_panel = None

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_back()
            elif event.key == pygame.K_SPACE:
                # Toggle auto-scroll
                self._auto_scroll = not self._auto_scroll
            elif event.key == pygame.K_UP:
                self._scroll_offset = max(0, self._scroll_offset - 50)
                self._auto_scroll = False
            elif event.key == pygame.K_DOWN:
                self._scroll_offset += 50
                self._auto_scroll = False

    def _on_back(self) -> None:
        """Return to title screen."""
        self.change_scene("title", campaign=self.client.campaign, has_save=False)

    def update(self, dt: float) -> None:
        """Update scene - handles scrolling."""
        if self._auto_scroll:
            self._scroll_offset += self._scroll_speed * dt

            # Loop back when we've scrolled past content
            if self.main_panel:
                max_scroll = self._content_height - self.main_panel.content_rect.height + 100
                if self._scroll_offset > max_scroll:
                    self._scroll_offset = max_scroll
                    self._auto_scroll = False  # Stop at end

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the credits scene."""
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

        # Create a clipping rect for the scrolling area
        scroll_area = pygame.Rect(
            content.x,
            content.y + 80,  # Below title
            content.width,
            content.height - 130,  # Leave room for title and footer
        )

        # Draw fixed title at top
        draw_double_border_title(
            surface,
            CREDITS_DATA["header"],
            content.x + 50,
            content.y + 10,
            content.width - 100,
        )

        # Set up clipping for scrolling content
        old_clip = surface.get_clip()
        surface.set_clip(scroll_area)

        # Draw scrolling content
        y = scroll_area.y - self._scroll_offset + 20

        for section in CREDITS_DATA["sections"]:
            # Section title
            title_font = fonts.get_body_font()
            title_text = f"═══  {section['title']}  ═══"
            title_surface = title_font.render(
                title_text, Typography.ANTIALIAS, Colors.TEXT_HEADER
            )
            title_x = content.x + (content.width - title_surface.get_width()) // 2
            if scroll_area.y - 50 < y < scroll_area.bottom + 50:
                surface.blit(title_surface, (title_x, y))
            y += title_font.get_height() + 20

            # Section entries
            entry_font = fonts.get_label_font()
            for role, name in section["entries"]:
                if role:
                    # Role and name on same line with dots
                    entry_text = f"{role} {'.' * (30 - len(role) - len(name))} {name}"
                else:
                    # Just name, centered
                    entry_text = name

                entry_surface = entry_font.render(
                    entry_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
                )

                if role:
                    entry_x = content.x + 60
                else:
                    entry_x = content.x + (content.width - entry_surface.get_width()) // 2

                if scroll_area.y - 30 < y < scroll_area.bottom + 30:
                    surface.blit(entry_surface, (entry_x, y))
                y += entry_font.get_height() + 8

            y += 30  # Section padding

        # Footer
        y += 20
        footer_font = fonts.get_label_font()
        footer_surface = footer_font.render(
            CREDITS_DATA["footer"], Typography.ANTIALIAS, Colors.TEXT_MUTED
        )
        footer_x = content.x + (content.width - footer_surface.get_width()) // 2
        if scroll_area.y - 30 < y < scroll_area.bottom + 30:
            surface.blit(footer_surface, (footer_x, y))

        # Restore clipping
        surface.set_clip(old_clip)

        # Draw fixed footer with controls
        control_font = fonts.get_small_font()
        control_text = "[ESC] Return    [SPACE] Pause    [UP/DOWN] Scroll"
        control_surface = control_font.render(
            control_text, Typography.ANTIALIAS, Colors.TEXT_MUTED
        )
        control_x = content.x + (content.width - control_surface.get_width()) // 2
        control_y = content.y + content.height - 30
        surface.blit(control_surface, (control_x, control_y))
