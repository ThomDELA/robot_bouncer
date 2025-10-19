"""High-level façade for configuring and running Robot Bouncer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from robot_bouncer.core.engine import BounceRule, GameEngine, GameState
from robot_bouncer.core.entities import Board, Position, Robot
from robot_bouncer.visuals.base import GameRenderer
from robot_bouncer.visuals.console import ConsoleRenderer
from robot_bouncer.solver.base import GameSolver
from robot_bouncer.solver.bfs import BfsSolver


@dataclass
class GameConfig:
    width: int = 5
    height: int = 5
    walls: Optional[Iterable[Position]] = None
    pads: Optional[Iterable[Position]] = None
    goals: Optional[Iterable[Position]] = None
    robot_start: Position = Position(0, 0)


class RobotBouncerApp:
    """Application coordinator hooking engine, renderer and solver."""

    def __init__(
        self,
        renderer: Optional[GameRenderer] = None,
        solver: Optional[GameSolver] = None,
    ) -> None:
        self.renderer = renderer or ConsoleRenderer()
        self.solver = solver

    def create_state(self, config: GameConfig) -> GameState:
        board = Board(
            width=config.width,
            height=config.height,
            walls=list(config.walls or []),
            bounce_pads=list(config.pads or []),
        )
        robot = Robot(position=config.robot_start, direction=self._default_direction(config))
        goals = list(config.goals or [Position(config.width - 1, config.height - 1)])
        return GameState(board=board, robot=robot, goals=goals)

    def _default_direction(self, config: GameConfig):
        from robot_bouncer.core.entities import Direction

        return Direction.EAST if config.width > 1 else Direction.SOUTH

    def build_engine(self) -> GameEngine:
        return GameEngine(rules=[BounceRule()])

    def ensure_solver(self, engine: GameEngine) -> GameSolver:
        return self.solver or BfsSolver(engine)

    def run(self, config: GameConfig) -> GameState:
        state = self.create_state(config)
        engine = self.build_engine()
        solver = self.ensure_solver(engine)
        result = solver.solve(state)
        solver.apply_solution(state, result)
        commands = result.to_commands()
        if commands:
            self.renderer.display_with_commands(state, commands)
        else:
            self.renderer.display(state)
        return state
