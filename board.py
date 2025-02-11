from enum import Enum


CompoundCoordinate = tuple[int, int] | tuple[int, int, int]
FullCoordinate = tuple[int, int, int]
Coordinate = tuple[int, int]


class Space(Enum):
    WALL = 0
    EMPTY = 1
    RED = 2
    BLUE = 3


def _hex_neighbors(coord: CompoundCoordinate) -> list[FullCoordinate]:
    if len(coord) == 2:
        q, r = coord
        s = -q - r
    else:
        q, r, s = coord
    directions = [
        (1, -1, 0),
        (1, 0, -1),
        (0, 1, -1),
        (-1, 1, 0),
        (-1, 0, 1),
        (0, -1, 1),
    ]
    return [(q + a, r + b, s + c) for a, b, c in directions]


class Board:

    def __init__(self, small: bool = False):
        self.size = 5 if small else 7
        self.miner_count = 3 if small else 6
        self.cells: dict[FullCoordinate, Space] = {}
        frontier = [(0, 0, 0)]
        for _ in range(self.size - 1):
            next_frontier = []
            while frontier:
                curr = frontier.pop()
                for neighbor in (
                    n for n in _hex_neighbors(curr) if n not in self.cells
                ):
                    self.cells[neighbor] = Space.WALL
                    next_frontier.append(neighbor)
            frontier = next_frontier
        red_miners = [(1, -3), (2, 1), (-3, 2), (6, -4), (-4, -2), (-2, 6)]
        blue_miners = [(-1, 3), (-2, -1), (3, -2), (-6, 4), (4, 2), (2, -6)]
        for cell in red_miners:
            if cell in self:
                self[cell] = Space.RED
        for cell in blue_miners:
            if cell in self:
                self[cell] = Space.BLUE

    def count_elements(self, element: Space) -> int:
        return len([c for c in self.cells.values() if c == element])

    def _full_coordinate(self, coord: CompoundCoordinate) -> FullCoordinate:
        if len(coord) == 2:
            q, r = coord
            s = -q - r
        else:
            q, r, s = coord
        return (q, r, s)

    def __setitem__(self, coord: CompoundCoordinate, value: Space):
        coord = self._full_coordinate(coord)
        if coord not in self.cells:
            raise ValueError(f"{coord} is not a valid coordinate.")
        self.cells[coord] = value

    def __getitem__(self, coord: CompoundCoordinate) -> Space:
        coord = self._full_coordinate(coord)
        if coord not in self.cells:
            raise ValueError(f"{coord} is not a valid coordinate.")
        return self.cells[coord]

    def __contains__(self, coord: CompoundCoordinate) -> bool:
        coord = self._full_coordinate(coord)
        return coord in self.cells

    def find_all(self, space: Space) -> set[Coordinate]:
        return {coord[:2] for coord in self.cells if self[coord] == space}

    def neighbors(
        self, coord: CompoundCoordinate, space: Space | None = None
    ) -> set[Coordinate]:
        if space is None:
            return {n[:2] for n in _hex_neighbors(coord) if n in self.cells}
        return {
            n[:2] for n in _hex_neighbors(coord) if n in self.cells and self[n] == space
        }

    def walkable_from_coord(self, start: CompoundCoordinate) -> set[Coordinate]:
        if self[start] == Space.WALL:
            return set()
        traversable = {self[start], Space.EMPTY}
        out: set[Coordinate] = set()
        frontier = set([start])
        visited: set[Coordinate] = set()
        while frontier:
            curr = frontier.pop()
            curr = curr[:2]
            visited.add(curr)
            if self[curr] not in traversable:
                continue
            if self[curr] == Space.EMPTY:
                out.add(curr)
            frontier |= self.neighbors(curr) - visited
        return out

    def walkable_by_player(self, player: Space) -> set[Coordinate]:
        if player not in {Space.BLUE, Space.RED}:
            raise ValueError("The only valid players are Space.RED and Space.BLUE")
        player_coords = self.find_all(player)
        out = set()
        for p in player_coords:
            out |= self.walkable_from_coord(p)
        return out

    def is_mineable(self, coord: CompoundCoordinate) -> bool:
        if self[coord] != Space.WALL:
            return False
        empty_neighbors = (
            self.neighbors(coord, Space.EMPTY)
            | self.neighbors(coord, Space.RED)
            | self.neighbors(coord, Space.BLUE)
        )
        if len(empty_neighbors) > 3:
            return False
        for n in empty_neighbors:
            if (
                len(
                    self.neighbors(n, Space.EMPTY)
                    | self.neighbors(n, Space.RED)
                    | self.neighbors(n, Space.BLUE)
                )
                >= 3
            ):
                return False
        return True

    def mineable_by_player(self, player: Space) -> set[Coordinate]:
        if player not in {Space.BLUE, Space.RED}:
            raise ValueError("The only valid players are Space.RED and Space.BLUE")
        neighboring_walls = set()
        player_coords = self.find_all(player)
        for hall in self.walkable_by_player(player) | player_coords:
            neighboring_walls |= {
                w for w in self.neighbors(hall, Space.WALL) if self.is_mineable(w)
            }
        return neighboring_walls

    def is_miner_dead(self, coord: CompoundCoordinate) -> bool:
        player = self[coord]
        if player not in {Space.BLUE, Space.RED}:
            raise ValueError("The only valid players are Space.RED and Space.BLUE")
        other_player = Space.RED if player == Space.BLUE else Space.BLUE
        enemy_count = 0
        frontier = set([coord])
        visited: set[Coordinate] = set()
        while frontier:
            curr = frontier.pop()
            curr = curr[:2]
            visited.add(curr)
            if self[curr] == player and curr != coord[:2]:
                return False
            if self[curr] == other_player:
                enemy_count += 1
                continue
            if self[curr] == Space.WALL:
                continue
            frontier |= self.neighbors(curr) - visited
        return enemy_count >= 2
