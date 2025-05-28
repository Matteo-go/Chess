import pygame
from game_runner import main
from themes import THEMES_DICT
from config import WIDTH, HEIGHT

pygame.init()
FONT = pygame.font.SysFont("Segoe UI", 28)
TITLE_FONT = pygame.font.SysFont("Segoe UI", 48, bold=True)

def draw_button(surface, rect, text, selected=False):
    base_color = (60, 60, 60)
    hover_color = (100, 140, 180) if selected else base_color
    pygame.draw.rect(surface, hover_color, rect, border_radius=10)
    label = FONT.render(text, True, (255, 255, 255))
    surface.blit(label, (
        rect.centerx - label.get_width() // 2,
        rect.centery - label.get_height() // 2
    ))

def main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - Menu")
    clock = pygame.time.Clock()

    selected_theme = "Chess.com"
    theme_buttons = []
    play_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 120, 300, 50)

    for i, name in enumerate(THEMES_DICT.keys()):
        rect = pygame.Rect(WIDTH//2 - 150, 180 + i * 70, 300, 50)
        theme_buttons.append((rect, name))

    mode_button_1v1 = pygame.Rect(WIDTH//2 - 150, 180 + len(theme_buttons)*70 + 40, 300, 50)

    running = True
    while running:
        screen.fill((25, 25, 25))
        title = TITLE_FONT.render("Ultimate Chess", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        for rect, name in theme_buttons:
            draw_button(screen, rect, name, selected=(name == selected_theme))

        draw_button(screen, mode_button_1v1, "Mode 1v1")

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, name in theme_buttons:
                    if rect.collidepoint(pos):
                        selected_theme = name
                if mode_button_1v1.collidepoint(pos):
                    time_selection_screen("1v1", THEMES_DICT[selected_theme])

def time_selection_screen(mode, theme):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    FONT = pygame.font.SysFont("Segoe UI", 28)
    TITLE_FONT = pygame.font.SysFont("Segoe UI", 42, bold=True)

    times = [60, 180, 300, 600, 1800]  # 1m, 3m, 5m, 10m, 30m
    labels = ["1 min", "3 min", "5 min", "10 min", "30 min"]
    buttons = []

    for i, label in enumerate(labels):
        rect = pygame.Rect(WIDTH//2 - 100, 150 + i * 70, 200, 50)
        buttons.append((rect, label, times[i]))

    launch_button = pygame.Rect(WIDTH//2 - 120, HEIGHT - 100, 240, 50)

    selected_time = None

    running = True
    while running:
        screen.fill((30, 30, 30))
        title = TITLE_FONT.render("Choisis le temps", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        for rect, label, time_val in buttons:
            draw_button(screen, rect, label, selected=(selected_time == time_val))

        draw_button(screen, launch_button, "Lancer la partie")

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, label, time_val in buttons:
                    if rect.collidepoint(pos):
                        selected_time = time_val
                if launch_button.collidepoint(pos) and selected_time:
                    main(mode, theme, selected_time)
                    return
