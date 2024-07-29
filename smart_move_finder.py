import random, time
import chess_engine

PIECE_SCORES = {
    "K" : 0,
    "P" : 1,
    "R" : 5,
    "B" : 3,
    "N" : 3,
    "Q" : 10
}

CHECK_MATE_SCORE = 1000
STALE_MATE_SCORE = 0

def find_random_moves(valid_moves):
    random_move = valid_moves[random.randint(0, len(valid_moves) -1)]
    print("Random Move from find_random_moves : " + str(random_move))

    return random_move # Return a random valid move 

def find_best_move_material_based(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1

    opponent_lowest_max_score = CHECK_MATE_SCORE # Start from check mate score and try to keep opponent max score as low as possible (MINMAX)
    best_player_moves = []

    for player_move in valid_moves:
        gs.make_move(player_move)
        # Generate all of the opponent future moves
        opponent_moves = gs.get_all_valid_moves()
        opponent_max_score = -CHECK_MATE_SCORE  # Set the max opponent score

        for opponent_move in opponent_moves:
            # Execture the move
            gs.make_move(opponent_move)

            if gs.is_check_mate :
                score = -turn_multiplier * CHECK_MATE_SCORE
            elif gs.is_stale_mate :
                score = STALE_MATE_SCORE
            else :
                score = -turn_multiplier * board_score_based_on_material(gs.board) # Update the new score value
            print("Move Score score : " + str(score))

            if score > opponent_max_score: # If score is better than best, then it's the new best
                opponent_max_score = score
                print("Actual Best opponent score : " + str(score))
                print("Actual Best opponent Move : " + str(player_move))
            elif score == opponent_max_score: # If score is same as best_score, add it to the best moves list
                print("Another move with the same Best score for the opponent: " + str(player_move))
            gs.undo_last_move()
        
        if  opponent_max_score < opponent_lowest_max_score:

            opponent_lowest_max_score = opponent_max_score
            best_player_moves = [player_move]  # Reset the best moves list

        elif opponent_max_score == opponent_lowest_max_score:
            best_player_moves.append(player_move)

        gs.undo_last_move()

    final_best_move = find_random_moves(best_player_moves) # Pick a random move in the list of best moves
    print("Best move count from find_best_move_material_based : " + str(len(best_player_moves)))
    return final_best_move

'''
Evaluate the board score based on material.
'''
def board_score_based_on_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += PIECE_SCORES[square[1]]
            elif square[0] == "b":
                score -= PIECE_SCORES[square[1]]
    print("Score based on material: " + str(score))
    return score

def find_best_move(gs, valid_moves):
    time.sleep(0.5) # Simulate delay for now as either the moves append too fast

    best_move = find_best_move_material_based(gs, valid_moves)
    return best_move
