"""Game scenes for different game states.

Each scene handles rendering and input for a specific game state:
- Title: Campaign selection and start
- Encounter: Main gameplay
- Dialog: Narrative text display
- GameOver: Death and retry options
- Victory: Campaign completion
"""

from storysmith.engine.game.scenes.base import Scene
from storysmith.engine.game.scenes.title import TitleScene
from storysmith.engine.game.scenes.encounter import EncounterScene
from storysmith.engine.game.scenes.game_over import GameOverScene
from storysmith.engine.game.scenes.victory import VictoryScene
from storysmith.engine.game.scenes.credits import CreditsScene

__all__ = [
    "Scene",
    "TitleScene",
    "EncounterScene",
    "GameOverScene",
    "VictoryScene",
    "CreditsScene",
]
