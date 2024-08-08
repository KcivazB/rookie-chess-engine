from moves.move import Move

class Knight():
    def __init__(self): 
        pass

    def get_moves(self, gs, r, c, moves):
        """
        Get all the knight moves for the knight located at r, c and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(gs.pinned_pieces) - 1, -1, -1):
            if gs.pinned_pieces[i][0] == r and gs.pinned_pieces[i][1] == c:
                piece_pinned = True
                gs.pinned_pieces.remove(gs.pinned_pieces[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))  # All possible knight moves
        ally_color = "w" if gs.white_to_move else "b"

        for move in knight_moves:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = gs.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # So it's either an enemy piece or an empty square
                        moves.append(Move((r, c), (end_row, end_col), gs.board))
