import chess
import chess.pgn
import chess.engine
import random

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")

move_number = 1
while not board.is_game_over():
    print(f"Move {move_number}")
    # white (Stockfish) makes a move
    engine_result = engine.analyse(board, chess.engine.Limit(time=0.01))
    best_move = engine_result["pv"][0]
    board.push(best_move)
    if board.is_game_over():
        break
    # black (random) makes a move
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    board.push(random_move)
    move_number += 1

game = chess.pgn.Game.from_board(board)
print(game)

engine.quit()
