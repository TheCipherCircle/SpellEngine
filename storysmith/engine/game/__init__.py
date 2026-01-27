"""PatternForge graphical game client.

Pygame-based interface for playing adventures with full graphics.

Installation:
    pip install patternforge[game]

Usage:
    patternforge game dread_citadel
"""

from patternforge.game.client import GameClient
from patternforge.game.audio import AudioManager

__all__ = ["GameClient", "AudioManager"]
