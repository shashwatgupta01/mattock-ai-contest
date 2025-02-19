from board import Board, Space, Coordinate

class bot:

    def distance(self, start: Coordinate, dest: Coordinate) -> int:
        q_diff = abs(start[0] - dest[0])
        r_diff = abs(start[1] - dest[1]) 
        s_diff = abs(-start[0]-start[1] - (-dest[0]-dest[1]))
        return max(q_diff, r_diff, s_diff)
        
    
    def closest_enemy(self, board: Board, color: Space) -> list[tuple(Coordinate, int)]:
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
                curr_value = 20 + (min_dist - i)
                out.append((coordinates[i][0], curr_value)) 
            return out
        if color == Space.BLUE:
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
                curr_value = 20 + (min_dist - i)
                out.append((coordinates[i][0], curr_value)) 
            return out
        


        
            
        ...
    
    def closest_teammate(self, Board) -> Coordinate:
        ...

    def make_tree(self):
        ...