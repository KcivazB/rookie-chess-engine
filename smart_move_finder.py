import random, time
import chess_engine
from constants import MAX_DEPTH, PIECE_SCORES, PIECE_POSITION_SCORE, CHECK_MATE_SCORE, STALE_MATE_SCORE
import pickle

def pick_random_valid_move(valid_moves):
    random_move = valid_moves[random.randint(0, len(valid_moves) - 1)]
    print("Random Move from find_random_moves : " + str(random_move))
    return random_move  # Return a random valid move 

def find_best_move(gs, valid_moves, return_queue):
    global next_moves, evaluation_count
    evaluation_count = 0
    next_moves = []
    start_time = time.time()

    transposition_table = TranspositionTable()
    transposition_table.load('transposition_table.pkl')

    print(f"Transposition table length : {len(transposition_table.table)}")

    find_moves_negamax_alpha_beta_with_memory(gs, valid_moves, MAX_DEPTH, -CHECK_MATE_SCORE, CHECK_MATE_SCORE, 1 if gs.white_to_move else -1, transposition_table)

    print("Search complete. Log written to negamax_log.txt")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Potential best moves count: {len(next_moves)}")
    print(f"Total possibilities evaluated: {evaluation_count} in {elapsed_time:.2f}s")

    transposition_table.save('transposition_table.pkl')

    best_move = pick_random_valid_move(next_moves)
    return_queue.put(best_move)

     
"""
Negamax function with alpha-beta pruning for move generation and evaluation.
Logs detailed move information and search parameters to a file.

Args:
    gs: The game state object containing the board and game status.
    valid_moves: List of all valid moves for the current player.
    depth: The current search depth.
    alpha: The best score that the maximizer can guarantee.
    beta: The best score that the minimizer can guarantee.
    turn_multiplier: 1 for white's turn, -1 for black's turn.
    log_file: File object to write the log information.

Returns:
    int: The score of the best move found.
"""
def find_moves_negamax_alpha_beta_with_memory(gs, valid_moves, depth, alpha, beta, turn_multiplier, transposition_table):
    global next_moves, evaluation_count

    board_hash = hash_board(gs.board)
    stored_score, stored_depth, flag, stored_best_move = transposition_table.lookup(board_hash)

    # Check for stored value in the transposition table (Null Window)
    if stored_depth is not None and stored_depth >= depth:
        if flag == 'exact':
            return stored_score
        elif flag == 'lower' and stored_score > alpha:
            alpha = stored_score
        elif flag == 'upper' and stored_score < beta:
            beta = stored_score

    # Base case: Return the evaluation of the board if depth is 0 or game is over
    if depth == 0 or gs.is_game_over:
        evaluation_count += 1
        score = turn_multiplier * board_score_based_on_gamestate(gs)
        return score

    max_score = -CHECK_MATE_SCORE
    best_moves = []

    # Iterate through all valid moves
    for move in valid_moves:
        gs.make_move(move)
        next_valid_moves = gs.get_all_valid_moves()
        score = -find_moves_negamax_alpha_beta_with_memory(gs, next_valid_moves, depth - 1, -beta, -alpha, -turn_multiplier, transposition_table)
        gs.undo_last_move()

        # Update the best score and best moves list
        if score > max_score:
            max_score = score
            best_moves = [move]
        elif score == max_score:
            best_moves.append(move)

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    # Store the result in the transposition table
    if depth == MAX_DEPTH:
        if max_score <= alpha:
            flag = 'upper'
        elif max_score >= beta:
            flag = 'lower'
        else:
            flag = 'exact'
        transposition_table.store(board_hash, max_score, depth, flag, best_moves[0] if best_moves else None)
        next_moves = best_moves

    return max_score




# def move_heuristic(gs, move):
#     # Placeholder for actual heuristic function
#     # Example: prioritize captures, checks, or other heuristics
#     gs.make_move(move)
#     score = board_score_based_on_gamestate(gs)
#     gs.undo_last_move()
#     return score

'''
Evaluate the board score based on gameState
A positive score is good for white
Negative score is good for black
'''
def board_score_based_on_gamestate(gs):
    score = 0
    pieces_score = 0
    central_control_score = 0

    if gs.is_check_mate:
        return CHECK_MATE_SCORE if gs.white_to_move else -CHECK_MATE_SCORE
    elif gs.is_stale_mate:
        return STALE_MATE_SCORE

    # Calculate piece scores
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piece_color = square[0]
                piece_type = square[1]
                piece_value = PIECE_SCORES[piece_type]
               
                position_score = PIECE_POSITION_SCORE[square][row][col]

                if piece_color == "w":
                    pieces_score += piece_value + position_score
                else:
                    pieces_score -= piece_value + position_score

                # Central control example
                if (row, col) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    central_control_score += 10 if piece_color == "w" else -10

    # Count attacked and defended pieces
    attacked_pieces_score = count_attacked_pieces(gs.board, 'w') - count_attacked_pieces(gs.board, 'b')
    defended_pieces_score = count_defended_pieces(gs.board, 'w') - count_defended_pieces(gs.board, 'b')

    return score + pieces_score + central_control_score + attacked_pieces_score + defended_pieces_score

def count_attacked_pieces(board, piece_color):
    """
    Counts the number of opponent pieces attacked by the given color's pieces.
    """
    attacked_pieces_count = 0

    # Define movement directions for each piece type
    directions = {
        'P': [(-1, -1), (-1, 1)] if piece_color == 'w' else [(1, -1), (1, 1)],
        'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
        'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
        'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
        'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    }

    # Iterate through each square on the board
    for row in range(len(board)):
        for col in range(len(board[row])):
            square = board[row][col]
            # Check if the piece belongs to the given color
            if square != '--' and square[0] == piece_color:
                piece_type = square[1]
                if piece_type in directions:
                    # Check all possible attack directions for the piece
                    for d in directions[piece_type]:
                        r, c = row + d[0], col + d[1]
                        if 0 <= r < len(board) and 0 <= c < len(board[0]):
                            # Check if the target square contains an opponent piece
                            if piece_type in 'RBNQK' and board[r][c][0] != piece_color:
                                attacked_pieces_count += 1
                            elif piece_type == 'P' and board[r][c] != '--' and board[r][c][0] != piece_color:
                                attacked_pieces_count += 1

    return attacked_pieces_count

def count_defended_pieces(board, piece_color):
    """
    Counts the number of pieces defended by the given color's pieces.
    """
    defended_pieces_count = 0

    # Define movement directions for each piece type
    directions = {
        'P': [(1, -1), (1, 1)] if piece_color == 'w' else [(-1, -1), (-1, 1)],
        'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
        'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
        'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
        'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    }

    # Iterate through each square on the board
    for row in range(len(board)):
        for col in range(len(board[row])):
            square = board[row][col]
            # Check if the piece belongs to the given color
            if square != '--' and square[0] == piece_color:
                piece_type = square[1]
                if piece_type in directions:
                    # Check all possible defense directions for the piece
                    for d in directions[piece_type]:
                        r, c = row + d[0], col + d[1]
                        if 0 <= r < len(board) and 0 <= c < len(board[0]):
                            # Check if the target square contains a piece of the same color
                            if piece_type in 'RBNQK' and board[r][c] != '--' and board[r][c][0] == piece_color:
                                defended_pieces_count += 1
                            elif piece_type == 'P' and board[r][c] != '--' and board[r][c][0] == piece_color:
                                defended_pieces_count += 1

    return defended_pieces_count

# '''
# Recursively implemented find_best_move_material_based -- Using minMax
# '''
# def find_moves_minmax(gs, valid_moves, depth, white_to_move):
#     global next_moves, evaluation_count
#     if depth == 0 : # Depth gets to 0 -> This is a terminal node
#         evaluation_count += 1
#         return board_score_based_on_gamestate(gs)
    
#     if white_to_move:
#         max_score = -CHECK_MATE_SCORE
#         for move in valid_moves:
#             gs.make_move(move)
#             next_valid_moves = gs.get_all_valid_moves()
#             score = find_moves_minmax(gs, next_valid_moves, depth -1, False)
#             if score > max_score :
#                 max_score = score
#                 if depth == MAX_DEPTH:
#                     next_moves = [move]
#             if score == max_score :
#                 max_score = score
#                 if depth == MAX_DEPTH:
#                     next_moves.append(move)
#             gs.undo_last_move()
#         return max_score
#     else :
#         min_score = CHECK_MATE_SCORE
#         for move in valid_moves:
#             gs.make_move(move)
#             next_valid_moves = gs.get_all_valid_moves()
#             score = find_moves_minmax(gs, next_valid_moves, depth -1, True)
#             if score < min_score :
#                 min_score = score
#                 if depth == MAX_DEPTH:
#                     next_moves = [move]
#             elif score == min_score :
#                 min_score = score
#                 if depth == MAX_DEPTH:
#                     next_moves.append(move)
#             gs.undo_last_move()
#         return min_score

def hash_board(board):
    return hash(str(board))

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def store(self, board_hash, score, depth, flag, best_move=None):
        self.table[board_hash] = (score, depth, flag, best_move)

    def lookup(self, board_hash):
        return self.table.get(board_hash, (None, None, None, None))

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.table, file)
        print(f"Transposition table saved to {filename}")

    def load(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.table = pickle.load(file)
            print(f"Transposition table loaded from {filename}")
        except FileNotFoundError:
            print(f"No existing transposition table found at {filename}. Starting fresh.")
            self.table = {}
