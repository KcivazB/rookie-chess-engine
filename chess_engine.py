class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves
        }

        self.white_to_move = True
        self.castle_authorization = {
            "WHITE": True,
            "BLACK": True
        }

        self.w_king_location = (7, 4)
        self.b_king_location = (0, 4)

        self.in_check = False
        self.pinned_pieces = []
        self.checks = []

        self.en_passant_possible_square = ()

        self.is_stale_mate = False
        self.is_check_mate = False

        self.move_log = []

    def make_move(self, move):
        """Execute a move and update the board."""
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)

        # Update the king's location if moved
        if move.piece_moved == "wK":
            self.w_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.b_king_location = (move.end_row, move.end_col)

        #Handle En Passant Move
        if move.is_en_passant_move :
            # Capture the pawn 
            self.board[move.start_row][move.end_col] = "--"

        # Handle pawn promotion (assuming promotion to queen for simplicity)
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        #Update en_passant_possible state
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible_square = ( (move.start_row + move.end_row) // 2, move.start_col )
            print("en passant possible in " + str(self.en_passant_possible_square))
        else:
            self.en_passant_possible_square = ()

        # Next player's turn
        self.white_to_move = not self.white_to_move

    def undo_last_move(self):
        """Undo the last move made."""
        if len(self.move_log) != 0:
            last_move = self.move_log.pop()
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved

            # Update the king's location if moved
            if last_move.piece_moved == "wK":
                self.w_king_location = (last_move.start_row, last_move.start_col)
            elif last_move.piece_moved == "bK":
                self.b_king_location = (last_move.start_row, last_move.start_col)
            
            if last_move.is_en_passant_move :
                self.board[last_move.end_row][last_move.end_col] = "--"
                self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured
                self.en_passant_possible_square = (last_move.end_row, last_move.end_col)

            self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()
            self.white_to_move = not self.white_to_move



    def get_all_valid_moves(self):
        temp_en_passant_possible_square = self.en_passant_possible_square
        self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()


        if self.white_to_move:
            K_row = self.w_king_location[0]
            K_col = self.w_king_location[1]
        else:
            K_row = self.b_king_location[0]
            K_col = self.b_king_location[1]
        
        if self.in_check: 
            if len(self.checks) == 1: # If theres only one check, block check or move king
                valid_moves = self.get_all_possible_moves()

                #To block a chess you either move or block one of the square between king and piece
                check = self.checks[0] # Get check data
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []

                #if the piece checking is a knight then you capture it or move
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else : # Piece checking is not a knight
                    for i in range(1,8):
                        valid_square = (K_row + check[2] * i, K_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #stop once you get to the piece that end checks 
                            break
                #Get rid of the moves that don't block check or move the king 
                for i in range(len(valid_moves) -1, -1, -1): 
                    if valid_moves[i].piece_moved[1] != "K" : #Not moving the king, so move has to block or capture 
                        if not (valid_moves[i].end_row, valid_moves[i].end_col) in valid_squares:
                            valid_moves.remove(valid_moves[i])
            else: # Double check -> King has to move
                self.get_king_moves(K_row, K_col, valid_moves)
        else:  # Not in check then all moves are valid ! 
            valid_moves = self.get_all_possible_moves()

        #If no valid move and check -> check_mate 
        #If no valid move and ! check -> stale_mate 
        if len(valid_moves) == 0:
            if self.is_in_check():
                self.is_check_mate = True
            else:
                self.is_stale_mate = True
        else:
            self.is_check_mate = False
            self.is_stale_mate = False

        self.en_passant_possible_square = temp_en_passant_possible_square
        return valid_moves

    def is_in_check(self):
        """Determine if the current player's king is in check."""
        if self.white_to_move:
            return self.is_square_under_attack(self.w_king_location[0], self.w_king_location[1])
        else:
            return self.is_square_under_attack(self.b_king_location[0], self.b_king_location[1])

    def is_square_under_attack(self, r, c):
        """Determine if a given square is under attack by the opponent."""
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move

        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False


    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color_to_play = self.board[r][c][0]
                if (color_to_play == "w" and self.white_to_move) or (color_to_play == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves


    def check_for_pins_and_checks(self):
        pinned_pieces = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.w_king_location[0]
            start_col = self.w_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.b_king_location[0]
            start_col = self.b_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "P" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pinned_pieces.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pinned_pieces, checks



    '''
    HANDLING PAWN MOVES
    '''
    def get_pawn_moves(self, r, c, moves):
        # Determine if the piece is pinned and the direction of the pin
        is_piece_pinned = False
        pin_direction = ()

        # Check if the pawn is pinned
        for i in range(len(self.pinned_pieces) - 1, -1, -1):
            if self.pinned_pieces[i][0] == r and self.pinned_pieces[i][1] == c:
                is_piece_pinned = True
                pin_direction = (self.pinned_pieces[i][2], self.pinned_pieces[i][3])
                self.pinned_pieces.remove(self.pinned_pieces[i])
                break

        # Generate pawn moves based on the color to move
        if self.white_to_move:
            self._get_white_pawn_moves(r, c, moves, is_piece_pinned, pin_direction)
        else:
            self._get_black_pawn_moves(r, c, moves, is_piece_pinned, pin_direction)

    def _get_white_pawn_moves(self, r, c, moves, is_piece_pinned, pin_direction):
        # White pawn moves
        # One square forward move
        if self.board[r-1][c] == "--":
            if not is_piece_pinned or pin_direction == (-1, 0):
                moves.append(Move((r, c), (r-1, c), self.board))
                # Two squares forward move from the base rank
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))

        # Capture to the left
        if c-1 >= 0:
            if self.board[r-1][c-1][0] == "b":
                if not is_piece_pinned or pin_direction == (-1, -1):
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            # Handle En Passant
            elif (r-1, c-1) == self.en_passant_possible_square:
                if not is_piece_pinned or pin_direction == (-1, -1):
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_en_passant_move=True))

        # Capture to the right
        if c+1 <= 7:
            if self.board[r-1][c+1][0] == "b":
                if not is_piece_pinned or pin_direction == (-1, 1):
                    moves.append(Move((r, c), (r-1, c+1), self.board))
            # Handle En Passant
            elif (r-1, c+1) == self.en_passant_possible_square:
                if not is_piece_pinned or pin_direction == (-1, 1):
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_en_passant_move=True))
        

    def _get_black_pawn_moves(self, r, c, moves, is_piece_pinned, pin_direction):
        # Black pawn moves
        # One square forward move
        if self.board[r+1][c] == "--":
            if not is_piece_pinned or pin_direction == (1, 0):
                moves.append(Move((r, c), (r+1, c), self.board))
                # Two squares forward move from the base rank
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

        # Capture to the left
        if c-1 >= 0:
            if self.board[r+1][c-1][0] == "w":
                if not is_piece_pinned or pin_direction == (1, -1):
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            # Handle En Passant
            elif (r+1, c-1) == self.en_passant_possible_square:
                if not is_piece_pinned or pin_direction == (1, -1):
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_en_passant_move=True))

        # Capture to the right
        if c+1 <= 7:
            if self.board[r+1][c+1][0] == "w":
                if not is_piece_pinned or pin_direction == (1, 1):
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            # Handle En Passant
            elif (r+1, c+1) == self.en_passant_possible_square:
                if not is_piece_pinned or pin_direction == (1, 1):
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_en_passant_move=True))

    def get_rook_moves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pinned_pieces) - 1, -1, -1):
            if self.pinned_pieces[i][0] == row and self.pinned_pieces[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pinned_pieces[i][2], self.pinned_pieces[i][3])
                if self.board[row][col][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pinned_pieces.remove(self.pinned_pieces[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check for possible moves only in boundaries of the board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def get_knight_moves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(self.pinned_pieces) - 1, -1, -1):
            if self.pinned_pieces[i][0] == row and self.pinned_pieces[i][1] == col:
                piece_pinned = True
                self.pinned_pieces.remove(self.pinned_pieces[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if self.white_to_move else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pinned_pieces) - 1, -1, -1):
            if self.pinned_pieces[i][0] == row and self.pinned_pieces[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pinned_pieces[i][2], self.pinned_pieces[i][3])
                self.pinned_pieces.remove(self.pinned_pieces[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def get_queen_moves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.w_king_location = (end_row, end_col)
                    else:
                        self.b_king_location = (end_row, end_col)
                    in_check, pinned_pieces, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.w_king_location = (row, col)
                    else:
                        self.b_king_location = (row, col)


class Move: 
    def __init__(self, from_square, end_square, board_state, is_en_passant_move = False):
        self.start_row = from_square[0]
        self.start_col = from_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.start_square = from_square
        self.end_square = end_square
        self.piece_moved = board_state[self.start_row][self.start_col]
        self.piece_captured = board_state[self.end_row][self.end_col]

        #Pawn Promotion : If pawn is on last rank
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7)
        
        #En Passant : If pawn is moved to en passant square
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        #Generate a specific id for a move
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __eq__(self, other):
        if isinstance(other, Move):
            return other.move_id == self.move_id

    def get_chess_notation(self):
        if self.piece_captured != "--":
            if self.piece_moved == "wP" or self.piece_moved == "bP":
                return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.get_rank_file(self.end_row, self.end_col)
        else:
            if self.piece_moved == "wP" or self.piece_moved == "bP":
                return self.get_rank_file(self.end_row, self.end_col)
            return self.piece_moved[1] + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
