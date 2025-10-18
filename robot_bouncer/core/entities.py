"""Core entity definitions for the Robot Bouncer game."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Tuple


class Direction(Enum):
    """Cardinal directions used by the robot."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

    @property
    def delta(self) -> Tuple[int, int]:
        return self.value


@dataclass(frozen=True)
class Position:
    """Represents a 2D position on the game board."""

    x: int
    y: int

    def move(self, direction: Direction) -> "Position":
        dx, dy = direction.delta
        return Position(self.x + dx, self.y + dy)


@dataclass
class Robot:
    """A controllable robot that moves around the board."""

    position: Position
    direction: Direction


@dataclass
class Board:
    """The playing field containing walls and bounce pads."""

    width: int
    height: int
    walls: List[Position] = field(default_factory=list)
    bounce_pads: List[Position] = field(default_factory=list)

    def in_bounds(self, position: Position) -> bool:
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def is_wall(self, position: Position) -> bool:
        return position in self.walls

    def is_bounce_pad(self, position: Position) -> bool:
        return position in self.bounce_pads

    def iter_tiles(self) -> Iterable[Position]:
        for x in range(self.width):
            for y in range(self.height):
                yield Position(x, y)
