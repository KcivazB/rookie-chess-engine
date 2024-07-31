import pygame as p
import time
import chess_engine
from constants import DIMENSION, IMAGE_DIR, SQ_SIZE, PIECES, IMAGES, THEMES, THEME, BOARD_WIDTH, BOARD_HEIGHT, MOVE_LOG_PANEL_WIDTH, MAX_FPS, BLACK_IS_HUMAN, WHITE_IS_HUMAN
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
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 12, False, False)


    gs = chess_engine.GameState(fen)
    # print(f"Initial GameState:")
    gs.print_self_data()

    valid_moves = gs.get_all_valid_moves()

    move_was_made = False
    square_selected = ()
    player_clicks = []

    load_images()
    running = True
    valid_moves_for_selected_piece = []


    is_white_human = WHITE_IS_HUMAN # True if white is a human, false if it's an AI -> TODO set it to int for level handling
    is_black_human = BLACK_IS_HUMAN # True if black is a human, false if it's an AI -> TODO set it to int for level handling

    while running:
        is_human_turn = (gs.white_to_move and is_white_human) or (not gs.white_to_move and is_black_human) # Determine if it's an human turn to play
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gs.is_game_over and is_human_turn: # IF game is not over and Human is playing
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if square_selected == (row, col) or col >= 8:
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
                                print(f"Half moves count : {gs.half_moves_count}")  # TODO Check what happens after this 

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
        if not gs.is_game_over:
            if not is_human_turn:
                if valid_moves:
                    ai_smart_move = smart_move_finder.find_best_move(gs, valid_moves)
                    gs.make_move(ai_smart_move)
                    move_was_made = True
                    print(f"Half moves count : {gs.half_moves_count}")  # TODO Check what happens after this 

    
        # Check for the half-move limit
        if gs.half_moves_count >= 75:
            gs.is_draw_due_to_75mr = True

        if move_was_made:
            valid_moves = gs.get_all_valid_moves()
            move_was_made = False
            # gs.print_self_data()    

        draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece, move_log_font)

        if gs.is_stale_mate:
            text = "White is stale mate - Draw game" if gs.white_to_move else "Black is stale mate - Draw game"
            draw_text_on_screen(screen, text)
        elif gs.is_check_mate:
            text = "White is check mate - Black won" if gs.white_to_move else "Black is check mate - White won"
            draw_text_on_screen(screen, text)
        elif gs.is_draw_due_to_75mr:
            text = "Draw due to 75-move rule"
            draw_text_on_screen(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


'''
Draw move logs
'''
def draw_move_log(screen, gs, font):
    # Create a new rectangle object
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT)
    # Draw it on the screen
    p.draw.rect(screen, THEMES[THEME]["highlighted"], move_log_rect)

    #Get all the move logs and their corresponding chess notation
    move_logs = gs.move_logs
    move_texts = []

    for i in range(0, len(move_logs), 2):
        move_string = str(i//2 + 1) + ". " + str(move_logs[i])
        if i+1 < len(move_logs):
            move_string += "-" + str(move_logs[i + 1])
        move_texts.append(move_string)

    padding = 50
    text_y = padding 
    line_spacing = 5

    # Add all the moves inside the new rectangle
    for i in range(len(move_texts)):
        text = move_texts[i]
        text_object = font.render(text, True, THEMES[THEME]["white"])
        text_location = move_log_rect.move(padding, text_y )
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


'''
Draw text on the screen
'''
def draw_text_on_screen(screen, text):
    font = p.font.SysFont("Helvetica", 60, True, False)
    text_object = font.render(text, 0, THEMES[THEME]["capture_color"])
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move( BOARD_WIDTH // 2 - text_object.get_width() // 2, BOARD_HEIGHT // 2 - text_object.get_height() // 2 )
    screen.blit(text_object, text_location)

'''
Responsible for all graphics within game state
'''
def draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece, move_log_font):
    draw_board_squares(screen, gs, square_selected, valid_moves_for_selected_piece)
    draw_pieces(screen, gs)
    draw_move_log(screen, gs, move_log_font)

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
