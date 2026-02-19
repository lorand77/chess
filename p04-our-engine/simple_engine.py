import chess
import math
import time

class SimpleEngine:
    def __init__(self, depth):
        self.depth = depth

        # Basic piece values (centipawns)
        # from https://github.com/thomasahle/sunfish
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 280,
            chess.BISHOP: 320,
            chess.ROOK: 479,
            chess.QUEEN: 929,
            chess.KING: 0
        }

        # Piece-square tables (white perspective)
        # from https://github.com/thomasahle/sunfish
        self.pst = {
            chess.PAWN: (
                 0,   0,   0,   0,   0,   0,   0,   0,
               -31,   8,  -7, -37, -36, -14,   3, -31,
               -22,   9,   5, -11, -10,  -2,   3, -19,
               -26,   3,  10,   9,   6,   1,   0, -23,
               -17,  16,  -2,  15,  14,   0,  15, -13,
                 7,  29,  21,  44,  40,  31,  44,   7,
                78,  83,  86,  73, 102,  82,  85,  90,
                 0,   0,   0,   0,   0,   0,   0,   0),
            chess.KNIGHT: (
               -74, -23, -26, -24, -19, -35, -22, -69,
               -23, -15,   2,   0,   2,   0, -23, -20,
               -18,  10,  13,  22,  18,  15,  11, -14,
                -1,   5,  31,  21,  22,  35,   2,   0,
                24,  24,  45,  37,  33,  41,  25,  17,
                10,  67,   1,  74,  73,  27,  62,  -2,
                -3,  -6, 100, -36,   4,  62,  -4, -14,
               -66, -53, -75, -75, -10, -55, -58, -70),
            chess.BISHOP: (
                -7,   2, -15, -12, -14, -15, -10, -10,
                19,  20,  11,   6,   7,   6,  20,  16,
                14,  25,  24,  15,   8,  25,  20,  15,
                13,  10,  17,  23,  17,  16,   0,   7,
                25,  17,  20,  34,  26,  25,  15,  10,
                -9,  39, -32,  41,  52, -10,  28, -14,
               -11,  20,  35, -42, -39,  31,   2, -22,
               -59, -78, -82, -76, -23,-107, -37, -50),
            chess.ROOK: (
               -30, -24, -18,   5,  -2, -18, -31, -32,
               -53, -38, -31, -26, -29, -43, -44, -53,
               -42, -28, -42, -25, -25, -35, -26, -46,
               -28, -35, -16, -21, -13, -29, -46, -30,
                 0,   5,  16,  13,  18,  -4,  -9,  -6,
                19,  35,  28,  33,  45,  27,  25,  15,
                55,  29,  56,  67,  55,  62,  34,  60,
                35,  29,  33,   4,  37,  33,  56,  50),
            chess.QUEEN: (
               -39, -30, -31, -13, -31, -36, -34, -42,
               -36, -18,   0, -19, -15, -15, -21, -38,
               -30,  -6, -13, -11, -16, -11, -16, -27,
               -14, -15,  -2,  -5,  -1, -10, -20, -22,
                 1, -16,  22,  17,  25,  20, -13,  -6,
                -2,  43,  32,  60,  72,  63,  43,   2,
                14,  32,  60, -10,  20,  76,  57,  24,
                 6,   1,  -8,-104,  69,  24,  88,  26),
            chess.KING: (
                17,  30,  -3, -14,   6,  -1,  40,  18,
                -4,   3, -14, -50, -57, -18,  13,   4,
               -47, -42, -43, -79, -64, -32, -29, -32,
               -55, -43, -52, -28, -51, -47,  -8, -50,
               -55,  50,  11,  -4, -19,  13,   0, -49,
               -62,  12, -57,  44, -67,  28,  37, -31,
               -32,  10,  55,  56,  56,  55,  10,   3,
                 4,  54,  47, -99, -99,  60,  83, -62),
        }

    def order_moves(self, board, moves):
        """Order moves to improve alpha-beta pruning (MVV-LVA, checks, promotions)"""
        def move_score(move):
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score += self.piece_values.get(victim.piece_type, 0) * 10
                    score -= self.piece_values.get(attacker.piece_type, 0) // 100
            if move.promotion:
                score += 8000
            if board.gives_check(move):
                score += 5000
            return score

        return sorted(moves, key=move_score, reverse=True)

    def evaluate(self, board, depth=0):
        """Evaluate position from the current player's perspective"""
        if board.is_checkmate():
            return -99999 - depth  # current player is checkmated
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            sq = square if piece.color == chess.WHITE else chess.square_mirror(square)
            value = self.piece_values[piece.piece_type] + self.pst[piece.piece_type][sq]
            score += value if piece.color == chess.WHITE else -value

        return score if board.turn == chess.WHITE else -score

    def quiescence(self, board, alpha, beta):
        self.nodes_visited += 1

        if board.is_game_over():
            return self.evaluate(board)

        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        captures = self.order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])
        for move in captures:
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def negamax(self, board, depth, alpha, beta):
        self.nodes_visited += 1

        if board.is_game_over():
            return self.evaluate(board, depth)
        if depth == 0:
            return self.quiescence(board, alpha, beta)

        moves = self.order_moves(board, list(board.legal_moves))

        best = -math.inf
        for move in moves:
            board.push(move)
            best = max(best, -self.negamax(board, depth - 1, -beta, -alpha))
            board.pop()
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best

    def get_best_move(self, board):
        self.nodes_visited = 0
        start_time = time.time()
        best_move = None
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf

        for move in self.order_moves(board, list(board.legal_moves)):
            board.push(move)
            value = -self.negamax(board, self.depth - 1, -beta, -alpha)
            board.pop()

            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)

        elapsed = time.time() - start_time
        print(f"  nodes={self.nodes_visited}  time={elapsed:.3f}s")
        return best_move
