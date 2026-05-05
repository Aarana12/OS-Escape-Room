import pygame
import random
import math


NEON_GREEN = (0, 255, 90)
NEON_LIGHT = (180, 255, 190)
DARK_BG = (0, 4, 1)


class CuttableMatrixGlyph:
    def __init__(self, font, width=800, height=600):
        self.font = font
        self.width = width
        self.height = height
        self.characters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&<>/[]{}"
        self.reset(random_start=True)

    def reset(self, random_start=False):
        self.char = random.choice(self.characters)
        self.x = random.randint(0, self.width)
        self.y = random.randint(-self.height, self.height) if random_start else random.randint(-180, -20)
        self.speed = random.uniform(0.2, 0.55)
        self.alpha = random.randint(120, 230)

        self.cut = False
        self.vx = 0
        self.vy = 0
        self.rotation = 0
        self.rotation_speed = 0

        self.image = self.font.render(self.char, True, NEON_GREEN).convert_alpha()
        self.cut_image = self.font.render(self.char, True, NEON_LIGHT).convert_alpha()

    def update(self, mouse_pos):
        mx, my = mouse_pos
        dx = self.x - mx
        dy = self.y - my
        distance = math.hypot(dx, dy)

        if not self.cut and distance < 28:
            self.cut = True

            if distance == 0:
                distance = 1

            force_x = dx / distance
            force_y = dy / distance

            self.vx = force_x * random.uniform(3.0, 6.0)
            self.vy = force_y * random.uniform(2.0, 4.0) - random.uniform(1.0, 2.5)
            self.rotation_speed = random.uniform(-8.0, 8.0)
            self.alpha = 255

        if self.cut:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.18
            self.rotation += self.rotation_speed
            self.alpha -= 8
        else:
            self.y += self.speed

        if self.y > self.height + 40 or self.x < -80 or self.x > self.width + 80 or self.alpha <= 0:
            self.reset(random_start=False)

    def draw(self, screen):
        image = self.cut_image if self.cut else self.image
        image.set_alpha(max(0, min(255, self.alpha)))

        if self.cut:
            rotated = pygame.transform.rotate(image, self.rotation)
            screen.blit(rotated, (int(self.x), int(self.y)))
        else:
            screen.blit(image, (int(self.x), int(self.y)))


class CuttableMatrixRain:
    def __init__(self, font, count=65, width=800, height=600):
        self.width = width
        self.height = height
        self.glyphs = [
            CuttableMatrixGlyph(font, width, height)
            for _ in range(count)
        ]

    def update_and_draw(self, screen, mouse_pos):
        screen.fill(DARK_BG)

        for glyph in self.glyphs:
            glyph.update(mouse_pos)
            glyph.draw(screen)

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        screen.blit(overlay, (0, 0))


class RepelLetter:
    def __init__(self, char, x, y, font):
        self.char = char
        self.font = font

        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)

        self.vx = 0
        self.vy = 0

        self.image = self.font.render(self.char, True, (220, 255, 225)).convert_alpha()
        self.glow = self.font.render(self.char, True, NEON_GREEN).convert_alpha()
        self.glow.set_alpha(95)

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def reset(self):
        self.x = self.base_x
        self.y = self.base_y
        self.vx = 0
        self.vy = 0

    def update(self, mouse_pos):
        mx, my = mouse_pos

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        dx = center_x - mx
        dy = center_y - my
        distance = math.hypot(dx, dy)

        repel_radius = 95

        if distance < repel_radius:
            if distance == 0:
                distance = 1

            strength = (repel_radius - distance) / repel_radius
            self.vx += (dx / distance) * strength * 4.0
            self.vy += (dy / distance) * strength * 4.0

        self.vx += (self.base_x - self.x) * 0.045
        self.vy += (self.base_y - self.y) * 0.045

        self.vx *= 0.82
        self.vy *= 0.82

        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        glow_offsets = [
            (-5, 0), (5, 0), (0, -5), (0, 5),
            (-3, -3), (3, -3), (-3, 3), (3, 3),
            (-2, 0), (2, 0), (0, -2), (0, 2),
        ]

        for ox, oy in glow_offsets:
            screen.blit(self.glow, (int(self.x + ox), int(self.y + oy)))

        screen.blit(self.image, (int(self.x), int(self.y)))


def create_repel_text(text, font, center_x, y):
    spacing = 3
    widths = []

    for char in text:
        widths.append(24 if char == " " else font.size(char)[0])

    total_width = sum(widths) + spacing * (len(text) - 1)
    start_x = center_x - total_width // 2

    letters = []
    current_x = start_x

    for char, width in zip(text, widths):
        if char != " ":
            letters.append(RepelLetter(char, current_x, y, font))

        current_x += width + spacing

    return letters


def draw_diamond_cursor(screen, mouse_pos, trail):
    for i, pos in enumerate(trail):
        alpha = int(25 + i * (150 / max(1, len(trail))))
        size = int(5 + i * 0.7)

        trail_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        cx = size * 2
        cy = size * 2

        points = [
            (cx, cy - size),
            (cx + size, cy),
            (cx, cy + size),
            (cx - size, cy),
        ]

        pygame.draw.polygon(trail_surface, (0, 255, 90, alpha), points)
        screen.blit(trail_surface, (pos[0] - cx, pos[1] - cy))

    mx, my = mouse_pos
    size = 12

    glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
    cx, cy = 30, 30

    glow_points = [
        (cx, cy - size - 8),
        (cx + size + 8, cy),
        (cx, cy + size + 8),
        (cx - size - 8, cy),
    ]

    pygame.draw.polygon(glow_surface, (0, 255, 90, 70), glow_points)
    screen.blit(glow_surface, (mx - cx, my - cy))

    points = [
        (mx, my - size),
        (mx + size, my),
        (mx, my + size),
        (mx - size, my),
    ]

    pygame.draw.polygon(screen, NEON_LIGHT, points)
    pygame.draw.polygon(screen, NEON_GREEN, points, 2)


class FinalRoom:
    def __init__(self, title_font, subtitle_font, small_font, rain_font, width=800, height=600):
        self.width = width
        self.height = height

        self.title_font = title_font
        self.subtitle_font = subtitle_font
        self.small_font = small_font
        self.rain_font = rain_font

        self.rain = CuttableMatrixRain(rain_font, count=65, width=width, height=height)

        # Change to "Congratulations" if you want the spelling fixed.
        self.title_letters = create_repel_text("Congradulations", title_font, width // 2, 70)
        self.subtitle_letters = create_repel_text("DeadLock Prevented", subtitle_font, width // 2, 145)

        self.trail = []
        self.last_mouse_pos = None

    def reset(self):
        self.rain = CuttableMatrixRain(self.rain_font, count=65, width=self.width, height=self.height)
        self.trail = []
        self.last_mouse_pos = None

        for letter in self.title_letters:
            letter.reset()

        for letter in self.subtitle_letters:
            letter.reset()

    def update_and_draw(self, screen, mouse_pos):
        pygame.mouse.set_visible(False)

        self.rain.update_and_draw(screen, mouse_pos)

        if self.last_mouse_pos != mouse_pos:
            self.trail.append(mouse_pos)

        self.last_mouse_pos = mouse_pos

        if len(self.trail) > 22:
            self.trail.pop(0)

        panel = pygame.Rect(85, 42, 630, 170)

        panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (0, 35, 12, 185),
            pygame.Rect(0, 0, panel.width, panel.height),
            border_radius=18,
        )
        screen.blit(panel_surface, panel.topleft)

        pygame.draw.rect(screen, NEON_GREEN, panel, 2, border_radius=18)

        glow_panel = pygame.Surface((650, 190), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_panel,
            (0, 255, 90, 45),
            pygame.Rect(10, 10, 630, 170),
            4,
            border_radius=20,
        )
        screen.blit(glow_panel, (75, 32))

        for letter in self.title_letters:
            letter.update(mouse_pos)
            letter.draw(screen)

        for letter in self.subtitle_letters:
            letter.update(mouse_pos)
            letter.draw(screen)

        message = self.small_font.render(
            "SYSTEM STATUS: ESCAPE COMPLETE  |  MOVE CURSOR TO CUT THE MATRIX",
            True,
            (120, 255, 150),
        )
        screen.blit(message, (112, 515))

        exit_text = self.small_font.render("ESC // EXIT", True, (90, 180, 100))
        screen.blit(exit_text, (350, 550))

        draw_diamond_cursor(screen, mouse_pos, self.trail)