import pygame
import requests
from game_runner import main
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
        "themes": pygame.Rect(WIDTH // 2 - 150, 340, 300, 60),
        "quit": pygame.Rect(WIDTH // 2 - 150, 430, 300, 60),
    }

    account_button = pygame.Rect(WIDTH - 200, 20, 160, 40)

    running = True
    while running:
        screen.fill((20, 20, 30))
        title = TITLE_FONT.render("Chess Game", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        draw_button(screen, buttons["play"], "Jouer")
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
                    time_selection_screen("1v1", THEMES_DICT[selected_theme])
                elif buttons["themes"].collidepoint(pos):
                    selected_theme = themes_screen(selected_theme)
                elif buttons["quit"].collidepoint(pos):
                    pygame.quit()
                    exit()
                elif account_button.collidepoint(pos):
                    show_account_info(screen, auth_data)

def time_selection_screen(mode, theme):
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
                    main(mode, theme, selected_time)
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
