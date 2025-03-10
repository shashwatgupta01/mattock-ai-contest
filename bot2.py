from board import Board, Space, Coordinate
from copy import deepcopy
import math

class bot2:
    count = 0

    def __init__(self, artificial_delay: float = 0):
        self.name = f"rando_{bot2.count}"
        self.artificial_delay = artificial_delay
        bot2.count += 1

    def minimax(self, prev_board: Board, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, color: Space) -> tuple[Coordinate | None, float]:
        if depth == 0 or not board.mineable_by_player(color):
            return None, self.evaluate(prev_board, board, color)

        possible_mine = list(board.mineable_by_player(color))
        best_mine = possible_mine[0]
        other_color = Space.RED if color == Space.BLUE else Space.BLUE
        
        if maximizing_player:
            max_eval = -math.inf
            for mine in possible_mine:
                board_copy = deepcopy(board)
                board_copy[mine] = Space.EMPTY
                current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, False, other_color)[1]
                
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_mine = mine
                
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break

            return best_mine, max_eval
        
        else:
            min_eval = math.inf
            for mine in possible_mine:
                board_copy = deepcopy(board)
                board_copy[mine] = Space.EMPTY
                current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, True, other_color)[1]
                
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_mine = mine
                
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break

            return best_mine, min_eval

    def movemax(self, prev_board: Board, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, color: Space) -> tuple[tuple[Coordinate, Coordinate] | None, float]:
        if depth == 0 or not board.mineable_by_player(color):
            return None, self.evaluate_walking(prev_board, board, color)

        player_locations = board.find_all(color)
        other_color = Space.RED if color == Space.BLUE else Space.BLUE
        best_move = None
        
        if maximizing_player:
            max_eval = -math.inf
            board_copy = deepcopy(board)
            for location in player_locations:
                for dest in board.walkable_from_coord(location):
                    board_copy[location], board_copy[dest] = Space.EMPTY, color
                    current_eval = self.movemax(board, board_copy, depth - 1, alpha, beta, False, other_color)[1]
                    
                    if current_eval > max_eval:
                        max_eval = current_eval
                        best_move = (location, dest)
                    
                    alpha = max(alpha, current_eval)
                    if beta <= alpha:
                        return best_move, max_eval
                    
                    board_copy[location], board_copy[dest] = color, Space.EMPTY  # Undo move
            return best_move, max_eval
        
        else:
            min_eval = math.inf
            board_copy = deepcopy(board)
            for location in player_locations:
                for dest in board.walkable_from_coord(location):
                    board_copy[location], board_copy[dest] = Space.EMPTY, color
                    current_eval = self.movemax(board, board_copy, depth - 1, alpha, beta, True, other_color)[1]
                    
                    if current_eval < min_eval:
                        min_eval = current_eval
                        best_move = (location, dest)
                    
                    beta = min(beta, current_eval)
                    if beta <= alpha:
                        return best_move, min_eval
                    
                    board_copy[location], board_copy[dest] = color, Space.EMPTY  # Undo move
            return best_move, min_eval

    def evaluate(self, prev_board: Board, board: Board, color: Space) -> float:
        red_mineable = len(board.mineable_by_player(Space.RED))
        blue_mineable = len(board.mineable_by_player(Space.BLUE))
        #dead_weight = 300 * len(board.is_miner_dead(Space.BLUE) - board.is_miner_dead(Space.RED))
        general_weight = 40 * red_mineable - 20 * blue_mineable if color == Space.RED else 40 * blue_mineable - 20 * red_mineable
        return general_weight + self.evaluate_walking(prev_board, board, color)

    def evaluate_walking(self, prev_board: Board, board: Board, color: Space) -> float:
        other_color = Space.RED if color == Space.BLUE else Space.BLUE
        our_spaces = board.find_all(color)
        other_spaces = board.find_all(other_color)
        walking_weight = 1000 * (len(prev_board.find_all(other_color)) - len(other_spaces))
        
        for us in our_spaces:
            for other in other_spaces:
                if self.distance(us, other) == 1:
                    walking_weight += 150
            for walkable in board.walkable_from_coord(us):
                if self.distance(us, walkable) == 1:
                    walking_weight += 15
        
        return walking_weight + 50 * self.closest_teammate(color, board) - 3 * self.closest_teammate(other_color, board) - 100 * len(board.mineable_by_player(other_color))

    def distance(self, start: Coordinate, dest: Coordinate) -> int:
        return max(abs(start[0] - dest[0]), abs(start[1] - dest[1]), abs(-start[0] - start[1] - (-dest[0] - dest[1])))

    def closest_teammate(self, color: Space, board: Board) -> float:
        min_dist = math.inf
        ours = board.find_all(color)
        for us in ours:
            for other in ours:
                if us != other:
                    min_dist = min(min_dist, self.distance(us, other))
        return min_dist if min_dist != math.inf else 0

    def mine(self, board: Board, color: Space) -> Coordinate:
        return self.minimax(board, board, 1, -math.inf, math.inf, True, color)[0]

    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate] | None:
        return self.movemax(board, board, 1, -math.inf, math.inf, True, color)[0]