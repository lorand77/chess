import chess
import time
import chess.svg
import chess.pgn
import chess.engine


board = chess.Board()
board
print(board)

def make_svg():
    svg_board = chess.svg.board(board)
    with open('board.svg', 'w') as f:
        f.write(svg_board)

board.legal_moves  
board.piece_at(chess.A8)

for m in board.legal_moves:
    print(m)

list(board.legal_moves)[0]
board.push(list(board.legal_moves)[0])
print(board)
len(list(board.legal_moves))


board.pop()
print(board)

board.is_check()
board.is_checkmate()
board.is_stalemate()
board.is_insufficient_material()
board.can_claim_threefold_repetition()
board.can_claim_fifty_moves()
board.is_game_over()

board.fen()

game = chess.pgn.Game.from_board(board)

with open("game.pgn", "w", encoding="utf-8") as f:
    print(game, file=f)

board.push_san("e4")
print(board)
board.pop()
print(board)

board.push(chess.Move.from_uci('e2e3'))
print(board)
board.pop()
make_svg()
print(board)


# Path to the Stockfish binary
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")

start_time = time.time()
info = engine.analyse(board, chess.engine.Limit(time=10))
elapsed_time = time.time() - start_time
print(f"Engine analysis took {elapsed_time:.2f} seconds")

print(info)
print("Score:", info["score"])          # +28 cp → white is slightly better
print("Best move:", info["pv"][0])      # e2e4

# Get top 5 moves
info = engine.analyse(board, chess.engine.Limit(time=10), multipv=5)
print(info)
for idx, pv_info in enumerate(info, start=1):
    print(f"Move {idx}: {pv_info['pv'][0]} - Score: {pv_info['score']}")

info = engine.analyse(board, chess.engine.Limit(time=10), multipv=100)
for idx, pv_info in enumerate(info, start=1):
    print(f"Move {idx}: {pv_info['pv'][0]} - Score: {pv_info['score']}")
