"""Base scene class for game states."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame
    from patternforge.game.client import GameClient


class Scene(ABC):
    """Abstract base class for game scenes.

    Each scene handles a specific game state (title, encounter, game over, etc.)
    and manages its own rendering and input handling.
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the scene.

        Args:
            client: Reference to the main game client
        """
        self.client = client

    @abstractmethod
    def enter(self, **kwargs: Any) -> None:
        """Called when entering this scene.

        Override to initialize scene-specific state.

        Args:
            **kwargs: Scene-specific parameters
        """
        pass

    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this scene.

        Override to clean up scene-specific resources.
        """
        pass

    @abstractmethod
    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle a pygame event.

        Args:
            event: Pygame event to handle
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene state.

        Args:
            dt: Delta time since last update in seconds
        """
        pass

    @abstractmethod
    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the scene.

        Args:
            surface: Surface to draw on
        """
        pass

    def change_scene(self, scene_name: str, **kwargs: Any) -> None:
        """Request a scene change.

        Args:
            scene_name: Name of the scene to change to
            **kwargs: Parameters to pass to the new scene
        """
        self.client.change_scene(scene_name, **kwargs)
