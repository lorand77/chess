import chess
import chess.engine
import sys
import os

# Configuration Constants
DEFAULT_SIMPLE_ENGINE_DEPTH = 4
DEFAULT_STOCKFISH_ELO = 1600
DEFAULT_NUM_GAMES = 10

# Add parent directory to path to import simple_engine
sys.path.insert(0, os.path.dirname(__file__))
from simple_engine import SimpleEngine


def play_game(simple_engine, stockfish_engine, simple_plays_white=True):
    """Play a single game between SimpleEngine and Stockfish"""
    board = chess.Board()
    
    while not board.is_game_over(claim_draw=True):
        # White's turn
        if simple_plays_white:
            move = simple_engine.get_best_move(board)
        else:
            result = stockfish_engine.play(board, chess.engine.Limit(time=0.5))
            move = result.move
        
        board.push(move)
        
        if board.is_game_over(claim_draw=True):
            break
        
        # Black's turn
        if not simple_plays_white:
            move = simple_engine.get_best_move(board)
        else:
            result = stockfish_engine.play(board, chess.engine.Limit(time=0.5))
            move = result.move
        
        board.push(move)
    
    return board.result()


def play_match(simple_depth=DEFAULT_SIMPLE_ENGINE_DEPTH, stockfish_elo=DEFAULT_STOCKFISH_ELO, num_games=DEFAULT_NUM_GAMES):
    """Play a match of multiple games between SimpleEngine and Stockfish"""
    
    print(f"SimpleEngine (depth {simple_depth}) vs Stockfish (Elo {stockfish_elo}) - {num_games} games\n")
    
    simple_engine = SimpleEngine(depth=simple_depth)
    
    # Initialize Stockfish
    stockfish_path = r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe"
    stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    
    stockfish.configure({
        "UCI_LimitStrength": True,
        "UCI_Elo": stockfish_elo,
        "Threads": 4,
        "Hash": 512
    })
    
    # Track results
    simple_wins = 0
    stockfish_wins = 0
    draws = 0
    
    # Play games
    for game_num in range(1, num_games + 1):
        simple_plays_white = (game_num % 2 == 1)
        result = play_game(simple_engine, stockfish, simple_plays_white)
        
        # Update statistics
        if result == "1-0":
            if simple_plays_white:
                simple_wins += 1
            else:
                stockfish_wins += 1
        elif result == "0-1":
            if simple_plays_white:
                stockfish_wins += 1
            else:
                simple_wins += 1
        else:
            draws += 1
        
        score = simple_wins + draws * 0.5
        print(f"Game {game_num}: {result}  |  SimpleEngine: {simple_wins}W {draws}D {stockfish_wins}L  Score: {score}/{game_num}")
    
    stockfish.quit()
    
    # Print summary
    print(f"\nSimpleEngine: {simple_wins}W {draws}D {stockfish_wins}L (Score: {score}/{num_games})")
    print(f"Win rate: {simple_wins/num_games*100:.1f}%\n")


if __name__ == "__main__":
    play_match(
        simple_depth=DEFAULT_SIMPLE_ENGINE_DEPTH,
        stockfish_elo=DEFAULT_STOCKFISH_ELO,
        num_games=DEFAULT_NUM_GAMES
    )
