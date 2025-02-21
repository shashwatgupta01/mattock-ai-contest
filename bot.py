from board import Board, Space, Coordinate
from copy import copy, deepcopy
import math

class bot:

    def minimax(self, board: Board, depth: int, alpha, beta, maximizing_player: bool, color: Space) -> tuple[Coordinate | None, tuple[Coordinate, Coordinate] | None, float]:

        if depth == 0 or not board.mineable_by_player(color):
            return None, self.evaluate(board, color)

        possible_mine = list(board.mineable_by_player(color))
        player_locations = board.find_all(color)
        possible_move: list[tuple[Coordinate, Coordinate]] = []
        
        
        best_mine = possible_mine[0]
        best_move = possible_move[0]

        if color == Space.RED:
            other_color = Space.BLUE
        else:
            other_color = Space.RED

        if maximizing_player:
            max_eval = -math.inf        
            for move in possible_mine:
                board_copy = board.__copy__()
                board_copy.__setitem__(move, Space.EMPTY)
                for location in player_locations:
                    walkable = list(board.walkable_from_coord(location))
                    for dest in walkable:
                        possible_move.append((location, dest))
                current_eval = self.minimax(board_copy, depth - 1, alpha, beta, False, other_color)[2]
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_mine = move
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            return best_mine, best_move, max_eval

        else:
            min_eval = math.inf
            for move in possible_mine:
                board_copy = board.__copy__()
                board_copy.__setitem__(move, Space.EMPTY)
                for location in player_locations:
                    walkable = list(board.walkable_from_coord(location))
                    for dest in walkable:
                        possible_move.append((location, dest))
                current_eval = self.minimax(board_copy, depth - 1, alpha, beta, True, other_color)[2]
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_mine = move
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            return best_mine, best_move, min_eval
        
    
        
    def evaluate(self, board: Board, color: Space) -> float:
        red_spaces = board.find_all(Space.RED)
        blue_spaces = board.find_all(Space.BLUE)
        red_player_dead = False
        blue_player_dead = False
        for red in red_spaces:
            red_player_dead = board.is_miner_dead(red) 
            if red_player_dead: 
                break
        for blue in blue_spaces:
            blue_player_dead = board.is_miner_dead(blue) 
            if blue_player_dead: 
                break
        if color == Space.RED:
            if red_player_dead: 
                dead_weight = -10 
            elif blue_player_dead: 
                dead_weight = 10

        self.closest_enemy(board, color)
        ...
    
    def distance(self, start: Coordinate, dest: Coordinate) -> int:
        q_diff = abs(start[0] - dest[0])
        r_diff = abs(start[1] - dest[1]) 
        s_diff = abs(-start[0]-start[1] - (-dest[0]-dest[1]))
        return max(q_diff, r_diff, s_diff)
        
    
    def closest_enemy(self, board: Board, color: Space) -> list[tuple[Coordinate, int]]:
        out: list[tuple[Coordinate, int]] = []
        if color == Space.RED: #red
            mineable_red = board.mineable_by_player(Space.RED)
            mineable_blue = board.mineable_by_player(Space.BLUE)
            distances: set[int] = set()
            coordinates: dict[int, tuple[Coordinate, Coordinate]] = {}
            for i in mineable_red:
                for j in mineable_blue:
                    curr_dist = self.distance(i,j)
                    distances.add(curr_dist) 
                    coordinates.update({curr_dist: (i,j)})
            min_dist = min(distances)
            for i in coordinates:
                curr_value = 10 + (min_dist - i)
                if i % 2 == 0: 
                    curr_value *= -1
                out.append((coordinates[i][0], curr_value)) 
        elif color == Space.BLUE:
            mineable_red = board.mineable_by_player(Space.RED)
            mineable_blue = board.mineable_by_player(Space.BLUE)
            distances: set[int] = set()
            coordinates: dict[int, tuple[Coordinate, Coordinate]] = {}
            for i in mineable_blue:
                for j in mineable_red:
                    curr_dist = self.distance(i,j)
                    distances.add(curr_dist) 
                    coordinates.update({curr_dist: (i,j)})
            min_dist = min(distances)
            for i in coordinates:
                curr_value = 10 + (min_dist - i)
                if i % 2 == 0: 
                    curr_value *= -1
                out.append((coordinates[i][0], curr_value)) 
        return out
    
    def closest_teammate(self, Board) -> Coordinate:
        ...

    def make_tree(self):
        ...