import pygame
from game_runner import main
from config import WIDTH, HEIGHT

pygame.init()
FONT = pygame.font.SysFont("arial", 32)
SMALL_FONT = pygame.font.SysFont("arial", 24)

# Thèmes disponibles : nom → (couleur claire, couleur foncée)
THEMES = {
    "Classic": ((240, 217, 181), (181, 136, 99)),
    "Dark": ((60, 60, 60), (30, 30, 30)),
    "Green": ((240, 240, 200), (100, 140, 100)),
    "Violet": ((180, 170, 255), (100, 80, 180)),
}

def draw_text_centered(surface, text, y, font, color=(255, 255, 255)):
    label = font.render(text, True, color)
    x = WIDTH // 2 - label.get_width() // 2
    surface.blit(label, (x, y))

def draw_button(surface, rect, text, selected=False):
    color = (100, 100, 100)
    if selected:
        color = (200, 100, 0)
    pygame.draw.rect(surface, color, rect)
    label = FONT.render(text, True, (255, 255, 255))
    surface.blit(label, (
        rect.x + rect.width // 2 - label.get_width() // 2,
        rect.y + rect.height // 2 - label.get_height() // 2
    ))

def main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - Menu")

    selected_theme = "Classic"
    selected_mode = "1v1"

    # Prépare les rectangles de bouton
    button_width = 300
    button_height = 50
    spacing = 20

    theme_buttons = []
    modes = ["1v1", "Bot (à venir)"]
    mode_buttons = []

    start_y = 100

    # Crée les boutons de thème
    for i, theme_name in enumerate(THEMES):
        rect = pygame.Rect(
            WIDTH//2 - button_width//2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
        )
        theme_buttons.append((rect, theme_name))

    # Crée les boutons de mode
    mode_start_y = start_y + len(theme_buttons)*(button_height + spacing) + 40
    for i, mode in enumerate(modes):
        rect = pygame.Rect(
            WIDTH//2 - button_width//2,
            mode_start_y + i * (button_height + spacing),
            button_width,
            button_height
        )
        mode_buttons.append((rect, mode))

    # Bouton "Play"
    play_button = pygame.Rect(WIDTH//2 - button_width//2, mode_start_y + 2*(button_height + spacing) + 20, button_width, button_height)

    running = True
    while running:
        screen.fill((20, 20, 20))

        draw_text_centered(screen, "Chess", 30, pygame.font.SysFont("arial", 48))

        # Thème
        draw_text_centered(screen, "Choose a theme:", start_y - 40, SMALL_FONT)
        for rect, name in theme_buttons:
            draw_button(screen, rect, name, selected=(name == selected_theme))

        # Mode
        draw_text_centered(screen, "Choose mode:", mode_start_y - 40, SMALL_FONT)
        for rect, name in mode_buttons:
            draw_button(screen, rect, name, selected=(name.startswith(selected_mode)))

        # Play
        draw_button(screen, play_button, "Play")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Sélection thème
                for rect, name in theme_buttons:
                    if rect.collidepoint(pos):
                        selected_theme = name

                # Sélection mode
                for rect, name in mode_buttons:
                    if rect.collidepoint(pos):
                        if name.startswith("1v1"):
                            selected_mode = "1v1"
                        else:
                            selected_mode = "bot"  # Placeholder

                # Lancer jeu
                if play_button.collidepoint(pos):
                    from themes import THEMES_DICT
                    main(game_mode=selected_mode, theme=THEMES_DICT[selected_theme])
                    return
