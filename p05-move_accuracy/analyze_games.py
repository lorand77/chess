import chess.pgn
import os

PLAYER = "lorand111"
PGN_DIR = "pgn_files"

games = []

for filename in sorted(os.listdir(PGN_DIR)):
    if not filename.endswith(".pgn"):
        continue
    filepath = os.path.join(PGN_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")

            if PLAYER.lower() == white.lower():
                player_color = chess.WHITE
                color_name = "white"
            elif PLAYER.lower() == black.lower():
                player_color = chess.BLACK
                color_name = "black"
            else:
                # Game doesn't involve the player, skip
                continue

            moves = list(game.mainline_moves())
            games.append({
                "game": game,
                "color": player_color,
                "color_name": color_name,
                "moves": moves,
            })

print(f"Loaded {len(games)} games for {PLAYER}")

for i, g in enumerate(games):  
    game = g["game"]
    date = game.headers.get("Date", "?")
    result = game.headers.get("Result", "?")
    opponent = game.headers.get("Black" if g["color"] == chess.WHITE else "White", "?")

    if result == "1-0":
        winner = "White won" + (" (you)" if g["color"] == chess.WHITE else f" ({opponent})")
    elif result == "0-1":
        winner = "Black won" + (" (you)" if g["color"] == chess.BLACK else f" ({opponent})")
    elif result == "1/2-1/2":
        winner = "Draw"
    else:
        winner = "Unknown"

    print(f"\nGame {i+1}: {date}  Playing as {g['color_name']}  vs {opponent}  Result: {result}  -> {winner}")
    board = game.board()
    for move_num, move in enumerate(g["moves"], start=1):
        san = board.san(move)
        board.push(move)

