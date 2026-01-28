"""Audio manager for PatternForge game.

Handles all sound effects, music, and ambiance with graceful fallback
when audio files are missing.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame


# Default volume levels
DEFAULT_VOLUMES = {
    "music": 0.6,
    "sfx": 1.0,
    "ambiance": 0.4,
    "ui": 0.15,  # Subtle UI sounds (clicks, typing)
}

# Audio file mapping: logical name -> relative path from audio root
AUDIO_FILES = {
    # Gameplay SFX (v2 assets)
    "crack_success": "sfx_v2/crack_success.wav",
    "crack_failure": "sfx_v2/crack_failure.wav",
    "hint_reveal": "sfx_v2/hint_reveal.wav",
    "xp_gain": "sfx_v2/xp_gain.wav",
    "typing_key": "sfx_v2/typing_key.wav",
    # Encounter SFX (v2 assets)
    "boss_appear": "sfx_v2/boss_appear.wav",
    "victory_fanfare": "sfx_v2/victory_fanfare.wav",
    "defeat_sting": "sfx_v2/defeat_sting.wav",
    # Music (v2 assets)
    "title_theme": "music_v2/title_theme.wav",
    "chapter_transition": "music_v2/chapter_transition.wav",
    # Ambiance (v2 assets)
    "dungeon_ambiance": "music_v2/dungeon_ambiance.wav",
}

# Category mapping for volume control
AUDIO_CATEGORIES = {
    "crack_success": "sfx",
    "crack_failure": "sfx",
    "hint_reveal": "sfx",
    "xp_gain": "sfx",
    "typing_key": "ui",  # Subtle UI sound
    "story_advance": "ui",  # Subtle UI sound
    "boss_appear": "sfx",
    "victory_fanfare": "sfx",
    "defeat_sting": "sfx",
    "title_theme": "music",
    "chapter_transition": "music",
    "dungeon_ambiance": "ambiance",
}


class AudioManager:
    """Manages game audio: sound effects, music, and ambiance.

    Provides graceful fallback when audio files are missing and
    volume control for different audio categories.
    """

    def __init__(self, audio_root: Path | None = None) -> None:
        """Initialize the audio manager.

        Args:
            audio_root: Root directory for audio files. Defaults to
                        assets/audio relative to the package.
        """
        self._initialized = False
        self._sounds: dict[str, "pygame.mixer.Sound"] = {}
        self._volumes = DEFAULT_VOLUMES.copy()
        self._current_music: str | None = None
        self._current_ambiance: str | None = None
        self._ambiance_channel: "pygame.mixer.Channel | None" = None
        self._sfx_channels: dict[str, "pygame.mixer.Channel"] = {}
        self._last_play_time: dict[str, float] = {}
        self._min_replay_interval = 0.05  # 50ms minimum between same sound

        # Determine audio root
        if audio_root is None:
            # Default to assets/audio relative to project root
            package_dir = Path(__file__).parent.parent.parent.parent
            audio_root = package_dir / "assets" / "audio"

        self._audio_root = audio_root

        # Initialize pygame mixer
        self._init_mixer()

        # Generate programmatic UI sounds after mixer is initialized
        self._generate_ui_sounds()

    def _init_mixer(self) -> None:
        """Initialize pygame mixer with appropriate settings."""
        try:
            import pygame.mixer

            # Initialize with good audio quality
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True

            # Reserve a channel for ambiance (persistent looping)
            pygame.mixer.set_num_channels(16)
            self._ambiance_channel = pygame.mixer.Channel(15)

        except Exception:
            # Gracefully handle audio initialization failure
            self._initialized = False

    def _generate_ui_sounds(self) -> None:
        """Generate subtle programmatic click sounds for UI interactions.

        Creates very short, soft click sounds for typing and story advance
        that don't distract from gameplay.
        """
        if not self._initialized:
            return

        try:
            import pygame
            import array
            import math

            # Audio parameters
            sample_rate = 44100

            # Generate typing click - very short soft click (0.03 seconds)
            typing_duration = 0.03
            typing_samples = int(sample_rate * typing_duration)
            typing_data = array.array('h')  # signed short

            for i in range(typing_samples):
                t = i / sample_rate
                # Quick exponential decay click
                envelope = math.exp(-t * 150)  # Fast decay
                # Mix of frequencies for soft click character
                wave = (
                    math.sin(2 * math.pi * 800 * t) * 0.5 +
                    math.sin(2 * math.pi * 1200 * t) * 0.3 +
                    math.sin(2 * math.pi * 400 * t) * 0.2
                )
                # Low amplitude for subtle sound
                sample = int(wave * envelope * 8000)
                typing_data.append(sample)
                typing_data.append(sample)  # Stereo

            typing_sound = pygame.mixer.Sound(buffer=typing_data)
            self._sounds["typing_key"] = typing_sound

            # Generate story advance click - slightly longer, softer (0.05 seconds)
            advance_duration = 0.05
            advance_samples = int(sample_rate * advance_duration)
            advance_data = array.array('h')

            for i in range(advance_samples):
                t = i / sample_rate
                # Smooth exponential decay
                envelope = math.exp(-t * 80)
                # Lower frequency for softer feel
                wave = (
                    math.sin(2 * math.pi * 600 * t) * 0.6 +
                    math.sin(2 * math.pi * 900 * t) * 0.3 +
                    math.sin(2 * math.pi * 300 * t) * 0.1
                )
                sample = int(wave * envelope * 6000)
                advance_data.append(sample)
                advance_data.append(sample)  # Stereo

            advance_sound = pygame.mixer.Sound(buffer=advance_data)
            self._sounds["story_advance"] = advance_sound

        except Exception:
            # Silently fail - sounds are optional
            pass

    def _load_sound(self, name: str) -> "pygame.mixer.Sound | None":
        """Load a sound file by logical name.

        Args:
            name: Logical name of the sound (e.g., 'crack_success')

        Returns:
            Loaded Sound object or None if loading failed
        """
        if not self._initialized:
            return None

        if name in self._sounds:
            return self._sounds[name]

        if name not in AUDIO_FILES:
            return None

        path = self._audio_root / AUDIO_FILES[name]

        if not path.exists():
            return None

        try:
            import pygame.mixer

            sound = pygame.mixer.Sound(str(path))
            self._sounds[name] = sound
            return sound
        except Exception:
            return None

    def play_sfx(self, name: str) -> None:
        """Play a sound effect.

        Uses dedicated channels per sound to prevent stacking.
        Includes debouncing to prevent rapid-fire sounds.

        Args:
            name: Logical name of the sound effect
        """
        import time

        sound = self._load_sound(name)
        if sound is None:
            return

        # Debounce: don't replay same sound too quickly
        current_time = time.time()
        last_time = self._last_play_time.get(name, 0)
        if current_time - last_time < self._min_replay_interval:
            return
        self._last_play_time[name] = current_time

        category = AUDIO_CATEGORIES.get(name, "sfx")
        volume = self._volumes.get(category, 1.0)
        sound.set_volume(volume)

        # Use dedicated channel for this sound to prevent stacking
        if name not in self._sfx_channels:
            try:
                import pygame.mixer
                # Get a free channel (channels 0-14, 15 is reserved for ambiance)
                channel = pygame.mixer.find_channel()
                if channel:
                    self._sfx_channels[name] = channel
            except Exception:
                pass

        channel = self._sfx_channels.get(name)
        if channel:
            channel.stop()  # Stop previous instance of this sound
            channel.play(sound)
        else:
            sound.play()  # Fallback to default behavior

    def play_music(self, name: str, loop: bool = True) -> None:
        """Play background music.

        Music is streamed and only one track can play at a time.
        Automatically stops any currently playing music first.

        Args:
            name: Logical name of the music track
            loop: Whether to loop the music (default True)
        """
        if not self._initialized:
            return

        # Don't restart same track if already playing
        if name == self._current_music:
            try:
                import pygame.mixer
                if pygame.mixer.music.get_busy():
                    return  # Already playing this track
            except Exception:
                pass

        if name not in AUDIO_FILES:
            return

        path = self._audio_root / AUDIO_FILES[name]

        if not path.exists():
            return

        try:
            import pygame.mixer

            # Stop current music before starting new
            pygame.mixer.music.stop()

            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._volumes.get("music", 0.6))
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
            self._current_music = name
        except Exception:
            pass

    def stop_music(self) -> None:
        """Stop currently playing music."""
        if not self._initialized:
            return

        try:
            import pygame.mixer

            pygame.mixer.music.stop()
            self._current_music = None
        except Exception:
            pass

    def play_ambiance(self, name: str, loop: bool = True) -> None:
        """Play ambient background sound.

        Ambiance plays on a dedicated channel at lower volume and
        can play alongside music. Won't restart if same track already playing.

        Args:
            name: Logical name of the ambiance track
            loop: Whether to loop the ambiance (default True)
        """
        if not self._initialized or self._ambiance_channel is None:
            return

        # Don't restart same ambiance if already playing
        if name == self._current_ambiance and self._ambiance_channel.get_busy():
            return

        sound = self._load_sound(name)
        if sound is None:
            return

        # Stop current ambiance before starting new
        self._ambiance_channel.stop()

        volume = self._volumes.get("ambiance", 0.4)
        sound.set_volume(volume)

        loops = -1 if loop else 0
        self._ambiance_channel.play(sound, loops=loops)
        self._current_ambiance = name

    def stop_ambiance(self) -> None:
        """Stop currently playing ambiance."""
        if not self._initialized or self._ambiance_channel is None:
            return

        self._ambiance_channel.stop()
        self._current_ambiance = None

    def set_volume(self, category: str, level: float) -> None:
        """Set volume for an audio category.

        Args:
            category: Category name ('music', 'sfx', or 'ambiance')
            level: Volume level from 0.0 to 1.0
        """
        level = max(0.0, min(1.0, level))
        self._volumes[category] = level

        if not self._initialized:
            return

        # Apply to currently playing audio
        try:
            import pygame.mixer

            if category == "music" and self._current_music:
                pygame.mixer.music.set_volume(level)

            if category == "ambiance" and self._current_ambiance:
                sound = self._sounds.get(self._current_ambiance)
                if sound:
                    sound.set_volume(level)
        except Exception:
            pass

    def get_volume(self, category: str) -> float:
        """Get volume for an audio category.

        Args:
            category: Category name ('music', 'sfx', or 'ambiance')

        Returns:
            Current volume level (0.0 to 1.0)
        """
        return self._volumes.get(category, 1.0)

    @property
    def is_initialized(self) -> bool:
        """Check if audio system is properly initialized."""
        return self._initialized

    @property
    def current_music(self) -> str | None:
        """Get the currently playing music track name."""
        return self._current_music

    @property
    def current_ambiance(self) -> str | None:
        """Get the currently playing ambiance track name."""
        return self._current_ambiance

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if not self._initialized:
            return

        try:
            import pygame.mixer

            self.stop_music()
            self.stop_ambiance()
            pygame.mixer.quit()
            self._initialized = False
        except Exception:
            pass
