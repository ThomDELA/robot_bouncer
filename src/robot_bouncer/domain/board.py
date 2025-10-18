"""Domain models representing the *Robot Bouncer* board game.

The implementation focuses on the mechanical aspects described in the
user-provided rule book: robots ricochet in straight lines until they hit an
obstacle, coloured diagonal barriers (``BOC``) may deflect them, and other
robots act as mobile obstacles.  The goal of the module is to provide a
lightweight but strongly-typed API that other layers (or puzzles) can use to
simulate the game.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Mapping, MutableMapping, Set


@dataclass(frozen=True, slots=True)
class Coordinate:
    """Two dimensional position on the board."""

    x: int
    y: int

    def translate(self, direction: "Direction") -> "Coordinate":
        """Return a new coordinate shifted by one step in ``direction``."""

        dx, dy = direction.delta
        return Coordinate(self.x + dx, self.y + dy)


class Direction(Enum):
    """Cardinal directions available to robot movement."""

    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @property
    def delta(self) -> tuple[int, int]:
        """Return the ``(dx, dy)`` translation vector for the direction."""

        return self.value

    @property
    def opposite(self) -> "Direction":
        """Return the direction that points 180° away."""

        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return opposites[self]


class BOCOrientation(Enum):
    """Orientation of a Barrière Oblique Colorée (coloured diagonal barrier)."""

    SLASH = "/"
    BACKSLASH = "\\"


@dataclass(frozen=True, slots=True)
class BOC:
    """Coloured diagonal barrier that may deflect robots."""

    color: str
    orientation: BOCOrientation

    def allows(self, robot_color: str) -> bool:
        """Return ``True`` when the robot is the same colour as the barrier."""

        return self.color.lower() == robot_color.lower()

    def deflect(self, direction: Direction) -> Direction:
        """Return the direction after the 90° deflection."""

        if self.orientation is BOCOrientation.SLASH:
            mapping = {
                Direction.NORTH: Direction.EAST,
                Direction.EAST: Direction.NORTH,
                Direction.SOUTH: Direction.WEST,
                Direction.WEST: Direction.SOUTH,
            }
        else:  # BOCOrientation.BACKSLASH
            mapping = {
                Direction.NORTH: Direction.WEST,
                Direction.WEST: Direction.NORTH,
                Direction.SOUTH: Direction.EAST,
                Direction.EAST: Direction.SOUTH,
            }
        return mapping[direction]


@dataclass(slots=True)
class Board:
    """Representation of a Ricochet Robots board."""

    width: int
    height: int
    walls: MutableMapping[Coordinate, Set[Direction]] = field(default_factory=dict)
    blockers: Set[Coordinate] = field(default_factory=set)
    bocs: MutableMapping[Coordinate, BOC] = field(default_factory=dict)

    def contains(self, coordinate: Coordinate) -> bool:
        """Return ``True`` when the coordinate is within board bounds."""

        return 0 <= coordinate.x < self.width and 0 <= coordinate.y < self.height

    def add_wall(self, position: Coordinate, direction: Direction) -> None:
        """Place a wall emanating from ``position`` in ``direction``."""

        self.walls.setdefault(position, set()).add(direction)
        neighbour = position.translate(direction)
        if self.contains(neighbour):
            self.walls.setdefault(neighbour, set()).add(direction.opposite)

    def is_blocked(self, position: Coordinate, direction: Direction) -> bool:
        """Return ``True`` when a wall blocks travel from ``position``."""

        return direction in self.walls.get(position, set())

    def travel(
        self,
        start: Coordinate,
        direction: Direction,
        occupied: Mapping[str, Coordinate],
        robot_color: str,
    ) -> Coordinate:
        """Return the square where a robot stops after moving in ``direction``."""

        position = start
        current_direction = direction
        occupied_positions = {coord for coord in occupied.values() if coord != start}

        while True:
            if self.is_blocked(position, current_direction):
                break

            candidate = position.translate(current_direction)
            if not self.contains(candidate):
                break
            if candidate in self.blockers:
                break
            if candidate in occupied_positions:
                break

            position = candidate
            boc = self.bocs.get(position)
            if boc and not boc.allows(robot_color):
                current_direction = boc.deflect(current_direction)
                continue

        return position


@dataclass(slots=True)
class GameState:
    """Immutable snapshot of the robots on the board."""

    board: Board
    robots: Dict[str, Coordinate]

    def move(self, robot_color: str, direction: Direction) -> "GameState":
        """Return a new state after moving ``robot_color`` in ``direction``."""

        if robot_color not in self.robots:
            raise KeyError(f"Unknown robot colour: {robot_color!r}")

        start = self.robots[robot_color]
        other_positions = {
            colour: coordinate
            for colour, coordinate in self.robots.items()
            if colour != robot_color
        }
        destination = self.board.travel(start, direction, other_positions, robot_color)

        if destination == start:
            return self

        new_positions = dict(self.robots)
        new_positions[robot_color] = destination
        return GameState(board=self.board, robots=new_positions)

    def iter_robots(self) -> Iterable[tuple[str, Coordinate]]:
        """Yield ``(colour, coordinate)`` pairs for each robot."""

        return self.robots.items()
