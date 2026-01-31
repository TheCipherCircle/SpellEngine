"""Game scenes for different game states.

Each scene handles rendering and input for a specific game state:
- Title: Campaign selection and start
- Encounter: Main gameplay
- Dialog: Narrative text display
- GameOver: Death and retry options
- Victory: Campaign completion
"""

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.scenes.title import TitleScene
from spellengine.engine.game.scenes.encounter import EncounterScene
from spellengine.engine.game.scenes.game_over import GameOverScene
from spellengine.engine.game.scenes.victory import VictoryScene
from spellengine.engine.game.scenes.credits import CreditsScene
from spellengine.engine.game.scenes.prologue_gate import PrologueGateScene
from spellengine.engine.game.scenes.chapter_complete import ChapterCompleteScene

__all__ = [
    "Scene",
    "TitleScene",
    "EncounterScene",
    "GameOverScene",
    "VictoryScene",
    "CreditsScene",
    "PrologueGateScene",
    "ChapterCompleteScene",
]
