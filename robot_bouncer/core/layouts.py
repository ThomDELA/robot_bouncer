"""Predefined board layouts inspired by the original game boards."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

from .entities import Position


@dataclass(frozen=True)
class BoardLayout:
    """Convenience container grouping the elements required to build a board."""

    width: int
    height: int
    walls: Sequence[Position]
    goals: Sequence[Position]
    pads: Sequence[Position] = ()
    robot_start: Position = Position(0, 0)


def _positions_from_coords(coords: Iterable[Tuple[int, int]]) -> Tuple[Position, ...]:
    return tuple(Position(x, y) for x, y in coords)


def classic_board_layout() -> BoardLayout:
    """Return a static layout matching the illustrated 16x16 board."""

    wall_coords = (
        # Central block surrounding the multi-colour goal
        (7, 8),
        (8, 7),
        (8, 8),
        # Top-left quadrant structures
        (3, 1),
        (3, 2),
        (2, 2),
        (6, 3),
        (5, 3),
        (6, 4),
        # Top-right quadrant structures
        (12, 2),
        (13, 1),
        (13, 2),
        (10, 4),
        (10, 5),
        (11, 4),
        # Bottom-left quadrant structures
        (2, 12),
        (2, 13),
        (1, 12),
        (5, 9),
        (6, 9),
        (5, 10),
        # Bottom-right quadrant structures
        (12, 12),
        (13, 12),
        (12, 13),
        (11, 9),
        (11, 10),
        (10, 10),
    )

    goal_coords = (
        # Top-left objectives
        (2, 1),
        (5, 2),
        (1, 4),
        (3, 6),
        # Top-right objectives
        (9, 2),
        (12, 1),
        (14, 3),
        (13, 6),
        # Centre objective (multicolour)
        (7, 7),
        # Bottom-left objectives
        (1, 9),
        (4, 10),
        (2, 14),
        (6, 12),
        # Bottom-right objectives
        (9, 12),
        (10, 9),
        (12, 14),
        (14, 10),
    )

    return BoardLayout(
        width=16,
        height=16,
        walls=_positions_from_coords(wall_coords),
        goals=_positions_from_coords(goal_coords),
        pads=(),
        robot_start=Position(1, 13),
    )


__all__ = ["BoardLayout", "classic_board_layout"]

