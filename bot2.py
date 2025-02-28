from board import Board, Space, Coordinate
import math

class bot2:
    count = 0

    def __init__(self, artificial_delay: float = 0):
        self.name = f"rando_{bot2.count}"
        self.artificial_delay = artificial_delay
        bot2.count += 1

    def minimax(self, prev_board: Board, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, color: Space) -> tuple[Coordinate | None, None | tuple[Coordinate, Coordinate] | None, float]:
        if depth == 0 or not board.mineable_by_player(color):
            return None, None, self.evaluate(prev_board, board, color)

        possible_mine = list(board.mineable_by_player(color))
        player_locations = board.find_all(color)
        other_color = Space.BLUE if color == Space.RED else Space.RED

        best_mine, best_move = None, None
        best_eval = -math.inf if maximizing_player else math.inf

        for mine in possible_mine:
            original_value = board[mine]
            board[mine] = Space.EMPTY

            for location in player_locations:
                for dest in board.walkable_from_coord(location):
                    # Validate move: Ensure destination is valid
                    if not self.is_valid_move(board, location, dest, color):
                        continue

                    prev_dest_value = board[dest]
                    board[dest], board[location] = color, Space.EMPTY

                    current_eval = self.minimax(board, board, depth - 1, alpha, beta, not maximizing_player, other_color)[2]

                    if maximizing_player:
                        if current_eval > best_eval:
                            best_eval, best_mine, best_move = current_eval, mine, (location, dest)
                        alpha = max(alpha, best_eval)
                    else:
                        if current_eval < best_eval:
                            best_eval, best_mine, best_move = current_eval, mine, (location, dest)
                        beta = min(beta, best_eval)

                    # Undo move
                    board[dest], board[location] = prev_dest_value, color
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break

            # Undo mining
            board[mine] = original_value
            if beta <= alpha:
                break

        return best_mine, best_move, best_eval

    def is_valid_move(self, board: Board, location: Coordinate, dest: Coordinate, color: Space) -> bool:
        # Check if destination is within bounds of the board
        if not self.is_within_bounds(board, dest):
            return False
        
        # Check if the destination is empty or can be occupied by the player's piece
        if board[dest] != Space.EMPTY and board[dest] != color:
            return False
        
        return True

    def is_within_bounds(self, board: Board, coord: Coordinate) -> bool:
        # Assuming board has a fixed grid size, for example: 8x8
        # You can replace these values with the actual board dimensions if they are different
        board_width = len(board.grid)  # Assuming 'grid' is a 2D array representation of the board
        board_height = len(board.grid[0]) if board.grid else 0
        
        x, y = coord
        return 0 <= x < board_width and 0 <= y < board_height

    def evaluate(self, prev_board: Board, board: Board, color: Space) -> float:
        mineable = {Space.RED: len(board.mineable_by_player(Space.RED)), Space.BLUE: len(board.mineable_by_player(Space.BLUE))}
    
        # Check if any miner of each color is dead
        enemy_color = Space.RED if color == Space.BLUE else Space.BLUE
        dead_weight = 0
        if any(board.is_miner_dead(miner) for miner in board.find_all(color)):
            dead_weight -= 300
        if any(board.is_miner_dead(miner) for miner in board.find_all(enemy_color)):
            dead_weight += 300

        # General weight for mineable spaces
        general_weight = 100 * mineable[color] - 50 * mineable[enemy_color]
        if mineable[color] == 0:
            general_weight -= 100000
        if mineable[enemy_color] == 0:
            general_weight += 100000

        # Walking weight: prioritize movement toward enemy
        enemy_positions = board.find_all(enemy_color)  # Cache enemy locations
        walking_weight = sum(5000 for walkable in board.walkable_by_player(color)
                             if any(self.distance(walkable, enemy) == 1 for enemy in enemy_positions))

        return general_weight + dead_weight + walking_weight

    def distance(self, start: Coordinate, dest: Coordinate) -> int:
        return max(abs(start[0] - dest[0]), abs(start[1] - dest[1]), abs(-start[0] - start[1] - (-dest[0] - dest[1])))

    def closest_enemy(self, board: Board, color: Space) -> list[tuple[Coordinate, float]]:
        mineable_own = list(board.mineable_by_player(color))
        mineable_enemy = list(board.mineable_by_player(Space.RED if color == Space.BLUE else Space.BLUE))

        if not mineable_own or not mineable_enemy:
            return []

        min_dist = min(self.distance(own, enemy) for own in mineable_own for enemy in mineable_enemy)
        return [(own, 100.0) for own in mineable_own if any(self.distance(own, enemy) == min_dist for enemy in mineable_enemy)]

    def mine(self, board: Board, color: Space) -> Coordinate:
        return self.minimax(board, board, 2, -math.inf, math.inf, True, color)[0]

    def move(self, board: Board, color: Space) -> tuple[Coordinate, Coordinate] | None:
        return self.minimax(board, board, 2, -math.inf, math.inf, True, color)[1]