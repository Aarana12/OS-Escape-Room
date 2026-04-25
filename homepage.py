import pygame

def run_homepage(screen):
    font = pygame.font.SysFont(None, 50)
    small_font = pygame.font.SysFont(None, 30)

    while True:
        screen.fill((0, 0, 0))  # black background

        # Title
        title = font.render("OS SIMULATION", True, (255, 255, 255))
        screen.blit(title, (220, 200))

        # Instructions
        start_text = small_font.render("Press ENTER to Start", True, (200, 200, 200))
        exit_text = small_font.render("Press ESC to Exit", True, (200, 200, 200))

        screen.blit(start_text, (260, 280))
        screen.blit(exit_text, (270, 320))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    return "exit"

        pygame.display.update()