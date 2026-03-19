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

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move
        self.whiteToMove = not self.whiteToMove # Switch turns

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    # Check to see if king is in check
    def getValidMoves(self):
        return self.getAllPossibleMoves()

    # Check all possible moves according to the rules
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # Call move function based on piece type

        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # White pawn moves
            if self.board[r-1][c] == "--": # 1 square pawn advance
                moves.append(Move((r,c),(r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # 2 square pawn advance
                    moves.append(Move((r,c),(r-2,c), self.board))
            if c-1 >=0:
                if self.board[r-1][c-1][0] == 'b': # Enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # Captrues to right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c+1), self.board))
            # ADD PAWN PROMOTIONS LATER HERE

    def getRookMoves(self, r, c, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1))
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                        break
                    else: # Friendly piece invalid
                        break
                else: # Off board
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece invalid
                        break
                else:  # Off board
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        if self.whiteToMove:
            allyColor = "w"
        else:
            allyColor = "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c), (endRow,endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,-1), (-1,0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        if self.whiteToMove:
            allyColor = "w"
        else:
            allyColor = "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c), (endRow,endCol), self.board))


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
        # Replicate hash function to get unique move ID for comparing moves
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Override 'equals' in order to compare moves
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]










