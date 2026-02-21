import chess
import chess.engine
import sys
import os

# Configuration Constants
STOCKFISH_PATH = r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe"
#STOCKFISH_PATH = "/usr/local/bin/stockfish"
DEFAULT_LORFISH_DEPTH = 4
DEFAULT_STOCKFISH_ELO = 1800
DEFAULT_NUM_GAMES = 100
STOCKFISH_TIME_LIMIT = 0.5  # seconds per move
STOCKFISH_THREADS = 4

# Add parent directory to path to import lorfish
sys.path.insert(0, os.path.dirname(__file__))
from lorfish import LorFish


def play_game(lorfish_engine, stockfish_engine, lorfish_plays_white=True):
    """Play a single game between LorFish and Stockfish"""
    board = chess.Board()
    
    while not board.is_game_over(claim_draw=True):
        # White's turn
        if lorfish_plays_white:
            move = lorfish_engine.get_best_move(board)
        else:
            result = stockfish_engine.play(board, chess.engine.Limit(time=STOCKFISH_TIME_LIMIT))
            move = result.move
        
        board.push(move)
        
        if board.is_game_over(claim_draw=True):
            break
        
        # Black's turn
        if not lorfish_plays_white:
            move = lorfish_engine.get_best_move(board)
        else:
            result = stockfish_engine.play(board, chess.engine.Limit(time=STOCKFISH_TIME_LIMIT))
            move = result.move
        
        board.push(move)
    
    return board.result()


def play_match(lorfish_depth=DEFAULT_LORFISH_DEPTH, stockfish_elo=DEFAULT_STOCKFISH_ELO, num_games=DEFAULT_NUM_GAMES):
    """Play a match of multiple games between LorFish and Stockfish"""
    
    print(f"LorFish (depth {lorfish_depth}) vs Stockfish (Elo {stockfish_elo}) - {num_games} games\n")
    
    lorfish_engine = LorFish(depth=lorfish_depth)
    
    # Initialize Stockfish
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    stockfish.configure({
        "UCI_LimitStrength": True,
        "UCI_Elo": stockfish_elo,
        "Threads": STOCKFISH_THREADS,
        "Hash": 512
    })
    
    # Track results
    lorfish_wins = 0
    stockfish_wins = 0
    draws = 0
    
    # Play games
    for game_num in range(1, num_games + 1):
        lorfish_plays_white = (game_num % 2 == 1)
        result = play_game(lorfish_engine, stockfish, lorfish_plays_white)
        
        # Update statistics
        if result == "1-0":
            if lorfish_plays_white:
                lorfish_wins += 1
            else:
                stockfish_wins += 1
        elif result == "0-1":
            if lorfish_plays_white:
                stockfish_wins += 1
            else:
                lorfish_wins += 1
        else:
            draws += 1
        
        score = lorfish_wins + draws * 0.5
        print(f"Game {game_num}: {result}  |  LorFish: {lorfish_wins}W {draws}D {stockfish_wins}L  Score: {score}/{game_num}")
    
    stockfish.quit()
    
    # Print summary
    print(f"\nLorFish: {lorfish_wins}W {draws}D {stockfish_wins}L (Score: {score}/{num_games})")


if __name__ == "__main__":
    play_match(
        lorfish_depth=DEFAULT_LORFISH_DEPTH,
        stockfish_elo=DEFAULT_STOCKFISH_ELO,
        num_games=DEFAULT_NUM_GAMES
    )
