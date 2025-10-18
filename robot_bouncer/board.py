"""Core board representation for Robot Ricochet."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Mapping, MutableSequence, Optional, Set, Tuple


class Direction(str, Enum):
    """Cardinal directions used by both walls and robot movement."""

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

    @property
    def delta(self) -> Tuple[int, int]:
        if self is Direction.NORTH:
            return (0, -1)
        if self is Direction.EAST:
            return (1, 0)
        if self is Direction.SOUTH:
            return (0, 1)
        if self is Direction.WEST:
            return (-1, 0)
        raise ValueError(f"Unsupported direction {self}")

    @property
    def opposite(self) -> "Direction":
        if self is Direction.NORTH:
            return Direction.SOUTH
        if self is Direction.EAST:
            return Direction.WEST
        if self is Direction.SOUTH:
            return Direction.NORTH
        if self is Direction.WEST:
            return Direction.EAST
        raise ValueError(f"Unsupported direction {self}")


@dataclass(frozen=True)
class Point:
    """Simple coordinate value."""

    x: int
    y: int

    def translate(self, direction: Direction, steps: int = 1) -> "Point":
        dx, dy = direction.delta
        return Point(self.x + dx * steps, self.y + dy * steps)


class Board:
    """Board state containing wall information."""

    width: int
    height: int
    _walls: Dict[Point, Set[Direction]]

    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Board must be positive in both dimensions")
        self.width = width
        self.height = height
        self._walls = {}

    def add_wall(self, point: Point, direction: Direction) -> None:
        """Add a blocking wall in the given direction from the point."""

        if not self.in_bounds(point):
            raise ValueError(f"Point {point} is outside of the board")
        if direction not in Direction:
            raise ValueError(f"Unknown direction {direction}")

        self._walls.setdefault(point, set()).add(direction)
        neighbor = point.translate(direction)
        if self.in_bounds(neighbor):
            self._walls.setdefault(neighbor, set()).add(direction.opposite)

    def walls_at(self, point: Point) -> Set[Direction]:
        return self._walls.get(point, set())

    def in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def move_until_blocked(
        self, start: Point, direction: Direction, occupied: Iterable[Point]
    ) -> Point:
        """Move from start toward direction until a wall or robot blocks the way."""

        occupied_lookup = {p for p in occupied if p != start}
        current = start
        while True:
            if direction in self.walls_at(current):
                break
            next_point = current.translate(direction)
            if not self.in_bounds(next_point):
                break
            if next_point in occupied_lookup:
                break
            current = next_point
        return current

    @classmethod
    def from_layout(cls, layout: Mapping[str, object]) -> "Board":
        width = int(layout["width"])
        height = int(layout["height"])
        board = cls(width, height)

        # Add perimeter walls by default
        for x in range(width):
            board.add_wall(Point(x, 0), Direction.NORTH)
            board.add_wall(Point(x, height - 1), Direction.SOUTH)
        for y in range(height):
            board.add_wall(Point(0, y), Direction.WEST)
            board.add_wall(Point(width - 1, y), Direction.EAST)

        for raw_wall in layout.get("walls", []):
            x, y, direction = raw_wall
            board.add_wall(Point(int(x), int(y)), Direction(direction))

        return board

    def to_ascii(
        self,
        robots: Mapping[str, Point],
        target: Optional[Tuple[str, Point]] = None,
    ) -> str:
        """Render the board using ASCII characters."""

        rows: MutableSequence[str] = []
        for y in range(self.height):
            # Horizontal boundary on top of the row
            top_segments: MutableSequence[str] = []
            for x in range(self.width):
                point = Point(x, y)
                top_segments.append("---" if Direction.NORTH in self.walls_at(point) else "   ")
            rows.append("+" + "+".join(top_segments) + "+")

            # Cell contents row with vertical walls
            cell_row = []
            for x in range(self.width):
                point = Point(x, y)
                is_target = bool(target and target[1] == point)
                left = "(" if is_target else " "
                right = ")" if is_target else " "
                center = " "
                for name, location in robots.items():
                    if location == point:
                        center = name[0].upper()
                        break
                else:
                    if is_target:
                        center = target[0][0].lower()
                contents = f"{left}{center}{right}"
                left_wall = "|" if Direction.WEST in self.walls_at(point) else " "
                cell_row.append(left_wall + contents)
            last_point = Point(self.width - 1, y)
            right_wall = "|" if Direction.EAST in self.walls_at(last_point) else " "
            rows.append("".join(cell_row) + right_wall)

        # Bottom boundary after the last row
        bottom_segments: MutableSequence[str] = []
        for x in range(self.width):
            point = Point(x, self.height - 1)
            bottom_segments.append("---" if Direction.SOUTH in self.walls_at(point) else "   ")
        rows.append("+" + "+".join(bottom_segments) + "+")

        return "\n".join(rows)


def load_layout_from_dict(data: Mapping[str, object]) -> Tuple[Board, Dict[str, Point], Tuple[str, Point]]:
    board = Board.from_layout(data["board"])
    robots = {name: Point(*pos) for name, pos in data["robots"].items()}
    target_info = data.get("target")
    if not target_info:
        raise ValueError("Layout is missing target info")
    target_robot = target_info.get("robot")
    target_point = Point(*target_info["position"])
    if target_robot not in robots:
        raise ValueError(f"Target robot '{target_robot}' is not defined")
    if not board.in_bounds(target_point):
        raise ValueError("Target position is out of bounds")
    return board, robots, (target_robot, target_point)
