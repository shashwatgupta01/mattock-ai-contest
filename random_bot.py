from random import choice
from board import Board, Space, Coordinate


class RandomPlayer:

    count = 0

    def __init__(self):
        self.name = f"rando_{RandomPlayer.count}"
        RandomPlayer.count += 1

    def mine(self, board: Board, color: Space) -> Coordinate:
        mineable = board.mineable_by_player(color)
        return choice(tuple(mineable))

    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate] | None:
        pieces = board.find_all(color)
        start = choice(tuple(pieces))
        ends = board.walkable_from_coord(start)
        if len(ends) == 0:
            return None
        return start, choice(tuple(ends))
