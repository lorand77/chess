import logging
import chess
import chess.pgn
import chess.engine
import random

logging.basicConfig(
    filename="uci.log",
    level=logging.DEBUG,
    filemode="w"
)

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine.configure({"Threads": 8, "Hash": 1024})

move_number = 1
score = []
while not board.is_game_over():
    print(f"Move {move_number}")
    # white (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
    best_move = engine_result["pv"][0]

    score.append(engine_result['score'].white().score())
    board.push(best_move)
    # engine.quit()
    # exit()
    if board.is_game_over():
        break
    # black (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
    best_move = engine_result["pv"][0]
    board.push(best_move)
    move_number += 1

game = chess.pgn.Game.from_board(board)
print(game.mainline_moves())

import matplotlib.pyplot as plt

plt.plot(score)
plt.xlabel('Move Number')
plt.ylabel('Score (White perspective)')
plt.title('Game Score Evolution')
plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
plt.grid(True)
plt.show()

engine.quit()
