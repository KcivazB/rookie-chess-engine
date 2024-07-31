import pygame as p

'''
SCREEN SETTINGS
'''
BOARD_WIDTH = BOARD_HEIGHT = 1024
MOVE_LOG_PANEL_WIDTH = BOARD_WIDTH // 4
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 
SQUARES = 8**2 
SQ_SIZE = BOARD_HEIGHT // DIMENSION 
MAX_FPS = 60

IMAGE_DIR = "images"
IMAGES = {}

'''
CHESS CONSTANTS
'''
PIECES = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
PIECES_SYMBOLS = {
    "wP" : "♙",
    "wR" : "♖",
    "wN" : "♘",
    "wB" : "♗",
    "wQ" : "♕",
    "wK" : "♔",
    "bP" : "♟︎",
    "bR" : "♜",
    "bN" : "♞",
    "bB" : "♝",
    "bQ" : "♛",
    "bK" : "♚"
}

'''
AI PART 
'''
MAX_DEPTH = 4

PIECE_SCORES = {
    "K" : 0,
    "P" : 1,
    "R" : 5,
    "B" : 3,
    "N" : 3,
    "Q" : 10
}

CHECK_MATE_SCORE = 1000
STALE_MATE_SCORE = 0

'''
THEMES PART 
'''
# Initial theme
THEME = "base"

# Themes dictionary
THEMES = {
    "base": {
        "white": p.Color("white"),
        "black": p.Color("gray"),
        "highlighted": p.Color("purple"),
        "possible_moves": p.Color("purple1"),
        "capture_color": p.Color("seagreen2"),
        "set": "staunty"
    },
    "sunset": {
        "white": p.Color("lightgoldenrodyellow"),
        "black": p.Color("sienna"),
        "highlighted": p.Color("coral"),
        "possible_moves": p.Color("darkorange1"),
        "capture_color": p.Color("firebrick"),
        "set": "staunty"
    },
    "forest": {
        "white": p.Color("honeydew"),
        "black": p.Color("forestgreen"),
        "highlighted": p.Color("darkolivegreen"),
        "possible_moves": p.Color("limegreen"),
        "capture_color": p.Color("darkred"),
        "set": "staunty"
    },
    "ocean": {
        "white": p.Color("azure"),
        "black": p.Color("midnightblue"),
        "highlighted": p.Color("dodgerblue"),
        "possible_moves": p.Color("deepskyblue"),
        "capture_color": p.Color("crimson"),
        "set": "staunty"
    },
    "desert": {
        "white": p.Color("wheat"),
        "black": p.Color("peru"),
        "highlighted": p.Color("sandybrown"),
        "possible_moves": p.Color("goldenrod"),
        "capture_color": p.Color("brown"),
        "set": "staunty"
    },
    "night": {
        "white": p.Color("lightgrey"),
        "black": p.Color("black"),
        "highlighted": p.Color("darkslateblue"),
        "possible_moves": p.Color("slateblue"),
        "capture_color": p.Color("red"),
        "set": "staunty"
    },
    "spring": {
        "white": p.Color("mintcream"),
        "black": p.Color("mediumseagreen"),
        "highlighted": p.Color("mediumspringgreen"),
        "possible_moves": p.Color("springgreen"),
        "capture_color": p.Color("mediumvioletred"),
        "set": "staunty"
    },
    "autumn": {
        "white": p.Color("oldlace"),
        "black": p.Color("saddlebrown"),
        "highlighted": p.Color("darkorange"),
        "possible_moves": p.Color("orangered"),
        "capture_color": p.Color("maroon"),
        "set": "staunty"
    },
    "pastel": {
        "white": p.Color("lavenderblush"),
        "black": p.Color("palevioletred"),
        "highlighted": p.Color("lightpink"),
        "possible_moves": p.Color("pink"),
        "capture_color": p.Color("deeppink"),
        "set": "staunty"
    },
    "grayscale": {
        "white": p.Color("gainsboro"),
        "black": p.Color("dimgray"),
        "highlighted": p.Color("darkgray"),
        "possible_moves": p.Color("lightgray"),
        "capture_color": p.Color("black"),
        "set": "staunty"
    }
}