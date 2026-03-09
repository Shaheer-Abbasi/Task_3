"""
Handle GameState and User Input
"""

import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8 # Chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animations
IMAGES = {}

"""
Initialize global dictionary of images
"""
def load_images():
    pieces = [
                'wp', 'wR', 'wN', 'wB', 'wQ', 'wK',
                'bp', 'bR', 'bN', 'bB', 'bQ', 'bK',
              ]
    # Make dictionary that holds key value pairs of {Piece: Image}
    for piece in pieces:
        # Assign the key value pair
        # Use transform.scale function to ensure the image is properly rendered based on size
        # image.load grabs the image and displays it
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    # Initialize the board state
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))
    gs = ChessEngine.GameState()
    print(gs.board)
    load_images() # Load the images that were defined earlier
    running = True
    # Check events for a 'quit' user input -- If so, then quit
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        clock.tick(MAX_FPS)
        p.display.flip()
        drawGameState(screen, gs)

"""
Function for graphics
"""
def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

"""
Draw the squares
"""
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")] # Array for light + dark color combo
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] # Mod returns 0 or 1 to index into colors array
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draw the pieces on the board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # If square is not empty
                screen.blit(IMAGES[piece], (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # Put piece on square

if __name__ == "__main__":
    main()