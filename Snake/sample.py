class Algo:

    def __init__(self, config):
        pass

    def take_turn(self, state, interface):

		# Unpack state data
        snake = state.snake
        head = snake[0]
        direction = state.direction
        apple = state.apple

		# Go directly towards apple
		# Select direction based on snake head position and apple position
        if head[0] < apple[0]:
        
	        # If snake is currently going north, it cannot turn south
            if direction == interface.N:
                return interface.E
            else:
                return interface.S
                
        elif head[0] > apple[0]:
        
	        # If snake is currently going south, it cannot turn north
            if direction == interface.S:
                return interface.E
            else:
                return interface.N
                
        elif head[1] < apple[1]:
        
	        # If snake is currently going west, it cannot turn east
            if direction == interface.W:
                return interface.N
            else:
                return interface.E
                
        elif head[1] > apple[1]:
        
	        # If snake is currently going east, it cannot turn west 
            if direction == interface.E:
                return interface.N
            else:
                return interface.W