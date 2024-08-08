from constants import DIMENSION
from castle_rights import CastleRights
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
from moves.move import Move

class GameState:
    def __init__(self, sounds, fen=None):
        # Create an empty board
        self.board = self.create_board()

        # Initialize other game state variables
        self.white_to_move = True
        self.w_king_location = (7, 4)  # Default position (for initial setup)
        self.b_king_location = (0, 4)  # Default position (for initial setup)
        self.in_check = False
        self.pinned_pieces = []
        self.checks = []
        self.en_passant_possible_square = ()
        self.en_passant_possible_square_log = [self.en_passant_possible_square]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castling_rights_log = [
            CastleRights(
                self.current_castling_rights.wKs,
                self.current_castling_rights.wQs,
                self.current_castling_rights.bKs,
                self.current_castling_rights.bQs
            )
        ]
        self.is_stale_mate = False
        self.is_check_mate = False
        self.is_draw_due_to_75mr = False

        self.is_game_over = False

        self.half_moves_count = 0
        self.half_moves_count_log = []  # New log for half moves count

        self.moves_count = 1

        self.move_logs = []

        # Load from FEN if provided
        if fen:
            self.load_from_fen(fen)
        else:
            self.setup_initial_board()

        self.move_functions = {
            "P": lambda r, c, moves: Pawn().get_moves(self, r, c, moves),
            "N": lambda r, c, moves: Knight().get_moves(self, r, c, moves),
            "B": lambda r, c, moves: Bishop().get_moves(self, r, c, moves),
            "R": lambda r, c, moves: Rook().get_moves(self, r, c, moves),
            "Q": lambda r, c, moves: Queen().get_moves(self, r, c, moves),
            "K": lambda r, c, moves: King().get_moves(self, r, c, moves)
        }

        # Load sound effects
        self.move_sound = sounds["move_sound"]
        self.capture_sound = sounds["capture_sound"]
        self.castle_sound = sounds["castle_sound"]
        self.check_sound = sounds["check_sound"]
        self.promotion_sound = sounds["promotion_sound"]

        # checkmate_sound = p.mixer.Sound('assets/sounds/checkmate.mp3')
        # stalemate = p.mixer.Sound('assets/sounds/stalemate.mp3')

    def create_board(self):
        # Create an empty board.
        return [["--" for _ in range(DIMENSION)] for _ in range(DIMENSION)]

    def setup_initial_board(self):
        """Setup the initial board configuration."""
        self.board[0] = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
        self.board[1] = ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"]
        self.board[6] = ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"]
        self.board[7] = ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]

        # Set kings' default positions for initial setup
        self.w_king_location = (7, 4)
        self.b_king_location = (0, 4)

    def load_from_fen(self, fen):
        """Load the board and game state from the FEN string."""
        parts = fen.split()
        rows = parts[0].split('/')

        # Load board configuration
        for r in range(DIMENSION):
            c = 0
            for char in rows[r]:
                if char.isdigit():
                    c += int(char)
                else:
                    piece = self.fen_char_to_piece(char)
                    self.board[r][c] = piece
                    c += 1

        # Set the active player
        self.white_to_move = parts[1] == 'w'

        # Set castling rights and en passant
        self.current_castling_rights = self.parse_castling_rights(parts[2])
        self.en_passant_possible_square = self.parse_en_passant(parts[3])

        # Set half moves count and moves count
        self.half_moves_count = int(parts[4])
        self.moves_count = int(parts[5])

        # Update kings' positions based on the FEN
        self.update_king_locations()

        # Check for any initial checks or pins
        self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()
        
        # Print the relevant state information
        self.print_self_data()

    def fen_char_to_piece(self, char):
        """Convert a FEN character to the internal piece notation."""
        if char.islower():
            return 'b' + char.upper()
        else:
            return 'w' + char

    def parse_castling_rights(self, castling_rights):
        """Parse the castling rights from the FEN string."""
        wKs = 'K' in castling_rights
        wQs = 'Q' in castling_rights
        bKs = 'k' in castling_rights
        bQs = 'q' in castling_rights
        return CastleRights(wKs, wQs, bKs, bQs)

    def parse_en_passant(self, en_passant):
        """Parse the en passant target square from the FEN string."""
        if (en_passant == '-') or (en_passant == ''):
            return ()
        else:
            col = ord(en_passant[0]) - ord('a')
            row = 8 - int(en_passant[1])
            return (row, col)

    def print_self_data(self):
        print(f"White to move: {self.white_to_move}")
        print(f"Current castling rights: {self.current_castling_rights}")
        print(f"En passant possible square: {self.en_passant_possible_square}")
        print(f"Half moves count: {self.half_moves_count}")
        print(f"Moves count: {self.moves_count}")
        print(f"In check: {self.in_check}")
        print(f"Pinned pieces: {self.pinned_pieces}")
        print(f"Checks: {self.checks}")

    def update_king_locations(self):
        """Update the locations of the kings based on the board state."""
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                if self.board[r][c] == 'wK':
                    self.w_king_location = (r, c)
                elif self.board[r][c] == 'bK':
                    self.b_king_location = (r, c)

    def make_move(self, move):
        """Execute a move and update the board."""
        self.half_moves_count_log.append(self.half_moves_count)

        # Execute the move
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved

        # Play sound effects
        if move.piece_captured != "--":
            self.capture_sound.play()  # Play capture sound
        else:
            self.move_sound.play()  # Play move sound

        # Handle pawn promotion
        if move.is_pawn_promotion:
            self.promotion_sound.play()  # Play promotion sound
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # Update kings' location
        if move.piece_moved == "wK":
            self.w_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.b_king_location = (move.end_row, move.end_col)

        # Update other game states
        if move.piece_moved[1] == "P" or move.piece_captured != "--":
            self.half_moves_count = 0
        else:
            self.half_moves_count += 1

        # Handle 75-move rule
        if self.half_moves_count >= 75:
            self.is_stale_mate = True
            self.is_game_over = True
            print("75-move rule reached: Game is a draw.")

        # Handle En Passant Move
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = "--"

        # Handle castling move
        if move.is_castling:
            self.castle_sound.play()  # Play castling sound

            if move.end_col - move.start_col == 2:  # King Side Castling
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:  # Queen Side Castling
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        # Update castling rights
        self.update_castling_rights(move)
        self.castling_rights_log.append(
            CastleRights(
                self.current_castling_rights.wKs, self.current_castling_rights.wQs,
                self.current_castling_rights.bKs, self.current_castling_rights.bQs
            )
        )

        # Update en passant possible square
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible_square = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible_square = ()

        self.en_passant_possible_square_log.append(self.en_passant_possible_square)

        # Switch player's turn
        self.white_to_move = not self.white_to_move

        # Check for check and checkmate
        self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()
        if self.in_check:
            self.check_sound.play()  # Play check sound
            if self.get_all_valid_moves() == []:
                self.is_check_mate = True
        elif self.is_check_mate:
            # Optionally play checkmate sound
            pass

        # Check for stalemate
        if not self.is_check_mate and self.get_all_valid_moves() == []:
            self.is_stale_mate = True
            # Optionally play stalemate sound

        self.move_logs.append(move)
   
    def undo_last_move(self):
        """Undo the last move made."""
        if len(self.move_logs) != 0:
            last_move = self.move_logs.pop()

            # Decrement moves_count on whites turns
            if self.white_to_move:
                self.moves_count -= 1

            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved

            # Update the king's location if moved
            if last_move.piece_moved == "wK":
                self.w_king_location = (last_move.start_row, last_move.start_col)
            elif last_move.piece_moved == "bK":
                self.b_king_location = (last_move.start_row, last_move.start_col)

            if last_move.is_en_passant_move:
                self.board[last_move.end_row][last_move.end_col] = "--"
                self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured

            self.en_passant_possible_square_log.pop() # Remove lastly created en passant log 
            self.en_passant_possible_square = self.en_passant_possible_square_log[-1] # Set it back to it's previous state

            # Restore castling rights
            self.castling_rights_log.pop()  # Remove the most recent castling rights
            self.current_castling_rights = self.castling_rights_log[-1]  # Restore previous castling rights

            # Undo castling move
            if last_move.is_castling:
                if last_move.end_col - last_move.start_col == 2:  # King Side Castling
                    self.board[last_move.end_row][last_move.end_col + 1] = self.board[last_move.end_row][last_move.end_col - 1]  # Restore the rook
                    self.board[last_move.end_row][last_move.end_col - 1] = "--"  # Remove the rook from the new position
                else:  # Queen Side Castling
                    self.board[last_move.end_row][last_move.end_col - 2] = self.board[last_move.end_row][last_move.end_col + 1]  # Restore the rook
                    self.board[last_move.end_row][last_move.end_col + 1] = "--"  # Remove the rook from the new position

            # Adjust 75-move rule counter
            self.half_moves_count = self.half_moves_count_log.pop()  # Reset counter

            # Restore any other game state variables
            self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()

            self.checkmate = False
            self.stalemate = False
            self.is_draw_due_to_75mr = False

            # Next player's turn
            self.white_to_move = not self.white_to_move

    def update_castling_rights(self, move):
        """
        Update the castling rights based on the move.
        """
        if move.piece_moved == "wK":
            self.current_castling_rights.wKs = False
            self.current_castling_rights.wQs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bKs = False
            self.current_castling_rights.bQs = False
        elif move.piece_moved == "wR":
            self.disable_white_rook_castling_rights(move.start_row, move.start_col)
        elif move.piece_moved == "bR":
            self.disable_black_rook_castling_rights(move.start_row, move.start_col)
        
        if move.piece_captured == "wR":
            self.disable_white_rook_castling_rights(move.end_row, move.end_col)
        elif move.piece_captured == "bR":
            self.disable_black_rook_castling_rights(move.end_row, move.end_col)

    def disable_white_rook_castling_rights(self, row, col):
        """
        Disable white rook castling rights based on its position.
        """
        if row == 7:
            if col == 0:  # Left Rook
                self.current_castling_rights.wQs = False
            elif col == 7:  # Right Rook
                self.current_castling_rights.wKs = False

    def disable_black_rook_castling_rights(self, row, col):
        """
        Disable black rook castling rights based on its position.
        """
        if row == 0:
            if col == 0:  # Left Rook
                self.current_castling_rights.bQs = False
            elif col == 7:  # Right Rook
                self.current_castling_rights.bKs = False

    def get_all_valid_moves(self):
        temp_en_passant_possible_square = self.en_passant_possible_square
        temp_castle_rights = CastleRights(self.current_castling_rights.wKs, self.current_castling_rights.wQs,
                                          self.current_castling_rights.bKs, self.current_castling_rights.bQs)

        self.in_check, self.pinned_pieces, self.checks = self.check_for_pins_and_checks()
        valid_moves = []

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
                else: # Piece checking is not a knight
                    for i in range(1,8):
                        valid_square = (K_row + check[2] * i, K_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #stop once you get to the piece that end checks 
                            break
                #Get rid of the moves that don't block check or move the king 
                for i in range(len(valid_moves) -1, -1, -1): 
                    if valid_moves[i].piece_moved[1] != "K": #Not moving the king, so move has to block or capture 
                        if not (valid_moves[i].end_row, valid_moves[i].end_col) in valid_squares:
                            valid_moves.remove(valid_moves[i])
            else: # Double check -> King has to move
                color = "w" if self.white_to_move else "b"
                K_row, K_col = self.w_king_location if color == "w" else self.b_king_location
                king_instance = King()
                king_instance.get_moves(self, K_row, K_col, valid_moves)

        else:  # Not in check then all moves are valid ! 
            valid_moves = self.get_all_possible_moves()
            #Not In check so we can add castling moves ! 
            self.get_castle_moves(K_row, K_col, valid_moves)


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
        self.current_castling_rights = temp_castle_rights

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
                piece = self.board[r][c]
                if piece != "--":
                    color_to_play = piece[0]
                    piece_type = piece[1]
                    if (color_to_play == "w" and self.white_to_move) or (color_to_play == "b" and not self.white_to_move):
                        self.move_functions[piece_type](r, c, moves)
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
    
    #Generate all the castling moves for the king 
    def get_castle_moves(self, r, c, moves):
        if self.is_square_under_attack(r, c):
            return 
        if (self.white_to_move and self.current_castling_rights.wKs) or (not self.white_to_move and self.current_castling_rights.bKs): #Check for King Side castle rights of color
            self.get_king_side_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wQs) or (not self.white_to_move and self.current_castling_rights.bQs): #Check for Queen Side castle rights of color
            self.get_queen_side_castle_moves(r, c, moves)    

    #Generate King Side Castle Moves
    def get_king_side_castle_moves(self, r, c, moves):
        ally_color = "w" if self.white_to_move else "b"
        # Check if squares are empty
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and self.board[r][c+3] == ally_color + "R":
            if not self.is_square_under_attack(r, c + 1) and not self.is_square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2) , self.board, is_castling = True))

    #Generate King Side Castle Moves
    def get_queen_side_castle_moves(self, r, c, moves):
        ally_color = "w" if self.white_to_move else "b"
        # Check if squares are empty
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--" and self.board[r][c-4] == ally_color + "R":
            if not self.is_square_under_attack(r, c - 1) and not self.is_square_under_attack(r, c -2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castling = True))
