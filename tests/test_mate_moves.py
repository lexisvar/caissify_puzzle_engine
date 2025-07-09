from chess_lesson_engine.chess_utils import evaluate_position
import chess

fen = 'Bq1B1K2/3PpN2/P3Pp2/P1p2P2/2Pk1b1R/1p6/pN1P1P2/QR6 w - - 0 1'
board = chess.Board(fen)
results = []
for move in board.legal_moves:
    san = board.san(move)
    board.push(move)
    # Get the PV from Stockfish for this move
    score, mate, info = evaluate_position(board.fen(), time_limit=10.0, min_depth=30, multipv=1)
    pv_moves = info.get('pv', [])
    pv_san = []
    temp_board = board.copy()
    for pv_move in pv_moves:
        pv_san.append(temp_board.san(pv_move))
        temp_board.push(pv_move)
    results.append((san, mate, score, pv_san))
    board.pop()
for san, mate, score, pv_san in results:
    print(f"Move: {san}, Mate: {mate}, Score: {score}, PV: {pv_san}")
