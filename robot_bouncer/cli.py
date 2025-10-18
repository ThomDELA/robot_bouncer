"""Command line interface to play Robot Ricochet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .board import load_layout_from_dict
from .game import GameState, parse_direction


def load_layout(path: Path) -> GameState:
    raw = json.loads(path.read_text())
    board, robots, (target_robot, target_point) = load_layout_from_dict(raw)
    return GameState(board, robots, target_robot, target_point)


def default_layout() -> GameState:
    data_path = Path(__file__).resolve().parent / "data" / "default_layout.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Default layout missing at {data_path}")
    return load_layout(data_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Robot Ricochet in the terminal")
    parser.add_argument(
        "layout",
        nargs="?",
        type=Path,
        help="Optional JSON layout to load",
    )
    return parser.parse_args()


def interactive_loop(state: GameState) -> None:
    print("Welcome to Robot Ricochet! Type 'help' for a list of commands.")
    while True:
        print()
        print(state.to_ascii())
        if state.is_solved():
            print("Congratulations! You've solved the puzzle in", len(state.history), "moves.")
            return
        try:
            command = input("> ").strip()
        except EOFError:
            print()
            return
        if not command:
            continue
        if command in {"quit", "exit"}:
            return
        if command == "help":
            print("Commands: move <robot> <direction>, reset, robots, target, help, quit")
            continue
        if command == "robots":
            for name, point in state.robots.items():
                marker = "*" if name == state.target_robot else " "
                print(f"{marker}{name}: ({point.x}, {point.y})")
            continue
        if command == "target":
            print(
                f"Target robot '{state.target_robot}' must reach ({state.target_point.x}, {state.target_point.y})."
            )
            continue
        if command == "reset":
            state.reset()
            continue
        if command.startswith("move"):
            parts = command.split()
            if len(parts) != 3:
                print("Usage: move <robot> <direction>")
                continue
            _, robot, direction_text = parts
            try:
                direction = parse_direction(direction_text)
            except ValueError as exc:
                print(exc)
                continue
            moved = state.move(robot, direction)
            if not moved:
                print("That robot cannot move in that direction.")
            continue
        print("Unknown command. Type 'help' for assistance.")


def main() -> None:
    args = parse_args()
    if args.layout:
        state = load_layout(args.layout)
    else:
        state = default_layout()
    interactive_loop(state)


if __name__ == "__main__":
    main()
