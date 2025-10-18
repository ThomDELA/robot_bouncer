"""Solver interfaces for Robot Bouncer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from robot_bouncer.core.engine import GameEngine, GameState
from robot_bouncer.core.entities import Position


class SolverResult:
    """Container for solver outputs."""

    def __init__(self, path: Iterable[Position], explored: int = 0, success: bool = False):
        self.path = list(path)
        self.explored = explored
        self.success = success

    def __repr__(self) -> str:
        return f"SolverResult(success={self.success}, steps={len(self.path)}, explored={self.explored})"


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
