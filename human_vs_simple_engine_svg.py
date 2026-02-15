import chess
import chess.pgn
import chess.svg
import webbrowser
import os
import tempfile
from simple_engine import SimpleEngine

def display_board_svg(board, last_move=None):
    """Display the chess board as an SVG and open in browser"""
    # Generate SVG with highlighting of last move
    if last_move:
        svg_data = chess.svg.board(
            board, 
            lastmove=last_move,
            size=400
        )
    else:
        svg_data = chess.svg.board(board, size=400)
    
    # Save to a temporary HTML file
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chess Board</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 20px;
                background-color: #f0f0f0;
            }}
            .board-container {{
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .info {{
                margin-top: 20px;
                text-align: center;
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 400px;
            }}
            h1 {{
                color: #333;
                margin: 0 0 10px 0;
            }}
            .turn {{
                font-size: 18px;
                font-weight: bold;
                color: #0066cc;
            }}
        </style>
    </head>
    <body>
        <div class="board-container">
            {svg_data}
        </div>
        <div class="info">
            <h1>{'White' if board.turn == chess.WHITE else 'Black'} to move</h1>
            <p class="turn">Move count: {board.fullmove_number}</p>
        </div>
    </body>
    </html>
    """
    
    # Write to temp file and open
    temp_file = os.path.join(tempfile.gettempdir(), "chess_board.html")
    with open(temp_file, "w") as f:
        f.write(html_content)
    
    # Open in default browser
    webbrowser.open('file://' + temp_file)
    print(f"Board displayed in browser (file: {temp_file})")

def display_board_text(board):
    """Display the chess board in text format"""
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
            
            if move_input.lower() == 'quit':
                return None
            
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
engine = SimpleEngine(depth=4)

print("Welcome to Human vs Simple Engine Chess!")
print("You are playing as White.")
print("Enter moves in UCI format (e.g., 'e2e4') or standard notation (e.g., 'e4').")
print("Type 'quit' to exit the game.")
print()

move_number = 1
last_move = None

try:
    while not board.is_game_over(claim_draw=True):
        # White (Human) makes a move
        display_board_svg(board, last_move)
        display_board_text(board)
        print(f"Move {move_number} - Your turn (White)")
        human_move = get_human_move(board)
        
        if human_move is None:  # User interrupted the game
            break
        
        san_notation = board.san(human_move)
        board.push(human_move)
        print(f"You played: {human_move.uci()} ({san_notation})")
        last_move = human_move
        
        if board.is_game_over(claim_draw=True):
            break
        
        # Black (Simple Engine) makes a move
        print(f"\nMove {move_number} - Simple Engine's turn (Black)...")
        engine_move = engine.get_best_move(board)
        san_notation = board.san(engine_move)
        board.push(engine_move)
        print(f"Simple Engine played: {engine_move.uci()} ({san_notation})")
        last_move = engine_move
        
        move_number += 1

    # Display final board state
    display_board_svg(board, last_move)
    display_board_text(board)
    
    # Display game result
    print("\nGame Over!")
    result = board.result()
    print(f"Result: {result}")
    
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            print("Checkmate! Black (Simple Engine) wins!")
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
    game.headers["Event"] = "Human vs Simple Engine"
    game.headers["White"] = "Human"
    game.headers["Black"] = "Simple Engine"
    game.headers["Result"] = result
    
    print("\nGame in PGN format:")
    print(game)

except Exception as e:
    print(f"\nError occurred: {e}")

finally:
    print("\nThanks for playing!")
