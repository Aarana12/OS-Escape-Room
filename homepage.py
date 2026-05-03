import pygame


def run_homepage(screen):
    title_font = pygame.font.SysFont(None, 64)
    subtitle_font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 26)

    while True:
        screen.fill((5, 8, 12))

        # Title
        title = title_font.render("OS ESCAPE ROOM", True, (120, 255, 160))
        subtitle = subtitle_font.render(
            "Solve operating system puzzles to escape",
            True,
            (220, 220, 220),
        )

        screen.blit(title, (180, 150))
        screen.blit(subtitle, (190, 215))

        # Room preview box
        pygame.draw.rect(screen, (20, 25, 35), pygame.Rect(170, 270, 460, 120))
        pygame.draw.rect(screen, (100, 255, 160), pygame.Rect(170, 270, 460, 120), 2)

        room1 = small_font.render("Room 1: CPU Scheduling", True, (200, 230, 255))
        room2 = small_font.render("Room 2: Deadlock Prevention", True, (200, 230, 255))
        screen.blit(room1, (210, 300))
        screen.blit(room2, (210, 335))

        # Controls
        start_text = small_font.render("Press ENTER to Start", True, (255, 255, 255))
        exit_text = small_font.render("Press ESC to Exit", True, (160, 160, 160))

        screen.blit(start_text, (285, 430))
        screen.blit(exit_text, (305, 465))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    return "exit"

        pygame.display.update()