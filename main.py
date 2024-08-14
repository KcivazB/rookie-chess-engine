import pygame as p
import sys
from constants import THEMES, PIECES

def draw_text_centered(screen, text, font, color, rect):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_text_left(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main_menu():
    p.init()
    screen = p.display.set_mode((600, 500))
    p.display.set_caption('Chess Main Menu')
    clock = p.time.Clock()

    font = p.font.SysFont("Arial", 30)
    small_font = p.font.SysFont("Arial", 20)

    selected_theme = "classic"  # Default theme
    selected_piece_set = "default"  # Default piece set
    is_white_human = True  # Default player types
    is_black_human = True
    fen_string = ""  # Default FEN

    input_active = False  # Track if FEN input is active
    input_rect = p.Rect(50, 400, 500, 32)

    menu_running = True
    while menu_running:
        screen.fill(p.Color("black"))
        
        title_rect = p.Rect(0, 50, 600, 50)
        draw_text_centered(screen, "Chess Main Menu", font, p.Color("white"), title_rect)

        theme_button_rect = p.Rect(200, 150, 200, 50)
        draw_text_centered(screen, f"Theme: {selected_theme}", small_font, p.Color("white"), theme_button_rect)

        piece_button_rect = p.Rect(200, 200, 200, 50)
        draw_text_centered(screen, f"Pieces: {selected_piece_set}", small_font, p.Color("white"), piece_button_rect)

        player_button_rect = p.Rect(200, 250, 200, 50)
        draw_text_centered(screen, f"White: {'Human' if is_white_human else 'AI'}, Black: {'Human' if is_black_human else 'AI'}", small_font, p.Color("white"), player_button_rect)

        draw_text_left(screen, "Enter FEN (Optional):", small_font, p.Color("white"), 50, 370)
        p.draw.rect(screen, p.Color("white"), input_rect, 2)
        draw_text_left(screen, fen_string, small_font, p.Color("white"), input_rect.x + 5, input_rect.y + 5)

        start_button_rect = p.Rect(200, 450, 200, 50)
        draw_text_centered(screen, "Start Game", small_font, p.Color("white"), start_button_rect)

        quit_button_rect = p.Rect(200, 500, 200, 50)
        draw_text_centered(screen, "Quit", small_font, p.Color("white"), quit_button_rect)

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                if theme_button_rect.collidepoint(event.pos):
                    themes = list(THEMES.keys())
                    current_theme_index = themes.index(selected_theme)
                    selected_theme = themes[(current_theme_index + 1) % len(themes)]
                elif piece_button_rect.collidepoint(event.pos):
                    piece_sets = PIECES
                    current_piece_set_index = piece_sets.index(selected_piece_set)
                    selected_piece_set = piece_sets[(current_piece_set_index + 1) % len(piece_sets)]
                elif player_button_rect.collidepoint(event.pos):
                    is_white_human = not is_white_human
                    is_black_human = not is_black_human
                elif input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                    if start_button_rect.collidepoint(event.pos):
                        global THEME
                        global WHITE_IS_HUMAN, BLACK_IS_HUMAN
                        THEME = selected_theme
                        WHITE_IS_HUMAN = is_white_human
                        BLACK_IS_HUMAN = is_black_human
                        main(fen_string if fen_string else None)  # Start the game with the selected FEN if provided
                    elif quit_button_rect.collidepoint(event.pos):
                        p.quit()
                        sys.exit()

            elif event.type == p.KEYDOWN and input_active:
                if event.key == p.K_RETURN:
                    input_active = False
                elif event.key == p.K_BACKSPACE:
                    fen_string = fen_string[:-1]
                else:
                    fen_string += event.unicode

        p.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
