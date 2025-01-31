from copy import deepcopy
import time
import traceback
from typing import Protocol
from multiprocessing import Pool, TimeoutError

from board import Coordinate, Board, Space


class Player(Protocol):

    @property
    def name(self) -> str: ...

    def mine(self, board: Board, color: Space) -> Coordinate: ...

    def move(
        self, board: Board, color: Space
    ) -> tuple[Coordinate, Coordinate] | None: ...


class Game:

    def __init__(
        self,
        red: Player,
        blue: Player,
        small: bool = False,
        time_per_move: float = 1.0,
        wait_full_time: bool = False,
    ):
        self.players = {Space.RED: red, Space.BLUE: blue}  # red, blue
        self.red_turn = True
        self.board = Board(small)
        self.winner: Space | None = None
        self.time_per_move = time_per_move
        self.wait_full_time = wait_full_time

    def step(self):
        if self.winner:
            return
        player_color = Space.RED if self.red_turn else Space.BLUE
        other_color = Space.BLUE if self.red_turn else Space.RED
        player = self.players[player_color]
        # Check if a player just lost by not being able to mine
        if len(self.board.mineable_by_player(player_color)) == 0:
            self.winner = other_color
            return
        # Current player needs to dig out a space
        with Pool(processes=2) as pool:
            delay = pool.apply_async(time.sleep, (self.time_per_move,))
            mine_res = pool.apply_async(
                player.mine, (deepcopy(self.board), player_color)
            )
            try:
                if self.wait_full_time:
                    delay.get()
                mine_coord = mine_res.get(1)
            # Player crashed or timed out
            except TimeoutError:
                self.winner = other_color
                print(f"{player.name} timed out!")
                return
            except Exception:
                self.winner = other_color
                print(f"{player.name} crashed!")
                traceback.print_exc()
                return
        # Current player made an illegal dig
        if not self.board.is_mineable(mine_coord):
            print(f"{player.name} illegally tried to mine at {mine_coord}")
            self.winner = other_color
            return
        # Dig out the space
        self.board[mine_coord] = (
            Space.EMPTY
            if self.board.count_elements(player_color) == self.board.miner_count
            else player_color
        )
        # Current player may move
        with Pool(processes=2) as pool:
            delay = pool.apply_async(time.sleep, (self.time_per_move,))
            move_res = pool.apply_async(
                player.move, (deepcopy(self.board), player_color)
            )
            try:
                if self.wait_full_time:
                    delay.get()
                move = move_res.get(1)
            # player crashed or timed out
            except TimeoutError:
                self.winner = other_color
                print(f"{player.name} timed out!")
                return
            except Exception:
                self.winner = other_color
                print(f"{player.name} crashed!")
                traceback.print_exc()
                return
        if move is not None:
            move_start, move_end = move
            if self.board[
                move_start
            ] != player_color or move_end not in self.board.walkable_from_coord(
                move_start
            ):
                print(
                    f"{player.name} tried to illegally move from {move_start} to {move_end}."
                )
                self.winner = other_color
                return
        # Clear dead enemies
        dead_enemies = {
            coord
            for coord in self.board.cells
            if self.board[coord] == other_color and self.board.is_miner_dead(coord)
        }
        for enemy in dead_enemies:
            self.board[enemy] = Space.EMPTY
        # Switch players
        self.red_turn = not self.red_turn


class Foo:

    def __init__(self):
        self.name = "boris"

    def mine(self, board: Board, color: Space) -> Coordinate:
        time.sleep(3)
        print("hi")
        return (0, 0)

    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate] | None:
        return (0, 0), (0, 1)


def main():
    g = Game(Foo(), Foo(), time_per_move=5, wait_full_time=True)
    g.step()


if __name__ == "__main__":
    main()
