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

engine_white = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine_black = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine_white.configure({"Threads": 10, "Hash": 1024})
engine_white.configure({"SyzygyPath": r"C:\Users\lorand\Programs\syzygy"})
engine_black.configure({"Threads": 10, "Hash": 1024})
engine_black.configure({"SyzygyPath": r"C:\Users\lorand\Programs\syzygy"})

engine_white.configure({
  #"UCI_LimitStrength": False
  "UCI_LimitStrength": True,
  "UCI_Elo": 3000
})
# engine_white.configure({"Skill Level": 20})

engine_black.configure({
  "UCI_LimitStrength": True,
  "UCI_Elo": 2600
})
# engine_black.configure({"Skill Level": 0})


def play_games(num_games=100):
    """Play multiple games and record results"""
    results = {'white_wins': 0, 'draws': 0, 'black_wins': 0}
    
    for game_num in range(1, num_games + 1):
        board = chess.Board()
        
        # Play the game
        while not board.is_game_over(claim_draw=True):

            engine_result = engine_white.play(board, chess.engine.Limit(time=0.5))
            board.push(engine_result.move)
            if board.is_game_over(claim_draw=True):
                break

            engine_result = engine_black.play(board, chess.engine.Limit(time=0.5))
            board.push(engine_result.move)
        
        # Record result
        result = board.result()
        if result == "1-0":
            results['white_wins'] += 1
        elif result == "0-1":
            results['black_wins'] += 1
        else:
            results['draws'] += 1
        
        print(f"Game {game_num}/{num_games}: {result}")
        game = chess.pgn.Game.from_board(board)
        print(game.mainline_moves())
        print()
    
    # Print summary
    print("\n" + "="*50)
    print(f"Results after {num_games} games:")
    print(f"White Wins: {results['white_wins']} ({results['white_wins']/num_games*100:.1f}%)")
    print(f"Draws:      {results['draws']} ({results['draws']/num_games*100:.1f}%)")
    print(f"Black Wins: {results['black_wins']} ({results['black_wins']/num_games*100:.1f}%)")
    print("="*50)
    
    return results

if __name__ == "__main__":
    play_games(10)
    engine_white.quit()
    engine_black.quit()