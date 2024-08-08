from moves.move import Move

class King():
    def __init__(self):
        pass

    def get_moves(self, gs, r, c, moves):
        """
        Get all the king moves for the king located at r, c and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if gs.white_to_move else "b"

        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = gs.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Not an ally piece - empty or enemy
                    # Temporarily move the king and check for checks
                    if ally_color == "w":
                        gs.w_king_location = (end_row, end_col)
                    else:
                        gs.b_king_location = (end_row, end_col)
                    
                    in_check, pinned_pieces, checks = gs.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), gs.board))
                    
                    # Move the king back to the original location
                    if ally_color == "w":
                        gs.w_king_location = (r, c)
                    else:
                        gs.b_king_location = (r, c)
