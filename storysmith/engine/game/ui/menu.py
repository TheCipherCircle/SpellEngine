"""Menu component with keyboard navigation and selection indicator.

Styled for corrupted SNES aesthetic with red arrow indicator.
"""

from typing import Callable, TYPE_CHECKING

from patternforge.game.ui.theme import Colors, Typography, get_fonts, LAYOUT

if TYPE_CHECKING:
    import pygame


class MenuItem:
    """A single menu item with key binding and callback."""

    def __init__(
        self,
        label: str,
        key: str,
        callback: Callable[[], None] | None = None,
        enabled: bool = True,
    ) -> None:
        """Initialize the menu item.

        Args:
            label: Display text
            key: Keyboard key (e.g., "N" for New Game)
            callback: Function to call when selected
            enabled: Whether the item is selectable
        """
        self.label = label
        self.key = key.upper()
        self.callback = callback
        self.enabled = enabled


class Menu:
    """A keyboard-navigable menu with selection indicator.

    Features:
    - Red arrow indicator (>) for current selection
    - [KEY] prefix styling
    - Muted text for unselected, primary for selected
    - Up/Down or key-based navigation
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        items: list[MenuItem] | None = None,
        centered: bool = True,
    ) -> None:
        """Initialize the menu.

        Args:
            x: X position
            y: Y position
            width: Menu width
            items: List of menu items
            centered: Whether to center items horizontally
        """
        import pygame

        self.rect = pygame.Rect(x, y, width, 0)
        self.items = items or []
        self.centered = centered
        self.selected_index = 0

        # Find first enabled item
        for i, item in enumerate(self.items):
            if item.enabled:
                self.selected_index = i
                break

        self._font = get_fonts().get_font(Typography.SIZE_BODY)
        self._update_height()

    def _update_height(self) -> None:
        """Calculate height based on number of items."""
        line_height = int(self._font.get_height() * Typography.LINE_HEIGHT) + 8
        self.rect.height = len(self.items) * line_height

    def add_item(self, item: MenuItem) -> None:
        """Add an item to the menu.

        Args:
            item: Menu item to add
        """
        self.items.append(item)
        self._update_height()

    def clear_items(self) -> None:
        """Remove all menu items."""
        self.items = []
        self.selected_index = 0
        self._update_height()

    def _move_selection(self, direction: int) -> None:
        """Move selection up or down, skipping disabled items.

        Args:
            direction: 1 for down, -1 for up
        """
        if not self.items:
            return

        original = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(self.items)

        # Skip disabled items
        attempts = 0
        while not self.items[self.selected_index].enabled:
            self.selected_index = (self.selected_index + direction) % len(self.items)
            attempts += 1
            if attempts >= len(self.items):
                self.selected_index = original
                break

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """Handle keyboard events.

        Args:
            event: Pygame event

        Returns:
            True if an item was activated
        """
        import pygame

        if event.type != pygame.KEYDOWN:
            return False

        # Arrow key navigation
        if event.key == pygame.K_UP:
            self._move_selection(-1)
            return False
        elif event.key == pygame.K_DOWN:
            self._move_selection(1)
            return False

        # Enter to activate
        if event.key == pygame.K_RETURN:
            if self.items and self.items[self.selected_index].enabled:
                callback = self.items[self.selected_index].callback
                if callback:
                    callback()
                    return True
            return False

        # Key-based activation
        key_name = pygame.key.name(event.key).upper()
        for i, item in enumerate(self.items):
            if item.enabled and item.key == key_name:
                self.selected_index = i
                if item.callback:
                    item.callback()
                    return True
                return False

        return False

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the menu.

        Args:
            surface: Surface to draw on
        """
        import pygame

        line_height = int(self._font.get_height() * Typography.LINE_HEIGHT) + 8
        indicator = "\u25ba "  # Right-pointing triangle as arrow

        for i, item in enumerate(self.items):
            y = self.rect.y + i * line_height

            # Determine colors based on state
            is_selected = i == self.selected_index

            if not item.enabled:
                text_color = Colors.TEXT_DIM
                key_color = Colors.TEXT_DIM
            elif is_selected:
                text_color = Colors.TEXT_PRIMARY
                key_color = Colors.SELECTION  # Red for selected key
            else:
                text_color = Colors.TEXT_MUTED
                key_color = Colors.TEXT_MUTED

            # Build the display string
            key_text = f"[{item.key}]"
            full_text = f"{key_text} {item.label}"

            if self.centered:
                # Calculate centered position
                text_surface = self._font.render(
                    full_text, Typography.ANTIALIAS, text_color
                )
                text_width = text_surface.get_width()

                # Add indicator width if selected
                indicator_width = 0
                if is_selected:
                    indicator_surface = self._font.render(
                        indicator, Typography.ANTIALIAS, Colors.SELECTION
                    )
                    indicator_width = indicator_surface.get_width()

                total_width = text_width + indicator_width
                x = self.rect.x + (self.rect.width - total_width) // 2

                # Draw indicator
                if is_selected:
                    surface.blit(indicator_surface, (x, y))
                    x += indicator_width

                # Draw text with key in different color
                # First render key part
                key_surface = self._font.render(
                    key_text, Typography.ANTIALIAS, key_color
                )
                surface.blit(key_surface, (x, y))
                x += key_surface.get_width()

                # Then render rest
                rest_text = f" {item.label}"
                rest_surface = self._font.render(
                    rest_text, Typography.ANTIALIAS, text_color
                )
                surface.blit(rest_surface, (x, y))

            else:
                # Left-aligned
                x = self.rect.x

                # Draw indicator
                if is_selected:
                    indicator_surface = self._font.render(
                        indicator, Typography.ANTIALIAS, Colors.SELECTION
                    )
                    surface.blit(indicator_surface, (x, y))
                    x += indicator_surface.get_width()
                else:
                    x += self._font.size(indicator)[0]  # Space for alignment

                # Draw key
                key_surface = self._font.render(
                    key_text, Typography.ANTIALIAS, key_color
                )
                surface.blit(key_surface, (x, y))
                x += key_surface.get_width()

                # Draw label
                rest_text = f" {item.label}"
                rest_surface = self._font.render(
                    rest_text, Typography.ANTIALIAS, text_color
                )
                surface.blit(rest_surface, (x, y))


class PromptBar:
    """A horizontal bar of keyboard prompts (e.g., "[H] Hint  [W] Walk Away").

    Used at the bottom of panels for quick reference.
    """

    def __init__(
        self,
        x: int,
        y: int,
        prompts: list[tuple[str, str]] | None = None,
    ) -> None:
        """Initialize the prompt bar.

        Args:
            x: X position
            y: Y position
            prompts: List of (key, label) tuples
        """
        self.x = x
        self.y = y
        self.prompts = prompts or []
        self._font = get_fonts().get_small_font()

    def set_prompts(self, prompts: list[tuple[str, str]]) -> None:
        """Set the prompts to display.

        Args:
            prompts: List of (key, label) tuples
        """
        self.prompts = prompts

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the prompt bar.

        Args:
            surface: Surface to draw on
        """
        x = self.x
        spacing = 24

        for key, label in self.prompts:
            # Key in brackets
            key_text = f"[{key.upper()}]"
            key_surface = self._font.render(
                key_text, Typography.ANTIALIAS, Colors.TEXT_MUTED
            )
            surface.blit(key_surface, (x, self.y))
            x += key_surface.get_width() + 4

            # Label
            label_surface = self._font.render(
                label, Typography.ANTIALIAS, Colors.TEXT_DIM
            )
            surface.blit(label_surface, (x, self.y))
            x += label_surface.get_width() + spacing
