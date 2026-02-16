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

        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        if maximizing_player:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                #if beta <= alpha:
                #    break  # Beta cut-off

            return max_eval

        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                #if beta <= alpha:
                #    break  # Alpha cut-off

            return min_eval

    # ==========================
    #  Find Best Move
    # ==========================
    def get_best_move(self, board):

        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf

        for move in board.legal_moves:
            board.push(move)
            board_value = self.minimax(
                board,
                self.depth - 1,
                -math.inf,
                math.inf,
                board.turn == chess.BLACK
            )
            board.pop()

            if board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        return best_move
