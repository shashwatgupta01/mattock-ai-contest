import pytest
from board import Space
from game import Game
from random_bot import RandomPlayer


@pytest.fixture
def blank_game() -> Game:
    game = Game(RandomPlayer(), RandomPlayer(), small=True)
    game.board.cells = {coord: Space.WALL for coord in game.board.cells}
    return game


def test_kill(blank_game: Game):
    g = blank_game
    g.board[0, 0] = Space.EMPTY
    g.board[0, -1] = Space.RED
    g.board[1, 0] = Space.RED
    g.board[-1, 1] = Space.BLUE
    g.red_turn = True
    assert g.board.is_miner_dead((-1, 1))
    g.clear_dead(Space.RED)
    assert g.board[0, 0] == Space.EMPTY
    assert g.board[0, -1] == Space.RED
    assert g.board[1, 0] == Space.RED
    assert g.board[-1, 1] == Space.BLUE
    g.clear_dead(Space.BLUE)
    assert g.board[0, 0] == Space.EMPTY
    assert g.board[0, -1] == Space.RED
    assert g.board[1, 0] == Space.RED
    assert g.board[-1, 1] == Space.EMPTY

