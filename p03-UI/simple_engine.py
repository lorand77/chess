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
            chess.KING: 0  # King value handled separately
        }

        # Piece-square tables (white perspective)
        # from https://github.com/thomasahle/sunfish
        self.pawn_table = (
             0,   0,   0,   0,   0,   0,   0,   0,
           -31,   8,  -7, -37, -36, -14,   3, -31,
           -22,   9,   5, -11, -10,  -2,   3, -19,
           -26,   3,  10,   9,   6,   1,   0, -23,
           -17,  16,  -2,  15,  14,   0,  15, -13,
             7,  29,  21,  44,  40,  31,  44,   7,
            78,  83,  86,  73, 102,  82,  85,  90,
             0,   0,   0,   0,   0,   0,   0,   0)

        self.knight_table = (
           -74, -23, -26, -24, -19, -35, -22, -69,
           -23, -15,   2,   0,   2,   0, -23, -20,
           -18,  10,  13,  22,  18,  15,  11, -14,
            -1,   5,  31,  21,  22,  35,   2,   0,
            24,  24,  45,  37,  33,  41,  25,  17,
            10,  67,   1,  74,  73,  27,  62,  -2,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
           -66, -53, -75, -75, -10, -55, -58, -70)

        self.bishop_table = (
            -7,   2, -15, -12, -14, -15, -10, -10,
            19,  20,  11,   6,   7,   6,  20,  16,
            14,  25,  24,  15,   8,  25,  20,  15,
            13,  10,  17,  23,  17,  16,   0,   7,
            25,  17,  20,  34,  26,  25,  15,  10,
            -9,  39, -32,  41,  52, -10,  28, -14,
           -11,  20,  35, -42, -39,  31,   2, -22,
           -59, -78, -82, -76, -23,-107, -37, -50)

        self.rook_table = (
           -30, -24, -18,   5,  -2, -18, -31, -32,
           -53, -38, -31, -26, -29, -43, -44, -53,
           -42, -28, -42, -25, -25, -35, -26, -46,
           -28, -35, -16, -21, -13, -29, -46, -30,
             0,   5,  16,  13,  18,  -4,  -9,  -6,
            19,  35,  28,  33,  45,  27,  25,  15,
            55,  29,  56,  67,  55,  62,  34,  60,
            35,  29,  33,   4,  37,  33,  56,  50)

        self.queen_table = (
           -39, -30, -31, -13, -31, -36, -34, -42,
           -36, -18,   0, -19, -15, -15, -21, -38,
           -30,  -6, -13, -11, -16, -11, -16, -27,
           -14, -15,  -2,  -5,  -1, -10, -20, -22,
             1, -16,  22,  17,  25,  20, -13,  -6,
            -2,  43,  32,  60,  72,  63,  43,   2,
            14,  32,  60, -10,  20,  76,  57,  24,
             6,   1,  -8,-104,  69,  24,  88,  26)

        self.king_table = (
            17,  30,  -3, -14,   6,  -1,  40,  18,
            -4,   3, -14, -50, -57, -18,  13,   4,
           -47, -42, -43, -79, -64, -32, -29, -32,
           -55, -43, -52, -28, -51, -47,  -8, -50,
           -55,  50,  11,  -4, -19,  13,   0, -49,
           -62,  12, -57,  44, -67,  28,  37, -31,
           -32,  10,  55,  56,  56,  55,  10,   3,
             4,  54,  47, -99, -99,  60,  83, -62)

        # Map piece types to their tables
        self.piece_square_tables = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: self.knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_table
        }

    # ==========================
    #  Move Ordering
    # ==========================
    def order_moves(self, board, moves):
        """
        Order moves to improve alpha-beta pruning.
        Prioritize: captures (MVV-LVA), checks, then other moves.
        """
        def move_score(move):
            score = 0
            
            # Prioritize captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    # Higher score for capturing valuable pieces with less valuable pieces
                    score += self.piece_values.get(victim.piece_type, 0) * 10
                    score -= self.piece_values.get(attacker.piece_type, 0) // 100
            
            # Prioritize checks
            board.push(move)
            if board.is_check():
                score += 5000
            board.pop()
            
            # Prioritize pawn promotions
            if move.promotion:
                score += 8000
            
            return score
        
        return sorted(moves, key=move_score, reverse=True)

    # ==========================
    #  Evaluation Function
    # ==========================
    def evaluate(self, board, depth=0):
        """
        Evaluate position from White's perspective.
        Positive score = good for White
        Negative score = good for Black
        """

        if board.is_checkmate():
            if board.turn:
                return -99999 - depth  # White to move and checkmated (prefer slower mate)
            else:
                return 99999 + depth   # Black to move and checkmated (prefer faster mate)

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0

        # Material + piece-square tables
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue

            value = self.piece_values[piece.piece_type]

            # Add piece-square table bonus
            pst = self.piece_square_tables[piece.piece_type]
            if piece.color == chess.WHITE:
                value += pst[square]
            else:
                value += pst[chess.square_mirror(square)]

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
            eval_score = self.evaluate(board, depth)
            return eval_score

        # Order moves for better pruning
        moves = self.order_moves(board, list(board.legal_moves))

        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                move_eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                max_eval = max(max_eval, move_eval)
                alpha = max(alpha, move_eval)
                if beta <= alpha:
                    break  # Beta cut-off
            
            return max_eval

        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                move_eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                min_eval = min(min_eval, move_eval)
                beta = min(beta, move_eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            
            return min_eval

    # ==========================
    #  Find Best Move
    # ==========================
    def get_best_move(self, board):
        start_time = time.time()
        self.nodes_visited = 0
        best_move = None
        alpha = -math.inf
        beta = math.inf

        # Order moves for better pruning
        moves = self.order_moves(board, list(board.legal_moves))

        if board.turn == chess.WHITE:
            best_value = -math.inf
            for move in moves:
                board.push(move)
                board_value = self.minimax(
                    board,
                    self.depth - 1,
                    alpha,
                    beta,
                    False
                )
                board.pop()

                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                alpha = max(alpha, best_value)
        else:
            best_value = math.inf
            for move in moves:
                board.push(move)
                board_value = self.minimax(
                    board,
                    self.depth - 1,
                    alpha,
                    beta,
                    True
                )
                board.pop()

                if board_value < best_value:
                    best_value = board_value
                    best_move = move
                beta = min(beta, best_value)

        elapsed_time = time.time() - start_time
        print(f"Nodes visited: {self.nodes_visited}, Time: {elapsed_time:.3f}s")
        return best_move
