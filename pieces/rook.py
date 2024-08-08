from moves.move import Move

class Rook():
    def __init__(self):
        pass

    def get_moves(self, gs, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(gs.pinned_pieces) - 1, -1, -1):
            if gs.pinned_pieces[i][0] == r and gs.pinned_pieces[i][1] == c:
                piece_pinned = True
                pin_direction = (gs.pinned_pieces[i][2], gs.pinned_pieces[i][3])
                if gs.board[r][c][1] != "Q":  # Can't remove queen from pin on rook moves
                    gs.pinned_pieces.remove(gs.pinned_pieces[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if gs.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # Boundaries check
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        end_piece = gs.board[end_row][end_col]
                        if end_piece == "--":  # Empty space is valid
                            moves.append(Move((r, c), (end_row, end_col), gs.board))
                        elif end_piece[0] == enemy_color:  # Capture enemy piece
                            moves.append(Move((r, c), (end_row, end_col), gs.board))
                            break
                        else:  # Friendly piece
                            break
                else:  # Off board
                    break
