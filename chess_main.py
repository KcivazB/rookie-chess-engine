import pygame as p
import chess_engine
from constants import DIMENSION, IMAGE_DIR, SQ_SIZE, PIECES, IMAGES, THEMES, THEME, WIDTH, HEIGHT, MAX_FPS
import cairosvg
import io
import argparse

'''
Initialize a global dictionary of the images. Called once
'''
def load_images():
    for piece in PIECES:
        img_path = f"{IMAGE_DIR}/pieces/{THEMES[THEME]['set']}/{piece}.svg"
        with open(img_path, 'rb') as svg_file:
            svg_data = svg_file.read()
        png_data = cairosvg.svg2png(bytestring=svg_data)
        image = p.image.load(io.BytesIO(png_data))
        image = p.transform.scale(image, (SQ_SIZE, SQ_SIZE))
        IMAGES[piece] = image

'''
The main driver for the code 
'''
def main(fen):
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = chess_engine.GameState(fen)
    valid_moves = gs.get_all_valid_moves()
    move_was_made = False
    # animate = False
    square_selected = ()
    player_clicks = []

    load_images()
    running = True
    valid_moves_for_selected_piece = []

    while running:
        if gs.is_stale_mate:
            print("White is stale mate" if gs.white_to_move else "Black is stale mate")
        if gs.is_check_mate:
            print("White is check mate" if gs.white_to_move else "Black is check mate")

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if square_selected == (row, col):
                    square_selected = ()
                    player_clicks = []
                    valid_moves_for_selected_piece = []
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)
                    valid_moves_for_selected_piece = [move.end_square for move in valid_moves if (move.start_row, move.start_col) == square_selected]
                if len(player_clicks) == 2:
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            move_was_made = True
                            # animate = True
                            square_selected = ()
                            player_clicks = []
                            valid_moves_for_selected_piece = []
                    if not move_was_made:
                        player_clicks = [square_selected]
                        valid_moves_for_selected_piece = [move.end_square for move in valid_moves if (move.start_row, move.start_col) == square_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE: # If BACKSPACE is pressed, undo last move
                    square_selected = ()
                    gs.undo_last_move()
                    move_was_made = True

                if e.key == p.K_r: # If R is pressed, Reinitialize the whole game state
                    gs = chess_engine.GameState(fen)
                    valid_moves = gs.get_all_valid_moves()
                    move_was_made = False
                    # animate = False
                    square_selected = ()
                    player_clicks = []

        if move_was_made:
            # if animate:
            #     animate_move(gs.move_log[-1], screen, gs, clock)
            valid_moves = gs.get_all_valid_moves()
            move_was_made = False
            # animate = False

        draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all graphics within game state
'''
def draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece):
    draw_board_squares(screen, gs, square_selected, valid_moves_for_selected_piece)
    draw_pieces(screen, gs)

'''
Draw the squares on the board
'''
def draw_board_squares(screen, gs, selected_square, valid_moves_for_selected_piece):
    colors = [THEMES[THEME]["white"], THEMES[THEME]["black"]]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            highlight_square_and_squares_moves(screen, gs, row, col, selected_square, valid_moves_for_selected_piece)

'''
Highlight the squares for selected piece and its moves
'''
def highlight_square_and_squares_moves(screen, gs, row, col, selected_square, valid_moves_for_selected_piece):
    colors = [THEMES[THEME]["white"], THEMES[THEME]["black"]]
    color = colors[(row + col) % 2]

    if selected_square and (row, col) == selected_square:
        selected_square_rect = p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, THEMES[THEME]["highlighted"], selected_square_rect)
    if (row, col) in valid_moves_for_selected_piece:
        opposite_color = colors[1] if color == colors[0] else colors[0]
        center_x = col * SQ_SIZE + SQ_SIZE // 2
        center_y = row * SQ_SIZE + SQ_SIZE // 2
        radius = SQ_SIZE // 10
        p.draw.circle(screen, opposite_color, (center_x, center_y), radius)
        if gs.board[row][col] != "--":
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(THEMES[THEME]["capture_color"])
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
        else:
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(THEMES[THEME]["possible_moves"])
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

'''
Animate the piece movement from start to end
'''
# def animate_move(move, screen, gs, clock):
#     colors = [THEMES[THEME]["white"], THEMES[THEME]["black"]]
#     delta_x = move.end_col - move.start_col
#     delta_y = move.end_row - move.start_row
#     frames_per_square = 5
#     frame_count = (abs(delta_x) + abs(delta_y)) * frames_per_square

#     for frame in range(frame_count + 1):
#         row, col = move.start_row, move.start_col
#         x = col * SQ_SIZE + delta_x * SQ_SIZE * frame / frame_count
#         y = row * SQ_SIZE + delta_y * SQ_SIZE * frame / frame_count
        
#         draw_board_squares(screen, gs, (), [])
#         draw_pieces(screen, gs)

#         color = colors[(move.end_row + move.end_col) % 2]
#         end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
#         p.draw.rect(screen, color, end_square)
#         if move.piece_captured != "--":
#             screen.blit(IMAGES[move.piece_captured], end_square)

#         piece = move.piece_moved
#         if piece != "--":
#             moving_piece = p.transform.scale(IMAGES[piece], (SQ_SIZE, SQ_SIZE))
#             screen.blit(moving_piece, p.Rect(x, y, SQ_SIZE, SQ_SIZE))

#         p.display.flip()
#         clock.tick(MAX_FPS)

'''
Draw the pieces on the board depending on the current GameState.board
'''
def draw_pieces(screen, game_state):
    board = game_state.board
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                piece_square = p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[piece], piece_square)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a chess game with an optional FEN string.')
    parser.add_argument('--FEN', type=str, help='The FEN string to set up the board.')
    args = parser.parse_args()

    main(args.FEN)
