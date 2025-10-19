"""Minimal working example for rendering the Robot Bouncer board."""
from __future__ import annotations

from robot_bouncer.app import GameConfig, RobotBouncerApp
from robot_bouncer.core.layouts import classic_board_layout
from robot_bouncer.visuals.console import ConsoleRenderer


def main() -> None:
    """Create a sample game state and render it to the console."""
    renderer = ConsoleRenderer()
    app = RobotBouncerApp(renderer=renderer)

    layout = classic_board_layout()
    config = GameConfig(
        width=layout.width,
        height=layout.height,
        walls=layout.walls,
        pads=layout.pads,
        goals=layout.goals,
        robot_start=layout.robot_start,
    )

    state = app.create_state(config)
    print(renderer.render(state))


if __name__ == "__main__":
    main()
