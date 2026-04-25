import pygame
from game.homepage import run_homepage
from game.game import run_game

pygame.init()
screen = pygame.display.set_mode((800, 600))

choice = run_homepage(screen)

if choice == "start":
    run_game()

pygame.quit()
