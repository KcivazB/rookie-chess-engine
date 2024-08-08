from .rook import Rook
from .bishop import Bishop

class Queen():
    def __init__(self):
        pass

    def get_moves(self, gs ,row, col, moves):
        Rook.get_moves(self, gs, row, col, moves)
        Bishop.get_moves(self, gs, row, col, moves)
