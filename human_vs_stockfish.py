import chess
import chess.pgn
import chess.engine

def display_board(board):
    """Display the chess board in a nice format"""
    print("\n" + "=" * 40)
    print(board)
    print("=" * 40)
    print(f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
    print(f"Legal moves: {', '.join([move.uci() for move in list(board.legal_moves)[:10]])}", end="")
    if len(list(board.legal_moves)) > 10:
        print(f" ... ({len(list(board.legal_moves))} total)")
    else:
        print()
    print()

def get_human_move(board):
    """Get a valid move from the human player"""
    while True:
        try:
            move_input = input("Enter your move (e.g., 'e2e4' or 'e4'): ").strip()
            
            # Try to parse the move
            try:
                # Try UCI format first (e.g., "e2e4")
                move = chess.Move.from_uci(move_input)
            except:
                # Try SAN format (e.g., "e4", "Nf3")
                move = board.parse_san(move_input)
            
            # Check if the move is legal
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move! Please try again.")
        except KeyboardInterrupt:
            print("\nGame interrupted by user.")
            return None
        except:
            print("Invalid move format! Use UCI (e.g., 'e2e4') or SAN (e.g., 'e4', 'Nf3').")

# Initialize board and engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\lorand\Programs\stockfish\stockfish-windows-x86-64-avx2.exe")
engine.configure({"Threads": 8, "Hash": 1024})

print("Welcome to Human vs Stockfish Chess!")
print("You are playing as White.")
print("Enter moves in UCI format (e.g., 'e2e4') or standard notation (e.g., 'e4').")
print()

move_number = 1

try:
    while not board.is_game_over(claim_draw=True):
        # White (Human) makes a move
        display_board(board)
        print(f"Move {move_number} - Your turn (White)")
        human_move = get_human_move(board)
        
        if human_move is None:  # User interrupted the game
            break
        
        san_notation = board.san(human_move)
        board.push(human_move)
        print(f"You played: {human_move.uci()} ({san_notation})")
        
        if board.is_game_over(claim_draw=True):
            break
        
        # Black (Stockfish) makes a move
        print(f"\nMove {move_number} - Stockfish's turn (Black)...")
        engine_result = engine.play(board, chess.engine.Limit(time=1.0))
        san_notation = board.san(engine_result.move)
        board.push(engine_result.move)
        print(f"Stockfish played: {engine_result.move.uci()} ({san_notation})")
        
        move_number += 1

    # Display final board state
    display_board(board)
    
    # Display game result
    print("\nGame Over!")
    result = board.result()
    print(f"Result: {result}")
    
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            print("Checkmate! Black (Stockfish) wins!")
        else:
            print("Checkmate! White (You) win!")
    elif board.is_stalemate():
        print("Stalemate!")
    elif board.is_insufficient_material():
        print("Draw by insufficient material!")
    elif board.can_claim_draw():
        print("Draw can be claimed!")
    
    # Save game to PGN
    game = chess.pgn.Game.from_board(board)
    game.headers["Event"] = "Human vs Stockfish"
    game.headers["White"] = "Human"
    game.headers["Black"] = "Stockfish"
    game.headers["Result"] = result
    
    print("\nGame in PGN format:")
    print(game)

finally:
    engine.quit()
    print("\nThanks for playing!")
