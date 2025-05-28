import pygame
from auth import auth_screen
from menu import show_menu  # ton menu principal

def launcher():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Chess Game")

    auth_data = auth_screen(screen, "login")  # 👈 démarre sur la page de login directement

    if auth_data:
        show_menu(auth_data)

if __name__ == "__main__":
    launcher()
