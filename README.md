# Robot Bouncer

This repository implements a small layered Python service themed around a "robot bouncer".  The codebase
focuses on a single slice of functionality: deciding whether a guest may enter a venue and exposing that
logic through a lightweight HTTP interface that powers a browser mini-game.

## Architecture overview

The project follows a conventional ``src`` layout.  The important modules live under ``src/robot_bouncer``:

```text
src/robot_bouncer/
├── adapters/
│   └── repositories/
│       └── in_memory.py        # Dictionary-backed repository implementation
├── config/
│   └── settings.py             # Simple settings dataclass and loader helper
├── domain/
│   ├── board.py                # Board game mechanics used in unit tests
│   ├── entities.py             # Guest entity with admission logic
│   └── exceptions.py           # Domain exception hierarchy
├── interfaces/
│   └── http/
│       ├── app.py              # ThreadingHTTPServer-based mini-game backend
│       └── static/             # Front-end assets served by the HTTP app
└── services/
    └── guard_service.py        # Application service coordinating decisions
```

The domain layer deliberately stays infrastructure-free.  Infrastructure concerns (HTTP serving and in-memory
persistence) live in dedicated packages so they can be swapped or extended without touching the core models.

## Usage example

The ``GuardService`` coordinates access decisions by delegating to a repository and the domain entity:

```python
from datetime import datetime, timedelta

from robot_bouncer.adapters.repositories.in_memory import InMemoryGuestRepository
from robot_bouncer.domain.entities import Guest
from robot_bouncer.services.guard_service import GuardService

repository = InMemoryGuestRepository(
    {
        "vip": Guest(
            identifier="vip",
            name="Val Vega",
            allowed=True,
            allowed_until=datetime.utcnow() + timedelta(hours=1),
        )
    }
)
service = GuardService(repository)

print(service.authorize("vip").name)  # -> "Val Vega"
```

The :mod:`robot_bouncer.domain.board` module provides a small Ricochet Robots style ruleset that is currently
used in unit tests.  It remains available for future gameplay or puzzle extensions.

## Running the HTTP mini-game

A minimal HTTP application ships with the repository.  It serves a static front-end and accepts simple POST
requests so you can test the admission flow in a browser:

```bash
python -m robot_bouncer.interfaces.http.app
```

Open <http://127.0.0.1:8000> to play.  The service randomly cycles through a handful of demo guests and
returns feedback based on whether your decision matches the underlying access rules.

## Tests

Install the project dependencies (``pip install -e .[test]`` if you maintain a local requirements file) and
run the automated test suite with ``pytest``.  The repository includes unit and integration tests covering the
board mechanics and the HTTP application behaviour.
