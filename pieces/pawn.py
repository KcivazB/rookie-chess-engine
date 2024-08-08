from moves.move import Move

class Pawn:
    def __init__(self):
        pass

    def get_moves(self, gs, r, c, moves):
        is_piece_pinned = False
        pin_direction = ()

        if gs.white_to_move:
            move_sign = -1
            start_row = 6
            back_row = 0
            enemy_color = "b"
            king_row, king_col = gs.w_king_location
        else:
            move_sign = 1
            start_row = 1
            back_row = 7
            enemy_color = "w"
            king_row, king_col = gs.b_king_location

        is_blocking_piece = False
        is_attacking_piece = False

        # Check if the piece is pinned
        for i in range(len(gs.pinned_pieces) - 1, -1, -1):
            if gs.pinned_pieces[i][0] == r and gs.pinned_pieces[i][1] == c:
                is_piece_pinned = True
                pin_direction = (gs.pinned_pieces[i][2], gs.pinned_pieces[i][3])
                gs.pinned_pieces.remove(gs.pinned_pieces[i])
                break

        # Move one square forward
        end_row = r + move_sign
        if 0 <= end_row < 8:  # Ensure end_row is within board bounds
            if gs.board[end_row][c] == "--":
                if not is_piece_pinned or pin_direction == (move_sign, 0):
                    pawn_promotion = end_row == back_row
                    moves.append(Move((r, c), (end_row, c), gs.board, is_pawn_promotion=pawn_promotion))
                    
                    # Move two squares forward from the starting position
                    if r == start_row:
                        end_row = r + 2 * move_sign
                        if 0 <= end_row < 8 and gs.board[end_row][c] == "--":
                            moves.append(Move((r, c), (end_row, c), gs.board))

        # Capture diagonally to the left
        if c - 1 >= 0:
            end_row = r + move_sign
            if 0 <= end_row < 8:
                if gs.board[end_row][c - 1][0] == enemy_color:
                    if not is_piece_pinned or pin_direction == (move_sign, -1):
                        pawn_promotion = end_row == back_row
                        moves.append(Move((r, c), (end_row, c - 1), gs.board, is_pawn_promotion=pawn_promotion))
                elif (end_row, c - 1) == gs.en_passant_possible_square:
                    if not is_piece_pinned or pin_direction == (move_sign, -1):
                        if king_row == r:
                            if king_col < c:
                                inside_range = range(king_col + 1, c - 1)
                                outside_range = range(c + 1, 8)
                            else:
                                inside_range = range(king_col - 1, c, -1)
                                outside_range = range(c + 2, 8)
                            for i in inside_range:
                                if gs.board[r][i] != "--":
                                    is_blocking_piece = True
                            for i in outside_range:
                                square = gs.board[r][i]
                                if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                    is_attacking_piece = True
                                elif square != "--":
                                    is_blocking_piece = True
                            if not is_attacking_piece or is_blocking_piece:
                                moves.append(Move((r, c), (end_row, c - 1), gs.board, is_en_passant=True))

        # Capture diagonally to the right
        if c + 1 <= 7:
            end_row = r + move_sign
            if 0 <= end_row < 8:
                if gs.board[end_row][c + 1][0] == enemy_color:
                    if not is_piece_pinned or pin_direction == (move_sign, 1):
                        pawn_promotion = end_row == back_row
                        moves.append(Move((r, c), (end_row, c + 1), gs.board, is_pawn_promotion=pawn_promotion))
                elif (end_row, c + 1) == gs.en_passant_possible_square:
                    if not is_piece_pinned or pin_direction == (move_sign, 1):
                        if king_row == r:
                            if king_col < c:
                                inside_range = range(king_col + 1, c)
                                outside_range = range(c + 2, 8)
                            else:
                                inside_range = range(king_col - 1, c + 1, -1)
                                outside_range = range(c - 1, -1, -1)
                            for i in inside_range:
                                if gs.board[r][i] != "--":
                                    is_blocking_piece = True
                            for i in outside_range:
                                square = gs.board[r][i]
                                if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                    is_attacking_piece = True
                                elif square != "--":
                                    is_blocking_piece = True
                            if not is_attacking_piece or is_blocking_piece:
                                moves.append(Move((r, c), (end_row, c + 1), gs.board, is_en_passant=True))
