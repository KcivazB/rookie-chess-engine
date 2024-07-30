import random, time
import chess_engine
from constants import MAX_DEPTH, PIECE_SCORES, CHECK_MATE_SCORE, STALE_MATE_SCORE


def pick_random_valid_move(valid_moves):
    random_move = valid_moves[random.randint(0, len(valid_moves) -1)]
    print("Random Move from find_random_moves : " + str(random_move))

    return random_move # Return a random valid move 

'''
Helper Method to make the first responsive call to MinMax
'''
def find_best_move_minmax(gs, valid_moves):
    global next_moves, evaluation_count
    evaluation_count = 0  # Reset the counter
    next_moves = [] #Init next moves as an array of all the potentials best moves 
    start_time = time.time()  # Record the start time
    find_moves_negamax(gs, valid_moves, MAX_DEPTH, 1 if gs.white_to_move else -1) # sets next_moves as an array of the potentials best moves
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Potential best moves count: {len(next_moves)}")
    print(f"Total possibilities evaluated: {evaluation_count} in {elapsed_time:.2f}s")

    return pick_random_valid_move(next_moves)

'''
Helper Method to make the first responsive call to NegaMax
'''
def find_best_move_negamax(gs, valid_moves):
    global next_moves, evaluation_count
    evaluation_count = 0  # Reset the counter
    next_moves = [] #Init next moves as an array of all the potentials best moves 
    start_time = time.time()  # Record the start time
    find_moves_minmax(gs, valid_moves, MAX_DEPTH, gs.white_to_move) # sets next_moves as an array of the potentials best moves
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Potential best moves count: {len(next_moves)}")
    print(f"Total possibilities evaluated: {evaluation_count} in {elapsed_time:.2f}s")

    return pick_random_valid_move(next_moves)

'''
Recursively implemented find_best_move_material_based -- Using minMax
'''
def find_moves_minmax(gs, valid_moves, depth, white_to_move):
    global next_moves, evaluation_count
    if depth == 0 : # Depth gets to 0 -> This is a terminal node
        evaluation_count += 1
        return board_score_based_on_gamestate(gs)
    
    if white_to_move:
        max_score = -CHECK_MATE_SCORE
        for move in valid_moves:
            gs.make_move(move)
            next_valid_moves = gs.get_all_valid_moves()
            score = find_moves_minmax(gs, next_valid_moves, depth -1, False)
            if score > max_score :
                max_score = score
                if depth == MAX_DEPTH:
                    next_moves = [move]
            if score == max_score :
                max_score = score
                if depth == MAX_DEPTH:
                    next_moves.append(move)
            gs.undo_last_move()
        return max_score
    else :
        min_score = CHECK_MATE_SCORE
        for move in valid_moves:
            gs.make_move(move)
            next_valid_moves = gs.get_all_valid_moves()
            score = find_moves_minmax(gs, next_valid_moves, depth -1, True)
            if score < min_score :
                min_score = score
                if depth == MAX_DEPTH:
                    next_moves = [move]
            elif score == min_score :
                min_score = score
                if depth == MAX_DEPTH:
                    next_moves.append(move)
            gs.undo_last_move()
        return min_score

'''
Recursively implemented find_best_move_material_based -- Using NegaMax -- Same as minMax but shorter to write
'''
def find_moves_negamax(gs, valid_moves, depth, turn_multiplier):
    global next_moves, evaluation_count
    if depth == 0 : # Depth gets to 0 -> This is a terminal node
        evaluation_count += 1
        return turn_multiplier * board_score_based_on_gamestate(gs)

    max_score = -CHECK_MATE_SCORE
    for move in valid_moves:
        gs.make_move(move)
        next_valid_moves = gs.get_all_valid_moves()
        gs.undo_last_move()
        score = -find_moves_negamax(gs, valid_moves, depth, -turn_multiplier) # Find the opponent max score
        if score > max_score: 
            max_score = score
            if depth == MAX_DEPTH:
                next_moves = [move]
        elif score == max_score: 
            max_score = score
            if depth == MAX_DEPTH:
                next_moves.append(move)
    return max_score


'''
Evaluate the board score based on gameState
A positive score is good for white
Negative score is good for black
'''
def board_score_based_on_gamestate(gs):
    score = 0
    pieces_score = 0

    #Attribute points for central pieces 
    #Attribute points for bishop pair (a pair is worth more than a lone bishop)
    #Changes points values depending on the game phase (opening, midlle , endgame)

    #If board is CHECK MATE or STALE MATE
    if gs.is_check_mate:
        if gs.white_to_move: # White is check mate
            return -CHECK_MATE_SCORE
        else : # White wins
            return CHECK_MATE_SCORE
    elif gs.is_stale_mate:
        return STALE_MATE_SCORE

    #Evaluate pieces scores 
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                pieces_score += PIECE_SCORES[square[1]]
            elif square[0] == "b":
                pieces_score -= PIECE_SCORES[square[1]]


    final_score = score + pieces_score
    return final_score
