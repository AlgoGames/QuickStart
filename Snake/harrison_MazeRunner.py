import numpy as np

N = 0
E = 1
S = 2
W = 3

WIDTH = 26
HEIGHT = 25

np.set_printoptions(linewidth=1000)

def is_out_of_bounds(coord):
    return coord[0] < 0 or coord[0] > HEIGHT - 1 or coord[1] < 0 or coord[1] > WIDTH - 1

def turn_right(turn):
    if turn == N:
        return E
    elif turn == E:
        return S
    elif turn == S:
        return W
    elif turn == W:
        return N
    
def turn_left(turn):
    if turn == N: 
        return W
    elif turn == E: 
        return N
    elif turn == S: 
        return E
    elif turn == W: 
        return S
    
def get_opposite_dir(dir):
    if dir == N:
        return S
    elif dir == E:
        return W
    elif dir == S:
        return N
    elif dir == W:
        return E

INCREMENTS = [np.array([-1, 0]), np.array([0, 1]), np.array([1, 0]), np.array([0, -1])]

class Algo:

    def __init__(self, config):
        pass

    def take_turn(self, state, interface):
        self.interface = interface
        self.state = state

        self.score_grid = np.zeros((HEIGHT, WIDTH))
        self.bool_grid = np.full((HEIGHT, WIDTH), True)

        for pos in state.snake[1:-1]:
            self.bool_grid[pos[0], pos[1]] = False

        self.fill_scores()
        interface.log(self.score_grid)
        return self.get_dir()


    def get_dir(self):
        apple = self.state.apple
        score = self.score_grid[apple[0], apple[1]]

        if score == 0: 
            self.interface.log("no path found :(")
            return self.state.direction

        cur_pos = apple
        last_dir = 0
        while score != 1:

            n = cur_pos + INCREMENTS[N]
            e = cur_pos + INCREMENTS[E]
            s = cur_pos + INCREMENTS[S]
            w = cur_pos + INCREMENTS[W]

            options = [(n, N), (e, E), (s, S), (w, W)]
            for pos, dir in options:
                if is_out_of_bounds(pos):
                    continue

                if self.score_grid[pos[0], pos[1]] == score - 1:
                    cur_pos = pos
                    score -= 1
                    last_dir = dir
                    break
            
        return get_opposite_dir(last_dir)

    def fill_scores(self):
        head = self.state.snake[0]
        self.score_grid[head[0], head[1]] = 1

        score = 2
        boundry = self.get_cell_boundaries(head)
        while len(boundry) != 0:
            for pos in boundry:
                self.score_grid[pos[0], pos[1]] = score

            if score < len(self.state.snake):
                tail = self.state.snake[-score]
                self.bool_grid[tail[0], tail[1]] = True

            boundry = self.get_next_boundary(boundry)
            score += 1


    def get_next_boundary(self, last_bounds):
        next_bounds = []
        for pos in last_bounds: 
            next_bounds.extend(self.get_cell_boundaries(pos))
        return list(set(tuple(arr) for arr in next_bounds))

    def get_cell_boundaries(self, pos):
        n = pos + INCREMENTS[N]
        s = pos + INCREMENTS[S]
        e = pos + INCREMENTS[E]
        w = pos + INCREMENTS[W]

        result = []
        if self.is_valid_neighbor(n):
            result.append(n)
        if self.is_valid_neighbor(s):
            result.append(s)
        if self.is_valid_neighbor(e):
            result.append(e)
        if self.is_valid_neighbor(w):
            result.append(w)

        # self.interface.log(result)

        return result


    def is_valid_neighbor(self, pos):
        if is_out_of_bounds(pos):
            return False
        
        return self.score_grid[pos[0], pos[1]] == 0 and self.bool_grid[pos[0], pos[1]]