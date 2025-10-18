"""Game engine orchestrating the Robot Bouncer mechanics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol

from .entities import Board, Direction, Position, Robot


class Rule(Protocol):
    """Protocol that game rules must implement."""

    def apply(self, state: "GameState") -> None:
        """Mutate the state according to the rule."""


@dataclass
class GameState:
    """Complete snapshot of the game."""

    board: Board
    robot: Robot
    goals: List[Position]

    def is_goal_reached(self) -> bool:
        return self.robot.position in self.goals


class GameEngine:
    """Coordinates the execution of rules on the game state."""

    def __init__(self, rules: Iterable[Rule]):
        self._rules: List[Rule] = list(rules)

    def step(self, state: GameState) -> GameState:
        for rule in self._rules:
            if state.is_goal_reached():
                break
            rule.apply(state)
        return state

    def run_until_goal(self, state: GameState, max_steps: int = 100) -> GameState:
        for _ in range(max_steps):
            self.step(state)
            if state.is_goal_reached():
                break
        return state


class BounceRule:
    """Rule that bounces the robot off walls and pads."""

    def apply(self, state: GameState) -> None:
        next_position = state.robot.position.move(state.robot.direction)
        if not state.board.in_bounds(next_position) or state.board.is_wall(next_position):
            state.robot.direction = self._bounce(state.robot.direction)
        else:
            state.robot.position = next_position
            if state.board.is_bounce_pad(next_position):
                state.robot.direction = self._bounce(state.robot.direction)

    @staticmethod
    def _bounce(direction: Direction) -> Direction:
        horizontal = {Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}
        vertical = {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH}
        return horizontal.get(direction, vertical[direction])


class GoalRule:
    """Stops the robot once it reaches a goal."""

    def apply(self, state: GameState) -> None:
        if state.is_goal_reached():
            return
