import numpy as np

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

WIDTH = 26
HEIGHT = 25

np.set_printoptions(linewidth=1000)

def is_out_of_bounds(coord):
    return coord[0] < 0 or coord[0] > HEIGHT - 1 or coord[1] < 0 or coord[1] > WIDTH - 1

def get_opposite_dir(dir):
    if dir == NORTH:
        return SOUTH
    elif dir == EAST:
        return WEST
    elif dir == SOUTH:
        return NORTH
    elif dir == WEST:
        return EAST

def turn_right(turn):
    if turn == NORTH:
        return EAST
    elif turn == EAST:
        return SOUTH
    elif turn == SOUTH:
        return WEST
    elif turn == WEST:
        return NORTH
    
def turn_left(turn):
    if turn == NORTH: 
        return WEST
    elif turn == EAST: 
        return NORTH
    elif turn == SOUTH: 
        return EAST
    elif turn == WEST: 
        return SOUTH

INCREMENTS = [np.array([-1, 0]), np.array([0, 1]), np.array([1, 0]), np.array([0, -1])]

class Algo:

    def __init__(self, config):
        pass

    def take_turn(self, state, interface):
        self.interface = interface
        self.state = state

        self.score_grid = np.zeros((HEIGHT, WIDTH))
        self.bool_grid = np.full((HEIGHT, WIDTH), True)

        for snake in state.snakes:
            for pos in snake:
                self.bool_grid[pos[0], pos[1]] = False

        self.fill_scores()
        interface.log(self.score_grid)

        return self.get_dir(self.get_nearest_apple())

    def get_nearest_apple(self):
        self.score_grid[self.score_grid == 0] = np.inf
        scores = [self.score_grid[x, y] for x, y in self.state.apples]
        ranked_apples = self.state.apples[np.argsort(scores)]
        self.interface.log(f"desired apple: {ranked_apples[0]}")        
        return ranked_apples[0]

    def get_dir(self, pos):
        score = self.score_grid[pos[0], pos[1]]
        head = self.state.snakes[0][0]

        path = []
        while pos[0] != head[0] or pos[1] != head[1]:
            north = pos + INCREMENTS[NORTH]
            south = pos + INCREMENTS[SOUTH]
            east = pos + INCREMENTS[EAST]
            west = pos + INCREMENTS[WEST]

            options = [(north, NORTH), (south, SOUTH), (east, EAST), (west, WEST)]

            for o in options:
                new_pos = o[0]
                dir = o[1]

                if is_out_of_bounds(new_pos):
                    continue
                elif self.score_grid[new_pos[0], new_pos[1]] == score - 1:
                    path.append(dir)
                    pos = new_pos
                    score -= 1
                    break
            
        self.interface.log(path)
        return get_opposite_dir(path[-1])


    def fill_scores(self):
        head = self.state.snakes[0][0]
        self.score_grid[head[0], head[1]] = 1

        score = 2
        boundry = self.get_cell_boundaries(head)
        while len(boundry) != 0:
            for pos in boundry:
                self.score_grid[pos[0], pos[1]] = score

            boundry = self.get_next_boundary(boundry)
            score += 1


    def get_next_boundary(self, last_bounds):
        next_bounds = []
        for pos in last_bounds: 
            next_bounds.extend(self.get_cell_boundaries(pos))
        return list(set(tuple(arr) for arr in next_bounds))

    def get_cell_boundaries(self, pos):
        right = pos + INCREMENTS[NORTH]
        left = pos + INCREMENTS[SOUTH]
        up = pos + INCREMENTS[EAST]
        down = pos + INCREMENTS[WEST]

        result = []
        if self.is_valid_neighbor(right):
            result.append(right)
        if self.is_valid_neighbor(left):
            result.append(left)
        if self.is_valid_neighbor(up):
            result.append(up)
        if self.is_valid_neighbor(down):
            result.append(down)

        # self.interface.log(result)

        return result


    def is_valid_neighbor(self, pos):
        if is_out_of_bounds(pos):
            return False
        
        return self.score_grid[pos[0], pos[1]] == 0 and self.bool_grid[pos[0], pos[1]]