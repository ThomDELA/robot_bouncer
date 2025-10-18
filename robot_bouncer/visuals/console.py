"""Console renderer implementation."""
from __future__ import annotations

from robot_bouncer.core.engine import GameState
from robot_bouncer.core.entities import Position

from .base import GameRenderer


class ConsoleRenderer(GameRenderer):
    """Renders the game state using ASCII characters."""

    def __init__(self, empty_tile: str = ".", wall_tile: str = "#", pad_tile: str = "*", goal_tile: str = "G", robot_tile: str = "R"):
        self.empty_tile = empty_tile
        self.wall_tile = wall_tile
        self.pad_tile = pad_tile
        self.goal_tile = goal_tile
        self.robot_tile = robot_tile

    def render(self, state: GameState) -> str:
        board = state.board
        tiles = [[self.empty_tile for _ in range(board.width)] for _ in range(board.height)]

        for wall in board.walls:
            if board.in_bounds(wall):
                tiles[wall.y][wall.x] = self.wall_tile

        for pad in board.bounce_pads:
            if board.in_bounds(pad):
                tiles[pad.y][pad.x] = self.pad_tile

        for goal in state.goals:
            if board.in_bounds(goal):
                tiles[goal.y][goal.x] = self.goal_tile

        robot_pos = state.robot.position
        if board.in_bounds(robot_pos):
            tiles[robot_pos.y][robot_pos.x] = self.robot_tile

        return "\n".join("".join(row) for row in tiles)

    @staticmethod
    def to_lines(rendered: str) -> list[str]:
        return rendered.splitlines()

    def highlight_path(self, state: GameState, path: list[Position], path_tile: str = "+") -> str:
        board = state.board
        tiles = [list(row) for row in self.render(state).splitlines()]
        for position in path:
            if board.in_bounds(position):
                tiles[position.y][position.x] = path_tile
        tiles[state.robot.position.y][state.robot.position.x] = self.robot_tile
        return "\n".join("".join(row) for row in tiles)
