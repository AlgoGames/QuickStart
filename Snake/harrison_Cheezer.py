import numpy as np

N = 0
E = 1
S = 2
W = 3

MAX_COL = 25
MAX_ROW = 24

class Algo:

    def __init__(self, config):
        self.has_homed = False
        self.last_apple = None
        self.done_stacking = False
        self.cycling = False

    def take_turn(self, state, interface):
        self.log = interface.log
        self.interface = interface

        self.snake = state.snake
        self.head = self.snake[0]
        self.direction = state.direction
        self.apple = state.apple

        if state.hunger >= 650 and self.head[1] % 2 == 1: 
            self.cycling = True
        
        if self.cycling:
            return self.cycle()

        if np.array_equal(self.last_apple, self.apple) and self.has_homed:
            if self.done_stacking:
                return self.get_apple()
            else:
                return self.stack()
        else:
            if not self.done_stacking and self.has_homed:
                return self.stack()

            self.stack_count = self.snake.shape[0]
            self.done_stacking = False
            self.has_homed = False
            self.last_apple = self.apple

            return self.home()

    def home(self):
        self.log("homing")
        self.log(f"pos: {self.head}")

        if self.head[0] == MAX_ROW and self.head[1] == 0:
            self.has_homed = True
            return N

        if self.head[0] == MAX_ROW:
            self.log("west")
            return W
        
        if self.direction == N:
            return E
        else:
            return S
    
    def stack(self):
        self.log("stacking")
        # self.log(self.interface.time_left)
        self.stack_count -= 1

        if self.direction == N:
            if self.head[0] == 0:
                if self.stack_count <= 0:
                    self.done_stacking = True
                return E
            else:
                return N
            
        if self.direction == S:
            if self.head[0] == MAX_ROW - 1:
                return E
            else:
                return S
            
        if self.direction == E:
            if self.head[0] == 0:
                return S
            else:
                return N
        
    def get_apple(self):
        self.log("getting apple")
        # self.log(self.interface.time_left)

        if self.head[1] < self.apple[1]:
            return E
        else:
            return self.home()
        
    
    def cycle(self):
        if self.head[1] == MAX_COL or self.head[0] == MAX_ROW:
            return self.home()
        else:
            return self.stack()