"""Title scene with book-like adventure cover layout.

Features:
- Full-screen splash art (80-100% coverage)
- Title overlaid at top center
- Menu options beneath title
- Flashing "START" option (arcade style)
- Difficulty selector (Normal/Heroic/Mythic - WoW-inspired)
- First-run welcome message (Hashtopia philosophy)
- Full Gruvbox styling
"""

from typing import TYPE_CHECKING, Any

from spellengine.adventures.models import DifficultyLevel
from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
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


# Welcome message for first-time players (Hashtopia philosophy)
WELCOME_MESSAGE = """Welcome to the Cipher Circle, Initiate.

Everything you need to succeed is already here.

The passwords you seek? Hidden in patterns.
The tools to find them? At your fingertips.
The knowledge to master them? Woven into every challenge.

No googling required. No external guides needed.
The answers are here. Learn to see them.

Press ENTER to begin your journey..."""

if TYPE_CHECKING:
    import pygame
    from spellengine.adventures.models import Campaign
    from spellengine.engine.game.client import GameClient


# Difficulty display info - WoW Blackrock Mountain style
DIFFICULTY_INFO = {
    DifficultyLevel.NORMAL: {
        "name": "NORMAL",
        "color": Colors.SUCCESS,  # Green
        "description": "Standard challenge - good for learning",
        "xp_mult": "1.0x",
    },
    DifficultyLevel.HEROIC: {
        "name": "HEROIC",
        "color": Colors.BLUE,  # Blue
        "description": "Harder hashes, fewer hints",
        "xp_mult": "1.5x",
    },
    DifficultyLevel.MYTHIC: {
        "name": "MYTHIC",
        "color": Colors.PURPLE,  # Purple (epic)
        "description": "Expert mode - no mercy",
        "xp_mult": "2.0x",
    },
}


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

        # Difficulty selection (WoW-style)
        self._selected_difficulty: DifficultyLevel = DifficultyLevel.NORMAL
        self._difficulty_panel: Panel | None = None

        # First-run welcome message state
        self._show_welcome: bool = False
        self._welcome_panel: Panel | None = None
        self._welcome_dismissed: bool = False

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

        # Create difficulty selector panel (upper right)
        diff_panel_width = 220
        diff_panel_height = 100
        self._difficulty_panel = Panel(
            screen_w - LAYOUT["panel_margin"] - diff_panel_width - LAYOUT["border_width"],
            LAYOUT["panel_margin"] + LAYOUT["border_width"] + 10,
            diff_panel_width,
            diff_panel_height,
            title="DIFFICULTY",
            major=False,
            bg_color=Colors.BG_DARK,
        )

        # Show welcome message for first-time players (no save exists)
        self._show_welcome = not self.has_save and not self._welcome_dismissed
        if self._show_welcome:
            self._create_welcome_panel()

    def _create_welcome_panel(self) -> None:
        """Create the welcome message panel for first-time players."""
        screen_w, screen_h = self.client.screen_size

        # Center the welcome panel
        panel_width = min(600, screen_w - 100)
        panel_height = min(400, screen_h - 100)
        panel_x = (screen_w - panel_width) // 2
        panel_y = (screen_h - panel_height) // 2

        self._welcome_panel = Panel(
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            title="THE CIPHER CIRCLE",
            major=True,
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

        items.append(MenuItem("Settings", "S", self._on_settings))
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
        self._difficulty_panel = None
        self._welcome_panel = None
        self._splash = None

    def _on_start(self) -> None:
        """Handle start button click."""
        self.change_scene("encounter", resume=False, difficulty=self._selected_difficulty)

    def _on_resume(self) -> None:
        """Handle resume button click."""
        self.change_scene("encounter", resume=True, difficulty=self._selected_difficulty)

    def _on_new_game(self) -> None:
        """Handle new game button click."""
        self.change_scene("encounter", resume=False, difficulty=self._selected_difficulty)

    def _on_settings(self) -> None:
        """Handle settings button click."""
        self.change_scene("settings")

    def _is_difficulty_unlocked(self, difficulty: DifficultyLevel) -> bool:
        """Check if a difficulty is unlocked.

        Args:
            difficulty: The difficulty to check

        Returns:
            True if unlocked, False if locked
        """
        # NORMAL and HEROIC always available
        if difficulty in (DifficultyLevel.NORMAL, DifficultyLevel.HEROIC):
            return True

        # MYTHIC requires Heroic completion
        if difficulty == DifficultyLevel.MYTHIC:
            # Check if player has completed Heroic on this campaign
            # Need to load from save state if available
            if self.client.adventure_state:
                campaign_id = self.campaign.id if self.campaign else ""
                completed = self.client.adventure_state.state.completed_difficulties.get(campaign_id, [])
                return DifficultyLevel.HEROIC.value in completed
            return False

        return True

    def _cycle_difficulty(self, direction: int = 1) -> None:
        """Cycle through difficulty levels, skipping locked ones.

        Args:
            direction: 1 for next, -1 for previous
        """
        difficulties = list(DifficultyLevel)
        current_idx = difficulties.index(self._selected_difficulty)

        # Try each difficulty in order until we find an unlocked one
        for _ in range(len(difficulties)):
            new_idx = (current_idx + direction) % len(difficulties)
            new_diff = difficulties[new_idx]

            if self._is_difficulty_unlocked(new_diff):
                self._selected_difficulty = new_diff
                # Play UI sound
                if self.client.audio:
                    self.client.audio.play_sfx("story_advance")
                return

            current_idx = new_idx

        # If no unlocked difficulty found, play error sound
        if self.client.audio:
            self.client.audio.play_sfx("error")

    def _on_credits(self) -> None:
        """Handle credits button click."""
        self.change_scene("credits")

    def _on_quit(self) -> None:
        """Handle quit button click."""
        self.client.quit()

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        # If welcome dialog is showing, only handle dismiss
        if self._show_welcome:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self._show_welcome = False
                    self._welcome_dismissed = True
                    # Play confirmation sound
                    if self.client.audio:
                        self.client.audio.play_sfx("story_advance")
            return  # Block other input while welcome is showing

        # Menu handles keyboard navigation
        if self.menu:
            self.menu.handle_event(event)

        # ESC to quit, D/Left/Right for difficulty
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_quit()
            elif event.key == pygame.K_d:
                # D key cycles difficulty forward
                self._cycle_difficulty(1)
            elif event.key == pygame.K_LEFT:
                # Left arrow cycles difficulty backward
                self._cycle_difficulty(-1)
            elif event.key == pygame.K_RIGHT:
                # Right arrow cycles difficulty forward
                self._cycle_difficulty(1)

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

        # === DIFFICULTY SELECTOR: Upper right corner (WoW-style) ===
        if self._difficulty_panel:
            self._draw_difficulty_panel(surface, fonts)

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

        # === WELCOME DIALOG: First-run message (drawn on top) ===
        if self._show_welcome:
            self._draw_welcome_dialog(surface, fonts)

    def _draw_welcome_dialog(self, surface: "pygame.Surface", fonts: Any) -> None:
        """Draw the first-run welcome dialog.

        Args:
            surface: Surface to draw on
            fonts: FontManager instance
        """
        import pygame

        if not self._welcome_panel:
            return

        screen_w, screen_h = self.client.screen_size

        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay
        surface.blit(overlay, (0, 0))

        # Draw the welcome panel
        self._welcome_panel.draw(surface)
        content = self._welcome_panel.content_rect

        # Draw the welcome message
        body_font = fonts.get_font(Typography.SIZE_BODY)
        line_height = body_font.get_height() + 4

        # Split message into lines
        lines = WELCOME_MESSAGE.strip().split("\n")
        y = content.y + SPACING["md"]

        for line in lines:
            if line.strip():
                # Render line
                text_surface = body_font.render(
                    line.strip(), Typography.ANTIALIAS, Colors.TEXT_PRIMARY
                )
                # Center horizontally
                text_x = content.x + (content.width - text_surface.get_width()) // 2
                surface.blit(text_surface, (text_x, y))
            y += line_height

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

    def _draw_difficulty_panel(self, surface: "pygame.Surface", fonts: Any) -> None:
        """Draw the difficulty selector panel (WoW Blackrock Mountain style).

        Args:
            surface: Surface to draw on
            fonts: FontManager instance
        """
        import pygame

        if not self._difficulty_panel:
            return

        self._difficulty_panel.draw(surface)
        content = self._difficulty_panel.content_rect

        # Get difficulty info
        diff_info = DIFFICULTY_INFO[self._selected_difficulty]
        is_locked = not self._is_difficulty_unlocked(self._selected_difficulty)

        # Draw difficulty name with colored text (or grayed if locked)
        name_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        name_color = Colors.TEXT_DIM if is_locked else diff_info["color"]
        name_text = diff_info["name"]
        if is_locked:
            name_text = f"🔒 {name_text}"
        name_surface = name_font.render(name_text, Typography.ANTIALIAS, name_color)
        name_x = content.x + (content.width - name_surface.get_width()) // 2
        name_y = content.y + 5
        surface.blit(name_surface, (name_x, name_y))

        # Draw XP multiplier or locked message
        xp_font = fonts.get_label_font()
        if is_locked:
            xp_text = "Complete Heroic to unlock"
            xp_color = Colors.TEXT_DIM
        else:
            xp_text = f"XP: {diff_info['xp_mult']}"
            xp_color = Colors.YELLOW
        xp_surface = xp_font.render(xp_text, Typography.ANTIALIAS, xp_color)
        xp_x = content.x + (content.width - xp_surface.get_width()) // 2
        xp_y = name_y + name_font.get_height() + 5
        surface.blit(xp_surface, (xp_x, xp_y))

        # Draw navigation hint
        hint_font = fonts.get_small_font()
        hint_text = "[D] or [←][→] to change"
        hint_surface = hint_font.render(hint_text, Typography.ANTIALIAS, Colors.TEXT_DIM)
        hint_x = content.x + (content.width - hint_surface.get_width()) // 2
        hint_y = content.y + content.height - hint_font.get_height() - 5
        surface.blit(hint_surface, (hint_x, hint_y))

        # Draw difficulty indicator dots (like WoW skull rating)
        # Locked difficulties show as locked icons
        difficulties = list(DifficultyLevel)
        current_idx = difficulties.index(self._selected_difficulty)
        dot_size = 8
        dot_spacing = 16
        total_width = len(difficulties) * dot_spacing - (dot_spacing - dot_size)
        dot_start_x = content.x + (content.width - total_width) // 2
        dot_y = xp_y + xp_font.get_height() + 8

        for i, diff in enumerate(difficulties):
            dot_x = dot_start_x + i * dot_spacing
            is_diff_locked = not self._is_difficulty_unlocked(diff)
            is_selected = i == current_idx

            if is_diff_locked:
                # Draw lock icon (small X) for locked difficulties
                pygame.draw.line(
                    surface, Colors.TEXT_DIM,
                    (dot_x + 2, dot_y + 2),
                    (dot_x + dot_size - 2, dot_y + dot_size - 2), 1
                )
                pygame.draw.line(
                    surface, Colors.TEXT_DIM,
                    (dot_x + dot_size - 2, dot_y + 2),
                    (dot_x + 2, dot_y + dot_size - 2), 1
                )
            elif i <= current_idx:
                # Filled circle for current and below
                dot_color = DIFFICULTY_INFO[diff]["color"]
                pygame.draw.circle(surface, dot_color, (dot_x + dot_size // 2, dot_y + dot_size // 2), dot_size // 2)
            else:
                # Outline for above current
                pygame.draw.circle(surface, Colors.BORDER, (dot_x + dot_size // 2, dot_y + dot_size // 2), dot_size // 2, 1)
