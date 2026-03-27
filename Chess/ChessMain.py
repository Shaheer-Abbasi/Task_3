"""
Handle GameState and User Input
"""

import os
import pygame as p
import ChessEngine

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
        IMAGES[piece] = p.transform.scale(p.image.load(os.path.join(os.path.dirname(__file__), "images", piece + ".png")), (SQ_SIZE, SQ_SIZE))

def main():
    # Initialize the board state
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))
    gs = ChessEngine.GameState()
    print(gs.board)
    load_images() # Load the images that were defined earlier
    validMoves = gs.getValidMoves()
    moveMade = False # Flag variable for when a move is made

    running = True
    sqSelected = () # Keep track of the last selected piece
    playerClicks = [] # Keep track of all player clicks
    # Check events for a 'quit' user input -- If so, then quit
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x,y) location of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col): # User clicked same sq twice (undo)
                        sqSelected = ()
                        playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # Append both first and second click
                if len(playerClicks) == 2: # After second click - make move
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for validMove in validMoves:
                        if move == validMove:
                            gs.makeMove(validMove)
                            moveMade = True
                            sqSelected = () # Reset user clicks
                            playerClicks = []
                            break
                    else:
                        playerClicks = [sqSelected]
            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo move when 'z' is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        clock.tick(MAX_FPS)
        drawGameState(screen, gs, validMoves, sqSelected)
        p.display.flip()

"""
Function for graphics
"""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
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


"""
Highlight valid moves + capturable enemy pieces
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # Selected piece belongs to the player
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight the selected square
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    targetRow, targetCol = move.endRow, move.endCol
                    isCapture = gs.board[targetRow][targetCol] != "--"

                    if isCapture:
                        # Draw ring around the capturable piece
                        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (150, 0, 0, 120),
                                      (SQ_SIZE//2, SQ_SIZE//2),
                                      SQ_SIZE//2, 6)
                        screen.blit(s, (targetCol*SQ_SIZE, targetRow*SQ_SIZE))
                    else:
                        # Draw dots on empty valid squares
                        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (50, 50, 50, 120),
                                      (SQ_SIZE // 2, SQ_SIZE // 2),
                                      SQ_SIZE // 8)
                        screen.blit(s, (targetCol*SQ_SIZE, targetRow*SQ_SIZE))


if __name__ == "__main__":
    main()