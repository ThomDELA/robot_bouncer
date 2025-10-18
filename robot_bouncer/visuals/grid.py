"""Utilities to build and interact with a visual game board grid."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from robot_bouncer.core.engine import GameState
from robot_bouncer.core.entities import Board, Direction, Position, Robot

from .console import ConsoleRenderer


@dataclass
class InteractiveBoard:
    """Helper class to manage a 16x16 board and render it on the console."""

    width: int = 16
    height: int = 16
    walls: Iterable[Position] = field(default_factory=list)
    goals: Iterable[Position] = field(default_factory=list)
    renderer: ConsoleRenderer = field(default_factory=ConsoleRenderer)

    def __post_init__(self) -> None:
        board = Board(
            width=self.width,
            height=self.height,
            walls=list(self.walls),
            bounce_pads=[],
        )
        robot = Robot(position=Position(0, 0), direction=Direction.EAST)
        self._state = GameState(board=board, robot=robot, goals=list(self.goals))

    @property
    def state(self) -> GameState:
        """Return a copy-like representation of the current game state."""

        board = self._state.board
        robot = self._state.robot
        return GameState(
            board=Board(
                width=board.width,
                height=board.height,
                walls=list(board.walls),
                bounce_pads=list(board.bounce_pads),
            ),
            robot=Robot(position=robot.position, direction=robot.direction),
            goals=list(self._state.goals),
        )

    def place_robot(self, position: Position) -> None:
        """Place the robot on the board if the tile is valid."""

        board = self._state.board
        if not board.in_bounds(position):
            raise ValueError("Robot position must be inside the board bounds.")
        if board.is_wall(position):
            raise ValueError("Robot cannot be placed on a wall.")
        self._state.robot.position = position

    def add_walls(self, *positions: Position) -> None:
        """Add one or many walls to the board."""

        board = self._state.board
        for position in positions:
            if not board.in_bounds(position):
                raise ValueError("Wall position must be inside the board bounds.")
            if position not in board.walls:
                board.walls.append(position)

    def clear_walls(self) -> None:
        """Remove all walls from the board."""

        self._state.board.walls.clear()

    def move_robot(self, direction: Direction) -> Position:
        """Move the robot in the specified direction until it hits an obstacle."""

        self._state.robot.direction = direction
        board = self._state.board

        current = self._state.robot.position
        while True:
            next_position = current.move(direction)
            if not board.in_bounds(next_position) or board.is_wall(next_position):
                break
            current = next_position

        self._state.robot.position = current
        return current

    def render(self) -> str:
        """Render the current state of the board."""

        return self.renderer.render(self._state)

    def render_with_path(self, path: List[Position]) -> str:
        """Render the board highlighting a path."""

        return self.renderer.highlight_path(self._state, path)
