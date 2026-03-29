"""
Handle GameState and User Input
"""

import os
import pygame as p
import ChessEngine
import SmartMoveFinder
import PlotGame

WIDTH = HEIGHT = 512
DIMENSION = 8 # Chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animations
IMAGES = {}

# Algorithm labels for UI
ALGO_OPTIONS = ["MinMax", "MinMaxAB", "Negamax", "NegamaxAB"]
ORDERING_OPTIONS = ["random", "captures_first"]
ORDERING_LABELS = {"random": "Random", "captures_first": "Captures First"}

# Colors
BG = (30, 30, 30)
PANEL = (50, 50, 50)
HOVER = (70, 70, 70)
ACCENT = (80, 160, 255)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (130, 130, 130)

# Initialize dict for images
def load_images():
    pieces = [
                'wp', 'wR', 'wN', 'wB', 'wQ', 'wK',
                'bp', 'bR', 'bN', 'bB', 'bQ', 'bK',
              ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(os.path.join(os.path.dirname(__file__), "images", piece + ".png")),
            (SQ_SIZE, SQ_SIZE))


# UI Helpers 
def draw_button(screen, rect, text, font, hover=False, selected=False):
    color = ACCENT if selected else (HOVER if hover else PANEL)
    p.draw.rect(screen, color, rect, border_radius=8)
    p.draw.rect(screen, GRAY, rect, width=2, border_radius=8)
    surf = font.render(text, True, WHITE)
    screen.blit(surf, surf.get_rect(center=rect.center))


# Home Screen 
def homeScreen(screen, clock):
    screen = p.display.set_mode((WIDTH, HEIGHT))
    font_title = p.font.SysFont("Arial", 48, bold=True)
    font_btn = p.font.SysFont("Arial", 24, bold=True)

    buttons = [
        ("Player vs Player", "pvp"),
        ("Player vs AI", "pvai"),
        ("AI vs AI", "aivai"),
    ]

    btn_w, btn_h = 280, 50
    start_y = 200
    spacing = 70

    rects = []
    for i in range(len(buttons)):
        r = p.Rect((WIDTH - btn_w) // 2, start_y + i * spacing, btn_w, btn_h)
        rects.append(r)

    while True:
        mx, my = p.mouse.get_pos()
        for e in p.event.get():
            if e.type == p.QUIT:
                return None
            if e.type == p.MOUSEBUTTONDOWN:
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        return buttons[i][1]

        screen.fill(BG)
        title = font_title.render("Chess", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        subtitle = p.font.SysFont("Arial", 16).render("Select a game mode", True, DARK_GRAY)
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 155)))

        for i, (label, _) in enumerate(buttons):
            draw_button(screen, rects[i], label, font_btn, hover=rects[i].collidepoint(mx, my))

        p.display.flip()
        clock.tick(MAX_FPS)


# Settings Screen
def settingsScreen(screen, clock, mode):
    """
    Returns config dict or None if user quit.
    For 'pvai': one AI config (black).
    For 'aivai': two independent AI configs (white + black).
    """
    SETTINGS_H = 580
    screen = p.display.set_mode((WIDTH, SETTINGS_H))

    font_title = p.font.SysFont("Arial", 32, bold=True)
    font_label = p.font.SysFont("Arial", 18, bold=True)
    font_val = p.font.SysFont("Arial", 18)
    font_btn = p.font.SysFont("Arial", 22, bold=True)

    # Defaults per player
    configs = {
        "white": {"algo_idx": 3, "depth": 3, "ord_idx": 0},
        "black": {"algo_idx": 3, "depth": 3, "ord_idx": 0},
    }

    players = ["black"] if mode == "pvai" else ["white", "black"]

    while True:
        mx, my = p.mouse.get_pos()
        click = False

        for e in p.event.get():
            if e.type == p.QUIT:
                return None
            if e.type == p.MOUSEBUTTONDOWN:
                click = True
            if e.type == p.KEYDOWN and e.key == p.K_ESCAPE:
                return "back"

        screen.fill(BG)

        # Title
        title_text = "AI Settings" if mode == "pvai" else "AI vs AI Settings"
        title = font_title.render(title_text, True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 35)))

        # Layout
        col_w = 220 if len(players) == 2 else 280
        total_w = col_w * len(players) + 20 * (len(players) - 1)
        start_x = (WIDTH - total_w) // 2
        row_y = 80

        clickable = []

        for pi, player in enumerate(players):
            cfg = configs[player]
            cx = start_x + pi * (col_w + 20)

            # Player label
            plabel = font_label.render(f"{'White' if player == 'white' else 'Black'} AI", True, ACCENT)
            screen.blit(plabel, plabel.get_rect(center=(cx + col_w // 2, row_y)))

            y = row_y + 35

            # Algorithm
            alabel = font_label.render("Algorithm", True, GRAY)
            screen.blit(alabel, (cx, y))
            y += 25

            for ai, algo_name in enumerate(ALGO_OPTIONS):
                r = p.Rect(cx, y, col_w, 30)
                selected = cfg["algo_idx"] == ai
                draw_button(screen, r, algo_name, font_val, hover=r.collidepoint(mx, my), selected=selected)
                if click and r.collidepoint(mx, my):
                    cfg["algo_idx"] = ai
                y += 35

            y += 10

            # Depth
            dlabel = font_label.render("Depth", True, GRAY)
            screen.blit(dlabel, (cx, y))
            y += 25

            depth_btn_w = (col_w - 30) // 4
            for d in range(1, 5):
                r = p.Rect(cx + (d - 1) * (depth_btn_w + 10), y, depth_btn_w, 32)
                selected = cfg["depth"] == d
                draw_button(screen, r, str(d), font_val, hover=r.collidepoint(mx, my), selected=selected)
                if click and r.collidepoint(mx, my):
                    cfg["depth"] = d
            y += 45

            # Move Ordering
            olabel = font_label.render("Move Ordering", True, GRAY)
            screen.blit(olabel, (cx, y))
            y += 25

            for oi, ord_key in enumerate(ORDERING_OPTIONS):
                r = p.Rect(cx, y, col_w, 30)
                selected = cfg["ord_idx"] == oi
                draw_button(screen, r, ORDERING_LABELS[ord_key], font_val,
                            hover=r.collidepoint(mx, my), selected=selected)
                if click and r.collidepoint(mx, my):
                    cfg["ord_idx"] = oi
                y += 35

        # Start Game button
        start_r = p.Rect((WIDTH - 200) // 2, SETTINGS_H - 65, 200, 45)
        draw_button(screen, start_r, "Start Game", font_btn, hover=start_r.collidepoint(mx, my))
        if click and start_r.collidepoint(mx, my):
            result = {}
            if mode == "pvai":
                result["playerOne"] = True
                result["playerTwo"] = False
                bc = configs["black"]
                result["black_algo"] = ALGO_OPTIONS[bc["algo_idx"]]
                result["black_depth"] = bc["depth"]
                result["black_ordering"] = ORDERING_OPTIONS[bc["ord_idx"]]
                # White is human, no AI config needed
                result["white_algo"] = None
                result["white_depth"] = None
                result["white_ordering"] = None
            else:
                result["playerOne"] = False
                result["playerTwo"] = False
                for player in ["white", "black"]:
                    c = configs[player]
                    result[f"{player}_algo"] = ALGO_OPTIONS[c["algo_idx"]]
                    result[f"{player}_depth"] = c["depth"]
                    result[f"{player}_ordering"] = ORDERING_OPTIONS[c["ord_idx"]]
            return result

        # Back hint
        hint = p.font.SysFont("Arial", 14).render("ESC to go back", True, DARK_GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, SETTINGS_H - 14)))

        p.display.flip()
        clock.tick(MAX_FPS)


# Game Loop 
def gameLoop(screen, clock, config):
    screen = p.display.set_mode((WIDTH, HEIGHT))
    gs = ChessEngine.GameState()
    load_images()
    validMoves = gs.getValidMoves()
    moveMade = False

    playerOne = config.get("playerOne", True) # White
    playerTwo = config.get("playerTwo", True) # Black

    # -1: no win  0: draw  1: white win  2: black win
    win = -1
    reason = ""
    sqSelected = ()
    playerClicks = []
    FiftyMoveRuleCounter = 0

    SmartMoveFinder.reset_log()

    while True:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                return "quit"

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

                if not humanTurn:
                    continue  # Block clicks during AI turn

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
                    for validMove in validMoves:
                        if move == validMove:
                            # 50-move rule: reset on capture or pawn move, increment otherwise
                            if validMove.pieceCaptured != "--" or validMove.pieceMoved[1] == 'p':
                                FiftyMoveRuleCounter = 0
                            else:
                                FiftyMoveRuleCounter += 1
                            gs.makeMove(validMove)
                            # Only flag moveMade if no promotion is pending
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
                    SmartMoveFinder.reset_log()
                elif e.key == p.K_m and win != -1:
                    return "menu"

        # AI move
        if not humanTurn and win == -1 and gs.pendingPromotion is None:
            side = "white" if gs.whiteToMove else "black"
            algo = config.get(f"{side}_algo", "NegamaxAB")
            depth = config.get(f"{side}_depth", 3)
            ordering = config.get(f"{side}_ordering", "random")

            aiMove = SmartMoveFinder.findBestMove(gs, validMoves, algo, depth, ordering)
            if aiMove is None:
                aiMove = validMoves[0] if validMoves else None
            if aiMove is not None:
                if aiMove.pieceCaptured != "--" or aiMove.pieceMoved[1] == 'p':
                    FiftyMoveRuleCounter = 0
                else:
                    FiftyMoveRuleCounter += 1
                gs.makeMove(aiMove)
                # Auto-complete AI promotions to Queen
                if gs.pendingPromotion is not None:
                    gs.completePromotion('Q')
                moveMade = True

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
            elif gs.positions.get(fen, 0) >= 3:
                win = 0
                reason = "Threefold repetition"

            moveMade = False

            # Save log and auto-generate graphs
            if win != -1:
                outcomes = {-1: "in_progress", 0: "draw", 1: "white_wins", 2: "black_wins"}
                log_path = SmartMoveFinder.save_log(outcomes[win])
                if log_path:
                    try:
                        PlotGame.plot_single(log_path)
                    except Exception as e:
                        print(f"Graph generation failed: {e}")

        clock.tick(MAX_FPS)
        drawGameState(screen, gs, validMoves, sqSelected, win, reason)
        p.display.flip()


# Promotion Picker 
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

    panel_w, panel_h = 320, 190
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2

    p.draw.rect(screen, p.Color(40, 40, 40), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
    p.draw.rect(screen, p.Color(200, 200, 200), (panel_x, panel_y, panel_w, panel_h), width=2, border_radius=12)

    font_large = p.font.SysFont("Arial", 42, bold=True)
    result_surf = font_large.render(result_text, True, result_color)
    screen.blit(result_surf, result_surf.get_rect(center=(WIDTH // 2, panel_y + 50)))

    font_small = p.font.SysFont("Arial", 24)
    reason_surf = font_small.render(reason, True, p.Color(180, 180, 180))
    screen.blit(reason_surf, reason_surf.get_rect(center=(WIDTH // 2, panel_y + 95)))

    font_hint = p.font.SysFont("Arial", 16)
    hint1 = font_hint.render("Press R to reset board", True, p.Color(130, 130, 130))
    screen.blit(hint1, hint1.get_rect(center=(WIDTH // 2, panel_y + 135)))
    hint2 = font_hint.render("Press M for menu", True, p.Color(130, 130, 130))
    screen.blit(hint2, hint2.get_rect(center=(WIDTH // 2, panel_y + 160)))


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
                                      (SQ_SIZE // 2, SQ_SIZE // 2),
                                      SQ_SIZE // 2, 6)
                        screen.blit(s, (targetCol * SQ_SIZE, targetRow * SQ_SIZE))
                    else:
                        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (50, 50, 50, 120),
                                      (SQ_SIZE // 2, SQ_SIZE // 2),
                                      SQ_SIZE // 8)
                        screen.blit(s, (targetCol * SQ_SIZE, targetRow * SQ_SIZE))


# Main 
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    load_images()

    while True:
        mode = homeScreen(screen, clock)
        if mode is None:
            break

        if mode == "pvp":
            config = {
                "playerOne": True, "playerTwo": True,
                "white_algo": None, "white_depth": None, "white_ordering": None,
                "black_algo": None, "black_depth": None, "black_ordering": None,
            }
        elif mode in ("pvai", "aivai"):
            config = settingsScreen(screen, clock, mode)
            if config is None:
                break
            if config == "back":
                continue
        else:
            continue

        result = gameLoop(screen, clock, config)
        if result == "quit":
            break
        # result == "menu" causes loops back to homeScreen

if __name__ == "__main__":
    main()