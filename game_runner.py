import pygame
from config import WIDTH, HEIGHT
from game import Game

def main(mode, theme, time_limit, auth_data):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    # 🟡 game_id est None en local
    game = Game(
        game_mode=mode,
        theme=theme,
        time_limit=time_limit,
        auth_data=auth_data,
        game_id=None  # en local on n’a pas besoin d’id de partie
    )

    running = True
    while running:
        clock.tick(60)
        game.update_clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                game.handle_click(pos)

        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


def online_main(game_id, auth_data, player_color):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Online")
    clock = pygame.time.Clock()

    # 🟢 Mode en ligne : on passe l’ID de partie
    game = Game(
        game_mode="online",
        theme=((186, 202, 68), (118, 150, 86)),  # ou récupère-le selon ton menu
        time_limit=300,                         # ou rends ça paramétrable aussi
        auth_data=auth_data,
        game_id=game_id,
        player_color=player_color
    )

    running = True
    while running:
        clock.tick(60)
        game.update_clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                game.handle_click(pos)

        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
