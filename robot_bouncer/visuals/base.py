"""Rendering interfaces for Robot Bouncer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol

from robot_bouncer.core.engine import GameState


class SupportsRender(Protocol):
    """Protocol for objects that can be rendered by a renderer."""

    def as_render_state(self) -> GameState:
        """Return a snapshot that can be rendered."""


class GameRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def render(self, state: GameState) -> str:
        """Render the given game state into a human-readable representation."""

    def display(self, state: GameState) -> None:
        """Render and print the state."""

        print(self.render(state))

    def display_with_commands(self, state: GameState, commands: Iterable[str]) -> None:
        """Display the state alongside the commands required to reach it."""

        self.display(state)
        for command in commands:
            print(command)
