import pygame
import requests
from game_runner import main, online_main
from themes import THEMES_DICT
from config import WIDTH, HEIGHT

pygame.init()
FONT = pygame.font.SysFont("Segoe UI", 28)
TITLE_FONT = pygame.font.SysFont("Segoe UI", 60, bold=True)

def draw_button(surface, rect, text, selected=False, color=(70, 70, 70)):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    bg = (100, 140, 200) if is_hover or selected else color
    pygame.draw.rect(surface, bg, rect, border_radius=10)
    label = FONT.render(text, True, (255, 255, 255))
    surface.blit(label, (
        rect.centerx - label.get_width() // 2,
        rect.centery - label.get_height() // 2
    ))

def show_menu(auth_data):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    selected_theme = "Chess.com"
    buttons = {
        "play": pygame.Rect(WIDTH // 2 - 150, 250, 300, 60),
        "online": pygame.Rect(WIDTH // 2 - 150, 320, 300, 60),
        "themes": pygame.Rect(WIDTH // 2 - 150, 390, 300, 60),
        "quit": pygame.Rect(WIDTH // 2 - 150, 460, 300, 60),
    }

    account_button = pygame.Rect(WIDTH - 200, 20, 160, 40)

    running = True
    while running:
        screen.fill((20, 20, 30))
        title = TITLE_FONT.render("Chess Game", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        draw_button(screen, buttons["play"], "Jouer")
        draw_button(screen, buttons["online"], "Jouer en ligne")
        draw_button(screen, buttons["themes"], "Thèmes du plateau")
        draw_button(screen, buttons["quit"], "Quitter le jeu", color=(150, 40, 40))
        draw_button(screen, account_button, "Compte", color=(80, 80, 120))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if buttons["play"].collidepoint(pos):
                    time_selection_screen("1v1", THEMES_DICT[selected_theme], auth_data)
                elif buttons["themes"].collidepoint(pos):
                    selected_theme = themes_screen(selected_theme)
                elif buttons["quit"].collidepoint(pos):
                    pygame.quit()
                    exit()
                elif account_button.collidepoint(pos):
                    show_account_info(screen, auth_data)
                elif buttons["online"].collidepoint(pos):
                    choose_online_game(auth_data)

def time_selection_screen(mode, theme, auth_data):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    times = [60, 180, 300, 600, 1800]
    labels = ["1 min", "3 min", "5 min", "10 min", "30 min"]
    buttons = [(pygame.Rect(WIDTH // 2 - 100, 150 + i * 70, 200, 50), labels[i], times[i]) for i in range(len(times))]
    launch_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT - 100, 240, 50)

    selected_time = None
    running = True

    while running:
        screen.fill((30, 30, 30))
        title = TITLE_FONT.render("Choisis le temps", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for rect, label, time_val in buttons:
            draw_button(screen, rect, label, selected=(selected_time == time_val))

        draw_button(screen, launch_button, "Lancer la partie")

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, label, time_val in buttons:
                    if rect.collidepoint(pos):
                        selected_time = time_val
                if launch_button.collidepoint(pos) and selected_time:
                    main(mode, theme, selected_time, auth_data)
                    return

def themes_screen(current_theme):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    back_button = pygame.Rect(20, HEIGHT - 60, 150, 40)

    theme_buttons = []
    for i, (name, theme) in enumerate(THEMES_DICT.items()):
        rect = pygame.Rect(WIDTH // 2 - 150, 130 + i * 70, 300, 50)
        theme_buttons.append((rect, name))

    selected = current_theme
    running = True

    while running:
        screen.fill((15, 15, 20))
        title = TITLE_FONT.render("Choisis ton thème", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for rect, name in theme_buttons:
            draw_button(screen, rect, name, selected=(name == selected))

        draw_button(screen, back_button, "Retour")

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, name in theme_buttons:
                    if rect.collidepoint(pos):
                        selected = name
                if back_button.collidepoint(pos):
                    return selected

def show_account_info(screen, auth_data):
    clock = pygame.time.Clock()
    back_button = pygame.Rect(20, HEIGHT - 70, 120, 40)

    headers = {
        "Authorization": f"Bearer {auth_data['access_token']}"
    }

    user_info = {
        "username": "Chargement...",
        "email": "-",
        "bio": "-"
    }

    try:
        response = requests.get("http://localhost:8000/api/users/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
        else:
            user_info["username"] = f"Erreur {response.status_code}"
    except Exception as e:
        user_info["username"] = f"Erreur: {str(e)}"

    running = True
    while running:
        screen.fill((25, 25, 35))

        title = TITLE_FONT.render("Mon compte", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        info_lines = [
            f"Nom d'utilisateur : {user_info.get('username', '-')}",
            f"Email : {user_info.get('email', '-')}",
            f"Bio : {user_info.get('bio', '-')}",
            f"Wins: {user_info.get('wins', '-')}",
            f"Losses: {user_info.get('losses', '-')}",
            f"Elo: {user_info.get('elo', '-')}"
        ]

        for i, line in enumerate(info_lines):
            text_surface = FONT.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (100, 180 + i * 50))

        draw_button(screen, back_button, "Retour", color=(90, 90, 90))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

def choose_online_game(auth_data):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Parties en ligne")
    font = pygame.font.SysFont("Segoe UI", 32)
    clock = pygame.time.Clock()
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}

    # Obtenir les parties disponibles
    try:
        response = requests.get("http://localhost:8000/api/games", headers=headers)
        available_games = response.json()
    except Exception as e:
        print("Erreur récupération des parties :", e)
        available_games = []

    waiting_games = [g for g in available_games if g.get("player_black_id") is None]

    # Boutons
    game_buttons = [(pygame.Rect(200, 100 + i * 60, 400, 50), g["id"]) for i, g in enumerate(waiting_games)]
    create_button = pygame.Rect(200, 100 + len(game_buttons) * 60 + 40, 400, 50)
    back_button = pygame.Rect(20, HEIGHT - 70, 120, 40)

    while True:
        screen.fill((30, 30, 30))
        label = font.render("Choisir une partie", True, (255, 255, 255))
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 30))

        for rect, game_id in game_buttons:
            pygame.draw.rect(screen, (100, 100, 255), rect, border_radius=8)
            text = font.render(f"Rejoindre partie {game_id}", True, (255, 255, 255))
            screen.blit(text, (rect.x + 20, rect.y + 10))

        draw_button(screen, create_button, "Créer une nouvelle partie", color=(0, 150, 0))
        draw_button(screen, back_button, "Retour", color=(80, 80, 80))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if back_button.collidepoint(pos):
                    return

                if create_button.collidepoint(pos):
                    game_id = create_online_game(auth_data)
                    if game_id:
                        wait_for_other_player(game_id, auth_data)
                    return

                for rect, game_id in game_buttons:
                    if rect.collidepoint(pos):
                        try:
                            join_online_game(game_id, auth_data)
                            wait_for_other_player(game_id, auth_data)
                        except Exception as e:
                            print("Erreur en rejoignant :", e)
                        return

def wait_for_other_player(game_id, auth_data):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lobby d’attente")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 32)

    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
    back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)

    dot_count = 0
    user_id = get_current_user_id(auth_data)

    while True:
        screen.fill((20, 20, 30))

        dots = "." * (dot_count % 4)
        label = font.render(f"En attente d’un adversaire{dots}", True, (255, 255, 255))
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 40))

        draw_button(screen, back_button, "Annuler", color=(90, 90, 90))

        pygame.display.flip()
        clock.tick(2)
        dot_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

        try:
            resp = requests.get(f"http://localhost:8000/api/games/{game_id}", headers=headers)
            if resp.status_code == 200:
                game = resp.json()
                white = game.get("player_white_id")
                black = game.get("player_black_id")
                if white and black:
                    # Tirage des rôles fait côté serveur : on vérifie juste qui on est
                    if user_id == white:
                        player_color = "white"
                        print("Tu es les BLANCS")
                    elif user_id == black:
                        player_color = "black"
                        print("Tu es les NOIRS")
                    else:
                        print("Erreur : ce joueur n’est pas dans la partie")
                    launch_online_game(game_id, auth_data, player_color)
                    return
        except Exception as e:
            print("Erreur en vérifiant la partie :", e)


def create_online_game(auth_data):
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}

    try:
        user_resp = requests.get("http://localhost:8000/api/users/me", headers=headers)
        if user_resp.status_code != 200:
            print("Erreur lors de la récupération de l'utilisateur.")
            return None

        user_id = user_resp.json().get("id")
        payload = {
            "player_white_id": user_id,
            "board_fen": "startpos",
            "current_turn": "white"
        }
        resp = requests.post("http://localhost:8000/api/games", json=payload, headers=headers)

        if resp.status_code == 200:
            return resp.json()["id"]
        else:
            print("Erreur création partie :", resp.status_code, resp.text)
            return None

    except Exception as e:
        print("Erreur réseau :", e)
        return None


def join_online_game(game_id, auth_data):
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
    requests.post(f"http://localhost:8000/api/games/{game_id}/join", headers=headers)

def launch_online_game(game_id, auth_data, player_color):
    online_main(game_id, auth_data, player_color)


def get_current_user_id(auth_data):
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
    try:
        resp = requests.get("http://localhost:8000/api/users/me", headers=headers)
        if resp.status_code == 200:
            return resp.json().get("id")
    except Exception as e:
        print("Erreur récupération ID utilisateur :", e)
    return None
