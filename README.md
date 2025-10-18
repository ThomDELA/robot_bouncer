# Robot Bouncer

This repository provides a modular architecture for the Robot Bouncer game. The system is ready to host
multiple independent features:

- **Game mechanics** implemented in `robot_bouncer.core`, where entities and the rule-based engine live.
- **Game visuals** exposed through the `robot_bouncer.visuals` package. A console renderer is included
  as a reference implementation.
- **Game solvers** defined in `robot_bouncer.solver`, featuring pluggable solver strategies such as a
  breadth-first search (BFS) solver.

## Project layout

```
robot_bouncer/
├── app.py                 # Application façade wiring together engine, renderer, and solver
├── core/                  # Game mechanics domain layer
│   ├── engine.py          # Rule-based engine and state representation
│   └── entities.py        # Core data structures (board, robot, positions)
├── visuals/               # Rendering abstractions and implementations
│   ├── base.py            # Renderer protocol
│   └── console.py         # ASCII console renderer
└── solver/                # Solver abstractions and algorithms
    ├── base.py            # Solver base classes and result container
    └── bfs.py             # Breadth-first search solver implementation
```

## Usage example

```python
from robot_bouncer.app import GameConfig, RobotBouncerApp
from robot_bouncer.core.entities import Position

app = RobotBouncerApp()
config = GameConfig(
    width=7,
    height=5,
)
state = app.run(config)
```

This skeleton is designed to grow with the project. Each layer is kept independent so future changes—such as swapping persistence technologies or adding new interfaces—can be made with minimal coupling.

## Playing the mini-game locally

The repository bundles a lightweight web experience so you can try the robot bouncer rules without extra dependencies.

1. From the project root run the HTTP server:

   ```bash
   python -m robot_bouncer.interfaces.http.app
   ```

2. Open <http://127.0.0.1:8000> in a browser. A single-page app served from the project will appear with story prompts for
   each guest. Decide whether to allow or deny entry and see your score update in real time.
