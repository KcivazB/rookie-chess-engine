from constants import PIECES_SYMBOLS

class Move: 
    def __init__(self, from_square, end_square, board_state, is_pawn_promotion = False, is_en_passant = False, is_castling = False):
        self.start_row = from_square[0]
        self.start_col = from_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.start_square = from_square
        self.end_square = end_square
        self.piece_moved = board_state[self.start_row][self.start_col]
        self.piece_captured = board_state[self.end_row][self.end_col]

        # Pawn Promotion: If pawn is on last rank
        self.is_pawn_promotion = is_pawn_promotion
        
        # En Passant: If pawn is moved to en passant square
        self.is_en_passant_move = is_en_passant
        if self.is_en_passant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # Castling: If this is a castling move
        self.is_castling = is_castling

        # Generate a specific id for a move
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        
        # Validate move coordinates
        self.validate_coordinates()

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def validate_coordinates(self):
        if not (0 <= self.start_row < 8 and 0 <= self.start_col < 8 and 0 <= self.end_row < 8 and 0 <= self.end_col < 8):
            raise ValueError(f"Invalid move coordinates: start=({self.start_row}, {self.start_col}), end=({self.end_row}, {self.end_col})")

    def __eq__(self, other):
        if isinstance(other, Move):
            return other.move_id == self.move_id

    def piece_to_symbol(self, piece):
        return PIECES_SYMBOLS[piece]

    def __str__(self):
        if self.is_castling:
            return "O-O" if self.end_col == 6 else "O-O-O"

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
        if col not in self.cols_to_files or row not in self.rows_to_ranks:
            raise ValueError(f"Invalid coordinates for get_rank_file: row={row}, col={col}")
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def to_uci(self):
        """
        Convert the move to UCI (Universal Chess Interface) format.

        Returns:
            str: The move in UCI format.
        """
        start_square_uci = self.get_rank_file(self.start_row, self.start_col)
        end_square_uci = self.get_rank_file(self.end_row, self.end_col)
        return start_square_uci + end_square_uci
