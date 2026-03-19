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
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], # White pawns
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]  # White pieces
        ]
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move
        self.whiteToMove = not self.whiteToMove # Switch turns

class Move():
    # Computer (Row, Col) --> (Rank, File)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]










