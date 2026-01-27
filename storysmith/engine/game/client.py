"""Main game client for PatternForge adventures.

Pygame-based graphical interface that wraps AdventureState.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame
    from storysmith.adventures.models import Campaign
    from storysmith.adventures.state import AdventureState
    from storysmith.adventures.assets import AssetLoader
    from storysmith.engine.game.scenes.base import Scene
    from storysmith.engine.game.audio import AudioManager


# Default window size
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768


class GameClient:
    """Main game client managing the game loop and scenes.

    Wraps AdventureState for game logic and manages Pygame rendering.
    """

    def __init__(
        self,
        campaign: "Campaign",
        player_name: str = "Player",
        save_dir: Path | None = None,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
    ) -> None:
        """Initialize the game client.

        Args:
            campaign: Campaign to play
            player_name: Player display name
            save_dir: Directory for save files
            width: Window width
            height: Window height
        """
        self.campaign = campaign
        self.player_name = player_name
        self.save_dir = save_dir or Path.home() / ".patternforge" / "saves"
        self.screen_size = (width, height)

        self._running = False
        self._screen: "pygame.Surface | None" = None
        self._clock: "pygame.time.Clock | None" = None

        # Adventure state (created on run)
        self.adventure_state: "AdventureState | None" = None

        # Asset loader
        self.assets: "AssetLoader | None" = None

        # Audio manager
        self.audio: "AudioManager | None" = None

        # Scene management
        self._scenes: dict[str, "Scene"] = {}
        self._current_scene: "Scene | None" = None
        self._current_scene_name: str | None = None
        self._pending_scene_change: tuple[str, dict[str, Any]] | None = None

    @property
    def save_path(self) -> Path:
        """Get the save file path for this campaign."""
        return self.save_dir / f"{self.campaign.id}_game.json"

    def has_save(self) -> bool:
        """Check if a save file exists."""
        return self.save_path.exists()

    def _init_pygame(self) -> None:
        """Initialize pygame and create window."""
        import os
        import pygame

        # Position window on left side of screen (for side-by-side with terminal)
        # Must set before pygame.init() for SDL to pick it up
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,25'

        pygame.init()
        pygame.display.set_caption(f"PatternForge - {self.campaign.title}")

        self._screen = pygame.display.set_mode(self.screen_size)

        # Try to reposition window after creation (backup for macOS)
        try:
            from ctypes import c_int, byref
            import ctypes.util
            sdl2 = ctypes.CDLL(ctypes.util.find_library('SDL2'))
            window = pygame.display.get_wm_info()['window']
            sdl2.SDL_SetWindowPosition(window, 0, 25)
        except Exception:
            pass  # Fallback if SDL2 direct access fails
        self._clock = pygame.time.Clock()

    def _init_scenes(self) -> None:
        """Initialize all scene objects."""
        from storysmith.engine.game.scenes.title import TitleScene
        from storysmith.engine.game.scenes.encounter import EncounterScene
        from storysmith.engine.game.scenes.game_over import GameOverScene
        from storysmith.engine.game.scenes.victory import VictoryScene

        self._scenes = {
            "title": TitleScene(self),
            "encounter": EncounterScene(self),
            "game_over": GameOverScene(self),
            "victory": VictoryScene(self),
        }

    def _init_adventure(self, resume: bool = False) -> None:
        """Initialize the adventure state.

        Args:
            resume: Whether to resume from save
        """
        from storysmith.adventures.state import AdventureState

        self.save_dir.mkdir(parents=True, exist_ok=True)

        if resume and self.save_path.exists():
            self.adventure_state = AdventureState.load(self.campaign, self.save_path)
        else:
            self.adventure_state = AdventureState(
                self.campaign,
                player_name=self.player_name,
                save_path=self.save_path,
            )

    def _init_assets(self) -> None:
        """Initialize the asset loader."""
        from storysmith.adventures.assets import AssetLoader

        self.assets = AssetLoader()

    def _init_audio(self) -> None:
        """Initialize the audio manager."""
        from storysmith.engine.game.audio import AudioManager

        self.audio = AudioManager()

    def change_scene(self, scene_name: str, **kwargs: Any) -> None:
        """Request a scene change.

        The actual change happens at the start of the next frame to avoid
        issues with scene changes during event handling.

        Args:
            scene_name: Name of the scene to change to
            **kwargs: Parameters to pass to the new scene's enter() method
        """
        self._pending_scene_change = (scene_name, kwargs)

    def _do_scene_change(self) -> None:
        """Perform pending scene change."""
        if self._pending_scene_change is None:
            return

        scene_name, kwargs = self._pending_scene_change
        self._pending_scene_change = None

        if self._current_scene:
            self._current_scene.exit()

        if scene_name in self._scenes:
            self._current_scene = self._scenes[scene_name]
            self._current_scene_name = scene_name
            self._current_scene.enter(**kwargs)
        else:
            raise ValueError(f"Unknown scene: {scene_name}")

    def quit(self) -> None:
        """Request game exit."""
        self._running = False

    def run(self, resume: bool = False) -> None:
        """Run the game.

        Args:
            resume: Whether to resume from save file
        """
        import pygame

        # Initialize
        self._init_pygame()
        self._init_audio()
        self._init_scenes()
        self._init_assets()
        self._init_adventure(resume)

        # Start with title screen or encounter depending on mode
        if resume and self.adventure_state:
            self.change_scene("encounter", resume=True)
        else:
            self.change_scene("title", campaign=self.campaign, has_save=self.has_save())

        self._running = True

        # Main game loop
        while self._running:
            dt = self._clock.tick(60) / 1000.0  # Delta time in seconds

            # Process pending scene change
            self._do_scene_change()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                # Global ESC handler - always works as emergency exit
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Return to title or quit if already at title
                    if self._current_scene_name == "title":
                        self._running = False
                    else:
                        self.change_scene("title", campaign=self.campaign, has_save=self.has_save())
                elif self._current_scene:
                    try:
                        self._current_scene.handle_event(event)
                    except Exception as e:
                        print(f"Error handling event: {e}")

            # Update
            if self._current_scene:
                try:
                    self._current_scene.update(dt)
                except Exception as e:
                    print(f"Error in update: {e}")

            # Draw
            if self._screen and self._current_scene:
                try:
                    self._current_scene.draw(self._screen)
                    pygame.display.flip()
                except Exception as e:
                    print(f"Error in draw: {e}")
                    # Fill with error color so user knows something is wrong
                    self._screen.fill((80, 0, 0))  # Dark red
                    pygame.display.flip()

        # Cleanup
        if self.audio:
            self.audio.cleanup()
        pygame.quit()


def launch_game(
    campaign: "Campaign",
    player_name: str = "Player",
    save_dir: Path | None = None,
    resume: bool = False,
) -> None:
    """Launch the game client for a campaign.

    Convenience function for starting the game from CLI.

    Args:
        campaign: Campaign to play
        player_name: Player display name
        save_dir: Directory for save files
        resume: Whether to resume from save
    """
    client = GameClient(
        campaign=campaign,
        player_name=player_name,
        save_dir=save_dir,
    )
    client.run(resume=resume)
