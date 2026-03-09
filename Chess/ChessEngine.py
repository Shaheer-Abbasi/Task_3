"""
Store data about current game state
Determine valid moves
Keep log of all moves
"""
class GameState():
    def __init__(self):
        """
        Breakdown of Pieces:
        bR = Black Rook
        bN = Black Knight
        bB = Black Bishop
        bQ = Black Queen
        bK = Black King
        bp = Black Pawn
        --------------------
        wp = White Pawn
        wR = White Rook
        wN = White Knight
        wB = White Bishop
        wQ = White Queen
        wK = White King
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Black pieces
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Black pawns
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Use "--" to represent blank spaces
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], # White pawns
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]  # White pieces
        ]
        self.whiteToMove = True
        self.moveLog = []