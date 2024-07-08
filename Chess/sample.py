import random

class Algo:

    def __init__(self, config):
        self.color = config['color']

    def take_turn(self, state, interface):
        # Log the FEN of the current state
        interface.log(state.fen)

        # Iterate over possible moves
        moves = state.all_valid_moves
        for m in moves:
            # Log the move
            interface.log(m)
            
            # Get the resulting game state if you played that move
            next_gs = interface.make_pseudo_move(state, m)
            # Log the resulting game state
            interface.log(next_gs.fen)
            
        # Return a random legal move
        return random.choice(moves)