"""Title scene with book-like adventure cover layout.

Features:
- Full-screen splash art (80-100% coverage)
- Title overlaid at top center
- Menu options beneath title
- Flashing "START" option (arcade style)
- Difficulty info in upper left corner
- Full Gruvbox styling
"""

from typing import TYPE_CHECKING, Any

from storysmith.engine.game.scenes.base import Scene
from storysmith.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    Menu,
    MenuItem,
    TextRenderer,
    get_fonts,
    draw_double_border_title,
)

if TYPE_CHECKING:
    import pygame
    from storysmith.adventures.models import Campaign
    from storysmith.engine.game.client import GameClient


class TitleScene(Scene):
    """Title screen with book-like adventure cover layout.

    Layout:
    - Background: Full-screen splash art (80-100% of screen)
    - Top center: Campaign title overlaid on splash
    - Below title: Menu options
    - Upper left: Difficulty/info line (compact)
    - Flashing START option for arcade feel
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the title scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)
        self.campaign: "Campaign | None" = None
        self.has_save = False

        # UI components
        self.menu: Menu | None = None
        self.main_panel: Panel | None = None
        self.tagline_panel: Panel | None = None

        # Cached assets
        self._splash: "pygame.Surface | None" = None

        # Flashing START animation state
        self._flash_timer: float = 0.0
        self._flash_visible: bool = True
        self._flash_interval: float = 0.5  # Toggle every 0.5 seconds (1 second cycle)
        self._start_menu_index: int = 0  # Index of START item in menu

    def enter(self, **kwargs: Any) -> None:
        """Enter the title scene.

        Args:
            campaign: The campaign to display
            has_save: Whether a save file exists
        """
        self.campaign = kwargs.get("campaign")
        self.has_save = kwargs.get("has_save", False)

        screen_w, screen_h = self.client.screen_size

        # Load campaign art assets (splash only - player sprite hidden)
        if self.campaign:
            self._splash = self.client.assets.get_splash(self.campaign.id)

        # Reset flash animation state
        self._flash_timer = 0.0
        self._flash_visible = True

        # Play title theme music
        if self.client.audio:
            self.client.audio.play_music("title_theme", loop=True)

        # Create main panel (full screen with border)
        self.main_panel = Panel(
            LAYOUT["panel_margin"],
            LAYOUT["panel_margin"],
            screen_w - LAYOUT["panel_margin"] * 2,
            screen_h - LAYOUT["panel_margin"] * 2,
            major=True,
        )

        # Create menu
        self._create_menu()

        # Create tagline panel at bottom
        tagline_height = 50
        self.tagline_panel = Panel(
            LAYOUT["panel_margin"] + LAYOUT["border_width"],
            screen_h - LAYOUT["panel_margin"] - tagline_height - LAYOUT["border_width"],
            screen_w - (LAYOUT["panel_margin"] + LAYOUT["border_width"]) * 2,
            tagline_height,
            major=False,
            bg_color=Colors.BG_DARK,
        )

    def _create_menu(self) -> None:
        """Create the menu with appropriate items."""
        screen_w, screen_h = self.client.screen_size

        items = []

        # Track which index is the "START" item for flashing
        if self.has_save:
            items.append(MenuItem("CONTINUE", "C", self._on_resume))
            items.append(MenuItem("START", "N", self._on_new_game))
            self._start_menu_index = 1  # "START" is second item
        else:
            items.append(MenuItem("START", "N", self._on_start))
            self._start_menu_index = 0  # "START" is first item

        items.append(MenuItem("Credits", "R", self._on_credits))
        items.append(MenuItem("Quit", "ESC", self._on_quit))

        # Center menu horizontally, position below title area
        menu_width = 300
        menu_x = (screen_w - menu_width) // 2
        # Position menu in upper-middle area (below title overlay)
        menu_y = 180

        self.menu = Menu(menu_x, menu_y, menu_width, items, centered=True)

    def exit(self) -> None:
        """Exit the title scene."""
        # Stop title music when leaving
        if self.client.audio:
            self.client.audio.stop_music()

        self.menu = None
        self.main_panel = None
        self.tagline_panel = None
        self._splash = None

    def _on_start(self) -> None:
        """Handle start button click."""
        self.change_scene("encounter", resume=False)

    def _on_resume(self) -> None:
        """Handle resume button click."""
        self.change_scene("encounter", resume=True)

    def _on_new_game(self) -> None:
        """Handle new game button click."""
        self.change_scene("encounter", resume=False)

    def _on_credits(self) -> None:
        """Handle credits button click."""
        self.change_scene("credits")

    def _on_quit(self) -> None:
        """Handle quit button click."""
        self.client.quit()

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        # Menu handles keyboard navigation
        if self.menu:
            self.menu.handle_event(event)

        # ESC to quit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_quit()

    def update(self, dt: float) -> None:
        """Update scene - handles flashing START animation."""
        # Update flash timer for arcade-style blinking START
        self._flash_timer += dt
        if self._flash_timer >= self._flash_interval:
            self._flash_timer = 0.0
            self._flash_visible = not self._flash_visible

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the title scene with book-like cover layout."""
        import pygame

        screen_w, screen_h = self.client.screen_size

        # Fill with darkest background
        surface.fill(Colors.BG_DARKEST)

        if not self.campaign:
            return

        # Draw main panel (border frame)
        if self.main_panel:
            self.main_panel.draw(surface)

        content = self.main_panel.content_rect if self.main_panel else pygame.Rect(
            20, 20, screen_w - 40, screen_h - 40
        )

        fonts = get_fonts()

        # === SPLASH IMAGE: 80-100% of screen, book-like cover ===
        if self._splash:
            splash_img = self._splash
            splash_w, splash_h = splash_img.get_size()

            # Scale to fill ~90% of content area (book cover feel)
            target_w = int(content.width * 0.95)
            target_h = int(content.height * 0.90)

            # Maintain aspect ratio while filling as much as possible
            scale_w = target_w / splash_w
            scale_h = target_h / splash_h
            scale = max(scale_w, scale_h)  # Use max to fill more area

            new_w, new_h = int(splash_w * scale), int(splash_h * scale)
            splash_img = pygame.transform.scale(splash_img, (new_w, new_h))
            splash_w, splash_h = new_w, new_h

            # Center the splash in content area
            splash_x = content.x + (content.width - splash_w) // 2
            splash_y = content.y + (content.height - splash_h) // 2

            # Draw splash with subtle border
            border_rect = pygame.Rect(
                splash_x - 2, splash_y - 2, splash_w + 4, splash_h + 4
            )
            pygame.draw.rect(surface, Colors.BORDER, border_rect, 2)
            surface.blit(splash_img, (splash_x, splash_y))

        # === TITLE: Centered VERTICALLY and horizontally ===
        # Title block (title + info + menu) should be centered vertically
        # Estimate total block height: title (~60) + info (~30) + menu (~120) = ~210px
        title_block_height = 210
        title_y = content.y + (content.height - title_block_height) // 2
        title_width = content.width - 60
        title_x = content.x + 30

        draw_double_border_title(
            surface,
            self.campaign.title,
            title_x,
            title_y,
            title_width,
        )

        # === DIFFICULTY/INFO: Upper LEFT corner, compact ===
        info_font = fonts.get_label_font()
        info_text = f"{self.campaign.difficulty.upper()} | {len(self.campaign.chapters)} Ch | {self.campaign.estimated_time}"
        info_surface = info_font.render(info_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        # Position in upper left corner
        info_x = content.x + SPACING["md"]
        info_y = title_y + SPACING["xxl"] + SPACING["lg"]
        surface.blit(info_surface, (info_x, info_y))

        # === MENU: Positioned below title area ===
        menu_y = title_y + SPACING["xxl"] + SPACING["xxl"]

        # Update menu position
        if self.menu and self.menu.rect.y != menu_y:
            self.menu.rect.y = menu_y

        # Draw menu with flashing START
        if self.menu:
            self._draw_menu_with_flashing_start(surface)

        # === TAGLINE: Bottom panel ===
        if self.tagline_panel:
            self.tagline_panel.draw(surface)

            # Draw tagline text
            tagline = '"The Circle awaits, Infiltrator."'
            tagline_font = fonts.get_font(Typography.SIZE_LABEL)
            tagline_surface = tagline_font.render(
                tagline, Typography.ANTIALIAS, Colors.TEXT_MUTED
            )
            tagline_rect = tagline_surface.get_rect(
                center=self.tagline_panel.rect.center
            )
            surface.blit(tagline_surface, tagline_rect)

    def _draw_menu_with_flashing_start(self, surface: "pygame.Surface") -> None:
        """Draw menu with flashing START option (arcade style).

        Args:
            surface: Surface to draw on
        """
        if not self.menu:
            return

        # Store original visibility of START item
        start_index = getattr(self, "_start_menu_index", 0)

        # Temporarily hide START text if flash is off
        if not self._flash_visible and start_index < len(self.menu.items):
            original_label = self.menu.items[start_index].label
            self.menu.items[start_index].label = ""
            self.menu.draw(surface)
            self.menu.items[start_index].label = original_label
        else:
            self.menu.draw(surface)
