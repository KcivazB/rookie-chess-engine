import random
import time
import pickle
from constants import STARTING_DEPTH, ENDING_DEPTH, END_GAME_SCORE, PIECE_SCORES, PIECE_POSITION_SCORE, CASTLING_RIGHT_SCORE, CHECK_MATE_SCORE, STALE_MATE_SCORE, MOVE_SEARCH_TIME_LIMIT

history_table = {}

def pick_random_valid_move(valid_moves):
    random_move = valid_moves[random.randint(0, len(valid_moves) - 1)]
    print("Random Move from pick_random_valid_move: " + str(random_move))
    return random_move

def find_best_move(gs, valid_moves, return_queue, time_limit=5.0):
    global next_moves, evaluation_count
    evaluation_count = 0
    next_moves = []
    start_time = time.time()
    
    best_move = None

    actual_board_score = material_score_only(gs) 
    depth = 1
    
    while True:
        time_elapsed = time.time() - start_time
        if time_elapsed >= time_limit:
            print(f"Time limit reached at depth {depth-1}. Returning best move found.")
            break
        
        print(f"Searching at depth: {depth}")
        find_moves_negamax_alpha_beta(gs, valid_moves, depth, -CHECK_MATE_SCORE, CHECK_MATE_SCORE, 1 if gs.white_to_move else -1)
        
        if time.time() - start_time >= time_limit:
            print(f"Time limit reached during search at depth {depth}.")
            break

        # The best move found at this depth
        best_move = next_moves[0] if next_moves else best_move
        depth += 1

    elapsed_time = time.time() - start_time
    print(f"Potential best moves count: {len(next_moves)}")
    print(f"Total possibilities evaluated: {evaluation_count} in {elapsed_time:.2f}s")
    print(f"Max depth reached: {depth-1}")
    
    return_queue.put(best_move)
    

def find_moves_negamax_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_moves, evaluation_count

    if depth == 0 or gs.is_game_over:
        evaluation_count += 1
        score = turn_multiplier * board_score_based_on_gamestate(gs)
        return score

    max_score = -CHECK_MATE_SCORE
    best_moves = []

    ordered_moves = order_moves(valid_moves, depth, gs)

    for move in ordered_moves:
        gs.make_move(move)
        next_valid_moves = gs.get_all_valid_moves()
        score = -find_moves_negamax_alpha_beta(gs, next_valid_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        gs.undo_last_move()

        if score > max_score:
            max_score = score
            best_moves = [move]
        elif score == max_score:
            best_moves.append(move)

        alpha = max(alpha, score)
        if alpha >= beta:
            # Alpha-beta cutoff
            if depth in history_table:
                if not history_table[depth][0]:
                    history_table[depth][0] = move
                else:
                    history_table[depth][1] = move
            break

    # Update the best moves found at this depth
    next_moves = best_moves

    # Update history with the move and its score
    for move in ordered_moves:
        update_history(move, 1)  # Adjust the score as needed based on your heuristic

    return max_score

def order_moves(moves, depth, gs):
    ordered_moves = []

    # Add PV move (if exists)
    pv_move = next_moves[0] if next_moves else None
    if pv_move in moves:
        ordered_moves.append(pv_move)
        moves.remove(pv_move)

    # Add hash move (if exists)
    hash_move = None
    if hash_move and hash_move in moves:
        ordered_moves.append(hash_move)
        moves.remove(hash_move)

    # Categorize captures and promotions
    winning_captures = []
    equal_captures = []
    for move in moves:
        if is_capture(move):
            if is_winning_capture(move, gs):
                winning_captures.append(move)
            else:
                equal_captures.append(move)

    # Add winning captures
    ordered_moves.extend(winning_captures)

    # Add equal captures
    ordered_moves.extend(equal_captures)

    # Add killer moves (if any)
    killer_moves = history_table.get(depth, [None, None])
    if killer_moves:
        if killer_moves[0] and killer_moves[0] in moves:
            ordered_moves.append(killer_moves[0])
            moves.remove(killer_moves[0])
        if killer_moves[1] and killer_moves[1] in moves:
            ordered_moves.append(killer_moves[1])
            moves.remove(killer_moves[1])

    # Sort remaining non-captures by history heuristic
    non_captures = [move for move in moves if not is_capture(move)]
    sorted_non_captures = sorted(non_captures, key=lambda move: history_heuristic(move), reverse=True)

    # Add sorted non-captures
    ordered_moves.extend(sorted_non_captures)

    # Add losing captures
    losing_captures = [move for move in moves if is_capture(move) and not is_winning_capture(move, gs)]
    ordered_moves.extend(losing_captures)

    return ordered_moves

def is_capture(move):
    return move.piece_captured != "--"

def evaluate_capture(move, gs):
    gs.make_move(move)
    captured_piece = move.piece_captured
    captured_value = PIECE_SCORES[captured_piece[1]] if captured_piece else 0
    capturing_piece = gs.board[move.end_row][move.end_col]
    capturing_value = PIECE_SCORES[capturing_piece[1]] if capturing_piece != "--" else 0
    gs.undo_last_move()
    capture_value = captured_value - capturing_value
    return capture_value

def is_winning_capture(move, gs):
    capture_value = evaluate_capture(move, gs)
    WINNING_CAPTURE_THRESHOLD = 800
    return capture_value >= WINNING_CAPTURE_THRESHOLD

def update_history(move, score):
    move_key = str(move)  # Convert move to a string representation if necessary
    if move_key in history_table:
        history_table[move_key] += score
    else:
        history_table[move_key] = score

def history_heuristic(move):
    move_key = str(move)
    return history_table.get(move_key, 0)

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

    # Count enemy castling rights
    castling_rights_score = count_enemy_castling_rights(gs)
    return score + pieces_score + central_control_score + attacked_pieces_score + defended_pieces_score + castling_rights_score

def material_score_only(gs):
    material_value = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piece_type = square[1]
                piece_value = PIECE_SCORES[piece_type]
                material_value += piece_value 
    return material_value

def count_attacked_pieces(board, piece_color):
    attacked_pieces_count = 0

    directions = {
        'P': [(-1, -1), (-1, 1)] if piece_color == 'w' else [(1, -1), (1, 1)],
        'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
        'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
        'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
        'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    }

    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "--" and piece[0] == piece_color:
                piece_type = piece[1]
                for direction in directions.get(piece_type, []):
                    r, c = row + direction[0], col + direction[1]
                    while 0 <= r < 8 and 0 <= c < 8:
                        target = board[r][c]
                        if target != "--":
                            if target[0] != piece_color:
                                attacked_pieces_count += PIECE_SCORES.get(target[1], 0)
                            break
                        if piece_type in ['P', 'N', 'K']:
                            break
                        r += direction[0]
                        c += direction[1]

    return attacked_pieces_count

def count_defended_pieces(board, piece_color):
    defended_pieces_count = 0

    directions = {
        'P': [(-1, -1), (-1, 1)] if piece_color == 'w' else [(1, -1), (1, 1)],
        'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
        'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
        'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
        'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    }

    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "--" and piece[0] == piece_color:
                piece_type = piece[1]
                for direction in directions.get(piece_type, []):
                    r, c = row + direction[0], col + direction[1]
                    while 0 <= r < 8 and 0 <= c < 8:
                        target = board[r][c]
                        if target != "--":
                            if target[0] != piece_color:
                                defended_pieces_count += PIECE_SCORES.get(target[1], 0)
                            break
                        if piece_type in ['P', 'N', 'K']:
                            break
                        r += direction[0]
                        c += direction[1]

    return defended_pieces_count

def count_enemy_castling_rights(gs):
    castling_rights_score = 0
    if gs.white_to_move:
        if gs.current_castling_rights.wKs or gs.current_castling_rights.wQs:
            castling_rights_score += CASTLING_RIGHT_SCORE
    else:
        if gs.current_castling_rights.bKs or gs.current_castling_rights.bQs:
            castling_rights_score += CASTLING_RIGHT_SCORE
    return castling_rights_score

def is_capture(move):
    return move.piece_captured != "--"

def evaluate_capture(move, gs):
    gs.make_move(move)
    captured_piece = move.piece_captured
    captured_value = PIECE_SCORES[captured_piece[1]] if captured_piece else 0
    capturing_piece = gs.board[move.end_row][move.end_col]
    capturing_value = PIECE_SCORES[capturing_piece[1]] if capturing_piece != "--" else 0
    gs.undo_last_move()
    capture_value = captured_value - capturing_value
    return capture_value

def is_winning_capture(move, gs):
    capture_value = evaluate_capture(move, gs)
    WINNING_CAPTURE_THRESHOLD = 320
    return capture_value >= WINNING_CAPTURE_THRESHOLD

def update_history(move, score):
    move_key = str(move)  # Convert move to a string representation if necessary
    if move_key in history_table:
        history_table[move_key] += score
    else:
        history_table[move_key] = score

def history_heuristic(move):
    move_key = str(move)
    return history_table.get(move_key, 0)

def material_score_only(gs):
    material_value = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piece_type = square[1]
                piece_value = PIECE_SCORES[piece_type]
                material_value += piece_value 
    return material_value
