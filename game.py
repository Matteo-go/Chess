import pygame
import os
from config import BOARD_ROWS, BOARD_COLS, SQUARE_SIZE, WIDTH, HEIGHT, BOARD_OFFSET_X, BOARD_OFFSET_Y
from pieces import Pawn, Rook, Knight, Bishop, Queen, King
import websocket
import threading
import json
import time

pygame.init()
FONT = pygame.font.SysFont("Segoe UI", 24)
TITLE_FONT = pygame.font.SysFont("Segoe UI", 48, bold=True)
PIECE_IMAGES = {}

def load_images():
    for file in os.listdir("assets/images"):
        if file.endswith(".png"):
            name = file.replace(".png", "")
            img = pygame.image.load(os.path.join("assets/images", file))
            PIECE_IMAGES[name] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))

def format_time(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02}:{seconds:02}"

class Game:
    def __init__(self, game_mode="1v1 Local", theme=((186, 202, 68), (118, 150, 86)), time_limit=300, auth_data=None, game_id=None, player_color=None):
        self.auth_data = auth_data
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.turn = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.captured_white = []
        self.captured_black = []
        self.theme = theme
        self.light_color, self.dark_color = theme
        self.quit_button_rect = pygame.Rect(WIDTH - 140, HEIGHT - 70, 110, 40)
        self.back_to_menu_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        self.last_move = None
        self.game_over = False
        self.winner = None
        self.quit_popup = False


        # TIMERS
        self.time_limit = time_limit
        self.white_time = time_limit
        self.black_time = time_limit
        self.last_tick = pygame.time.get_ticks()

        # ONLINE GAME
        self.online = game_mode == "online"
        self.game_id = game_id
        self.ws = None
        self.player_color = player_color
        self.my_color = player_color if self.online else None

        if self.online:
            self.connect_websocket()
            if auth_data and "user_id" in auth_data:
                self.player_white_id = auth_data["user_id"] if player_color == "white" else None
                self.my_color = player_color
            else:
                print("❌ Erreur : 'user_id' manquant dans auth_data :", auth_data)


        load_images()
        self.setup_board()

    def setup_board(self):
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, cls in enumerate(order):
            self.board[0][col] = cls("black", col, 0)
            self.board[7][col] = cls("white", col, 7)
        for col in range(BOARD_COLS):
            self.board[1][col] = Pawn("black", col, 1)
            self.board[6][col] = Pawn("white", col, 6)

    def update_clock(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        elapsed = (now - self.last_tick) / 1000  # en secondes
        self.last_tick = now

        if self.online:
            if self.turn == self.my_color:
                if self.turn == "white":
                    self.white_time = max(0, self.white_time - elapsed)
                    if self.white_time == 0:
                        self.game_over = True
                        self.winner = "Black"
                else:
                    self.black_time = max(0, self.black_time - elapsed)
                    if self.black_time == 0:
                        self.game_over = True
                        self.winner = "White"
            else:
                # Simulation du timer adverse pour affichage fluide
                if self.turn == "white":
                    self.white_time = max(0, self.white_time - elapsed)
                else:
                    self.black_time = max(0, self.black_time - elapsed)
        else:
            # Mode local 1v1
            if self.turn == "white":
                self.white_time = max(0, self.white_time - elapsed)
                if self.white_time == 0:
                    self.game_over = True
                    self.winner = "Black"
            else:
                self.black_time = max(0, self.black_time - elapsed)
                if self.black_time == 0:
                    self.game_over = True
                    self.winner = "White"


    def draw(self, win):
        win.fill((30, 30, 30))
        self.draw_board(win)
        self.draw_pieces(win)
        self.draw_captured(win)
        self.draw_timers(win)
        self.draw_quit_button(win)
        if self.quit_popup:
            self.draw_quit_popup(win)
        if self.game_over:
            self.display_winner(win)

    def draw_board(self, win):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                pygame.draw.rect(win, color, (x, y, SQUARE_SIZE, SQUARE_SIZE), border_radius=6)

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
            win.blit(pygame.transform.scale(PIECE_IMAGES[key], (28, 28)), (x_left, y_start + i * 30))
        for i, piece in enumerate(self.captured_black):
            key = f"white-{piece}"
            win.blit(pygame.transform.scale(PIECE_IMAGES[key], (28, 28)), (x_right, y_start + i * 30))

    def draw_timers(self, win):
        font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        white_label = font.render(format_time(self.white_time), True, (255, 255, 255))
        black_label = font.render(format_time(self.black_time), True, (255, 255, 255))
        center_x = WIDTH // 2
        win.blit(white_label, (center_x - white_label.get_width() - 150, 20))
        win.blit(black_label, (center_x + 150, 20))


    def draw_quit_button(self, win):
        pygame.draw.rect(win, (180, 0, 0), self.quit_button_rect, border_radius=10)
        label = FONT.render("Quitter", True, (255, 255, 255))
        win.blit(label, (
            self.quit_button_rect.centerx - label.get_width() // 2,
            self.quit_button_rect.centery - label.get_height() // 2
        ))

    def draw_quit_popup(self, win):
        popup = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 120)
        pygame.draw.rect(win, (50, 50, 50), popup, border_radius=12)
        pygame.draw.rect(win, (200, 200, 200), popup, 2)
        label = FONT.render("Voulez-vous abandonner ?", True, (255, 255, 255))
        win.blit(label, (popup.centerx - label.get_width() // 2, popup.y + 15))
        self.yes_button = pygame.Rect(popup.x + 40, popup.y + 70, 80, 30)
        self.no_button = pygame.Rect(popup.x + 180, popup.y + 70, 80, 30)
        pygame.draw.rect(win, (100, 100, 100), self.yes_button, border_radius=6)
        pygame.draw.rect(win, (100, 100, 100), self.no_button, border_radius=6)
        win.blit(FONT.render("Oui", True, (255, 255, 255)), (self.yes_button.x + 20, self.yes_button.y + 5))
        win.blit(FONT.render("Non", True, (255, 255, 255)), (self.no_button.x + 18, self.no_button.y + 5))

    def display_winner(self, win):
        popup_width, popup_height = 400, 200
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = HEIGHT // 2 - popup_height // 2

        popup = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Fond semi-transparent
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # noir semi-transparent
        win.blit(overlay, (0, 0))

        # Boîte de victoire
        pygame.draw.rect(win, (245, 245, 245), popup, border_radius=15)
        pygame.draw.rect(win, (80, 80, 80), popup, 3, border_radius=15)

        text = f"{self.winner} wins!" if self.winner else "Draw"
        label = TITLE_FONT.render(text, True, (30, 30, 30))
        win.blit(label, (
            popup.centerx - label.get_width() // 2,
            popup.y + 30
        ))

        # Bouton retour au menu
        self.back_to_menu_button_rect = pygame.Rect(popup.centerx - 100, popup.bottom - 60, 200, 40)
        pygame.draw.rect(win, (100, 100, 255), self.back_to_menu_button_rect, border_radius=8)
        btn_text = FONT.render("Retour au menu", True, (255, 255, 255))
        win.blit(btn_text, (
            self.back_to_menu_button_rect.centerx - btn_text.get_width() // 2,
            self.back_to_menu_button_rect.centery - btn_text.get_height() // 2
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
            if self.back_to_menu_button_rect.collidepoint(pos):
                import menu
                menu.show_menu(self.auth_data)
            return

        if self.quit_button_rect.collidepoint(pos):
            self.quit_popup = True
            return

        col = (pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
        row = (pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE

        if not (0 <= col < BOARD_COLS and 0 <= row < BOARD_ROWS):
            return

        piece = self.board[row][col]

        # ❌ En ligne, on ne joue que si c'est notre tour
        if self.online:
            if self.turn != self.my_color:
                return  # ce n'est pas ton tour

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
                self.update_clock()
                self.turn = "black" if self.turn == "white" else "white"
                self.last_tick = pygame.time.get_ticks()
                self.check_game_end()

                # 🌐 Si mode en ligne : envoyer l'état
                if self.online and self.ws:
                    move_data = {
                        "fen": self.to_fen(),
                        "turn": self.turn,
                        "white_time": self.white_time,
                        "black_time": self.black_time
                    }
                    self.ws.send(json.dumps(move_data))


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
        self.last_move = (piece, piece.row, piece.col, row, col)

    def handle_promotion(self, piece):
        if piece.name == "pawn":
            is_promotion_row = (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == BOARD_ROWS - 1)
            if is_promotion_row:
                promoted_piece = self.choose_promotion(piece.color, piece.col, piece.row)
                self.board[piece.row][piece.col] = promoted_piece

    def choose_promotion(self, color, col, row):
        screen = pygame.display.get_surface()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        piece_classes = [Queen, Rook, Bishop, Knight]
        piece_names = ["queen", "rook", "bishop", "knight"]

        popup_width, popup_height = 300, 100
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = HEIGHT // 2 - popup_height // 2
        popup = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        pygame.draw.rect(screen, (240, 240, 240), popup, border_radius=12)
        pygame.draw.rect(screen, (100, 100, 100), popup, 2, border_radius=12)

        spacing = popup_width // 5
        image_rects = []
        for i, name in enumerate(piece_names):
            key = f"{color}-{name}"
            img = pygame.transform.scale(PIECE_IMAGES[key], (48, 48))
            x = popup_x + spacing * (i + 1) - 24
            y = popup_y + popup_height // 2 - 24
            rect = pygame.Rect(x, y, 48, 48)
            screen.blit(img, (x, y))
            image_rects.append((rect, piece_classes[i]))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for rect, cls in image_rects:
                        if rect.collidepoint(pos):
                            return cls(color, col, row)


    def get_legal_moves(self, piece):
        all_moves = piece.get_valid_moves(self.board, self.last_move)
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
                    if (king.row, king.col) in piece.get_valid_moves(self.board, self.last_move):
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

    def to_fen(self):
        piece_to_char = {
            "pawn": "p", "rook": "r", "knight": "n", "bishop": "b", "queen": "q", "king": "k"
        }

        fen = ""
        for row in self.board:
            empty = 0
            for piece in row:
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    symbol = piece_to_char[piece.name]
                    fen += symbol.upper() if piece.color == "white" else symbol
            if empty > 0:
                fen += str(empty)
            fen += "/"
        fen = fen.rstrip("/") + f" {self.turn} - - 0 1"
        return fen

    def load_fen(self, fen):
        from pieces import Pawn, Rook, Knight, Bishop, Queen, King

        fen_parts = fen.split(" ")
        rows = fen_parts[0].split("/")
        self.turn = fen_parts[1]
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

        char_to_piece = {
            "p": Pawn, "r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k": King
        }

        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    color = "white" if char.isupper() else "black"
                    piece_class = char_to_piece[char.lower()]
                    self.board[row_idx][col_idx] = piece_class(color, col_idx, row_idx)
                    col_idx += 1

    def connect_websocket(self):

        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.load_fen(data["fen"])
                self.turn = data["turn"]
                self.white_time = data.get("white_time", self.white_time)
                self.black_time = data.get("black_time", self.black_time)
                self.last_tick = pygame.time.get_ticks()
            except Exception as e:
                print("Erreur réception WebSocket :", e)

        ws_url = f"ws://localhost:8000/ws/games/{self.game_id}"
        self.ws = websocket.WebSocketApp(ws_url, on_message=on_message)

        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()

    def close(self):
        if self.online and self.ws:
            self.ws.close()

    async def listen_to_server(self):
        try:
            async for message in self.ws:
                data = json.loads(message)

                if data["type"] == "update":
                    fen = data.get("fen")
                    turn = data.get("turn")
                    white_time = data.get("white_time")
                    black_time = data.get("black_time")
                    winner = data.get("winner")
                    game_over = data.get("game_over")

                    if fen:
                        self.board.set_fen(fen)
                    if turn:
                        self.turn = turn
                    if white_time is not None:
                        self.white_time = white_time
                    if black_time is not None:
                        self.black_time = black_time
                    if winner:
                        self.winner = winner
                    if game_over is not None:
                        self.game_over = game_over

                    self.sync_clock()
                    self.refresh_captured_pieces()

        except Exception as e:
            print("Erreur WebSocket : ", e)

    def sync_clock(self):
        self.last_tick = pygame.time.get_ticks()

    def refresh_captured_pieces(self):
        # Tu peux l’implémenter comme tu veux, exemple :
        self.captured_white = self.board.get_captured("white")
        self.captured_black = self.board.get_captured("black")

    def simulate_opponent_timer(self):
        if self.game_mode != "online":
            return

        # On simule uniquement si c’est le tour de l’adversaire
        if self.current_turn != self.my_color:
            elapsed = time.time() - self.last_update_time
            if self.current_turn == "white":
                self.white_time_left -= elapsed
            else:
                self.black_time_left -= elapsed
            self.last_update_time = time.time()

