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
    "base": {
        "white": p.Color("white"),
        "black": p.Color("gray"),
        "highlighted": p.Color("purple"),
        "possible_moves": p.Color("violet"),
        "capture_color" : p.Color("red"),
        "set": "staunty"
    },
    "blue": {
        "white": p.Color("lightblue"),
        "black": p.Color("navy"),
        "highlighted": p.Color("gold"),
        "possible_moves": p.Color("yellow"),
        "capture_color" : p.Color("red"),
        "set": "anarcandy"
    },
    "green": {
        "white": p.Color("honeydew"),
        "black": p.Color("darkgreen"),
        "highlighted": p.Color("yellow"),
        "possible_moves": p.Color("lightgreen"),
        "capture_color" : p.Color("red"),
        "set": "riohacha"
    },
    "red": {
        "white": p.Color("lightcoral"),
        "black": p.Color("darkred"),
        "highlighted": p.Color("orange"),
        "possible_moves": p.Color("salmon"),
        "capture_color" : p.Color("red"),
        "set": "maestro"
    },
    "light_pink": {
        "white": p.Color("mistyrose"),
        "black": p.Color("palevioletred"),
        "highlighted": p.Color("lightcoral"),
        "possible_moves": p.Color("lightpink"),
        "capture_color" : p.Color("red"),
        "set": "spatial"
    },
    "brown": {
        "white": p.Color("wheat"),
        "black": p.Color("saddlebrown"),
        "highlighted": p.Color("gold"),
        "possible_moves": p.Color("tan"),
        "capture_color" : p.Color("red"),
        "set": "kiwen-suwi"
    },
    "dark": {
        "white": p.Color("lightgray"),
        "black": p.Color("black"),
        "highlighted": p.Color("red"),
        "possible_moves": p.Color("darkred"),
        "capture_color" : p.Color("red"),
        "set": "monarchy"
    },
    "neon": {
        "white": p.Color("cyan"),
        "black": p.Color("magenta"),
        "highlighted": p.Color("lime"),
        "possible_moves": p.Color("lightgreen"),
        "capture_color" : p.Color("red"),
        "set": "pixel"
    }
}
