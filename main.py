import pygame
from homepage import run_homepage
from game import run_game

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("OS Escape Room")

choice = run_homepage(screen)

if choice == "start":
    run_game()

pygame.quit()
