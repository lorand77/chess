import chess
import math

class SimpleEngine:
    def __init__(self, depth=3):
        self.depth = depth

        # Basic piece values (centipawns)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0  # King value handled separately
        }

        # Simple piece-square table for pawns (white perspective)
        self.pawn_table = [
             0,  5,  5, -5, -5,  5,  5,  0,
             0, 10, 10,  0,  0, 10, 10,  0,
             0, 10, 20, 20, 20, 20, 10,  0,
             5, 15, 15, 25, 25, 15, 15,  5,
            10, 20, 20, 30, 30, 20, 20, 10,
            20, 30, 30, 40, 40, 30, 30, 20,
            50, 50, 50, 50, 50, 50, 50, 50,
             0,  0,  0,  0,  0,  0,  0,  0
        ]

    # ==========================
    #  Evaluation Function
    # ==========================
    def evaluate(self, board):
        """
        Evaluate position from White's perspective.
        Positive score = good for White
        Negative score = good for Black
        """

        if board.is_checkmate():
            if board.turn:
                return -99999  # White to move and checkmated
            else:
                return 99999   # Black to move and checkmated

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0

        # Material + piece-square tables
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue

            value = self.piece_values[piece.piece_type]

            # Add pawn positional bonus
            if piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    value += self.pawn_table[square]
                else:
                    value += self.pawn_table[chess.square_mirror(square)]

            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

        return score

    # ==========================
    #  Minimax + Alpha-Beta
    # ==========================
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        self.nodes_visited += 1

        if depth == 0 or board.is_game_over():
            eval_score = self.evaluate(board)
            #print(f"  {'  ' * (self.depth - depth)}Leaf node at depth {depth}: eval = {eval_score}")
            return eval_score

        if maximizing_player:
            max_eval = -math.inf
            print(f"  {'  ' * (self.depth - depth)}MAX at depth {depth}, exploring {board.legal_moves.count()} moves")
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                print(f"  {'  ' * (self.depth - depth)}MAX: move {move} -> eval {eval}")

                max_eval = max(max_eval, eval)
                #alpha = max(alpha, eval)
                #if beta <= alpha:
                #    break  # Beta cut-off
            
            print(f"  {'  ' * (self.depth - depth)}MAX returning: {max_eval}")
            return max_eval

        else:
            min_eval = math.inf
            print(f"  {'  ' * (self.depth - depth)}MIN at depth {depth}, exploring {board.legal_moves.count()} moves")
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                print(f"  {'  ' * (self.depth - depth)}MIN: move {move} -> eval {eval}")

                min_eval = min(min_eval, eval)
                #beta = min(beta, eval)
                #if beta <= alpha:
                #    break  # Alpha cut-off
            
            print(f"  {'  ' * (self.depth - depth)}MIN returning: {min_eval}")
            return min_eval

    # ==========================
    #  Find Best Move
    # ==========================
    def get_best_move(self, board):
        self.nodes_visited = 0

        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf
        
        player = "WHITE" if board.turn == chess.WHITE else "BLACK"
        print(f"\n{'='*60}")
        print(f"Finding best move for {player} at depth {self.depth}")
        print(f"{'='*60}")

        for move in board.legal_moves:
            print(f"\nEvaluating root move: {move}")
            board.push(move)
            board_value = self.minimax(
                board,
                self.depth - 1,
                -math.inf,
                math.inf,
                board.turn == chess.WHITE
            )
            board.pop()
            print(f"Root move {move} has value: {board_value}")

            if board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                    print(f"  -> New best move for WHITE: {best_move} (value: {best_value})")
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
                    print(f"  -> New best move for BLACK: {best_move} (value: {best_value})")

        print(f"\n{'='*60}")
        print(f"FINAL BEST MOVE: {best_move} with value {best_value}")
        print(f"Total nodes visited: {self.nodes_visited}")
        print(f"{'='*60}\n")
        return best_move
