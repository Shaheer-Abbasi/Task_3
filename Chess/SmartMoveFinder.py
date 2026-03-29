import random
import time
import json
import os
from datetime import datetime

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0

# ── Logging ──────────────────────────────────────────────────────────
game_log = []
_move_counter = 0

def _log_move(algorithm, depth, nodes, elapsed, ordering):
    global _move_counter
    _move_counter += 1
    game_log.append({
        "move_number": _move_counter,
        "algorithm": algorithm,
        "depth": depth,
        "nodes": nodes,
        "time": round(elapsed, 3),
        "move_ordering": ordering,
    })

def reset_log():
    global game_log, _move_counter
    game_log = []
    _move_counter = 0

def save_log(outcome="unknown"):
    if not game_log:
        return None
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    first = game_log[0]
    algo = first["algorithm"]
    depth = first["depth"]
    ordering = first["move_ordering"]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{algo}_d{depth}_{ordering}.json"
    filepath = os.path.join(log_dir, filename)
    data = {
        "metadata": {
            "algorithm": algo,
            "depth": depth,
            "move_ordering": ordering,
            "total_moves": len(game_log),
            "total_nodes": sum(m["nodes"] for m in game_log),
            "total_time": round(sum(m["time"] for m in game_log), 3),
            "outcome": outcome,
            "timestamp": ts,
        },
        "moves": game_log,
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Log saved: {filepath}")
    return filepath


# ── Move Ordering ────────────────────────────────────────────────────
def orderMoves(moves, mode):
    random.shuffle(moves)
    if mode == "captures_first":
        def mvv_lva(m):
            if m.pieceCaptured != "--":
                return -(pieceScore.get(m.pieceCaptured[1], 0) - pieceScore.get(m.pieceMoved[1], 0))
            return 1
        moves.sort(key=mvv_lva)


# ── Shared Evaluation ────────────────────────────────────────────────
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


# MINIMAX  (no pruning)
def findBestMoveMinMax(gs, validMoves, depth=3, ordering="random"):
    global _bestMove, _nodes
    _bestMove = None
    _nodes = 0
    _depth = depth
    orderMoves(validMoves, ordering)
    start = time.time()
    _minmax(gs, validMoves, depth, depth, gs.whiteToMove)
    elapsed = time.time() - start
    label = "MinMax"
    print(f"[{label}] Depth: {depth} | Nodes: {_nodes} | Time: {elapsed:.3f}s")
    _log_move(label, depth, _nodes, elapsed, ordering)
    return _bestMove

def _minmax(gs, validMoves, depth, rootDepth, whiteToMove):
    global _bestMove, _nodes
    _nodes += 1

    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            if gs.pendingPromotion is not None:
                gs.completePromotion('Q')
            nextMoves = gs.getValidMoves()
            score = _minmax(gs, nextMoves, depth - 1, rootDepth, False)
            if score > maxScore:
                maxScore = score
                if depth == rootDepth:
                    _bestMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            if gs.pendingPromotion is not None:
                gs.completePromotion('Q')
            nextMoves = gs.getValidMoves()
            score = _minmax(gs, nextMoves, depth - 1, rootDepth, True)
            if score < minScore:
                minScore = score
                if depth == rootDepth:
                    _bestMove = move
            gs.undoMove()
        return minScore

# 2. MINIMAX + ALPHA-BETA  (with pruning)
def findBestMoveMinMaxAB(gs, validMoves, depth=3, ordering="random"):
    global _bestMove, _nodes
    _bestMove = None
    _nodes = 0
    orderMoves(validMoves, ordering)
    start = time.time()
    _minmaxAB(gs, validMoves, depth, depth, -CHECKMATE, CHECKMATE, gs.whiteToMove)
    elapsed = time.time() - start
    label = "MinMaxAB"
    print(f"[{label}] Depth: {depth} | Nodes: {_nodes} | Time: {elapsed:.3f}s")
    _log_move(label, depth, _nodes, elapsed, ordering)
    return _bestMove

def _minmaxAB(gs, validMoves, depth, rootDepth, alpha, beta, whiteToMove):
    global _bestMove, _nodes
    _nodes += 1

    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            if gs.pendingPromotion is not None:
                gs.completePromotion('Q')
            nextMoves = gs.getValidMoves()
            score = _minmaxAB(gs, nextMoves, depth - 1, rootDepth, alpha, beta, False)
            if score > maxScore:
                maxScore = score
                if depth == rootDepth:
                    _bestMove = move
            if maxScore > alpha:
                alpha = maxScore
            gs.undoMove()
            if alpha >= beta:
                break
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            if gs.pendingPromotion is not None:
                gs.completePromotion('Q')
            nextMoves = gs.getValidMoves()
            score = _minmaxAB(gs, nextMoves, depth - 1, rootDepth, alpha, beta, True)
            if score < minScore:
                minScore = score
                if depth == rootDepth:
                    _bestMove = move
            if minScore < beta:
                beta = minScore
            gs.undoMove()
            if alpha >= beta:
                break
        return minScore

# 3. NEGAMAX  (no pruning)
def findBestMoveNegamax(gs, validMoves, depth=3, ordering="random"):
    global _bestMove, _nodes
    _bestMove = None
    _nodes = 0
    orderMoves(validMoves, ordering)
    turnMultiplier = 1 if gs.whiteToMove else -1
    start = time.time()
    _negamax(gs, validMoves, depth, depth, turnMultiplier)
    elapsed = time.time() - start
    label = "Negamax"
    print(f"[{label}] Depth: {depth} | Nodes: {_nodes} | Time: {elapsed:.3f}s")
    _log_move(label, depth, _nodes, elapsed, ordering)
    return _bestMove

def _negamax(gs, validMoves, depth, rootDepth, turnMultiplier):
    global _bestMove, _nodes
    _nodes += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        if gs.pendingPromotion is not None:
            gs.completePromotion('Q')
        nextMoves = gs.getValidMoves()
        score = -_negamax(gs, nextMoves, depth - 1, rootDepth, -turnMultiplier)
        gs.undoMove()
        if score > maxScore:
            maxScore = score
            if depth == rootDepth:
                _bestMove = move
    return maxScore

# 4. NEGAMAX + ALPHA-BETA  (with pruning)
def findBestMoveNegamaxAB(gs, validMoves, depth=3, ordering="random"):
    global _bestMove, _nodes
    _bestMove = None
    _nodes = 0
    orderMoves(validMoves, ordering)
    turnMultiplier = 1 if gs.whiteToMove else -1
    start = time.time()
    _negamaxAB(gs, validMoves, depth, depth, -CHECKMATE, CHECKMATE, turnMultiplier)
    elapsed = time.time() - start
    label = "NegamaxAB"
    print(f"[{label}] Depth: {depth} | Nodes: {_nodes} | Time: {elapsed:.3f}s")
    _log_move(label, depth, _nodes, elapsed, ordering)
    return _bestMove

def _negamaxAB(gs, validMoves, depth, rootDepth, alpha, beta, turnMultiplier):
    global _bestMove, _nodes
    _nodes += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        if gs.pendingPromotion is not None:
            gs.completePromotion('Q')
        nextMoves = gs.getValidMoves()
        score = -_negamaxAB(gs, nextMoves, depth - 1, rootDepth, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        if score > maxScore:
            maxScore = score
            if depth == rootDepth:
                _bestMove = move
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

# Exporter
ALGORITHMS = {
    "MinMax":     findBestMoveMinMax,
    "MinMaxAB":   findBestMoveMinMaxAB,
    "Negamax":    findBestMoveNegamax,
    "NegamaxAB":  findBestMoveNegamaxAB,
}

def findBestMove(gs, validMoves, algorithm="NegamaxAB", depth=3, ordering="random"):
    fn = ALGORITHMS[algorithm]
    return fn(gs, validMoves, depth, ordering)
