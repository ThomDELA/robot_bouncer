"""Breadth-first search solver for Robot Bouncer."""
from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Optional

from robot_bouncer.core.engine import GameEngine, GameState
from robot_bouncer.core.entities import Direction, Position

from .base import GameSolver, SolverResult


class BfsSolver(GameSolver):
    """Simple BFS solver on the discrete grid."""

    def __init__(self, engine: GameEngine, allowed_directions: Optional[Iterable[Direction]] = None):
        super().__init__(engine)
        self.allowed_directions = list(allowed_directions or Direction)

    def solve(self, state: GameState) -> SolverResult:
        start = state.robot.position
        goals = set(state.goals)
        queue = deque([start])
        parents: Dict[Position, Optional[Position]] = {start: None}
        explored = 0

        board = state.board
        while queue:
            current = queue.popleft()
            explored += 1
            if current in goals:
                path = self._reconstruct_path(current, parents)
                return SolverResult(path=path, explored=explored, success=True)

            for direction in self.allowed_directions:
                next_position = current.move(direction)
                if not board.in_bounds(next_position) or board.is_wall(next_position):
                    continue
                if next_position in parents:
                    continue
                parents[next_position] = current
                queue.append(next_position)

        return SolverResult(path=[start], explored=explored, success=False)

    @staticmethod
    def _reconstruct_path(goal: Position, parents: Dict[Position, Optional[Position]]) -> List[Position]:
        path: List[Position] = []
        current: Optional[Position] = goal
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()
        return path
