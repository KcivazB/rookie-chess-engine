import random, time

def find_random_moves(valid_moves):
    time.sleep(1.5) # Simulate delay for now as either the moves append too fast
    return valid_moves[random.randint(0, len(valid_moves) -1)] # Return a random valid move 


def find_best_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) -1)] # Return a random valid move 
