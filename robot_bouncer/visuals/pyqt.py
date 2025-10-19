"""PyQt renderer capable of showing the game board and commands."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from typing import Iterable, List, Optional, Sequence

from robot_bouncer.core.engine import GameState

from .base import GameRenderer


@dataclass
class _QtBindings:
    """Container for imported Qt modules and compatibility helpers."""

    QtWidgets: object
    QtCore: object
    align_center: object
    frame_box: object


def _load_pyqt() -> _QtBindings:
    """Load PyQt6 or PyQt5 and expose a unified interface."""

    if find_spec("PyQt6") is not None:
        QtWidgets = import_module("PyQt6.QtWidgets")
        QtCore = import_module("PyQt6.QtCore")
        align_center = QtCore.Qt.AlignmentFlag.AlignCenter
        frame_box = getattr(QtWidgets.QFrame, "Shape").Box
        return _QtBindings(
            QtWidgets=QtWidgets,
            QtCore=QtCore,
            align_center=align_center,
            frame_box=frame_box,
        )
    if find_spec("PyQt5") is not None:
        QtWidgets = import_module("PyQt5.QtWidgets")
        QtCore = import_module("PyQt5.QtCore")
        align_center = QtCore.Qt.AlignCenter
        frame_box = getattr(getattr(QtWidgets.QFrame, "Shape", QtWidgets.QFrame), "Box")
        return _QtBindings(
            QtWidgets=QtWidgets,
            QtCore=QtCore,
            align_center=align_center,
            frame_box=frame_box,
        )
    raise ModuleNotFoundError("PyQt6 or PyQt5 is required to use PyQtRenderer.")


class PyQtRenderer(GameRenderer):
    """Render the game state using a PyQt window."""

    def __init__(
        self,
        empty_tile: str = "·",
        wall_tile: str = "█",
        pad_tile: str = "◎",
        goal_tile: str = "★",
        robot_tile: str = "🤖",
        cell_size: int = 48,
    ) -> None:
        self.empty_tile = empty_tile
        self.wall_tile = wall_tile
        self.pad_tile = pad_tile
        self.goal_tile = goal_tile
        self.robot_tile = robot_tile
        self.cell_size = cell_size
        self._qt: Optional[_QtBindings] = None

    def render(self, state: GameState) -> str:
        tiles = self._compose_tiles(state)
        return "\n".join("".join(row) for row in tiles)

    def display(self, state: GameState) -> None:
        self.display_with_commands(state, [])

    def display_with_commands(self, state: GameState, commands: Iterable[str]) -> None:
        qt = self._require_qt()
        QtWidgets = qt.QtWidgets
        commands_list = list(commands)

        app = QtWidgets.QApplication.instance()
        owns_app = False
        if app is None:
            app = QtWidgets.QApplication(["robot-bouncer"])
            owns_app = True

        window = self._create_window(qt, state, commands_list)
        window.show()
        if owns_app:
            exec_method = getattr(app, "exec", None)
            if exec_method is None:
                exec_method = getattr(app, "exec_", None)
            if exec_method is None:
                raise AttributeError("QApplication instance does not provide an exec method.")
            exec_method()

    def _require_qt(self) -> _QtBindings:
        if self._qt is None:
            self._qt = _load_pyqt()
        return self._qt

    def _create_window(
        self,
        qt: _QtBindings,
        state: GameState,
        commands: Sequence[str],
    ) -> object:
        QtWidgets = qt.QtWidgets

        class GameWindow(QtWidgets.QWidget):
            def __init__(self, outer: PyQtRenderer, game_state: GameState, command_list: Sequence[str]):
                super().__init__()
                self._outer = outer
                self._state = game_state
                self._commands = command_list
                self._qt = outer._require_qt()
                self._init_ui()

            def _init_ui(self) -> None:
                self.setWindowTitle("Robot Bouncer")
                layout = self._qt.QtWidgets.QVBoxLayout(self)
                layout.addWidget(self._build_board())
                layout.addWidget(self._build_commands())

            def _build_board(self) -> object:
                board_widget = self._qt.QtWidgets.QGroupBox("Board")
                board_layout = self._qt.QtWidgets.QGridLayout()
                board_layout.setSpacing(0)
                board_layout.setContentsMargins(8, 8, 8, 8)
                tiles = self._outer._compose_tiles(self._state)
                for y, row in enumerate(tiles):
                    for x, cell in enumerate(row):
                        label = self._qt.QtWidgets.QLabel(cell)
                        label.setAlignment(self._qt.align_center)
                        label.setFixedSize(self._outer.cell_size, self._outer.cell_size)
                        label.setFrameShape(self._qt.frame_box)
                        board_layout.addWidget(label, y, x)
                board_widget.setLayout(board_layout)
                return board_widget

            def _build_commands(self) -> object:
                box = self._qt.QtWidgets.QGroupBox("Commands")
                inner = self._qt.QtWidgets.QVBoxLayout()
                if self._commands:
                    for command in self._commands:
                        inner.addWidget(self._qt.QtWidgets.QLabel(command))
                else:
                    inner.addWidget(self._qt.QtWidgets.QLabel("No commands available."))
                box.setLayout(inner)
                return box

        return GameWindow(self, state, commands)

    def _compose_tiles(self, state: GameState) -> List[List[str]]:
        board = state.board
        tiles = [[self.empty_tile for _ in range(board.width)] for _ in range(board.height)]

        for position in board.walls:
            if board.in_bounds(position):
                tiles[position.y][position.x] = self.wall_tile

        for pad in board.bounce_pads:
            if board.in_bounds(pad):
                tiles[pad.y][pad.x] = self.pad_tile

        for goal in state.goals:
            if board.in_bounds(goal):
                tiles[goal.y][goal.x] = self.goal_tile

        robot_pos = state.robot.position
        if board.in_bounds(robot_pos):
            tiles[robot_pos.y][robot_pos.x] = self.robot_tile

        return tiles
