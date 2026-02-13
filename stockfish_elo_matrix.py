import logging
import chess
import chess.pgn
import chess.engine
import csv
from datetime import datetime

# logging.basicConfig(
#     filename="uci.log",
#     level=logging.DEBUG,
#     filemode="w"
# )

def play_games_for_elo_pair(engine_white, engine_black, white_elo, black_elo, num_games=100):
    """Play multiple games for a specific Elo pairing and record results"""
    results = {'white_wins': 0, 'draws': 0, 'black_wins': 0}
    
    # Configure engines for this Elo pair
    engine_white.configure({
        "UCI_LimitStrength": True,
        "UCI_Elo": white_elo
    })
    
    engine_black.configure({
        "UCI_LimitStrength": True,
        "UCI_Elo": black_elo
    })
    
    print(f"\nPlaying {num_games} games: White Elo {white_elo} vs Black Elo {black_elo}")
    
    for game_num in range(1, num_games + 1):
        board = chess.Board()
        
        # Play the game
        while not board.is_game_over(claim_draw=True):
            engine_result = engine_white.play(board, chess.engine.Limit(time=0.001))
            board.push(engine_result.move)
            if board.is_game_over(claim_draw=True):
                break

            engine_result = engine_black.play(board, chess.engine.Limit(time=0.001))
            board.push(engine_result.move)
        
        # Record result
        result = board.result()
        if result == "1-0":
            results['white_wins'] += 1
        elif result == "0-1":
            results['black_wins'] += 1
        else:
            results['draws'] += 1
        
        if game_num % 10 == 0:
            print(f"  Progress: {game_num}/{num_games} games completed")
    
    # Print summary for this pairing
    print(f"  Results - W:{results['white_wins']} D:{results['draws']} L:{results['black_wins']}")
    
    return results


def run_elo_matrix_experiment():
    """Run games across all Elo combinations with difference <= 400"""
    
    # Initialize engines
    engine_white = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
    engine_black = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
    engine_white.configure({"Threads": 10, "Hash": 1024})
    engine_black.configure({"Threads": 10, "Hash": 1024})
    
    # Elo range: 1500 to 2800 by 100
    elo_values = list(range(1500, 2900, 100))
    
    # Prepare results storage
    all_results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"elo_matrix_results_{timestamp}.csv"
    
    # Open CSV file for writing
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['white_elo', 'black_elo', 'elo_diff', 'num_games', 'white_wins', 'draws', 'black_wins', 
                      'white_win_pct', 'draw_pct', 'black_win_pct']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_combinations = sum(1 for w in elo_values for b in elo_values if abs(w - b) <= 400)
        completed = 0
        
        print(f"Starting Elo matrix experiment")
        print(f"Total combinations to test: {total_combinations}")
        print(f"Results will be saved to: {output_file}")
        print("="*70)
        
        # Loop through all Elo combinations
        for white_elo in elo_values:
            for black_elo in elo_values:
                # Check if absolute difference is <= 400
                elo_diff = white_elo - black_elo
                if abs(elo_diff) <= 400:
                    # Play 100 games for this combination
                    results = play_games_for_elo_pair(engine_white, engine_black, 
                                                      white_elo, black_elo, num_games=100)
                    
                    # Calculate percentages
                    total_games = 100
                    white_win_pct = results['white_wins'] / total_games * 100
                    draw_pct = results['draws'] / total_games * 100
                    black_win_pct = results['black_wins'] / total_games * 100
                    
                    # Store results
                    result_row = {
                        'white_elo': white_elo,
                        'black_elo': black_elo,
                        'elo_diff': elo_diff,
                        'num_games': total_games,
                        'white_wins': results['white_wins'],
                        'draws': results['draws'],
                        'black_wins': results['black_wins'],
                        'white_win_pct': f"{white_win_pct:.1f}",
                        'draw_pct': f"{draw_pct:.1f}",
                        'black_win_pct': f"{black_win_pct:.1f}"
                    }
                    
                    writer.writerow(result_row)
                    csvfile.flush()  # Ensure data is written immediately
                    all_results.append(result_row)
                    
                    completed += 1
                    print(f"\nProgress: {completed}/{total_combinations} combinations completed ({completed/total_combinations*100:.1f}%)")
                    print("="*70)
        
    # Clean up
    engine_white.quit()
    engine_black.quit()
    
    print(f"\nExperiment completed!")
    print(f"All results saved to: {output_file}")
    print(f"Total combinations tested: {completed}")
    
    return all_results


if __name__ == "__main__":
    run_elo_matrix_experiment()
