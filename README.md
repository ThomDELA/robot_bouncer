# Robot Bouncer

A Python-based service that determines whether a guest should be granted access by a robot bouncer. This repository currently contains the foundational project architecture and example code to illustrate how different layers interact.

## Project layout

```
robot_bouncer/
├── src/
│   └── robot_bouncer/
│       ├── __init__.py
│       ├── adapters/
│       │   └── repositories/
│       │       └── in_memory.py
│       ├── config/
│       │   └── settings.py
│       ├── domain/
│       │   ├── entities.py
│       │   └── exceptions.py
│       ├── interfaces/
│       │   └── http/
│       │       └── app.py
│       └── services/
│           └── guard_service.py
├── tests/
│   ├── integration/
│   └── unit/
│       └── test_guard_service.py
└── README.md
```

## Architectural overview

The codebase is organized around a layered architecture:

- **Domain layer (`src/robot_bouncer/domain`)** – Contains entities and domain-specific exceptions that represent core business logic without infrastructure concerns.
- **Application layer (`src/robot_bouncer/services`)** – Hosts orchestrating services that coordinate domain objects and enforce business workflows.
- **Adapters layer (`src/robot_bouncer/adapters`)** – Provides infrastructure implementations, such as repositories, that satisfy protocols defined in the application layer.
- **Interface layer (`src/robot_bouncer/interfaces`)** – Entry points that expose the application to the outside world (HTTP, CLI, etc.).
- **Configuration (`src/robot_bouncer/config`)** – Centralized settings and configuration utilities shared across the application.
- **Tests (`tests/`)** – Structured into `unit` and `integration` packages to keep fast tests separated from broader integration coverage.

This skeleton is designed to grow with the project. Each layer is kept independent so future changes—such as swapping persistence technologies or adding new interfaces—can be made with minimal coupling.
