# Robot Bouncer

Robot Bouncer is a lightweight command line interface for playing the board game
**Ricochet Robots**. The rules are faithfully modelled after the official game:

* The board is a 16×16 grid with internal walls. Robots cannot pass through
  walls or other robots.
* When a robot moves in one of the four cardinal directions it continues sliding
  until a wall or another robot stops it. Partial moves are not allowed.
* A puzzle is solved when the designated target robot reaches the target space.
  Other robots may be used as obstacles to help route the target robot.

This project ships with a sample layout (`robot_bouncer/data/default_layout.json`),
but you can load any custom scenario at runtime.

## Getting started

The project has no third‑party dependencies. Launch the interactive interface
with Python 3.9 or newer:

```bash
python -m robot_bouncer
```

Use `help` inside the interface for a list of available commands. You can also
provide a custom layout file:

```bash
python -m robot_bouncer path/to/layout.json
```

### Layout files

Layouts are JSON documents with three sections:

```json
{
  "board": {
    "width": 16,
    "height": 16,
    "walls": [
      [7, 7, "south"],
      [7, 7, "east"]
    ]
  },
  "robots": {
    "red": [2, 1],
    "blue": [13, 3]
  },
  "target": {
    "robot": "red",
    "position": [8, 7]
  }
}
```

Walls are described by the coordinate they originate from and the direction they
block. The loader automatically adds walls around the perimeter of the board, so
layouts only need to describe interior obstacles.

## Development

Run the unit tests with:

```bash
python -m unittest discover
```

The tests cover the movement logic that prevents robots from passing through
walls or other robots.