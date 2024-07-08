import numpy as np
import heapq


class SearchShortCircuit(Exception):
    pass



class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.tpos = tuple(position)
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.tpos == other.tpos



class Algo:

    def __init__(self, config):
        self.d_opposites = [2,3,0,1] #TODO: fix since coord change
        self.N = np.array([-1, 0])
        self.E = np.array([0, 1])
        self.S = np.array([1, 0])
        self.W = np.array([0, -1])
        self.moves = np.array([self.N, self.E, self.S, self.W])
        self.max = np.array([24,25])
        self.short_circuit_thresh = 10


    def save_info_before(self, state):
        pass

    def save_info_after(self, state):
        pass


    def check_loc(self, loc, state, as_bool=True):
        res = 1
        if np.any(loc > self.max) | np.any(loc < 0):
            res = -1 #wall
        elif np.any((loc[0] == state.snakes[0][:,0]) & (loc[1] == state.snakes[0][:,1])):
            res = -2 #self
        elif np.any((loc[0] == state.snakes[1][:,0]) & (loc[1] == state.snakes[1][:,1])):
            res = -3 #opponent
        
        if as_bool:
            return res > 0
        else:
            return res


    @staticmethod
    def get_distances(snake_head, apples):
        return np.abs(apples[:,0] - snake_head[0]) + np.abs(apples[:,1] - snake_head[1])


    @staticmethod
    def get_matrix(state):
        mat = np.zeros((25,26), dtype=np.int8)
        mat[state.snakes[0][:,0], state.snakes[0][:,1]] = 1
        mat[state.snakes[1][:,0], state.snakes[1][:,1]] = 1
        return mat


    def astar(self, matrix, start, end):
        rows, cols = matrix.shape
        open_list = []
        closed_list = set()
        start_node = Node(start)
        end_node = Node(end)
        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)

            if current_node == end_node:
                path = []
                while current_node is not None:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1]  # Return reversed path

            closed_list.add(current_node.tpos)

            for offset in self.moves:
                neighbor_position = current_node.position + offset

                if (neighbor_position[0] < 0 or
                    neighbor_position[0] >= rows or
                    neighbor_position[1] < 0 or
                    neighbor_position[1] >= cols):
                    continue

                if matrix[neighbor_position[0], neighbor_position[1]] == 1:
                    continue

                neighbor_node = Node(neighbor_position, current_node)

                if neighbor_node.tpos in closed_list:
                    continue

                neighbor_node.g = current_node.g + 1
                neighbor_node.h = np.sum(np.abs(neighbor_node.position - end_node.position))
                neighbor_node.f = neighbor_node.g + neighbor_node.h

                for open_node in open_list:
                    if neighbor_node == open_node and neighbor_node.g > open_node.g:
                        break
                else:
                    heapq.heappush(open_list, neighbor_node)

            time_left = self.interface.get_time_left()
            if time_left < 200:
                self.interface.log(f'{time_left} ms left')
            if time_left <= self.short_circuit_thresh:
                self.interface.log(f'Ran out of time: {time_left} ms left')
                raise SearchShortCircuit()

        return None  # No path found


    def rank_apples(self, state):
        distances = self.get_distances(state.snakes[0][0], state.apples)
        ranked_apples = state.apples[np.argsort(distances)]
        return ranked_apples
        

    def rank_moves(self, snake, apple, cur_direction):
        to_move = np.array([[2,0],[3,1]])
        rel = apple - snake[0]
        d = np.argmax(np.abs(rel)) #0 means max dist to cover is in x direction
        sgn = (np.sign(rel)==1).astype(int) #0 if need to travel in negative direction

        i = 0      # right ax right dir, wrong ax right dir,    wrong ax wrong dir,  right ax wrong dir
        ranked_moves = [to_move[d,sgn[d]], to_move[d^1,sgn[d^1]], to_move[d^1,sgn[d^1]^1], to_move[d,sgn[d]^1]]
        if ranked_moves[i] == self.d_opposites[cur_direction]:
            i += 1

        return i, ranked_moves


    def finalize_move(self, i, ranked_moves, state):
        if i == 3: #last resort: only option
            return ranked_moves[i]

        move = ranked_moves[i]
        new_head = state.snakes[0][0] + self.moves[move]
        if not self.check_loc(new_head, state):
            move = self.finalize_move(i+1, ranked_moves, state)
        
        return move


    def get_quick_move(self, state):
        ranked_apples = self.rank_apples(state)
        i,ranked_moves = self.rank_moves(state.snakes[0], ranked_apples[0], state.directions[0])
        return self.finalize_move(i, ranked_moves, state)


    def take_turn(self, state, interface):
        self.interface = interface
        self.save_info_before(state)

        mat = self.get_matrix(state)
        ranked_apples = self.rank_apples(state)
        try:

            for i in range(5):
                interface.log(f'Desire: {state.snakes[0][0]} -> {ranked_apples[i]}')
                desired_path = self.astar(mat, state.snakes[0][0], ranked_apples[i])
                if desired_path is not None:
                    desired_path = desired_path[1:]
                    break

                if desired_path is None:
                    interface.log('Did not find a path')
                    raise SearchShortCircuit()

        except SearchShortCircuit:
            interface.log('Short circuit')
            move = self.get_quick_move(state)
            self.save_info_after(state)
            return move

        interface.log(f'Path: {desired_path}')

        diff = desired_path[0] - state.snakes[0][0]
        if diff[0] == 0:
            if diff[1] > 0:
                move = interface.E
            else:
                move = interface.W
        else: 
            if diff[0] > 0:
                move = interface.S
            else:
                move = interface.N

        interface.log(f'Move: {move}')

        self.save_info_after(state)
        interface.log(f"Time at return: {interface.get_time_left()}")
        return move
