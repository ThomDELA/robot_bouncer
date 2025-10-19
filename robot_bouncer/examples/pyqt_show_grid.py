"""Display the Robot Bouncer board using the PyQt renderer."""
from __future__ import annotations

from robot_bouncer.app import GameConfig, RobotBouncerApp
from robot_bouncer.core.entities import Position
from robot_bouncer.visuals.pyqt import PyQtRenderer


def main() -> None:
    """Render a sample board in a PyQt window."""
    renderer = PyQtRenderer(cell_size=56)
    app = RobotBouncerApp(renderer=renderer)

    config = GameConfig(
        width=8,
        height=6,
        walls=[
            Position(2, y) for y in range(1, 5)
        ] + [
            Position(5, y) for y in range(0, 4)
        ],
        pads=[Position(1, 4), Position(6, 1)],
        goals=[Position(7, 5)],
        robot_start=Position(0, 0),
    )

    state = app.create_state(config)
    renderer.display(state)


if __name__ == "__main__":
    main()
