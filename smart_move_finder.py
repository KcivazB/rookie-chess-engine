import random
import time
from transposition_table import TranspositionTable
from constants import (
    STARTING_DEPTH,
    ENDING_DEPTH,
    END_GAME_SCORE,
    PIECE_SCORES,
    PIECE_POSITION_SCORE,
    CASTLING_RIGHT_SCORE,
    CHECK_MATE_SCORE,
    STALE_MATE_SCORE,
    WINNING_CAPTURE_THRESHOLD,
)


class MoveSearch:
    """
    A class to handle the AI logic for finding the best move in a chess game.
    """
    def __init__(self, game_state):
        self.game_state = game_state  # The current game state
        self.history_table = {}  # History table for non-capture move ordering
        self.transposition_table = TranspositionTable()  # The transposition table
        self.evaluation_count = 0  # Number of positions evaluated
        self.next_moves = []  # List to store the best moves found at the root depth

    def pick_random_move(self, moves):
        random_move = random.choice(moves)
        print("Random Move from find_random_moves: " + str(random_move))
        return random_move

    def find_best_move(self, valid_moves, return_queue):
        """
        Finds the best move by initiating the search process.
        
        Args:
            valid_moves (list): List of all valid moves for the current position.
            return_queue (Queue): Queue to return the best move to the caller.
        """
        self.evaluation_count = 0
        self.next_moves = []
        start_time = time.time()

        # Load the transposition table if it exists
        self.transposition_table.load('transposition_table.pkl')

        # Decide the depth of search based on the material score
        material_score = self.material_score()
        search_depth = ENDING_DEPTH if material_score <= END_GAME_SCORE else STARTING_DEPTH

        print(f"Material score: {material_score}")
        print(f"Using {'Ending Depth' if material_score <= END_GAME_SCORE else 'Starting Depth'} for score: {material_score}")

        # Start the negamax search with alpha-beta pruning
        self.negamax_search(valid_moves, search_depth, -CHECK_MATE_SCORE, CHECK_MATE_SCORE, 1 if self.game_state.white_to_move else -1)

        elapsed_time = time.time() - start_time
        print(f"Total possibilities evaluated: {self.evaluation_count} in {elapsed_time:.2f}s")
        print(f"Potential best moves count: {len(self.next_moves)}")

        # Save the transposition table for future use
        self.transposition_table.save('transposition_table.pkl')
        best_move = self.pick_random_move(self.next_moves)
        return_queue.put(best_move)

    def negamax_search(self, valid_moves, depth, alpha, beta, turn_multiplier):
        """
        Negamax search with alpha-beta pruning, incorporating transposition table and move ordering.

        Args:
            valid_moves (list): List of all valid moves for the current position.
            depth (int): The current search depth.
            alpha (int): Alpha value for alpha-beta pruning.
            beta (int): Beta value for alpha-beta pruning.
            turn_multiplier (int): 1 if it's white's turn, -1 if it's black's turn.

        Returns:
            int: The evaluated score of the best move found.
        """
        # Hash the current board position
        board_hash = hash(str(self.game_state.board))
        stored_score, stored_depth, flag, stored_best_move = self.transposition_table.lookup(board_hash)

        # Check the transposition table to potentially skip searching this node
        if stored_depth is not None and stored_depth >= depth:
            if flag == 'exact':
                return stored_score
            elif flag == 'lower':
                alpha = max(alpha, stored_score)
            elif flag == 'upper':
                beta = min(beta, stored_score)

        # Base case: if depth is 0 or game is over, evaluate the board
        if depth == 0 or self.game_state.is_game_over:
            self.evaluation_count += 1
            return turn_multiplier * self.evaluate_board()

        max_score = -CHECK_MATE_SCORE
        ordered_moves = self.order_moves(valid_moves, depth, stored_best_move)

        for move in ordered_moves:
            # Recursively search deeper after making the move
            self.game_state.make_move(move)
            next_valid_moves = self.game_state.get_all_valid_moves()
            score = -self.negamax_search(next_valid_moves, depth - 1, -beta, -alpha, -turn_multiplier)
            self.game_state.undo_last_move()

            if score > max_score:
                max_score = score
                if depth == STARTING_DEPTH:
                    self.next_moves = [move]
            elif score == max_score:
                if depth == STARTING_DEPTH:
                    self.next_moves.append(move)

            alpha = max(alpha, score)
            if alpha >= beta:
                # Store the current move as a killer move
                if depth in self.transposition_table.killer_moves:
                    self.transposition_table.killer_moves[depth] = [move] + self.transposition_table.killer_moves.get(depth, [None, None])[:1]
                break

        # Store the evaluation in the transposition table
        if depth == STARTING_DEPTH:
            flag = 'upper' if max_score <= alpha else 'lower' if max_score >= beta else 'exact'
            self.transposition_table.store(board_hash, max_score, depth, flag, self.next_moves[0] if self.next_moves else None)

        # Update history heuristic
        for move in ordered_moves:
            self.update_history(move)

        return max_score

    def order_moves(self, moves, depth, hash_move):
        """
        Orders the moves based on various heuristics: principal variation, hash move, captures, and killer moves.

        Args:
            moves (list): List of possible moves.
            depth (int): Current search depth.
            hash_move (Move): The move from the transposition table.

        Returns:
            list: Ordered list of moves.
        """
        ordered_moves = []

        # Get the best move from the principal variation
        pv_move = self.next_moves[0] if self.next_moves else None

        # Add principal variation move first
        if pv_move in moves:
            ordered_moves.append(pv_move)
            moves.remove(pv_move)

        # Add hash move from the transposition table
        if hash_move and hash_move in moves:
            ordered_moves.append(hash_move)
            moves.remove(hash_move)

        # Sort captures into winning and equal categories
        winning_captures = [move for move in moves if self.is_capture_move(move) and self.is_winning_capture(move)]
        equal_captures = [move for move in moves if self.is_capture_move(move) and not self.is_winning_capture(move)]
        non_captures = [move for move in moves if not self.is_capture_move(move)]

        # Add killer moves if available
        if depth in self.transposition_table.killer_moves:
            killer_move1, killer_move2 = self.transposition_table.killer_moves[depth]
            if killer_move1 in moves:
                ordered_moves.append(killer_move1)
                moves.remove(killer_move1)
            if killer_move2 in moves:
                ordered_moves.append(killer_move2)
                moves.remove(killer_move2)

        # Add winning captures, equal captures, and non-captures (sorted by history heuristic)
        ordered_moves.extend(winning_captures)
        ordered_moves.extend(equal_captures)
        ordered_moves.extend(sorted(non_captures, key=lambda move: self.history_heuristic(move), reverse=True))

        # Add losing captures last
        losing_captures = [move for move in moves if self.is_capture_move(move) and not self.is_winning_capture(move)]
        ordered_moves.extend(losing_captures)

        return ordered_moves

    def evaluate_board(self):
        """
        Evaluates the board based on material, central control, castling rights, and other heuristics.
        
        Returns:
            int: The evaluation score of the board position.
        """
        score = 0

        # Check for checkmate or stalemate
        if self.game_state.is_check_mate:
            return CHECK_MATE_SCORE if self.game_state.white_to_move else -CHECK_MATE_SCORE
        elif self.game_state.is_stale_mate:
            return STALE_MATE_SCORE

        # Calculate the material score and positional bonuses
        pieces_score = sum(
            PIECE_SCORES[square[1]] + PIECE_POSITION_SCORE[square][row][col]
            for row in range(len(self.game_state.board))
            for col, square in enumerate(self.game_state.board[row])
            if square != "--"
        )

        # Add score for central control
        central_control_score = sum(
            10 if self.game_state.board[row][col][0] == "w" else -10
            for (row, col) in [(3, 3), (3, 4), (4, 3), (4, 4)]
            if self.game_state.board[row][col] != "--"
        )

        # Add scores for attacked and defended pieces and castling rights
        attacked_pieces_score = self.count_attacked_pieces('w') - self.count_attacked_pieces('b')
        defended_pieces_score = self.count_defended_pieces('w') - self.count_defended_pieces('b')
        castling_rights_score = self.count_enemy_castling_rights()

        # Aggregate the final score
        score += pieces_score + central_control_score + attacked_pieces_score + defended_pieces_score + castling_rights_score
        return score

    def material_score(self):
        """
        Calculates the material score of the current board.
        
        Returns:
            int: The material score.
        """
        return sum(PIECE_SCORES[square[1]] for row in self.game_state.board for square in row if square != "--")

    def update_history(self, move):
        move_key = str(move)
        self.history_table[move_key] = self.history_table.get(move_key, 0) + 1

    def history_heuristic(self, move):
        """
        Retrieves the history heuristic value for the given move.
        
        Args:
            move (Move): The move to retrieve the history heuristic for.
        
        Returns:
            int: The history heuristic value.
        """
        return self.history_table.get(str(move), 0)

    def is_capture_move(self, move):
        """
        Checks if a move is a capture move.
        """
        return move.piece_captured != "--"

    def is_winning_capture(self, move):
        """
        Determines if a capture move is a winning capture (i.e., captures a higher value piece).
        
        Args:
            move (Move): The capture move to evaluate.
        
        Returns:
            bool: True if the capture is winning, False otherwise.
        """
        capture_value = self.evaluate_capture(move)
        return capture_value >= WINNING_CAPTURE_THRESHOLD

    def evaluate_capture(self, move):
        """
        Evaluates the value of a capture move by comparing the values of the captured and capturing pieces.
        
        Args:
            move (Move): The capture move to evaluate.
        
        Returns:
            int: The net value of the capture (captured piece value - capturing piece value).
        """
        self.game_state.make_move(move)

        captured_value = PIECE_SCORES[move.piece_captured[1]] if move.piece_captured else 0
        capturing_piece = self.game_state.board[move.end_row][move.end_col]
        capturing_value = PIECE_SCORES[capturing_piece[1]] if capturing_piece != "--" else 0

        self.game_state.undo_last_move()

        return captured_value - capturing_value

    def count_attacked_pieces(self, piece_color):
        """
        Counts the number of opponent pieces attacked by the given color's pieces.
        
        Args:
            piece_color (str): 'w' for white, 'b' for black.
        
        Returns:
            int: The number of attacked opponent pieces.
        """
        directions = {
            'P': [(-1, -1), (-1, 1)] if piece_color == 'w' else [(1, -1), (1, 1)],
            'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
            'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
            'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        }

        attacked_pieces_count = 0

        for row in range(len(self.game_state.board)):
            for col in range(len(self.game_state.board[row])):
                square = self.game_state.board[row][col]
                if square != '--' and square[0] == piece_color:
                    piece_type = square[1]
                    if piece_type in directions:
                        for d in directions[piece_type]:
                            r, c = row + d[0], col + d[1]
                            if 0 <= r < len(self.game_state.board) and 0 <= c < len(self.game_state.board[0]):
                                if piece_type in 'RBNQK' and self.game_state.board[r][c][0] != piece_color:
                                    attacked_pieces_count += 1
                                elif piece_type == 'P' and self.game_state.board[r][c] != '--' and self.game_state.board[r][c][0] != piece_color:
                                    attacked_pieces_count += 1

        return attacked_pieces_count

    def count_defended_pieces(self, piece_color):
        """
        Counts the number of pieces defended by the given color's pieces.
        
        Args:
            piece_color (str): 'w' for white, 'b' for black.
        
        Returns:
            int: The number of defended pieces.
        """
        directions = {
            'P': [(1, -1), (1, 1)] if piece_color == 'w' else [(-1, -1), (-1, 1)],
            'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
            'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
            'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        }

        defended_pieces_count = 0

        for row in range(len(self.game_state.board)):
            for col in range(len(self.game_state.board[row])):
                square = self.game_state.board[row][col]
                if square != '--' and square[0] == piece_color:
                    piece_type = square[1]
                    if piece_type in directions:
                        for d in directions[piece_type]:
                            r, c = row + d[0], col + d[1]
                            if 0 <= r < len(self.game_state.board) and 0 <= c < len(self.game_state.board[0]):
                                if piece_type in 'RBNQK' and self.game_state.board[r][c] != '--' and self.game_state.board[r][c][0] == piece_color:
                                    defended_pieces_count += 1
                                elif piece_type == 'P' and self.game_state.board[r][c] != '--' and self.game_state.board[r][c][0] == piece_color:
                                    defended_pieces_count += 1

        return defended_pieces_count

    def count_enemy_castling_rights(self):
        """
        Counts the castling rights of the opponent and adjusts the score accordingly.
        
        Returns:
            int: The score adjustment based on the opponent's castling rights.
        """
        score = 0
        if not self.game_state.white_to_move: 
            if self.game_state.current_castling_rights.wKs or self.game_state.current_castling_rights.wQs:
                score -= CASTLING_RIGHT_SCORE            
        else: 
            if self.game_state.current_castling_rights.bKs or self.game_state.current_castling_rights.bQs: 
                score -= CASTLING_RIGHT_SCORE

        return score


def find_best_move(gs, valid_moves, return_queue):
    """
    Wrapper function to create a MoveSearch instance and find the best move.
    
    Args:
        gs (GameState): The current game state.
        valid_moves (list): List of all valid moves for the current position.
        return_queue (Queue): Queue to return the best move to the caller.
    """
    search_agent = MoveSearch(gs)
    search_agent.find_best_move(valid_moves, return_queue)
