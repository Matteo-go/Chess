import pygame
import os
from config import BOARD_ROWS, BOARD_COLS, SQUARE_SIZE, WIDTH, HEIGHT, BOARD_OFFSET_X, BOARD_OFFSET_Y
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

pygame.init()
FONT = pygame.font.SysFont("Segoe UI", 20)
TITLE_FONT = pygame.font.SysFont("Segoe UI", 36, bold=True)

PIECE_IMAGES = {}

def load_images():
    for file in os.listdir("assets/images"):
        if file.endswith(".png"):
            name = file.replace(".png", "")
            img = pygame.image.load(os.path.join("assets/images", file))
            PIECE_IMAGES[name] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))

class Game:
    def __init__(self, game_mode="1v1", theme=((186, 202, 68), (118, 150, 86))):
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.selected_piece = None
        self.valid_moves = []
        self.turn = "white"
        self.game_over = False
        self.winner = None
        self.quit_popup = False
        self.light_color, self.dark_color = theme
        self.game_mode = game_mode
        self.back_to_menu_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        self.quit_button_rect = pygame.Rect(WIDTH - 140, 30, 110, 40)
        self.captured_white = []
        self.captured_black = []
        load_images()
        self.setup_board()

    def setup_board(self):
        for col in range(BOARD_COLS):
            self.board[1][col] = Pawn("black", col, 1)
            self.board[6][col] = Pawn("white", col, 6)

        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, cls in enumerate(order):
            self.board[0][col] = cls("black", col, 0)
            self.board[7][col] = cls("white", col, 7)

    def draw_board(self, win):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                pygame.draw.rect(win, color, (x, y, SQUARE_SIZE, SQUARE_SIZE), border_radius=6)

        # Coordonnées
        for i in range(BOARD_ROWS):
            label = FONT.render(str(8 - i), True, (30, 30, 30))
            win.blit(label, (BOARD_OFFSET_X - 20, BOARD_OFFSET_Y + i * SQUARE_SIZE + 5))

        for j in range(BOARD_COLS):
            label = FONT.render(chr(ord('a') + j), True, (30, 30, 30))
            win.blit(label, (BOARD_OFFSET_X + j * SQUARE_SIZE + SQUARE_SIZE - 20, BOARD_OFFSET_Y + BOARD_ROWS * SQUARE_SIZE + 5))

        for move in self.valid_moves:
            r, c = move
            center_x = BOARD_OFFSET_X + c * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_OFFSET_Y + r * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(win, (50, 50, 50), (center_x, center_y), 10)

    def draw_pieces(self, win):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece:
                    key = f"{piece.color}-{piece.name}"
                    x = BOARD_OFFSET_X + col * SQUARE_SIZE
                    y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                    win.blit(PIECE_IMAGES[key], (x, y))

    def draw_captured(self, win):
        x_left = BOARD_OFFSET_X - 60
        x_right = BOARD_OFFSET_X + BOARD_COLS * SQUARE_SIZE + 10
        y_start = BOARD_OFFSET_Y

        for i, piece in enumerate(self.captured_white):
            key = f"black-{piece}"
            y = y_start + (i * 30)
            win.blit(pygame.transform.scale(PIECE_IMAGES[key], (28, 28)), (x_left, y))

        for i, piece in enumerate(self.captured_black):
            key = f"white-{piece}"
            y = y_start + (i * 30)
            win.blit(pygame.transform.scale(PIECE_IMAGES[key], (28, 28)), (x_right, y))

    def draw_quit_button(self, win):
        pygame.draw.rect(win, (200, 0, 0), self.quit_button_rect, border_radius=8)
        label = FONT.render("Quitter", True, (255, 255, 255))
        win.blit(label, (
            self.quit_button_rect.centerx - label.get_width() // 2,
            self.quit_button_rect.centery - label.get_height() // 2
        ))

    def draw_quit_popup(self, win):
        popup_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 120)
        pygame.draw.rect(win, (50, 50, 50), popup_rect, border_radius=12)
        pygame.draw.rect(win, (220, 220, 220), popup_rect, 2)

        label = FONT.render("Voulez-vous abandonner ?", True, (255, 255, 255))
        win.blit(label, (popup_rect.centerx - label.get_width() // 2, popup_rect.y + 15))

        self.yes_button = pygame.Rect(popup_rect.x + 40, popup_rect.y + 70, 80, 30)
        self.no_button = pygame.Rect(popup_rect.x + 180, popup_rect.y + 70, 80, 30)

        pygame.draw.rect(win, (120, 180, 120), self.yes_button, border_radius=6)
        pygame.draw.rect(win, (180, 80, 80), self.no_button, border_radius=6)

        win.blit(FONT.render("Oui", True, (255, 255, 255)), (self.yes_button.x + 22, self.yes_button.y + 5))
        win.blit(FONT.render("Non", True, (255, 255, 255)), (self.no_button.x + 18, self.no_button.y + 5))

    def draw(self, win):
        win.fill((240, 240, 240))  # fond doux
        self.draw_board(win)
        self.draw_pieces(win)
        self.draw_captured(win)
        self.draw_quit_button(win)
        if self.quit_popup:
            self.draw_quit_popup(win)
        if self.game_over:
            self.display_winner(win)

    def display_winner(self, win):
        win.fill((0, 0, 0))
        label = TITLE_FONT.render(f"{self.winner} wins!" if self.winner else "Draw!", True, (255, 255, 255))
        win.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 80))

        pygame.draw.rect(win, (60, 60, 60), self.back_to_menu_button_rect, border_radius=10)
        btn_label = FONT.render("Retour au menu", True, (255, 255, 255))
        win.blit(btn_label, (
            self.back_to_menu_button_rect.centerx - btn_label.get_width() // 2,
            self.back_to_menu_button_rect.centery - btn_label.get_height() // 2
        ))

    def handle_click(self, pos):
        if self.quit_popup:
            if self.yes_button.collidepoint(pos):
                self.game_over = True
                self.winner = "Black" if self.turn == "white" else "White"
                self.quit_popup = False
            elif self.no_button.collidepoint(pos):
                self.quit_popup = False
            return

        if self.game_over:
            return

        if self.quit_button_rect.collidepoint(pos):
            self.quit_popup = True
            return

        col = (pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
        row = (pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE

        if 0 <= col < BOARD_COLS and 0 <= row < BOARD_ROWS:
            piece = self.board[row][col]

            if self.selected_piece:
                if (row, col) in self.valid_moves:
                    target = self.board[row][col]
                    if target:
                        if target.color == "white":
                            self.captured_black.append(target.name)
                        else:
                            self.captured_white.append(target.name)
                    self.move_piece(self.selected_piece, row, col)
                    self.handle_promotion(self.selected_piece)
                    self.turn = "black" if self.turn == "white" else "white"
                    self.check_game_end()
                self.selected_piece = None
                self.valid_moves = []
            elif piece and piece.color == self.turn:
                self.selected_piece = piece
                self.valid_moves = self.get_legal_moves(piece)

    def move_piece(self, piece, row, col):
        self.board[piece.row][piece.col] = None
        piece.row = row
        piece.col = col
        self.board[row][col] = piece

    def handle_promotion(self, piece):
        if piece.name == "pawn":
            if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == BOARD_ROWS - 1):
                self.board[piece.row][piece.col] = Queen(piece.color, piece.col, piece.row)

    def get_legal_moves(self, piece):
        all_moves = piece.get_valid_moves(self.board)
        legal_moves = []
        for move in all_moves:
            backup = self.board[move[0]][move[1]]
            orig_row, orig_col = piece.row, piece.col
            self.board[orig_row][orig_col] = None
            self.board[move[0]][move[1]] = piece
            piece.row, piece.col = move
            if not self.is_in_check(piece.color):
                legal_moves.append(move)
            self.board[orig_row][orig_col] = piece
            self.board[move[0]][move[1]] = backup
            piece.row, piece.col = orig_row, orig_col
        return legal_moves

    def is_in_check(self, color):
        king = None
        for row in self.board:
            for piece in row:
                if piece and piece.name == "king" and piece.color == color:
                    king = piece
                    break
        if not king:
            return True

        for row in self.board:
            for piece in row:
                if piece and piece.color != color:
                    if (king.row, king.col) in piece.get_valid_moves(self.board):
                        return True
        return False

    def check_game_end(self):
        for row in self.board:
            for piece in row:
                if piece and piece.color == self.turn:
                    if self.get_legal_moves(piece):
                        return
        if self.is_in_check(self.turn):
            self.game_over = True
            self.winner = "White" if self.turn == "black" else "Black"
        else:
            self.game_over = True
            self.winner = None
