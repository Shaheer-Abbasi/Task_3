"""
Handle GameState and User Input
"""

import os
import pygame as p
import ChessEngine
from collections import Counter

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
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(os.path.join(os.path.dirname(__file__), "images", piece + ".png")), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))
    gs = ChessEngine.GameState()
    print(gs.board)
    load_images()
    validMoves = gs.getValidMoves()
    moveMade = False

    # -1: no win  0: draw  1: white win  2: black win
    win = -1
    reason = ""

    sqSelected = ()
    playerClicks = []
    running = True
    FiftyMoveRuleCounter = 0

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                # If promotion picker is active, check if player clicked a piece option
                if gs.pendingPromotion is not None:
                    choice = getPromotionChoice(p.mouse.get_pos(), gs.pendingPromotion[2])
                    if choice:
                        gs.completePromotion(choice)
                        moveMade = True
                    continue  # Block all other board interaction during promotion

                if win != -1:
                    continue  # Block clicks after game over

                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move.pieceCaptured == "--" or move.pieceMoved != 'wp' or move.pieceMoved != 'bp':
                        FiftyMoveRuleCounter += 1
                    else:
                        FiftyMoveRuleCounter = 0
                    if move in validMoves:
                        gs.makeMove(move)
                        # Only flag moveMade if no promotion is pending (promotion completes the move)
                        if gs.pendingPromotion is None:
                            moveMade = True
                        sqSelected = ()
                        playerClicks = []
                        break
                    else:
                        playerClicks = [sqSelected]

            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo
                    # Cancel pending promotion first, then undo
                    if gs.pendingPromotion is not None:
                        gs.undoMove()
                    else:
                        gs.undoMove()
                    moveMade = True
                    win = -1
                    reason = ""
                elif e.key == p.K_r:  # Reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    FiftyMoveRuleCounter = 0
                    win = -1
                    reason = ""

        if moveMade:
            validMoves = gs.getValidMoves()
            fen = gs.getFEN()

            if len(validMoves) == 0:
                if gs.inCheck():
                    win = 2 if gs.whiteToMove else 1
                    reason = "Checkmate"
                else:
                    win = 0
                    reason = "Stalemate"
            elif FiftyMoveRuleCounter == 50:
                win = 0
                reason = "50 Move Rule"
            elif gs.positions[fen] >= 3:
                win = 0
                reason = "Threefold repetition"

            moveMade = False

        clock.tick(MAX_FPS)
        drawGameState(screen, gs, validMoves, sqSelected, win, reason)
        p.display.flip()

    print("WIN: ", win, "REASON: ", reason)


"""
Return which promotion piece the player clicked, or None.
Options are drawn in drawPromotionPicker; this maps click coords back to a choice.
"""
def getPromotionChoice(mousePos, color):
    options = ['Q', 'R', 'B', 'N']
    picker_w = SQ_SIZE * 4
    picker_h = SQ_SIZE + 20
    picker_x = (WIDTH - picker_w) // 2
    picker_y = (HEIGHT - picker_h) // 2

    mx, my = mousePos
    for i, piece in enumerate(options):
        rect = p.Rect(picker_x + i * SQ_SIZE, picker_y + 10, SQ_SIZE, SQ_SIZE)
        if rect.collidepoint(mx, my):
            return piece
    return None


"""
Draw the promotion picker overlay centered on the board
"""
def drawPromotionPicker(screen, color):
    options = ['Q', 'R', 'B', 'N']
    picker_w = SQ_SIZE * 4
    picker_h = SQ_SIZE + 20
    picker_x = (WIDTH - picker_w) // 2
    picker_y = (HEIGHT - picker_h) // 2

    # Dim the board behind the picker
    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    # Panel background
    p.draw.rect(screen, p.Color(30, 30, 30), (picker_x - 8, picker_y - 8, picker_w + 16, picker_h + 16), border_radius=10)
    p.draw.rect(screen, p.Color(200, 200, 200), (picker_x - 8, picker_y - 8, picker_w + 16, picker_h + 16), width=2, border_radius=10)

    # Label
    font = p.font.SysFont("Arial", 16, bold=True)
    label = font.render("Choose promotion piece", True, p.Color("white"))
    label_rect = label.get_rect(center=(WIDTH // 2, picker_y - 20))
    # Widen background to include label
    p.draw.rect(screen, p.Color(30, 30, 30), (picker_x - 8, picker_y - 36, picker_w + 16, 24), border_radius=6)
    screen.blit(label, label_rect)

    # Draw each piece option
    mx, my = p.mouse.get_pos()
    for i, piece in enumerate(options):
        rect = p.Rect(picker_x + i * SQ_SIZE, picker_y + 10, SQ_SIZE, SQ_SIZE)
        # Highlight on hover
        if rect.collidepoint(mx, my):
            p.draw.rect(screen, p.Color(80, 80, 80), rect, border_radius=6)
        else:
            p.draw.rect(screen, p.Color(50, 50, 50), rect, border_radius=6)
        # Draw piece image
        key = color + piece
        if key in IMAGES:
            screen.blit(IMAGES[key], rect)


"""
Function for graphics
"""
def drawGameState(screen, gs, validMoves, sqSelected, win=-1, reason=""):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    if gs.pendingPromotion is not None:
        drawPromotionPicker(screen, gs.pendingPromotion[2])
    elif win != -1:
        drawEndScreen(screen, win, reason)


"""
Draw the end-game overlay with winner and reason
"""
def drawEndScreen(screen, win, reason):
    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    if win == 1:
        result_text = "White Wins!"
        result_color = p.Color("white")
    elif win == 2:
        result_text = "Black Wins!"
        result_color = p.Color("black")
    else:
        result_text = "Draw"
        result_color = p.Color("lightgray")

    panel_w, panel_h = 320, 140
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2

    p.draw.rect(screen, p.Color(40, 40, 40), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
    p.draw.rect(screen, p.Color(200, 200, 200), (panel_x, panel_y, panel_w, panel_h), width=2, border_radius=12)

    font_large = p.font.SysFont("Arial", 42, bold=True)
    result_surf = font_large.render(result_text, True, result_color)
    result_rect = result_surf.get_rect(center=(WIDTH // 2, panel_y + 50))
    screen.blit(result_surf, result_rect)

    font_small = p.font.SysFont("Arial", 24)
    reason_surf = font_small.render(reason, True, p.Color(180, 180, 180))
    reason_rect = reason_surf.get_rect(center=(WIDTH // 2, panel_y + 100))
    screen.blit(reason_surf, reason_rect)


"""
Draw the squares
"""
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlight valid moves + capturable enemy pieces
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    targetRow, targetCol = move.endRow, move.endCol
                    isCapture = gs.board[targetRow][targetCol] != "--" or move.isEnpassantMove

                    if isCapture:
                        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (150, 0, 0, 120),
                                      (SQ_SIZE//2, SQ_SIZE//2),
                                      SQ_SIZE//2, 6)
                        screen.blit(s, (targetCol*SQ_SIZE, targetRow*SQ_SIZE))
                    else:
                        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (50, 50, 50, 120),
                                      (SQ_SIZE // 2, SQ_SIZE // 2),
                                      SQ_SIZE // 8)
                        screen.blit(s, (targetCol*SQ_SIZE, targetRow*SQ_SIZE))


if __name__ == "__main__":
    main()