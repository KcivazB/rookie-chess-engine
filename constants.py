import pygame as p

WIDTH = HEIGHT = 1024
DIMENSION = 8 
SQUARES = 8**2 
SQ_SIZE = WIDTH // DIMENSION 
PIECES = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
IMAGES = {}
MAX_FPS = 15

IMAGE_DIR = "images"

# Initial theme
THEME = "base"

# Themes dictionary
THEMES = {
    # Customize themes for highlights or anything
    "base": {
        "white": p.Color("white"),
        "black": p.Color("gray"),
        "highlighted": p.Color("purple"),
        "possible_moves": p.Color("purple"),
        "set": "staunty"
    },
    "blue": {
        "white": p.Color("deepskyblue"),
        "black": p.Color("dodgerblue4"),
        "highlighted": p.Color("gold"),
        "possible_moves": p.Color("gold"),
        "set": "anarcandy"
    },
    "green": {
        "white": p.Color("seagreen1"),
        "black": p.Color("seagreen3"),
        "highlighted": p.Color("yellow"),
        "possible_moves": p.Color("yellow"),
        "set": "riohacha"
    },
    "red": {
        "white": p.Color("indianred1"),
        "black": p.Color("indianred3"),
        "highlighted": p.Color("orange"),
        "possible_moves": p.Color("orange"),
        "set": "maestro"
    },
    "light_pink": {
        "white": p.Color("lightpink1"),
        "black": p.Color("palevioletred3"),
        "highlighted": p.Color("lightcoral"),
        "possible_moves": p.Color("lightcoral"),
        "set": "spatial"
    },
    "brown": {
        "white": p.Color("beige"),
        "black": p.Color("brown"),
        "highlighted": p.Color("gold"),
        "possible_moves": p.Color("gold"),
        "set": "kiwen-suwi"
    },
    "dark": {
        "white": p.Color("darkgray"),
        "black": p.Color("black"),
        "highlighted": p.Color("red"),
        "possible_moves": p.Color("red"),
        "set": "monarchy"
    },
    "neon": {
        "white": p.Color("cyan"),
        "black": p.Color("magenta"),
        "highlighted": p.Color("lime"),
        "possible_moves": p.Color("lime"),
        "set": "pixel"
    }
}