from board import Board, Space, Coordinate
from copy import copy, deepcopy
import math

class bot:
    
    count = 0

    def __init__(self, artificial_delay: float = 0):
        self.name = f"rando_{bot.count}"
        self.artificial_delay = artificial_delay
        bot.count += 1

    def minimax(self, prev_board: Board, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, color: Space) -> tuple[Coordinate | None, None | tuple[Coordinate, Coordinate] | None, float]:
        #I also think we should maximize a few things with saving a copy of the previous board and running it compared to evaluate. A lot of the 
        #heuristy values are dependant on if they are better than last board or not. Ex. if move made was our highest valued closest_enemy then that should return highest eval. 
        #also if the amount of mineable_by_player spaces increases compared to previous board, then evaluated higher. 

        #Also, not moving isn't an option with current set up. 
        if depth == 0 or not board.mineable_by_player(color):
            return None, None, self.evaluate(prev_board, board, color)

        possible_mine = list(board.mineable_by_player(color))
        player_locations = board.find_all(color)
        #possible_move = board.walkable_by_player(color)
        
        
        best_mine = possible_mine[0]
        
        best_move = None

        if color == Space.RED:
            other_color = Space.BLUE
        else:
            other_color = Space.RED

        if maximizing_player:
            max_eval_1 = -math.inf
            for mine in possible_mine:
                board_copy = board.__copy__()
                board_copy.__setitem__(mine, Space.EMPTY)
                current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, False, other_color)[2] 
                if beta <= alpha:
                    break
                if current_eval > max_eval_1:
                    max_eval_1 = current_eval
                    best_mine = mine
            max_eval_2 = -math.inf
            for location in player_locations:
                walkable = list(board.walkable_from_coord(location))
                walkable.append(location)
                for dest in walkable: #maybe to make it faster, instead of checking each place to walk toward, always walk towards the closest player, or if can kill player. 
                    board_copy.__setitem__(dest, color) 
                    board_copy.__setitem__(location, Space.EMPTY)
                    current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, False, other_color)[2]
                    if current_eval > max_eval_2:
                        max_eval_2 = current_eval
                        if location != dest: 
                            best_move = location, dest
                        else: 
                            best_move = None
                    alpha = max(alpha, current_eval)
                    if beta <= alpha:
                        break
            

            return best_mine, best_move, max_eval_1 + max_eval_2

        else:
            min_eval_1 = math.inf
            board_copy = board.__copy__()
            board_copy[best_mine] = Space.EMPTY  
            for mine in possible_mine:
                board_copy = board.__copy__()
                board_copy.__setitem__(mine, Space.EMPTY)
                current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, True, other_color)[2]
                if alpha <= beta:
                    break
                if current_eval < min_eval_1: 
                    best_mine = mine
                    min_eval_1 = current_eval
            min_eval_2 = math.inf
            for location in player_locations:
                walkable = list(board.walkable_from_coord(location))
                #walkable.append(best_mine)
                for dest in walkable:
                    board_copy.__setitem__(location, Space.EMPTY)
                    board_copy.__setitem__(dest, color)
                    current_eval = self.minimax(board, board_copy, depth - 1, alpha, beta, True, other_color)[2]
                    if current_eval < min_eval_2:
                        min_eval_2 = current_eval
                        best_move = location, dest
                        beta = min(beta, current_eval)
                    if alpha <= beta:
                        break
            return best_mine, best_move, min_eval_1 + min_eval_2
        #Maybe check if other_color neighbors are walkable from current color, then see if we can maximize our mineable spaces while minimizing their spaces. 
    
        
    def evaluate(self, prev_board: Board, board: Board, color: Space) -> float:
        red_spaces = board.find_all(Space.RED)
        prev_red_spaces = prev_board.find_all(Space.RED)
        blue_spaces = board.find_all(Space.BLUE)
        prev_blue_spaces = prev_board.find_all(Space.BLUE)
        red_last_mineable = prev_board.mineable_by_player(Space.RED)
        blue_last_mineable = prev_board.mineable_by_player(Space.BLUE)
        red_mineable = board.mineable_by_player(Space.RED)
        blue_mineable = board.mineable_by_player(Space.BLUE)
        red_mineable_len = len(red_mineable)
        blue_mineable_len = len(blue_mineable)
        #dead players
        red_player_dead = False
        blue_player_dead = False
        dead_weight = 0
        general_weight = 0
        mined_space_value = 0
        walking_weight = self.evaluate_walking(prev_board, board, color)

        '''for mined in self.closest_enemy(prev_board, color):
            if mined[0] == mined_space:
                mined_space_value = mined[1]'''
        for red in red_spaces:
            red_player_dead = board.is_miner_dead(red) 
            if red_player_dead: 
                break
        for blue in blue_spaces:
            blue_player_dead = board.is_miner_dead(blue) 
            if blue_player_dead: 
                break
        if color == Space.RED:

            """if blue_player_dead: 
                walking_weight += 1000 
            if red_player_dead: 
                walking_weight -= 1000"""

            general_weight += red_mineable_len * 4
            general_weight -= blue_mineable_len * 2
            if red_mineable_len == 0:
                general_weight -= 10000
            if blue_mineable_len == 0:
                general_weight += 10000
            

            if red_player_dead: 
                dead_weight -= 3
            elif blue_player_dead: 
                dead_weight += 3

        if color == Space.BLUE:
            
            """if blue_player_dead: 
                walking_weight -= 1000 
            if red_player_dead: 
                walking_weight += 1000"""
            
            general_weight -= red_mineable_len * 2
            general_weight += blue_mineable_len * 4
            if blue_mineable_len == 0:
                general_weight -= 10000
            if red_mineable_len == 0:
                general_weight += 10000

            if blue_player_dead: 
                dead_weight -= 3
            elif red_player_dead: 
                dead_weight += 3
        # next to opponent (also do next to opponent and mineable_by_player spaces increases)

        return dead_weight + walking_weight + general_weight
    

    def evaluate_walking(self, prev_board: Board, board: Board, color: Space) -> float:
        red_spaces = board.find_all(Space.RED)
        prev_red_spaces = prev_board.find_all(Space.RED)
        blue_spaces = board.find_all(Space.BLUE)
        prev_blue_spaces = prev_board.find_all(Space.BLUE)
        walking_weight = 0 
        if color == Space.BLUE: 
            other_color = Space.RED 
        else: 
            other_color = Space.BLUE
        if color == Space.RED: 
            """if len(prev_blue_spaces) > len(blue_spaces): 
                walking_weight += 1000 
            if len(prev_red_spaces) > len(red_spaces): 
                walking_weight -= 1000"""
            for us in red_spaces: 
                for other in blue_spaces:
                    if self.distance(us, other) == 1: 
                        walking_weight += 150
                for walkable in board.walkable_by_player(Space.RED): 
                    if self.distance(us, walkable) == 1: 
                        walking_weight += 15
        else: 
            """if len(prev_blue_spaces) > len(blue_spaces): 
                walking_weight -= 1000 
            if len(prev_red_spaces) > len(red_spaces): 
                walking_weight += 1000"""
            for us in blue_spaces: 
                for other in red_spaces:
                    if self.distance(us, other) == 1: 
                        walking_weight += 150
                for walkable in board.walkable_by_player(Space.BLUE): 
                    if self.distance(us, walkable) == 1: 
                        walking_weight += 15 
                
        return walking_weight + 3 * self.closest_teammate(color, board) - 3 * self.closest_teammate(other_color, board)

    def distance(self, start: Coordinate, dest: Coordinate) -> int:
        q_diff = abs(start[0] - dest[0])
        r_diff = abs(start[1] - dest[1]) 
        s_diff = abs(-start[0]-start[1] - (-dest[0]-dest[1]))
        return max(q_diff, r_diff, s_diff)
        
    
    def closest_enemy(self, board: Board, color: Space) -> list[tuple[Coordinate, int]]: 
        out: list[tuple[Coordinate, int]] = []
        mineable_red = board.mineable_by_player(Space.RED)
        mineable_blue = board.mineable_by_player(Space.BLUE)
        distances: set[int] = set()
        coordinates: dict[int, tuple[Coordinate, Coordinate]] = {}
        if color == Space.RED: #red
            for i in mineable_red:
                for j in mineable_blue:
                    curr_dist = self.distance(i,j)
                    distances.add(curr_dist) 
                    coordinates.update({curr_dist: (i,j)})
            min_dist = min(distances)
            for i in coordinates:
                curr_value = 100 + (min_dist - i)
                if i == 2: 
                    curr_value *= -1
                out.append((coordinates[i][0], curr_value)) 
        elif color == Space.BLUE:
            for i in mineable_blue:
                for j in mineable_red:
                    curr_dist = self.distance(i,j)
                    distances.add(curr_dist) 
                    coordinates.update({curr_dist: (i,j)})
            min_dist = min(distances)
            for i in coordinates:
                curr_value = 100 + (min_dist - i)
                if i == 2: 
                    curr_value *= -1
                out.append((coordinates[i][0], curr_value)) 
        return out
    
    def mine(self, board: Board, color: Space) -> Coordinate:
        return self.minimax(board, board, 2, -float('inf'), float('inf'), True, color)[0] #Does this run the minimax twice for mine and move? We could probably speed up by just running once and saving the moves locally then making them. 
    
    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate] | None:
        return self.minimax(board, board, 2, -float('inf'), float('inf'), True, color)[1]

    
    def closest_teammate(self, color: Space, board: Board) -> float:
        min = math.inf
        if color == Space.RED: 
            red_spaces = board.find_all(Space.RED) 
            for us in red_spaces: 
                for other in red_spaces: 
                    current = self.distance(us, other)
                    if current < min and current > 0: 
                        min = current
        else: 
            blue_spaces = board.find_all(Space.RED) 
            for us in blue_spaces: 
                for other in blue_spaces: 
                    current = self.distance(us, other)
                    if current < min and current > 0: 
                        min = current 

        return min
