"""Game state management for Robot Ricochet."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Tuple

from .board import Board, Direction, Point


@dataclass
class GameState:
    """Mutable game state representing the puzzle in progress."""

    board: Board
    robots: Dict[str, Point]
    target_robot: str
    target_point: Point
    history: List[Tuple[str, Direction]]
    _start_positions: Dict[str, Point]

    def __init__(
        self,
        board: Board,
        robots: Mapping[str, Point],
        target_robot: str,
        target_point: Point,
    ) -> None:
        self.board = board
        self._start_positions = {name: Point(pos.x, pos.y) for name, pos in robots.items()}
        self.robots = {name: Point(pos.x, pos.y) for name, pos in robots.items()}
        self.target_robot = target_robot
        self.target_point = target_point
        self.history = []

    def move(self, robot: str, direction: Direction) -> bool:
        """Move the robot in the given direction if it can travel."""

        if robot not in self.robots:
            raise KeyError(f"Unknown robot '{robot}'")
        start = self.robots[robot]
        destination = self.board.move_until_blocked(
            start, direction, self.robots.values()
        )
        if destination == start:
            return False
        self.robots[robot] = destination
        self.history.append((robot, direction))
        return True

    def is_solved(self) -> bool:
        return self.robots[self.target_robot] == self.target_point

    def reset(self) -> None:
        self.robots = {name: Point(pos.x, pos.y) for name, pos in self._start_positions.items()}
        self.history.clear()

    def to_ascii(self) -> str:
        return self.board.to_ascii(self.robots, (self.target_robot, self.target_point))


def parse_direction(value: str) -> Direction:
    normalized = value.lower()
    for direction in Direction:
        if direction.value.startswith(normalized):
            return direction
    raise ValueError(f"Unknown direction '{value}'")
