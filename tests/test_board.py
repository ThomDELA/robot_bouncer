import unittest

from robot_bouncer.board import Board, Direction, Point


class BoardMovementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board(4, 4)
        # Ensure perimeter walls are present via layout for consistency
        layout = {
            "width": 4,
            "height": 4,
            "walls": [
                [1, 1, "east"],
                [2, 1, "south"],
            ],
        }
        self.board = Board.from_layout(layout)

    def test_move_blocked_by_wall(self) -> None:
        start = Point(1, 1)
        destination = self.board.move_until_blocked(start, Direction.EAST, [])
        self.assertEqual(destination, Point(1, 1))

    def test_move_until_robot(self) -> None:
        start = Point(0, 2)
        occupied = [Point(2, 2)]
        destination = self.board.move_until_blocked(start, Direction.EAST, occupied)
        self.assertEqual(destination, Point(1, 2))


if __name__ == "__main__":
    unittest.main()
