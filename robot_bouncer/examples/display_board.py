"""Minimal working example for rendering the Robot Bouncer board."""
from __future__ import annotations

from robot_bouncer.app import GameConfig, RobotBouncerApp
from robot_bouncer.core.entities import Position
from robot_bouncer.visuals.console import ConsoleRenderer


def main() -> None:
    """Create a sample game state and render it to the console."""
    renderer = ConsoleRenderer()
    app = RobotBouncerApp(renderer=renderer)

    config = GameConfig(
        width=7,
        height=5,
        walls=[Position(3, y) for y in range(5)],
        pads=[Position(1, 2), Position(5, 1)],
        goals=[Position(6, 4)],
        robot_start=Position(0, 0),
    )

    state = app.create_state(config)
    print(renderer.render(state))


if __name__ == "__main__":
    main()
