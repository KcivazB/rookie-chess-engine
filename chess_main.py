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
        #TODO : CHANGE THIS LATER TO LET THE PLAYER SELECT THE SET INDEPENDANTLY FROM THE THEME
        img_path = f"{IMAGE_DIR}/pieces/{THEMES[THEME]['set']}/{piece}.svg" 
        
        # Convert SVG to PNG in-memory
        with open(img_path, 'rb') as svg_file:
            svg_data = svg_file.read()
        
        png_data = cairosvg.svg2png(bytestring=svg_data)
        
        # Load the PNG data into a Pygame surface
        image = p.image.load(io.BytesIO(png_data))
        
        # Scale the image to fit the square size
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

    move_was_made = False #flag for when a move is made

    square_selected = () # No square selected initially (tuple: rank, file) 
    player_clicks = [] # track the clicks (2 tuples : [(2, 6), (4, 6)]

    load_images()
    running = True
    valid_moves_for_selected_piece = []

    while running : 
        if gs.is_stale_mate : 
            print ("White is stale mate" if gs.white_to_move else "Black  is stale mate")
            
        if gs.is_check_mate : 
            print ("White is check mate" if gs.white_to_move else "Black is check mate")

        for e in p.event.get():
            if e.type == p.QUIT :
                running = False
            #MOUSE EVENT HANDLER
            elif e.type == p.MOUSEBUTTONDOWN :
                location = p.mouse.get_pos() # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if square_selected == (row, col): # square clicked is already selected
                    square_selected = () # un-select it
                    player_clicks = [] # reset the player clicks
                    valid_moves_for_selected_piece = [] # Reset valid moves for selected piece
                else: 
                    square_selected = (row, col) # select the square
                    player_clicks.append(square_selected) # append it to the clicks
                    valid_moves_for_selected_piece = [move.end_square for move in valid_moves if (move.start_row, move.start_col) == square_selected] # Calculate valid moves for the selected piece
                if len(player_clicks) == 2 :
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]: 
                            gs.make_move(valid_moves[i])
                            move_was_made = True
                            square_selected = () # un-select it
                            player_clicks = [] # reset the player clicks
                            valid_moves_for_selected_piece = [] # Reset valid moves for selected piece
                    if not move_was_made:
                        player_clicks = [square_selected] # reset the player clicks to the last selected square
                        valid_moves_for_selected_piece = [move.end_square for move in valid_moves if (move.start_row, move.start_col) == square_selected]
                    
            #KEYDOWN EVENT HANDLER
            elif e.type == p.KEYDOWN: 
                if e.key == p.K_BACKSPACE:
                    print("Undoing last move")
                    square_selected = () 
                    gs.undo_last_move()
                    move_was_made = True

        if move_was_made : 
            valid_moves = gs.get_all_valid_moves()
            move_was_made = False

        draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all graphics within game state
'''
def draw_game_state(screen, gs, square_selected, valid_moves_for_selected_piece):

    # Add piece hilighting or move suggestions
    draw_board_squares(screen, gs, square_selected, valid_moves_for_selected_piece,) # Draw the board's squares 
    draw_pieces(screen, gs) #Draw pieces on those squares

'''
Draw the squares on the board
'''
def draw_board_squares(screen, gs, selected_square, valid_moves_for_selected_piece): 
    colors = [THEMES[THEME]["white"], THEMES[THEME]["black"]]
    for row in range (DIMENSION): 
        for col in range (DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if selected_square and (row, col) == selected_square:
                p.draw.rect(screen, THEMES[THEME]["highlighted"], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            elif (row, col) in valid_moves_for_selected_piece:                    

                # Draw a small circle of opposite color in the middle of the square
                opposite_color = colors[1] if color == colors[0] else colors[0]
                center_x = col * SQ_SIZE + SQ_SIZE // 2
                center_y = row * SQ_SIZE + SQ_SIZE // 2
                radius = SQ_SIZE // 10  # Adjust the radius as needed
                p.draw.circle(screen, opposite_color, (center_x, center_y), radius)

                # If the square is not empty, then move is a capture. -> Highlight the square in another color
                if gs.board[row][col] != "--":
                    # Add a coloured transparent overlay for valid moves
                    s = p.Surface((SQ_SIZE, SQ_SIZE))
                    s.set_alpha(100)  # transparency value -> 0: transparent, 255: opaque
                    s.fill(THEMES[THEME]["capture_color"])  # theme color with transparency
                    screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

                else:
                    # Add a coloured transparent overlay for valid moves
                    s = p.Surface((SQ_SIZE, SQ_SIZE))
                    s.set_alpha(100)  # transparency value -> 0: transparent, 255: opaque
                    s.fill(THEMES[THEME]["possible_moves"])  # theme color with transparency
                    screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))



'''
Draw the pieces on the board depending on the current GameState.board
'''
def draw_pieces(screen, game_state): 
    board = game_state.board  # Access the board from the GameState object
    for row in range (DIMENSION): 
        for col in range (DIMENSION):
            piece = board[row][col]
            if piece != "--" : 
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a chess game with an optional FEN string.')
    parser.add_argument('--FEN', type=str, help='The FEN string to set up the board.')
    args = parser.parse_args()

    main(args.FEN)