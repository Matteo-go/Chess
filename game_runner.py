import pygame
from game import Game
from config import WIDTH, HEIGHT

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

def main(game_mode, theme):
    clock = pygame.time.Clock()
    FPS = 60
    game = Game(game_mode, theme)
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if game.game_over and game.back_to_menu_button_rect.collidepoint(pos):
                    from menu import main_menu
                    main_menu()
                    return
                else:
                    game.handle_click(pos)

        game.draw(SCREEN)
        pygame.display.flip()

    pygame.quit()
