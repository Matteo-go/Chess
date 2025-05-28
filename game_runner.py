import pygame
from config import WIDTH, HEIGHT
from game import Game

def main(mode, theme, time_limit):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    game = Game(mode, theme, time_limit)

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
