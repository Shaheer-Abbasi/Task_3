import random
import time

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

nextMove = None
nodesEvaluated = 0


def findBestMoveMinMax(gs, validMoves):
    global nextMove, nodesEvaluated
    nextMove = None
    nodesEvaluated = 0
    start = time.time()
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    elapsed = time.time() - start
    print(f"[MinMax] Depth: {DEPTH} | Nodes: {nodesEvaluated} | Time: {elapsed:.3f}s")
    return nextMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove, nodesEvaluated
    nodesEvaluated += 1

    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()

            score = findMoveMinMax(gs, nextMoves, depth - 1, False)

            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()

        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()

            score = findMoveMinMax(gs, nextMoves, depth - 1, True)

            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()

        return minScore


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score


def findBestMoveAlphaBeta(gs, validMoves):
    global nextMove, nodesEvaluated
    nextMove = None
    nodesEvaluated = 0
    random.shuffle(validMoves)
    turnMultiplier = 1 if gs.whiteToMove else -1
    start = time.time()
    MaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, turnMultiplier)
    elapsed = time.time() - start
    print(f"[AlphaBeta] Depth: {DEPTH} | Nodes: {nodesEvaluated} | Time: {elapsed:.3f}s")
    return nextMove


def MaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, nodesEvaluated
    nodesEvaluated += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE

    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -MaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        if maxScore > alpha:
            alpha = maxScore

        if alpha >= beta:
            break

    return maxScore
