"""Minimal example demonstrating robot movement and bouncing."""
from __future__ import annotations

import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from robot_bouncer.core.engine import BounceRule, GameEngine, GameState
from robot_bouncer.core.entities import Board, Direction, Position, Robot


def main() -> None:
    """Simulate a single robot moving until it hits a wall or goal."""
    board = Board(width=5, height=1)
    robot = Robot(position=Position(0, 0), direction=Direction.EAST)
    goals = [Position(4, 0)]

    engine = GameEngine(rules=[BounceRule()])
    state = GameState(board=board, robot=robot, goals=goals)

    print(f"Start -> position={state.robot.position} direction={state.robot.direction.name}")
    step = 0
    while not state.is_goal_reached() and step < 10:
        step += 1
        engine.step(state)
        print(
            f"Step {step}: position={state.robot.position} direction={state.robot.direction.name}"
        )

    if state.is_goal_reached():
        print("Goal reached!")
    else:
        print("Goal not reached within step limit.")


if __name__ == "__main__":
    main()
