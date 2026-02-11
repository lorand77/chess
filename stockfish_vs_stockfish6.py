import logging
import chess
import chess.pgn
import chess.engine

# logging.basicConfig(
#     filename="uci.log",
#     level=logging.DEBUG,
#     filemode="w"
# )

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine.configure({"Threads": 8, "Hash": 1024})
engine.configure({"SyzygyPath": r"C:\Users\lorand\Programs\syzygy"})

move_number = 1
while not board.is_game_over(claim_draw=True):
    print(f"Move {move_number}")
    # white (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
    best_move = engine_result["pv"][0]
    board.push(best_move)
    if board.is_game_over(claim_draw=True):
        break
    # black (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
    best_move = engine_result["pv"][0]
    board.push(best_move)
    move_number += 1

game = chess.pgn.Game.from_board(board)
print(game.mainline_moves())

engine.quit()
