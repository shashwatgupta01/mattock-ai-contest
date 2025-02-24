from board import Board, Space, Coordinate
from copy import copy, deepcopy
import math

class bot:
    
    count = 0

    def __init__(self, artificial_delay: float = 0):
        self.name = f"rando_{bot.count}"
        self.artificial_delay = artificial_delay
        bot.count += 1

    def minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, color: Space) -> tuple[Coordinate | None, None | tuple[Coordinate, Coordinate] | None, float]:
        #I think the maximizing_player boolean should take care of which player we are, so we should pick either maximizing player or color dependency. 
        #(Same comment) I think we should pick color dependency, so that way evaluate works for certain colors and minimize will still pick the smallest number. 
        #I also think we should maximize a few things with saving a copy of the previous board and running it compared to evaluate. A lot of the 
        #heuristy values are dependant on if they are better than last board or not. Ex. if move made was our highest valued closest_enemy then that should return highest eval. 
        #also if the amount of mineable_by_player spaces increases compared to previous board, then evaluated higher. 
        if depth == 0 or not board.mineable_by_player(color):
            return None, None, self.evaluate(board, color)

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
        #dead players
        red_player_dead = False
        blue_player_dead = False
        dead_weight = 0
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
        if color == Space.BLUE:
            if blue_player_dead: 
                dead_weight = -10 
            elif red_player_dead: 
                dead_weight = 10
        #next to opponent (also do next to opponent and mineable_by_player spaces increases)
        return dead_weight
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
    
    def mine(self, board: Board, color: Space) -> Coordinate:
        return self.minimax(board, 3, 0, 0, True, color)[0]
    
    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate]:
        return self.minimax(board, 3, 0, 0, True, color)[1]

    
    def closest_teammate(self, Board) -> Coordinate:
        ...

    def make_tree(self):
        ...