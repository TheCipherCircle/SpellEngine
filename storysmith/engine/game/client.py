"""Main game client for PatternForge adventures.

Pygame-based graphical interface that wraps AdventureState.
"""

import subprocess
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame
    from storysmith.adventures.models import Campaign
    from storysmith.adventures.state import AdventureState
    from storysmith.adventures.assets import AssetLoader
    from storysmith.engine.game.scenes.base import Scene
    from storysmith.engine.game.audio import AudioManager


class DisplayMode(Enum):
    """Display mode options."""
    WINDOWED = "windowed"
    FULLSCREEN_WINDOWED = "fullscreen_windowed"  # Borderless fullscreen
    FULLSCREEN = "fullscreen"


# Default window size (used for windowed mode)
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 800


class GameClient:
    """Main game client managing the game loop and scenes.

    Wraps AdventureState for game logic and manages Pygame rendering.
    """

    # Test session tracking (class-level for persistence)
    _test_session_id: str | None = None
    _test_log_path: Path | None = None
    _test_terminal_opened: bool = False

    def __init__(
        self,
        campaign: "Campaign",
        player_name: str = "Player",
        save_dir: Path | None = None,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        display_mode: DisplayMode = DisplayMode.FULLSCREEN_WINDOWED,
        game_mode: str = "full",
        tools: dict | None = None,
    ) -> None:
        """Initialize the game client.

        Args:
            campaign: Campaign to play
            player_name: Player display name
            save_dir: Directory for save files
            width: Window width (for windowed mode)
            height: Window height (for windowed mode)
            display_mode: Display mode (windowed, fullscreen_windowed, fullscreen)
            game_mode: Tool availability mode (full/hashcat/john/observer)
            tools: Dict of available tool paths
        """
        self.campaign = campaign
        self.player_name = player_name
        self.save_dir = save_dir or Path.home() / ".patternforge" / "saves"
        self._windowed_size = (width, height)  # Store for mode switching
        self.screen_size = (width, height)
        self.display_mode = display_mode
        self.game_mode = game_mode
        self.tools = tools or {}

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

    def _init_test_session(self) -> None:
        """Initialize a test session for tracking crack commands."""
        from storysmith.cli import __version__

        # Generate unique session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = uuid.uuid4().hex[:8]
        GameClient._test_session_id = f"{timestamp}_{short_id}"

        # Create test log directory and file
        test_log_dir = Path.home() / ".storysmith" / "test_logs"
        test_log_dir.mkdir(parents=True, exist_ok=True)
        GameClient._test_log_path = test_log_dir / f"playtest_{GameClient._test_session_id}.log"
        GameClient._test_terminal_opened = False

        # Write session header
        with open(GameClient._test_log_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("  STORYSMITH PLAYTEST LOG\n")
            f.write("=" * 60 + "\n")
            f.write(f"Session ID: {GameClient._test_session_id}\n")
            f.write(f"Version: {__version__}\n")
            f.write(f"Campaign: {self.campaign.title} ({self.campaign.id})\n")
            f.write(f"Game Mode: {self.game_mode}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

    def log_crack_command(self, hash_value: str, command: str, result: str) -> None:
        """Log a crack command and result to the test session.

        Args:
            hash_value: The hash being cracked
            command: The command that was run
            result: The result/output
        """
        if not GameClient._test_log_path:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(GameClient._test_log_path, "a") as f:
            f.write(f"[{timestamp}] CRACK ATTEMPT\n")
            f.write(f"Hash: {hash_value}\n")
            f.write(f"Command: {command}\n")
            f.write(f"Result: {result}\n")
            f.write("-" * 40 + "\n\n")

    def open_test_terminal(self) -> None:
        """Open a terminal window that tails the test log."""
        if GameClient._test_terminal_opened or not GameClient._test_log_path:
            return

        GameClient._test_terminal_opened = True
        log_path = GameClient._test_log_path

        # AppleScript to open Terminal with tail -f on the log file
        applescript = f'''
        tell application "Terminal"
            do script "clear; echo '=== STORYSMITH PLAYTEST LOG ==='; echo 'Session: {GameClient._test_session_id}'; echo ''; tail -f \\"{log_path}\\" 2>/dev/null"
            set custom title of front window to "Playtest Log - {GameClient._test_session_id}"
        end tell
        '''

        try:
            subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                timeout=5,
            )
        except Exception as e:
            print(f"[verbose] Failed to open test terminal: {e}")

    def finalize_test_session(self, stats: dict) -> None:
        """Finalize the test session and prompt for submission.

        Args:
            stats: Final game stats (xp, deaths, clean_solves, etc.)
        """
        if not GameClient._test_log_path:
            return

        # Write final stats to log
        with open(GameClient._test_log_path, "a") as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write("  PLAYTEST COMPLETE\n")
            f.write("=" * 60 + "\n")
            f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total XP: {stats.get('total_xp', 0)}\n")
            f.write(f"Deaths: {stats.get('deaths', 0)}\n")
            f.write(f"Clean Solves: {stats.get('clean_solves', 0)}\n")
            f.write(f"Hints Used: {stats.get('hints_used', 0)}\n")
            f.write("=" * 60 + "\n\n")
            f.write("This log will be included with your playtest report.\n")
            f.write("Press ENTER to send and close...\n")

        # If terminal is open, it will show this via tail -f
        # The terminal script handles the "press enter to close" prompt

    def _init_pygame(self) -> None:
        """Initialize pygame and create window."""
        import pygame

        pygame.init()
        pygame.display.set_caption(f"PatternForge - {self.campaign.title}")

        # Set up display based on mode
        self._set_display_mode(self.display_mode)
        self._clock = pygame.time.Clock()

    def _set_display_mode(self, mode: DisplayMode) -> None:
        """Set the display mode.

        Args:
            mode: Display mode to set
        """
        import pygame

        self.display_mode = mode

        if mode == DisplayMode.WINDOWED:
            # Standard windowed mode
            self._screen = pygame.display.set_mode(self._windowed_size, pygame.RESIZABLE)
            self.screen_size = self._windowed_size

        elif mode == DisplayMode.FULLSCREEN_WINDOWED:
            # Borderless fullscreen (covers screen but not exclusive)
            display_info = pygame.display.Info()
            screen_w, screen_h = display_info.current_w, display_info.current_h
            self._screen = pygame.display.set_mode(
                (screen_w, screen_h),
                pygame.NOFRAME
            )
            self.screen_size = (screen_w, screen_h)

        elif mode == DisplayMode.FULLSCREEN:
            # True fullscreen (exclusive mode)
            display_info = pygame.display.Info()
            screen_w, screen_h = display_info.current_w, display_info.current_h
            self._screen = pygame.display.set_mode(
                (screen_w, screen_h),
                pygame.FULLSCREEN
            )
            self.screen_size = (screen_w, screen_h)

        # Reinitialize scenes if they exist (they cache screen dimensions)
        if self._scenes and self._current_scene_name:
            self._reinit_current_scene()

    def _reinit_current_scene(self) -> None:
        """Reinitialize current scene after display mode change."""
        if self._current_scene and self._current_scene_name:
            # Exit and re-enter current scene to recalculate layouts
            scene_name = self._current_scene_name
            self._current_scene.exit()

            # Re-enter with appropriate params
            if scene_name == "title":
                self._current_scene.enter(campaign=self.campaign, has_save=self.has_save())
            elif scene_name == "encounter":
                self._current_scene.enter()
            else:
                self._current_scene.enter()

    def cycle_display_mode(self) -> None:
        """Cycle through display modes: windowed -> fullscreen_windowed -> fullscreen."""
        modes = [DisplayMode.WINDOWED, DisplayMode.FULLSCREEN_WINDOWED, DisplayMode.FULLSCREEN]
        current_idx = modes.index(self.display_mode)
        next_idx = (current_idx + 1) % len(modes)
        self._set_display_mode(modes[next_idx])
        print(f"Display mode: {self.display_mode.value}")

    def _init_scenes(self) -> None:
        """Initialize all scene objects."""
        from storysmith.engine.game.scenes.title import TitleScene
        from storysmith.engine.game.scenes.encounter import EncounterScene
        from storysmith.engine.game.scenes.game_over import GameOverScene
        from storysmith.engine.game.scenes.victory import VictoryScene
        from storysmith.engine.game.scenes.credits import CreditsScene

        self._scenes = {
            "title": TitleScene(self),
            "encounter": EncounterScene(self),
            "game_over": GameOverScene(self),
            "victory": VictoryScene(self),
            "credits": CreditsScene(self),
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

    def _take_screenshot(self) -> None:
        """Capture and save a screenshot of the current frame."""
        from datetime import datetime
        import pygame

        if not self._screen:
            return

        # Create screenshots directory
        screenshots_dir = Path.home() / ".storysmith" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp and scene name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scene_name = self._current_scene_name or "unknown"
        filename = f"storysmith_{scene_name}_{timestamp}.png"
        filepath = screenshots_dir / filename

        # Save screenshot
        try:
            pygame.image.save(self._screen, str(filepath))
            print(f"Screenshot saved: {filepath}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")

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
        self._init_test_session()

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
                # Screenshot capture (F12)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                    self._take_screenshot()
                # Display mode toggle (F11)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.cycle_display_mode()
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
    display_mode: str = "fullscreen_windowed",
    game_mode: str = "full",
    tools: dict | None = None,
) -> None:
    """Launch the game client for a campaign.

    Convenience function for starting the game from CLI.

    Args:
        campaign: Campaign to play
        player_name: Player display name
        save_dir: Directory for save files
        resume: Whether to resume from save
        display_mode: Display mode (windowed, fullscreen_windowed, fullscreen)
        game_mode: Tool availability mode (full/hashcat/john/observer)
        tools: Dict of available tool paths
    """
    # Parse display mode string to enum
    mode_map = {
        "windowed": DisplayMode.WINDOWED,
        "fullscreen_windowed": DisplayMode.FULLSCREEN_WINDOWED,
        "fullscreen": DisplayMode.FULLSCREEN,
    }
    mode = mode_map.get(display_mode, DisplayMode.FULLSCREEN_WINDOWED)

    client = GameClient(
        campaign=campaign,
        player_name=player_name,
        save_dir=save_dir,
        display_mode=mode,
        game_mode=game_mode,
        tools=tools or {},
    )
    client.run(resume=resume)
