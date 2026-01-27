"""Game scenes for different game states.

Each scene handles rendering and input for a specific game state:
- Title: Campaign selection and start
- Encounter: Main gameplay
- Dialog: Narrative text display
- GameOver: Death and retry options
- Victory: Campaign completion
"""

from patternforge.game.scenes.base import Scene
from patternforge.game.scenes.title import TitleScene
from patternforge.game.scenes.encounter import EncounterScene
from patternforge.game.scenes.game_over import GameOverScene
from patternforge.game.scenes.victory import VictoryScene

__all__ = [
    "Scene",
    "TitleScene",
    "EncounterScene",
    "GameOverScene",
    "VictoryScene",
]
