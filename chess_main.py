import pygame as p
import chess_engine
from constants import DIMENSION, IMAGE_DIR, SQ_SIZE, PIECES, IMAGES, THEMES, THEME, WIDTH, HEIGHT, MAX_FPS
import smart_move_finder
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
    square_selected = ()
    player_clicks = []

    load_images()
    running = True
    valid_moves_for_selected_piece = []

    is_over = gs.is_check_mate or gs.is_stale_mate

    is_white_human = True # True if white is a human, false if it's an AI -> TODO set it to int for level handling
    is_black_human = False # True if black is a human, false if it's an AI -> TODO set it to int for level handling

    while running:
        is_human_turn = (gs.white_to_move and is_white_human) or (not gs.white_to_move and is_black_human) # Determine if it's an human turn to play


        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not is_over and is_human_turn: # IF game is not over and Human is playing
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
                    square_selected = ()
                    player_clicks = []


        
        #AI MOVE FINDER LOGIC
        if not is_over:
            if not is_human_turn:
                if valid_moves:
                    smart_move = smart_move_finder.find_random_moves(valid_moves)
                    gs.make_move(smart_move)
                    move_was_made = True
                
        if move_was_made:
            valid_moves = gs.get_all_valid_moves()
            move_was_made = False

        draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece)

        if gs.is_stale_mate:
            text = "White is stale mate - Draw game" if gs.white_to_move else "Black is stale mate - Draw game"
            draw_text_on_screen(screen, text)
        if gs.is_check_mate:
            text = "White is check mate" if gs.white_to_move else "Black is check mate"
            draw_text_on_screen(screen, text)


        clock.tick(MAX_FPS)
        p.display.flip()

'''
Draw text on the screen
'''
def draw_text_on_screen(screen, text):
    font = p.font.SysFont("Helvetica", 60, True, False)
    text_object = font.render(text, 0, THEMES[THEME]["capture_color"])
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move( WIDTH // 2 - text_object.get_width() // 2, HEIGHT // 2 - text_object.get_height() // 2 )
    screen.blit(text_object, text_location)

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
