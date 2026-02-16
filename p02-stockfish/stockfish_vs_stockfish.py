import chess
import chess.pgn
import chess.engine
import random

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine.configure({"Threads": 8, "Hash": 1024})

move_number = 1
while not board.is_game_over():
    print(f"Move {move_number}")
    # white (Stockfish) makes a move
    engine_result = list(engine.analyse(board, chess.engine.Limit(time=0.1), multipv=256))
    for i in range(len(engine_result)):
        line = engine_result[i]
        print(f"Line {i + 1}: {line['pv'][0]} {line['score'].white().score(mate_score=100000)}")
    best_move = engine_result[0]["pv"][0]
    board.push(best_move)
    if board.is_game_over():
        break
    # black (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
    best_move = engine_result["pv"][0]
    board.push(best_move)
    move_number += 1

game = chess.pgn.Game.from_board(board)
print(game.mainline_moves())

engine.quit()
