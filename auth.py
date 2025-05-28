import pygame
import requests

API_URL = "http://localhost:8000/api/users"

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
LIGHT_BLUE = (135, 206, 250)
WIDTH, HEIGHT = 800, 600

pygame.font.init()
FONT = pygame.font.SysFont("Segoe UI", 24)
BIG_FONT = pygame.font.SysFont("Segoe UI", 36)


class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = GRAY
        self.color_active = LIGHT_BLUE
        self.color = self.color_inactive
        self.text = text
        self.is_password = is_password
        self.active = False
        self.update_text_surface()

    def update_text_surface(self):
        display_text = '*' * len(self.text) if self.is_password else self.text
        self.txt_surface = FONT.render(display_text, True, BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.update_text_surface()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


def auth_screen(screen, mode="login"):
    username_box = InputBox(300, 200, 200, 40)
    password_box = InputBox(300, 270, 200, 40, is_password=True)
    boxes = [username_box, password_box]

    button_rect = pygame.Rect(320, 340, 160, 50)
    toggle_rect = pygame.Rect(240, 420, 320, 30)

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((30, 30, 30))

        title = BIG_FONT.render("Connexion" if mode == "login" else "Inscription", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        labels = ["Nom d'utilisateur", "Mot de passe"]
        for i, box in enumerate(boxes):
            label = FONT.render(labels[i], True, WHITE)
            screen.blit(label, (box.rect.x, box.rect.y - 25))
            box.draw(screen)

        # Bouton principal
        pygame.draw.rect(screen, BLUE, button_rect, border_radius=10)
        button_label = FONT.render("Se connecter" if mode == "login" else "S'inscrire", True, WHITE)
        screen.blit(button_label, (
            button_rect.centerx - button_label.get_width() // 2,
            button_rect.centery - button_label.get_height() // 2
        ))

        # Lien vers l’autre mode
        toggle_label = FONT.render(
            "Pas encore de compte ? S'inscrire ici" if mode == "login" else "Déjà un compte ? Se connecter ici",
            True, WHITE)
        screen.blit(toggle_label, toggle_rect)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    if not username or not password:
                        continue
                    try:
                        if mode == "register":
                            r = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
                        else:
                            r = requests.post(f"{API_URL}/token", json={"username": username, "password": password})
                        if r.status_code == 200:
                            return r.json()
                    except Exception as e:
                        print(f"Erreur: {e}")
                elif toggle_rect.collidepoint(event.pos):
                    return auth_screen(screen, "register" if mode == "login" else "login")

            for box in boxes:
                box.handle_event(event)
