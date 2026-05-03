import pygame
import random
import math


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class NeonLetter:
    def __init__(self, char, x, y, font):
        self.char = char
        self.font = font

        self.base_x = x
        self.base_y = y
        self.x = float(x)
        self.y = float(y)

        self.clicks = 0
        self.shake_timer = 0

        self.falling = False
        self.vx = 0
        self.vy = 0
        self.rotation = 0
        self.rotation_speed = 0

        self.main_color = (230, 255, 245)
        self.glow_color = (0, 255, 180)
        self.hot_pink = (255, 35, 210)

        self.image = self.font.render(self.char, True, self.main_color).convert_alpha()
        self.glow_1 = self.font.render(self.char, True, self.glow_color).convert_alpha()
        self.glow_2 = self.font.render(self.char, True, self.hot_pink).convert_alpha()

        self.glow_1.set_alpha(70)
        self.glow_2.set_alpha(45)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and not self.falling:
            self.clicks += 1
            self.shake_timer = 20

            if self.clicks >= 3:
                self.falling = True
                self.vx = random.uniform(-3.0, 3.0)
                self.vy = random.uniform(-7.0, -3.5)
                self.rotation_speed = random.uniform(-8.0, 8.0)

    def update(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1

        if self.falling:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.38
            self.rotation += self.rotation_speed

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw_glow(self, screen, image, x, y, spread):
        offsets = [
            (-spread, 0),
            (spread, 0),
            (0, -spread),
            (0, spread),
            (-spread, -spread),
            (spread, -spread),
            (-spread, spread),
            (spread, spread),
        ]

        for ox, oy in offsets:
            screen.blit(image, (x + ox, y + oy))

    def draw(self, screen):
        draw_x = self.x
        draw_y = self.y

        if self.shake_timer > 0 and not self.falling:
            draw_x += random.randint(-5, 5)
            draw_y += random.randint(-3, 3)

        if self.falling:
            rotated = pygame.transform.rotate(self.image, self.rotation)
            rotated_rect = rotated.get_rect(
                center=(draw_x + self.rect.width / 2, draw_y + self.rect.height / 2)
            )
            screen.blit(rotated, rotated_rect)
            return

        self.draw_glow(screen, self.glow_1, draw_x, draw_y, 5)
        self.draw_glow(screen, self.glow_2, draw_x, draw_y, 3)
        screen.blit(self.glow_1, (draw_x, draw_y))
        screen.blit(self.image, (draw_x, draw_y))


class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.4, 1.6)
        self.size = random.randint(1, 3)
        self.color = random.choice([
            (0, 255, 180),
            (255, 35, 210),
            (70, 130, 255),
            (255, 255, 255),
        ])
        self.alpha = random.randint(60, 160)

    def update(self):
        self.y += self.speed

        if self.y > SCREEN_HEIGHT:
            self.y = -10
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            surface,
            (*self.color, self.alpha),
            (self.size * 2, self.size * 2),
            self.size,
        )
        screen.blit(surface, (self.x, self.y))


def create_title_letters(text, font, center_x, y):
    spacing = 4
    letter_widths = []

    for char in text:
        if char == " ":
            letter_widths.append(24)
        else:
            letter_widths.append(font.size(char)[0])

    total_width = sum(letter_widths) + spacing * (len(text) - 1)
    start_x = center_x - total_width // 2

    letters = []
    current_x = start_x

    for char, width in zip(text, letter_widths):
        if char != " ":
            letters.append(NeonLetter(char, current_x, y, font))
        current_x += width + spacing

    return letters


def draw_text_with_glow(screen, font, text, pos, main_color, glow_color):
    x, y = pos

    glow = font.render(text, True, glow_color).convert_alpha()
    glow.set_alpha(70)

    main = font.render(text, True, main_color).convert_alpha()

    for offset in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)]:
        screen.blit(glow, (x + offset[0], y + offset[1]))

    screen.blit(main, (x, y))


def draw_cyberpunk_background(screen, tick):
    screen.fill((3, 5, 16))

    # Vertical gradient
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(5 + ratio * 20)
        g = int(8 + ratio * 8)
        b = int(25 + ratio * 35)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    # Distant neon skyline
    skyline_color = (12, 18, 35)
    neon_edge = (0, 255, 180)

    buildings = [
        (35, 320, 55, 180),
        (105, 280, 70, 220),
        (200, 340, 50, 160),
        (285, 300, 85, 200),
        (420, 330, 60, 170),
        (515, 275, 75, 225),
        (630, 315, 55, 185),
        (705, 290, 65, 210),
    ]

    for x, y, w, h in buildings:
        pygame.draw.rect(screen, skyline_color, pygame.Rect(x, y, w, h))
        pygame.draw.line(screen, neon_edge, (x, y), (x + w, y), 1)

        for window_y in range(y + 18, y + h - 10, 28):
            for window_x in range(x + 10, x + w - 8, 18):
                if random.random() > 0.82:
                    pygame.draw.rect(
                        screen,
                        random.choice([(0, 255, 180), (255, 35, 210), (70, 130, 255)]),
                        pygame.Rect(window_x, window_y, 5, 8),
                    )

    # Moving perspective grid
    grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    horizon_y = 380
    grid_color = (0, 255, 180, 65)
    pink_grid = (255, 35, 210, 45)

    pygame.draw.line(grid_surface, (0, 255, 180, 120), (0, horizon_y), (SCREEN_WIDTH, horizon_y), 2)

    for i in range(18):
        offset = (tick * 1.6) % 35
        y = horizon_y + i * 20 + offset
        if y < SCREEN_HEIGHT:
            pygame.draw.line(grid_surface, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

    center_x = SCREEN_WIDTH // 2
    for x in range(-500, SCREEN_WIDTH + 500, 80):
        pygame.draw.line(grid_surface, pink_grid, (center_x, horizon_y), (x, SCREEN_HEIGHT), 1)

    screen.blit(grid_surface, (0, 0))

    # Scan lines
    scan_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(scan_surface, (255, 255, 255, 15), (0, y), (SCREEN_WIDTH, y))
    screen.blit(scan_surface, (0, 0))


def draw_panel(screen, rect, border_color, fill_color=(8, 12, 28), border_width=2):
    panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(
        panel_surface,
        (*fill_color, 190),
        pygame.Rect(0, 0, rect.width, rect.height),
        border_radius=18,
    )
    screen.blit(panel_surface, rect.topleft)

    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=18)

    glow_surface = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
    pygame.draw.rect(
        glow_surface,
        (*border_color, 45),
        pygame.Rect(8, 8, rect.width, rect.height),
        3,
        border_radius=20,
    )
    screen.blit(glow_surface, (rect.x - 8, rect.y - 8))


def draw_room_card(screen, rect, title, description, number, font_title, font_body):
    draw_panel(screen, rect, (0, 255, 180), (9, 15, 33), 2)

    badge_rect = pygame.Rect(rect.x + 18, rect.y + 24, 48, 48)
    pygame.draw.rect(screen, (255, 35, 210), badge_rect, border_radius=12)
    pygame.draw.rect(screen, (255, 160, 245), badge_rect, 2, border_radius=12)

    number_text = font_title.render(str(number), True, (255, 255, 255))
    number_rect = number_text.get_rect(center=badge_rect.center)
    screen.blit(number_text, number_rect)

    draw_text_with_glow(
        screen,
        font_title,
        title,
        (rect.x + 82, rect.y + 22),
        (235, 255, 245),
        (0, 255, 180),
    )

    desc = font_body.render(description, True, (180, 200, 220))
    screen.blit(desc, (rect.x + 82, rect.y + 58))

    pygame.draw.line(
        screen,
        (255, 35, 210),
        (rect.x + 22, rect.y + rect.height - 18),
        (rect.x + rect.width - 22, rect.y + rect.height - 18),
        2,
    )


def draw_start_button(screen, rect, text, font, mouse_pos):
    hovering = rect.collidepoint(mouse_pos)

    if hovering:
        fill = (255, 35, 210)
        border = (255, 190, 245)
        text_color = (255, 255, 255)
    else:
        fill = (8, 16, 35)
        border = (0, 255, 180)
        text_color = (210, 255, 235)

    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(button_surface, (*fill, 220), pygame.Rect(0, 0, rect.width, rect.height), border_radius=16)
    screen.blit(button_surface, rect.topleft)

    pygame.draw.rect(screen, border, rect, 2, border_radius=16)

    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def run_homepage(screen):
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("consolas", 58, bold=True)
    subtitle_font = pygame.font.SysFont("consolas", 24)
    card_title_font = pygame.font.SysFont("consolas", 24, bold=True)
    card_body_font = pygame.font.SysFont("consolas", 18)
    button_font = pygame.font.SysFont("consolas", 24, bold=True)
    small_font = pygame.font.SysFont("consolas", 17)

    title_letters = create_title_letters("OS ESCAPE ROOM", title_font, SCREEN_WIDTH // 2, 72)

    particles = [Particle() for _ in range(55)]

    start_button = pygame.Rect(265, 505, 270, 48)
    tick = 0

    while True:
        tick += 1
        mouse_pos = pygame.mouse.get_pos()

        draw_cyberpunk_background(screen, tick)

        for particle in particles:
            particle.update()
            particle.draw(screen)

        #main hologram panel
        main_panel = pygame.Rect(55, 42, 690, 515)
        draw_panel(screen, main_panel, (0, 255, 180), (5, 8, 20), 2)

        #title
        for letter in title_letters:
            letter.update()
            letter.draw(screen)

        #subtitle
        draw_text_with_glow(
            screen,
            subtitle_font,
            "SOLVE THE SYSTEM. BREAK THE LOCK.",
            (185, 150),
            (220, 235, 255),
            (255, 35, 210),
        )

        #decorative bars
        pygame.draw.line(screen, (0, 255, 180), (120, 185), (680, 185), 2)
        pygame.draw.line(screen, (255, 35, 210), (180, 193), (620, 193), 1)

        #room cards
        draw_room_card(
            screen,
            pygame.Rect(125, 220, 550, 95),
            "CPU SCHEDULING",
            "Choose the most efficient scheduling algorithm.",
            1,
            card_title_font,
            card_body_font,
        )

        draw_room_card(
            screen,
            pygame.Rect(125, 335, 550, 95),
            "DEADLOCK PREVENTION",
            "Build a safe resource allocation order.",
            2,
            card_title_font,
            card_body_font,
        )

        #bttom status line
        status_text = small_font.render(
            "PYGAME SYSTEM ONLINE  |  INPUT: KEYBOARD  |  STATUS: LOCKED",
            True,
            (150, 255, 210),
        )
        screen.blit(status_text, (135, 460))

        #Buttons
        draw_start_button(screen, start_button, "ENTER  //  START", button_font, mouse_pos)

        exit_text = small_font.render("ESC // EXIT", True, (170, 180, 200))
        screen.blit(exit_text, (356, 562))

        #Subtle animated corner accents
        pulse = int(120 + 80 * math.sin(tick * 0.06))
        accent_color = (0, pulse, 180)

        pygame.draw.line(screen, accent_color, (70, 58), (135, 58), 3)
        pygame.draw.line(screen, accent_color, (70, 58), (70, 122), 3)

        pygame.draw.line(screen, accent_color, (730, 58), (665, 58), 3)
        pygame.draw.line(screen, accent_color, (730, 58), (730, 122), 3)

        pygame.draw.line(screen, accent_color, (70, 540), (135, 540), 3)
        pygame.draw.line(screen, accent_color, (70, 540), (70, 476), 3)

        pygame.draw.line(screen, accent_color, (730, 540), (665, 540), 3)
        pygame.draw.line(screen, accent_color, (730, 540), (730, 476), 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    return "start"

                for letter in title_letters:
                    letter.handle_click(event.pos)

        pygame.display.update()
        clock.tick(60)