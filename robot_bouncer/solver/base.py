"""Solver interfaces for Robot Bouncer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

from robot_bouncer.core.engine import GameEngine, GameState
from robot_bouncer.core.entities import Direction, Position


class SolverResult:
    """Container for solver outputs."""

    def __init__(self, path: Iterable[Position], explored: int = 0, success: bool = False):
        self.path = list(path)
        self.explored = explored
        self.success = success

    def __repr__(self) -> str:
        return f"SolverResult(success={self.success}, steps={len(self.path)}, explored={self.explored})"

    def to_commands(self) -> List[str]:
        """Translate the path into human-readable movement commands."""

        commands: List[str] = []
        if len(self.path) < 2:
            return commands

        previous = self.path[0]
        for current in self.path[1:]:
            dx = current.x - previous.x
            dy = current.y - previous.y
            direction = self._direction_from_delta(dx, dy)
            commands.append(self._format_command(direction, current))
            previous = current
        return commands

    @staticmethod
    def _direction_from_delta(dx: int, dy: int) -> Direction:
        if dx == 0 and dy == 0:
            raise ValueError("Consecutive positions in the solver path must be distinct.")
        if dx > 0:
            return Direction.EAST
        if dx < 0:
            return Direction.WEST
        if dy > 0:
            return Direction.SOUTH
        return Direction.NORTH

    @staticmethod
    def _format_command(direction: Direction, destination: Position) -> str:
        name = direction.name.capitalize()
        return f"Move {name} to ({destination.x}, {destination.y})"


class GameSolver(ABC):
    """Abstract solver capable of guiding the robot to a goal."""

    def __init__(self, engine: GameEngine):
        self.engine = engine

    @abstractmethod
    def solve(self, state: GameState) -> SolverResult:
        """Attempt to solve the game and return a result."""

    def apply_solution(self, state: GameState, result: SolverResult) -> GameState:
        for position in result.path:
            state.robot.position = position
        return state


class NoOpSolver(GameSolver):
    """Fallback solver that does nothing."""

    def solve(self, state: GameState) -> SolverResult:
        return SolverResult(path=[state.robot.position], explored=0, success=state.is_goal_reached())
