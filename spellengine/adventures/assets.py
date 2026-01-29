"""Asset loader for adventure game graphics.

Handles loading encounter images, chapter cards, and badges.
Supports placeholder fallbacks for development.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import pygame

# Asset directories
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

# Art style type
ArtStyle = Literal["original", "crunched"]

# Default art style - "crunched" uses the corrupted SNES aesthetic
DEFAULT_ART_STYLE: ArtStyle = "crunched"


class AssetLoader:
    """Loads and caches game assets.

    Provides placeholder images when actual assets are missing,
    allowing development without full art pipeline.

    Supports multiple art styles:
    - "original": Clean AI-generated art (dread_citadel/)
    - "crunched": Corrupted SNES aesthetic (dread_citadel_crunched/)
    """

    def __init__(
        self,
        assets_dir: Path | None = None,
        art_style: ArtStyle | None = None,
    ) -> None:
        """Initialize the asset loader.

        Args:
            assets_dir: Override default assets directory
            art_style: Art style to use ("original" or "crunched").
                       Defaults to "crunched" for the corrupted SNES look.
        """
        self.assets_dir = assets_dir or ASSETS_DIR
        self.images_dir = self.assets_dir / "images"
        self.art_style: ArtStyle = art_style or DEFAULT_ART_STYLE
        self._cache: dict[str, "pygame.Surface"] = {}
        self._pygame_initialized = False

    def _get_campaign_images_dir(self, campaign_id: str) -> Path:
        """Get the images directory for a campaign based on art style.

        Args:
            campaign_id: Campaign identifier (e.g., "dread_citadel")

        Returns:
            Path to the campaign's images directory
        """
        if self.art_style == "crunched":
            crunched_dir = self.images_dir / f"{campaign_id}_crunched"
            if crunched_dir.exists():
                return crunched_dir
            # Fall back to original if crunched doesn't exist
        return self.images_dir / campaign_id

    def set_art_style(self, style: ArtStyle) -> None:
        """Change the art style and clear the cache.

        Args:
            style: New art style ("original" or "crunched")
        """
        if style != self.art_style:
            self.art_style = style
            self.clear_cache()

    def _ensure_pygame(self) -> None:
        """Ensure pygame is imported and display initialized."""
        if not self._pygame_initialized:
            import pygame
            if not pygame.get_init():
                pygame.init()
            self._pygame_initialized = True

    def _create_placeholder(
        self, width: int, height: int, label: str = "?"
    ) -> "pygame.Surface":
        """Create a placeholder surface with text.

        Args:
            width: Surface width
            height: Surface height
            label: Text to display on placeholder

        Returns:
            Pygame surface with placeholder graphics
        """
        import pygame

        self._ensure_pygame()

        # Gruvbox colors
        bg_color = (40, 40, 40)  # #282828
        border_color = (80, 73, 69)  # #504945
        text_color = (168, 153, 132)  # #a89984

        surface = pygame.Surface((width, height))
        surface.fill(bg_color)

        # Draw border
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 3)

        # Draw diagonal lines pattern
        for i in range(-height, width, 20):
            pygame.draw.line(
                surface, border_color, (i, height), (i + height, 0), 1
            )

        # Draw label text
        font = pygame.font.Font(None, min(width, height) // 4)
        text = font.render(label, True, text_color)
        text_rect = text.get_rect(center=(width // 2, height // 2))
        surface.blit(text, text_rect)

        return surface

    def get_encounter_image(
        self, campaign_id: str, encounter_id: str
    ) -> "pygame.Surface | None":
        """Load an encounter image.

        Args:
            campaign_id: Campaign identifier
            encounter_id: Encounter identifier

        Returns:
            Pygame surface with the image, or None if no encounter-specific art exists.
            When no art exists, the encounter scene should use the background image instead.
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"encounter:{self.art_style}:{campaign_id}:{encounter_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try to load actual image
        image_path = self._get_campaign_images_dir(campaign_id) / f"{encounter_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # No encounter-specific art - return None so scene uses background instead
        # Cache None to avoid repeated filesystem checks
        self._cache[cache_key] = None
        return None

    def get_chapter_card(
        self, campaign_id: str, chapter_id: str
    ) -> "pygame.Surface":
        """Load a chapter title card.

        Args:
            campaign_id: Campaign identifier
            chapter_id: Chapter identifier

        Returns:
            Pygame surface with the chapter card (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"chapter:{self.art_style}:{campaign_id}:{chapter_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / f"{chapter_id}_card.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (512x256)
        placeholder = self._create_placeholder(512, 256, chapter_id[:12])
        self._cache[cache_key] = placeholder
        return placeholder

    def get_badge(self, badge_id: str) -> "pygame.Surface":
        """Load an achievement badge.

        Args:
            badge_id: Badge/achievement identifier

        Returns:
            Pygame surface with the badge (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"badge:{badge_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self.images_dir / "badges" / f"{badge_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (64x64)
        placeholder = self._create_placeholder(64, 64, badge_id[:6])
        self._cache[cache_key] = placeholder
        return placeholder

    def clear_cache(self) -> None:
        """Clear the asset cache."""
        self._cache.clear()

    def preload_campaign(self, campaign_id: str, encounter_ids: list[str]) -> None:
        """Preload all assets for a campaign.

        Args:
            campaign_id: Campaign identifier
            encounter_ids: List of encounter IDs to preload
        """
        for encounter_id in encounter_ids:
            self.get_encounter_image(campaign_id, encounter_id)

    def get_splash(self, campaign_id: str) -> "pygame.Surface":
        """Load a campaign splash image.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Pygame surface with the splash image (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"splash:{self.art_style}:{campaign_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / f"splash_{campaign_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (640x200)
        placeholder = self._create_placeholder(640, 200, f"SPLASH:{campaign_id[:8]}")
        self._cache[cache_key] = placeholder
        return placeholder

    def get_boss_sprite(
        self, campaign_id: str, boss_id: str
    ) -> "pygame.Surface":
        """Load a boss sprite image.

        Args:
            campaign_id: Campaign identifier
            boss_id: Boss identifier (e.g., 'gatekeeper', 'crypt_guardian')

        Returns:
            Pygame surface with the boss sprite (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"boss:{self.art_style}:{campaign_id}:{boss_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / f"boss_{boss_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (256x256)
        placeholder = self._create_placeholder(256, 256, f"BOSS:{boss_id[:8]}")
        self._cache[cache_key] = placeholder
        return placeholder

    def get_player_sprite(self, campaign_id: str) -> "pygame.Surface":
        """Load the player sprite image.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Pygame surface with the player sprite (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"player:{self.art_style}:{campaign_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / "player_apprentice.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (128x128)
        placeholder = self._create_placeholder(128, 128, "PLAYER")
        self._cache[cache_key] = placeholder
        return placeholder

    def get_background(
        self, campaign_id: str, bg_id: str
    ) -> "pygame.Surface":
        """Load a background image.

        Args:
            campaign_id: Campaign identifier
            bg_id: Background identifier (e.g., 'throne_room', 'outer_gates')

        Returns:
            Pygame surface with the background (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"bg:{self.art_style}:{campaign_id}:{bg_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / f"bg_{bg_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (640x400)
        placeholder = self._create_placeholder(640, 400, f"BG:{bg_id[:10]}")
        self._cache[cache_key] = placeholder
        return placeholder

    def get_ui_element(
        self, campaign_id: str, element_id: str
    ) -> "pygame.Surface":
        """Load a UI element image.

        Args:
            campaign_id: Campaign identifier
            element_id: UI element identifier (e.g., 'lock_md5', 'panel_success', 'icon_xp')

        Returns:
            Pygame surface with the UI element (or placeholder)
        """
        import pygame

        self._ensure_pygame()

        cache_key = f"ui:{self.art_style}:{campaign_id}:{element_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        image_path = self._get_campaign_images_dir(campaign_id) / f"{element_id}.png"
        if image_path.exists():
            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                self._cache[cache_key] = surface
                return surface
            except pygame.error:
                pass

        # Fall back to placeholder (64x64 for icons, 256x128 for panels)
        if element_id.startswith("panel_"):
            placeholder = self._create_placeholder(256, 128, element_id[:12])
        else:
            placeholder = self._create_placeholder(64, 64, element_id[:8])
        self._cache[cache_key] = placeholder
        return placeholder
