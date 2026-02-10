import chess
import chess.pgn
import chess.engine
import random

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine.configure({"Threads": 8, "Hash": 1024})

move_number = 1
last_move_score = 0
while not board.is_game_over():
    print(f"Move {move_number}")
    # white (Stockfish) makes a move
    engine_result = list(engine.analyse(board, chess.engine.Limit(time=0.5), multipv=256))
    ok_moves = []
    ok_moves_scores = []
    for i in range(len(engine_result)):
        line = engine_result[i]
        if line["score"].white().score(mate_score=100000) - last_move_score > -20:
            ok_moves.append(line["pv"][0])
            ok_moves_scores.append(line["score"].white().score(mate_score=100000))
    if not ok_moves:
        ok_moves.append(engine_result[0]["pv"][0])
        ok_moves_scores.append(engine_result[0]["score"].white().score(mate_score=100000))
    print(ok_moves)
    print(ok_moves_scores)
    current_move_idx = random.randint(0, len(ok_moves) - 1)
    board.push(ok_moves[current_move_idx])
    last_move_score = ok_moves_scores[current_move_idx]
    print(f"Chosen move: {ok_moves[current_move_idx]}, score: {last_move_score}")
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
