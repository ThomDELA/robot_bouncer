"""Unit tests covering the Robot Bouncer board mechanics."""

from __future__ import annotations

from robot_bouncer.domain.board import (
    BOC,
    BOCOrientation,
    Board,
    Coordinate,
    Direction,
    GameState,
)


def _simple_board() -> Board:
    return Board(width=4, height=4)


def test_robot_moves_until_board_edge() -> None:
    board = _simple_board()
    state = GameState(board=board, robots={"red": Coordinate(1, 1)})

    moved = state.move("red", Direction.NORTH)

    assert moved.robots["red"] == Coordinate(1, 0)


def test_robot_stops_before_other_robot() -> None:
    board = _simple_board()
    state = GameState(
        board=board,
        robots={
            "red": Coordinate(1, 1),
            "blue": Coordinate(3, 1),
        },
    )

    moved = state.move("red", Direction.EAST)

    assert moved.robots["red"] == Coordinate(2, 1)


def test_robot_passes_through_matching_boc() -> None:
    board = _simple_board()
    board.bocs[Coordinate(2, 1)] = BOC("red", BOCOrientation.SLASH)
    state = GameState(board=board, robots={"red": Coordinate(1, 1)})

    moved = state.move("red", Direction.EAST)

    assert moved.robots["red"] == Coordinate(3, 1)


def test_robot_deflects_on_non_matching_boc() -> None:
    board = _simple_board()
    board.bocs[Coordinate(2, 1)] = BOC("green", BOCOrientation.SLASH)
    state = GameState(board=board, robots={"red": Coordinate(1, 1)})

    moved = state.move("red", Direction.EAST)

    assert moved.robots["red"] == Coordinate(2, 0)
