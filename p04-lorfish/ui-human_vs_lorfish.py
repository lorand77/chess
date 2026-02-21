import chess
import chess.pgn
import os
import pygame
import pygame.freetype
import sys
from lorfish import LorFish

# Initialize pygame
pygame.init()
pygame.freetype.init()

# Constants
ENGINE_DEPTH = 2
#
SQUARE_SIZE = 80
PIECE_SCALE = 0.75
BOARD_SIZE = 8 * SQUARE_SIZE
INFO_WIDTH = 300
WINDOW_WIDTH = BOARD_SIZE + INFO_WIDTH
WINDOW_HEIGHT = BOARD_SIZE
FPS = 60

# Colors
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
SELECTED = (246, 246, 130)
CHECK_COLOR = (235, 97, 80)  # Red background for king in check
BACKGROUND = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
PIECE_NAMES = {
    chess.PAWN: "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK: "rook",
    chess.QUEEN: "queen",
    chess.KING: "king",
}


class ChessGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Human vs LorFish - Chess")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        #self.board = chess.Board("7k/7p/6Pp/8/8/7P/7P/7K b - - 0 1")
        #self.board = chess.Board("rnb1k3/ppp5/8/3N4/7b/2p5/6P1/6RK b - - 0 8")
        #self.board = chess.Board("6k1/6q1/6q1/8/8/8/8/7K w - - 24 13")
        #self.board = chess.Board("r1b1k1nr/pp3ppp/1q2p3/3pP3/1b1N4/N7/PP1B1PPP/R2QKB1R b KQkq - 0 9")
        #self.board = chess.Board("7k/2PP4/8/8/8/8/8/2K5 w - - 0 1")
        self.engine = LorFish(depth=ENGINE_DEPTH)

        self.font_text = pygame.freetype.SysFont("Arial", 24)
        self.font_small = pygame.freetype.SysFont("Arial", 18)

        self.piece_images = self.load_piece_images()

        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        self.game_over = False
        self.move_history = []
        self.thinking = False
        self.promotion_pending = None  # (from_square, to_square) when waiting for promotion choice
        self.engine_should_move = False  # Flag to trigger engine move on next frame

    def load_piece_images(self):
        images = {}
        for color in [chess.WHITE, chess.BLACK]:
            color_prefix = "w" if color == chess.WHITE else "b"
            for piece_type, name in PIECE_NAMES.items():
                filename = f"{color_prefix}_{name}_1x_ns.png"
                path = os.path.join(ASSET_DIR, filename)
                try:
                    image = pygame.image.load(path).convert_alpha()
                    target_size = int(SQUARE_SIZE * PIECE_SCALE)
                    target_width = target_size
                    if piece_type == chess.PAWN:
                        target_width = int(target_size * 0.8)
                    image = pygame.transform.smoothscale(image, (target_width, target_size))
                    images[(color, piece_type)] = image
                except pygame.error:
                    images[(color, piece_type)] = None
        return images

    def square_from_mouse(self, pos):
        """Convert mouse position to chess square"""
        x, y = pos
        if x >= BOARD_SIZE or y >= BOARD_SIZE or x < 0 or y < 0:
            return None
        file = x // SQUARE_SIZE
        rank = 7 - (y // SQUARE_SIZE)
        return chess.square(file, rank)

    def square_to_pixel(self, square):
        """Convert chess square to pixel coordinates"""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        x = file * SQUARE_SIZE
        y = (7 - rank) * SQUARE_SIZE
        return x, y

    def draw_board(self):
        """Draw the chess board"""
        for rank in range(8):
            for file in range(8):
                x = file * SQUARE_SIZE
                y = rank * SQUARE_SIZE
                color = WHITE if (rank + file) % 2 == 0 else BLACK

                square = chess.square(file, 7 - rank)

                # Highlight last move
                if self.last_move and square in [self.last_move.from_square, self.last_move.to_square]:
                    color = HIGHLIGHT

                # Highlight selected square
                if self.selected_square == square:
                    color = SELECTED
                
                # Highlight king in check with red background
                piece = self.board.piece_at(square)
                if self.board.is_check() and piece and piece.piece_type == chess.KING and piece.color == self.board.turn:
                    color = CHECK_COLOR

                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Draw red pulsing border around king in check
                if self.board.is_check() and piece and piece.piece_type == chess.KING and piece.color == self.board.turn:
                    # Thick red border
                    pygame.draw.rect(self.screen, (220, 50, 50), (x, y, SQUARE_SIZE, SQUARE_SIZE), 5)
                    # Inner lighter border for glow effect
                    pygame.draw.rect(self.screen, (255, 150, 150), (x + 5, y + 5, SQUARE_SIZE - 10, SQUARE_SIZE - 10), 2)

        # Draw coordinates
        for i in range(8):
            # Files (a-h)
            color = BLACK if i % 2 == 1 else WHITE
            label, _ = self.font_small.render(chr(ord('a') + i), color)
            self.screen.blit(label, (i * SQUARE_SIZE + 5, BOARD_SIZE - 20))

            # Ranks (1-8)
            color = WHITE if i % 2 == 0 else BLACK
            label, _ = self.font_small.render(str(i + 1), color)
            self.screen.blit(label, (5, (7 - i) * SQUARE_SIZE + 5))

    def draw_legal_move_hints(self):
        """Draw circles on legal move destinations"""
        if self.selected_square is not None:
            for move in self.legal_moves:
                if move.from_square == self.selected_square:
                    x, y = self.square_to_pixel(move.to_square)
                    center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)

                    # Draw a circle for legal moves
                    if self.board.piece_at(move.to_square):
                        # Capture move - draw ring
                        pygame.draw.circle(self.screen, (200, 50, 50), center, 30, 5)
                    else:
                        # Normal move - draw dot
                        pygame.draw.circle(self.screen, (100, 100, 100), center, 12)

    def draw_pieces(self):
        """Draw the chess pieces"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                x, y = self.square_to_pixel(square)
                image = self.piece_images.get((piece.color, piece.piece_type))
                if image is not None:
                    offset_x = (SQUARE_SIZE - image.get_width()) // 2
                    offset_y = (SQUARE_SIZE - image.get_height()) // 2
                    self.screen.blit(image, (x + offset_x, y + offset_y))
                else:
                    # Fallback circle if image is missing
                    center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                    color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                    pygame.draw.circle(self.screen, color, center, 25)

    def draw_promotion_dialog(self):
        """Draw promotion piece selection dialog"""
        if self.promotion_pending is None:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 320
        dialog_height = 120
        dialog_x = (BOARD_SIZE - dialog_width) // 2
        dialog_y = (BOARD_SIZE - dialog_height) // 2
        
        pygame.draw.rect(self.screen, (60, 60, 60), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # Title
        title, _ = self.font_text.render("Choose Promotion:", TEXT_COLOR)
        self.screen.blit(title, (dialog_x + 20, dialog_y + 15))
        
        # Piece options
        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        piece_y = dialog_y + 55
        piece_spacing = 70
        start_x = dialog_x + 20
        
        for i, piece_type in enumerate(pieces):
            piece_x = start_x + i * piece_spacing
            color = chess.WHITE  # Human is always white
            
            # Draw piece image
            image = self.piece_images.get((color, piece_type))
            if image:
                # Scale down for dialog
                small_image = pygame.transform.smoothscale(image, (50, 50))
                self.screen.blit(small_image, (piece_x + 5, piece_y))
            
            # Draw selection box
            pygame.draw.rect(self.screen, (150, 150, 150), (piece_x, piece_y, 60, 60), 2)

    def draw_info_panel(self):
        """Draw the information panel"""
        panel_x = BOARD_SIZE
        pygame.draw.rect(self.screen, BACKGROUND, (panel_x, 0, INFO_WIDTH, WINDOW_HEIGHT))

        y_offset = 20

        # Title
        title, _ = self.font_text.render("Chess Game", TEXT_COLOR)
        self.screen.blit(title, (panel_x + 20, y_offset))
        y_offset += 50

        # Players
        white_text, _ = self.font_small.render("White: Human", TEXT_COLOR)
        self.screen.blit(white_text, (panel_x + 20, y_offset))
        y_offset += 30

        black_text, _ = self.font_small.render("Black: LorFish", TEXT_COLOR)
        self.screen.blit(black_text, (panel_x + 20, y_offset))
        y_offset += 50

        # Current turn
        if not self.game_over:
            if self.thinking:
                turn_text = "Engine thinking..."
                color = (255, 200, 100)
            else:
                turn = "White" if self.board.turn == chess.WHITE else "Black"
                turn_text = f"Turn: {turn}"
                color = TEXT_COLOR
            text, _ = self.font_small.render(turn_text, color)
            self.screen.blit(text, (panel_x + 20, y_offset))
        y_offset += 50

        # Game status
        if self.game_over:
            result = self.board.result()
            status_text = f"Game Over: {result}"
            text, _ = self.font_small.render(status_text, (255, 100, 100))
            self.screen.blit(text, (panel_x + 20, y_offset))
            y_offset += 30

            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                text, _ = self.font_small.render(f"{winner} wins!", (100, 255, 100))
                self.screen.blit(text, (panel_x + 20, y_offset))
            elif self.board.is_stalemate():
                text, _ = self.font_small.render("Stalemate!", TEXT_COLOR)
                self.screen.blit(text, (panel_x + 20, y_offset))
        elif self.board.is_check():
            text, _ = self.font_small.render("Check!", (255, 100, 100))
            self.screen.blit(text, (panel_x + 20, y_offset))

        y_offset += 50

        # Move history (last 10 moves)
        history_title, _ = self.font_small.render("Move History:", TEXT_COLOR)
        self.screen.blit(history_title, (panel_x + 20, y_offset))
        y_offset += 30

        start_idx = max(0, len(self.move_history) - 10)
        for i, move_str in enumerate(self.move_history[start_idx:]):
            move_text, _ = self.font_small.render(move_str, (200, 200, 200))
            self.screen.blit(move_text, (panel_x + 30, y_offset + i * 25))
        
        # Controls hint
        y_offset += 300
        hint_text, _ = self.font_small.render("Press R to undo", (150, 150, 150))
        self.screen.blit(hint_text, (panel_x + 20, y_offset))

    def handle_promotion_click(self, pos):
        """Handle click on promotion dialog"""
        if self.promotion_pending is None:
            return False
        
        dialog_width = 320
        dialog_height = 120
        dialog_x = (BOARD_SIZE - dialog_width) // 2
        dialog_y = (BOARD_SIZE - dialog_height) // 2
        
        piece_y = dialog_y + 55
        piece_spacing = 70
        start_x = dialog_x + 20
        
        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        
        for i, piece_type in enumerate(pieces):
            piece_x = start_x + i * piece_spacing
            rect = pygame.Rect(piece_x, piece_y, 60, 60)
            
            if rect.collidepoint(pos):
                # Make the promotion move
                from_square, to_square = self.promotion_pending
                move = chess.Move(from_square, to_square, promotion=piece_type)
                
                san = self.board.san(move)
                move_num = self.board.fullmove_number
                self.board.push(move)
                self.last_move = move
                
                # Format move history (white just moved)
                self.move_history.append(f"{move_num}. {san}")
                
                # Check if game is over
                if self.board.is_game_over():
                    self.game_over = True
                else:
                    # Trigger engine move on next frame
                    self.engine_should_move = True
                
                self.promotion_pending = None
                self.selected_square = None
                self.legal_moves = []
                return True
        
        return False

    def handle_square_click(self, square):
        """Handle a square being clicked"""
        if self.game_over or self.board.turn != chess.WHITE or self.thinking:
            return

        # If no square is selected, select this square if it has a white piece
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
        else:
            # Try to make a move
            move = None
            for legal_move in self.legal_moves:
                if legal_move.to_square == square:
                    move = legal_move
                    break

            if move:
                # Check if this is a pawn promotion
                piece = self.board.piece_at(self.selected_square)
                if piece and piece.piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                    # Show promotion dialog
                    self.promotion_pending = (self.selected_square, square)
                    return
                
                # Make the move
                san = self.board.san(move)
                move_num = self.board.fullmove_number
                self.board.push(move)
                self.last_move = move
                
                # Format move history
                if self.last_move and self.board.turn == chess.BLACK:
                    # White just moved
                    self.move_history.append(f"{move_num}. {san}")
                else:
                    # Black just moved
                    self.move_history.append(f"{move_num}... {san}")
                
                self.selected_square = None
                self.legal_moves = []

                # Check if game is over
                if self.board.is_game_over():
                    self.game_over = True
                else:
                    # Trigger engine move on next frame after UI updates
                    self.engine_should_move = True
            else:
                # Deselect or select a different piece
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.WHITE:
                    self.selected_square = square
                    self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
                else:
                    self.selected_square = None
                    self.legal_moves = []

    def make_engine_move(self):
        """Make a move for the engine"""
        if self.game_over or self.board.turn != chess.BLACK:
            return

        self.thinking = True
        pygame.display.flip()

        # Get engine move
        engine_move = self.engine.get_best_move(self.board)

        if engine_move:
            san = self.board.san(engine_move)
            move_num = self.board.fullmove_number
            self.board.push(engine_move)
            self.last_move = engine_move
            self.move_history.append(f"{move_num}... {san}")

            # Check if game is over
            if self.board.is_game_over():
                self.game_over = True

        self.thinking = False

    def undo_move(self):
        """Undo the last two moves (engine and human)"""
        # Clear promotion dialog and pending engine move regardless
        self.promotion_pending = None
        self.engine_should_move = False

        if self.game_over:
            self.game_over = False
        
        if self.board.turn == chess.WHITE:
            # It's white's turn, so we need to undo black's last move and white's previous move
            if len(self.board.move_stack) >= 2:
                self.board.pop()  # Undo black's move
                self.board.pop()  # Undo white's move
                # Remove last 2 entries from move history
                if len(self.move_history) >= 2:
                    self.move_history = self.move_history[:-2]
                self.last_move = self.board.peek() if self.board.move_stack else None
                self.selected_square = None
                self.legal_moves = []
        else:
            # It's black's turn (shouldn't happen in normal play, but handle it)
            if len(self.board.move_stack) >= 1:
                self.board.pop()  # Undo white's move
                if len(self.move_history) >= 1:
                    self.move_history = self.move_history[:-1]
                self.last_move = self.board.peek() if self.board.move_stack else None
                self.selected_square = None
                self.legal_moves = []

    def run(self):
        """Main game loop"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check if clicking on promotion dialog
                        if self.promotion_pending and self.handle_promotion_click(event.pos):
                            continue
                        
                        square = self.square_from_mouse(event.pos)
                        if square is not None:
                            self.handle_square_click(square)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # R key for undo
                        self.undo_move()

            # Draw everything first
            self.screen.fill(BACKGROUND)
            self.draw_board()
            self.draw_legal_move_hints()
            self.draw_pieces()
            self.draw_info_panel()
            self.draw_promotion_dialog()

            pygame.display.flip()
            
            # Make engine move AFTER drawing white's move
            if self.engine_should_move and not self.game_over and not self.thinking and not self.promotion_pending:
                self.engine_should_move = False
                self.make_engine_move()
            
            self.clock.tick(FPS)

        # Save game to PGN
        game = chess.pgn.Game.from_board(self.board)
        game.headers["Event"] = "Human vs LorFish"
        game.headers["White"] = "Human"
        game.headers["Black"] = "LorFish"
        game.headers["Result"] = self.board.result()

        print("\nGame in PGN format:")
        print(game)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ChessGUI()
    game.run()
