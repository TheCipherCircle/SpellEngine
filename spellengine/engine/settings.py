"""Game Settings - User preferences and persistence.

Handles loading/saving user preferences for audio, visual effects,
and accessibility options. Settings persist across sessions.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# Default settings directory
SETTINGS_DIR = Path.home() / ".spellengine"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


@dataclass
class GameSettings:
    """User preferences for the game.

    All volume values are 0.0-1.0.
    Boolean toggles control feature availability.
    """

    # Audio
    audio_enabled: bool = True  # Master audio toggle
    sfx_volume: float = 0.7
    music_volume: float = 0.5
    ambiance_volume: float = 0.4

    # Visual Effects
    effects_enabled: bool = True
    screen_shake: bool = True
    crt_scanlines: bool = False
    flash_effects: bool = True

    # Accessibility
    reduce_motion: bool = False  # Disables shake and flash when True
    high_contrast: bool = False  # Future: higher contrast UI

    # Display (remembered from last session)
    last_display_mode: str = "fullscreen_windowed"

    def __post_init__(self) -> None:
        """Clamp values to valid ranges."""
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
        self.music_volume = max(0.0, min(1.0, self.music_volume))
        self.ambiance_volume = max(0.0, min(1.0, self.ambiance_volume))

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameSettings":
        """Create settings from dictionary.

        Unknown keys are ignored, missing keys use defaults.
        """
        # Filter to only known fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @property
    def shake_enabled(self) -> bool:
        """Check if screen shake should be active."""
        return self.effects_enabled and self.screen_shake and not self.reduce_motion

    @property
    def flash_enabled(self) -> bool:
        """Check if flash effects should be active."""
        return self.effects_enabled and self.flash_effects and not self.reduce_motion


def load_settings() -> GameSettings:
    """Load settings from disk.

    Returns default settings if file doesn't exist or is invalid.
    """
    if not SETTINGS_FILE.exists():
        return GameSettings()

    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        return GameSettings.from_dict(data)
    except (json.JSONDecodeError, OSError, TypeError) as e:
        print(f"[Settings] Failed to load settings: {e}")
        return GameSettings()


def save_settings(settings: GameSettings) -> bool:
    """Save settings to disk.

    Returns True if successful, False otherwise.
    """
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings.to_dict(), f, indent=2)
        return True
    except OSError as e:
        print(f"[Settings] Failed to save settings: {e}")
        return False


# Global settings instance (loaded once, shared across game)
_settings: GameSettings | None = None


def get_settings() -> GameSettings:
    """Get the global settings instance.

    Loads from disk on first call, returns cached instance after.
    """
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def update_settings(**kwargs: Any) -> GameSettings:
    """Update settings and save to disk.

    Args:
        **kwargs: Setting fields to update

    Returns:
        Updated settings instance
    """
    global _settings
    settings = get_settings()

    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    # Re-clamp after updates
    settings.__post_init__()

    save_settings(settings)
    return settings
