import chess
import chess.engine
import chess.pgn
import random
import matplotlib.pyplot as plt
import statistics

engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")

move_counts = []

for game_num in range(30):
    board = chess.Board()
    move_number = 1
    
    while not board.is_game_over():
        # white (Stockfish) makes a move
        engine_result = engine.analyse(board, chess.engine.Limit(time=0.1))
        best_move = engine_result["pv"][0]
        board.push(best_move)
        
        if board.is_game_over():
            break
        
        # black (random) makes a move
        legal_moves = list(board.legal_moves)
        random_move = random.choice(legal_moves)
        board.push(random_move)
        move_number += 1
    
    move_counts.append(move_number)
    print(f"Game {game_num + 1}: {move_number} moves")
    
    game = chess.pgn.Game.from_board(board)
    print(game.mainline_moves())
    print()

engine.quit()

median_moves = statistics.median(move_counts)
print(f"\nMedian number of moves: {median_moves}")

plt.hist(move_counts, bins=20, edgecolor='black')
plt.axvline(median_moves, color='red', linestyle='--', linewidth=2, label=f'Median: {median_moves}')
plt.xlabel('Number of Moves')
plt.ylabel('Frequency')
plt.title('Stockfish vs Random: Move Count Distribution (30 games)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
