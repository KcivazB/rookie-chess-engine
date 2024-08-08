import pickle

class TranspositionTable:
    """
    A class to manage the transposition table used to store previously evaluated positions.
    """
    def __init__(self):
        self.table = {}  # Dictionary to store board positions and their evaluations
        self.killer_moves = {}  # Dictionary to store killer moves for each depth

    def store(self, board_hash, score, depth, flag, best_move=None):
        """
        Stores the evaluation of a board position in the transposition table.
        
        Args:
            board_hash (int): The hash of the current board position.
            score (int): The evaluated score for this position.
            depth (int): The depth at which this evaluation was made.
            flag (str): Indicates whether this is an exact score, or an upper/lower bound.
            best_move (Move): The best move found from this position, if any.
        """
        self.table[board_hash] = (score, depth, flag, best_move)
        if best_move:
            if depth not in self.killer_moves:
                self.killer_moves[depth] = [None, None]
            self.killer_moves[depth][1] = self.killer_moves[depth][0]
            self.killer_moves[depth][0] = best_move  # Store the best move as a killer move

    def lookup(self, board_hash):
        """
        Retrieves the stored evaluation of a board position if it exists.
        
        Args:
            board_hash (int): The hash of the current board position.

        Returns:
            tuple: The stored score, depth, flag, and best move for this position.
        """
        return self.table.get(board_hash, (None, None, None, None))

    def save(self, filename):
        """
        Saves the transposition table to a file.
        
        Args:
            filename (str): The name of the file where the table will be saved.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self.table, file)
        print(f"Transposition table saved to {filename}")

    def load(self, filename):
        """
        Loads the transposition table from a file.
        
        Args:
            filename (str): The name of the file from which the table will be loaded.
        """
        try:
            with open(filename, 'rb') as file:
                self.table = pickle.load(file)
            print(f"Transposition table loaded from {filename}")
        except FileNotFoundError:
            print(f"No existing transposition table found at {filename}. Starting fresh.")
            self.table = {}
