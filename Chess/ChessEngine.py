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

        # Keep track of king locations
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # Current castling rights + log for undo
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castlingRightsLog = [CastleRights(True, True, True, True)]

        # En passant: square where capture is possible (row, col), or ()
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [()]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move

        # Update king location after a king move
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Auto promote pawn to queen
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Move the rook too when castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        # En passant: capture the pawn that is beside
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # En passant: if a pawn moves 2 squares, the square it skipped is the en passant target
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update castling rights after every move
        self.updateCastleRights(move)
        self.castlingRightsLog.append(
            CastleRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs
            )
        )

        self.whiteToMove = not self.whiteToMove # Switch turns

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Restore king location on undo
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo rook movement from castle
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queenside castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # Undo en passant capture: restore the captured pawn
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # clear the landing square
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # restore captured pawn

            # Restore en passant state
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # Restore previous castling rights
            self.castlingRightsLog.pop()
            lastRights = self.castlingRightsLog[-1]
            self.currentCastlingRights = CastleRights(
                lastRights.wks,
                lastRights.bks,
                lastRights.wqs,
                lastRights.bqs
            )

    # Check to see if king is in check
    def getValidMoves(self):
        # Get all legal moves, not just all possible raw moves
        tempCastleRights = CastleRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs
        )

        moves = self.getAllPossibleMoves()

        # Add castling moves if legal
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # Remove moves that leave own king in check
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.pop(i)
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        self.currentCastlingRights = tempCastleRights
        return moves

    # Check if current player's king is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Check if enemy can attack square (r, c)
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    # Update castle rights when king/rook moves or rook is captured
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

        # If rook gets captured, remove that castle right too
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

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
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: # Captures to right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

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

    # Generate legal castle moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return

        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    # Kingside castle
    def getKingsideCastleMoves(self, r, c, moves):
        if c + 2 < 8:
            if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
                if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    # Queenside castle
    def getQueensideCastleMoves(self, r, c, moves):
        if c - 3 >= 0:
            if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
                if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


# Store castle rights
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # Computer (Row, Col) --> (Rank, File)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isCastleMove=False, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isCastleMove = isCastleMove
        self.isEnpassantMove = isEnpassantMove

        # En passant captures the pawn beside us, not on the landing square
        if self.isEnpassantMove:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'

        self.isPawnPromotion = (
            (self.pieceMoved == "wp" and self.endRow == 0) or
            (self.pieceMoved == "bp" and self.endRow == 7)
        )

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