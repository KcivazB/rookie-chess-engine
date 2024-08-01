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

WHITE_IS_HUMAN = False
BLACK_IS_HUMAN = False


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
    "K": 0,
    "P": 208,
    "R": 1276,
    "B": 825,
    "N": 781,
    "Q": 2538
}

CHECK_MATE_SCORE = 32000
STALE_MATE_SCORE = 0

PAWN_POSITION_SCORE_WHITE = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [ 90, 90, 90, 90, 90, 90, 90, 90],
    [ 30, 30, 40, 60, 60, 40, 30, 30],
    [ 10, 10, 20, 40, 40, 20, 10, 10],
    [  5,  5, 10, 20, 20, 10,  5,  5],
    [  0,  0,  0,-10,-10,  0,  0,  0],
    [  5, -5,-10,  0,  0,-10, -5,  5],
    [  0,  0,  0,  0,  0,  0,  0,  0]
]

PAWN_POSITION_SCORE_BLACK = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  5, -5,-10,  0,  0,-10, -5,  5],
    [  0,  0,  0,-10,-10,  0,  0,  0],
    [  5,  5, 10, 20, 20, 10,  5,  5],
    [ 10, 10, 20, 40, 40, 20, 10, 10],
    [ 30, 30, 40, 60, 60, 40, 30, 30],
    [ 90, 90, 90, 90, 90, 90, 90, 90],
    [  0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_POSITION_SCORE_WHITE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

KNIGHT_POSITION_SCORE_BLACK = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]


BISHOP_POSITION_SCORE_WHITE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 15, 15, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

BISHOP_POSITION_SCORE_BLACK = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  0, 10, 15, 15, 10,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]


ROOK_POSITION_SCORE_WHITE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 20, 20, 20, 20, 20, 20,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0]
]

ROOK_POSITION_SCORE_BLACK = [
    [  0,  0,  0,  5,  5,  0,  0,  0],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [  5, 20, 20, 20, 20, 20, 20,  5],
    [  0,  0,  0,  0,  0,  0,  0,  0]
]


QUEEN_POSITION_SCORE_WHITE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5, 10, 10,  5,  0, -5],
    [ -5,  0,  5, 10, 10,  5,  0, -5],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

QUEEN_POSITION_SCORE_BLACK = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [ -5,  0,  5, 10, 10,  5,  0, -5],
    [ -5,  0,  5, 10, 10,  5,  0, -5],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]


KING_POSITION_SCORE_WHITE = [
    [-50,-30,-30,-30,-30,-30,-30,-50],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-50,-40,-30,-20,-20,-30,-40,-50]
]

KING_POSITION_SCORE_BLACK = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

PIECE_POSITION_SCORE = {
    "wP": PAWN_POSITION_SCORE_WHITE,
    "bP": PAWN_POSITION_SCORE_BLACK,
    "wR": ROOK_POSITION_SCORE_WHITE,
    "bR": ROOK_POSITION_SCORE_BLACK,
    "wN": KNIGHT_POSITION_SCORE_WHITE,
    "bN": KNIGHT_POSITION_SCORE_BLACK,
    "wB": BISHOP_POSITION_SCORE_WHITE,
    "bB": BISHOP_POSITION_SCORE_BLACK,
    "wQ": QUEEN_POSITION_SCORE_WHITE,
    "bQ": QUEEN_POSITION_SCORE_BLACK,
    "wK": KING_POSITION_SCORE_WHITE,
    "bK": KING_POSITION_SCORE_BLACK
}

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