import pygame
import math
import sys
import random

WIDTH, HEIGHT = 1200, 675
VIEW_WIDTH = 900
HUD_WIDTH = WIDTH - VIEW_WIDTH

TILE = 64
FOV = math.radians(65)
HALF_FOV = FOV / 2
NUM_RAYS = 240
MAX_DEPTH = 900
RAY_STEP = 3

MAZE = [
    "111111111111111",
    "100000000000001",
    "101110111011101",
    "100010001000001",
    "111010101110101",
    "100000100000001",
    "101110111010101",
    "100010000010001",
    "101011101110101",
    "100000000000001",
    "111111111111111",
]

EMERALD = (20, 220, 145)
DARK_EMERALD = (5, 65, 48)
GOLD = (238, 190, 75)
PALE_GOLD = (255, 225, 145)
WHITE = (235, 240, 225)
DARK = (5, 13, 17)


class CyberMaze:
    def __init__(self, screen):
        self.screen = screen
        self.player_x = 96
        self.player_y = 96
        self.angle = 0.0

        self.keys = [
            [3 * TILE + 32, 3 * TILE + 32],
            [11 * TILE + 32, 5 * TILE + 32],
            [7 * TILE + 32, 9 * TILE + 32],
        ]

        self.collected = 0
        self.won = False
        self.mouse_locked = True

        self.health = 100
        self.score = 0
        self.elapsed = 0.0

        self.font_small = pygame.font.SysFont("georgia", 17)
        self.font_medium = pygame.font.SysFont("georgia", 23, bold=True)
        self.font_large = pygame.font.SysFont("georgia", 36, bold=True)

        self.ray_depths = [MAX_DEPTH] * NUM_RAYS
        self.particles = []
        self.animation = 0.0

        for _ in range(45):
            self.particles.append([
                random.randint(0, VIEW_WIDTH),
                random.randint(0, HEIGHT),
                random.uniform(0.3, 1.2),
            ])

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def is_wall(self, x, y):
        col = int(x // TILE)
        row = int(y // TILE)

        if row < 0 or row >= len(MAZE):
            return True
        if col < 0 or col >= len(MAZE[0]):
            return True

        return MAZE[row][col] == "1"

    def movement(self, dt):
        if self.won:
            return

        keys = pygame.key.get_pressed()
        speed = 165 * dt

        move_x = 0
        move_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_x += math.cos(self.angle) * speed
            move_y += math.sin(self.angle) * speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_x -= math.cos(self.angle) * speed
            move_y -= math.sin(self.angle) * speed

        if keys[pygame.K_a]:
            move_x += math.cos(self.angle - math.pi / 2) * speed
            move_y += math.sin(self.angle - math.pi / 2) * speed

        if keys[pygame.K_d]:
            move_x += math.cos(self.angle + math.pi / 2) * speed
            move_y += math.sin(self.angle + math.pi / 2) * speed

        if keys[pygame.K_LEFT]:
            self.angle -= 1.8 * dt
        if keys[pygame.K_RIGHT]:
            self.angle += 1.8 * dt

        new_x = self.player_x + move_x
        new_y = self.player_y + move_y

        if not self.is_wall(new_x, self.player_y):
            self.player_x = new_x
        if not self.is_wall(self.player_x, new_y):
            self.player_y = new_y

        self.angle %= math.tau

        self.collect_keys()
        self.elapsed += dt

    def mouse_control(self, event):
        if event.type == pygame.MOUSEMOTION and self.mouse_locked:
            self.angle += event.rel[0] * 0.003
            self.angle %= math.tau

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.mouse_locked = False
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)

        if event.type == pygame.MOUSEBUTTONDOWN and not self.mouse_locked:
            self.mouse_locked = True
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)

    def collect_keys(self):
        for key in self.keys[:]:
            distance = math.hypot(
                key[0] - self.player_x,
                key[1] - self.player_y
            )

            if distance < 34:
                self.keys.remove(key)
                self.collected += 1
                self.score += 100

    def check_exit(self):
        exit_x = 13 * TILE + 32
        exit_y = 9 * TILE + 32

        distance = math.hypot(
            exit_x - self.player_x,
            exit_y - self.player_y
        )

        if distance < 42 and self.collected == 3:
            self.won = True
            self.score += max(0, int(500 - self.elapsed * 2))

    def draw_environment(self):
        for y in range(HEIGHT // 2):
            shade = max(3, 20 - int(y / 25))
            pygame.draw.line(
                self.screen,
                (shade, shade + 12, shade + 13),
                (0, y),
                (VIEW_WIDTH, y)
            )

        for y in range(HEIGHT // 2, HEIGHT):
            progress = (y - HEIGHT // 2) / (HEIGHT // 2)
            shade = int(10 + progress * 13)

            pygame.draw.line(
                self.screen,
                (shade, shade + 15, shade + 12),
                (0, y),
                (VIEW_WIDTH, y)
            )

        # Subtle floor perspective lines
        for i in range(1, 10):
            y = HEIGHT // 2 + i * i * 4
            if y < HEIGHT:
                pygame.draw.line(
                    self.screen,
                    (12, 45, 36),
                    (0, y),
                    (VIEW_WIDTH, y),
                    1
                )

    def cast_rays(self):
        self.ray_depths = [MAX_DEPTH] * NUM_RAYS
        column_width = VIEW_WIDTH / NUM_RAYS

        for ray in range(NUM_RAYS):
            ray_angle = self.angle - HALF_FOV + (
                ray / NUM_RAYS
            ) * FOV

            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            distance = 0
            hit_x = self.player_x
            hit_y = self.player_y

            while distance < MAX_DEPTH:
                distance += RAY_STEP
                hit_x = self.player_x + cos_a * distance
                hit_y = self.player_y + sin_a * distance

                if self.is_wall(hit_x, hit_y):
                    break

            corrected = distance * math.cos(ray_angle - self.angle)
            corrected = max(1, corrected)
            self.ray_depths[ray] = corrected

            wall_height = min(
                HEIGHT * 2,
                int((TILE * HEIGHT) / corrected)
            )

            wall_top = HEIGHT // 2 - wall_height // 2
            wall_bottom = HEIGHT // 2 + wall_height // 2

            brightness = max(0.12, 1 - corrected / 850)

            # Stone wall lighting
            texture = int((hit_x + hit_y) // 10) % 3
            base = [48, 65, 58][texture]

            red = int((base + 10) * brightness)
            green = int((base + 35) * brightness)
            blue = int((base + 22) * brightness)

            if int(hit_x) % TILE < 5 or int(hit_y) % TILE < 5:
                red = int(red * 0.55)
                green = int(green * 0.55)
                blue = int(blue * 0.55)

            x = int(ray * column_width)
            w = math.ceil(column_width) + 1

            pygame.draw.rect(
                self.screen,
                (red, green, blue),
                (x, wall_top, w, wall_height)
            )

            # Emerald magical wall seams
            if int(hit_x + hit_y) % 97 < 4:
                pygame.draw.line(
                    self.screen,
                    (15, int(90 * brightness), 58),
                    (x, wall_top),
                    (x, wall_bottom),
                    1
                )

            # Wall top and bottom shadow
            pygame.draw.line(
                self.screen,
                (8, 24, 21),
                (x, wall_top),
                (x, wall_top + 3),
                2
            )

    def project_object(self, x, y):
        dx = x - self.player_x
        dy = y - self.player_y

        distance = math.hypot(dx, dy)
        angle_to_object = math.atan2(dy, dx)

        relative_angle = (
            angle_to_object - self.angle + math.pi
        ) % math.tau - math.pi

        if abs(relative_angle) > HALF_FOV + 0.2:
            return None

        if distance < 1:
            return None

        screen_x = int(
            (0.5 + relative_angle / FOV) * VIEW_WIDTH
        )

        ray_index = int(screen_x / VIEW_WIDTH * NUM_RAYS)
        ray_index = max(0, min(NUM_RAYS - 1, ray_index))

        if distance > self.ray_depths[ray_index] + 20:
            return None

        size = min(HEIGHT * 1.2, int(HEIGHT * 0.75 / distance * 100))

        screen_y = HEIGHT // 2 + int(size * 0.10)

        return screen_x, screen_y, size, distance

    def draw_key_sprite(self, x, y):
        projected = self.project_object(x, y)
        if not projected:
            return

        sx, sy, size, distance = projected

        if size < 4:
            return

        radius = max(3, size // 7)
        pulse = 1 + 0.15 * math.sin(self.animation * 3)

        # Golden magical glow
        glow_radius = int(radius * 2.8 * pulse)

        glow = pygame.Surface(
            (glow_radius * 2 + 4, glow_radius * 2 + 4),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (255, 185, 40, 35),
            (glow_radius + 2, glow_radius + 2),
            glow_radius
        )

        self.screen.blit(
            glow,
            (sx - glow_radius - 2, sy - glow_radius - 2)
        )

        # Key ring
        pygame.draw.circle(
            self.screen,
            PALE_GOLD,
            (sx, sy),
            radius,
            max(2, radius // 4)
        )

        pygame.draw.circle(
            self.screen,
            GOLD,
            (sx, sy),
            max(2, radius // 2)
        )

        # Key shaft and teeth
        shaft = max(2, radius // 3)
        pygame.draw.line(
            self.screen,
            GOLD,
            (sx, sy + radius),
            (sx, sy + radius * 3),
            shaft
        )

        pygame.draw.line(
            self.screen,
            PALE_GOLD,
            (sx, sy + radius * 2),
            (sx + radius, sy + radius * 2),
            shaft
        )

    def draw_portal(self):
        portal_x = 13 * TILE + 32
        portal_y = 9 * TILE + 32

        projected = self.project_object(portal_x, portal_y)
        if not projected:
            return

        sx, sy, size, distance = projected

        if size < 8:
            return

        radius = max(8, size // 2)
        pulse = 1 + 0.04 * math.sin(self.animation * 2)

        width = max(4, radius // 8)
        rect = pygame.Rect(
            sx - radius,
            sy - radius * 1.45,
            radius * 2,
            radius * 2.9
        )

        # Magical portal glow
        glow_size = min(400, radius * 3)

        glow = pygame.Surface(
            (glow_size * 2, glow_size * 2),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            glow,
            (255, 190, 60, 30),
            (glow_size // 3, glow_size // 5,
             glow_size * 4 // 3, glow_size * 8 // 5)
        )

        self.screen.blit(
            glow,
            (sx - glow_size, sy - glow_size)
        )

        # Portal frame
        pygame.draw.ellipse(
            self.screen,
            (105, 68, 24),
            rect,
            width * 3
        )

        pygame.draw.ellipse(
            self.screen,
            GOLD,
            rect,
            width
        )

        inner = rect.inflate(-width * 4, -width * 4)

        pygame.draw.ellipse(
            self.screen,
            PALE_GOLD,
            inner,
            max(2, width // 2)
        )

        # Portal center
        center_rect = inner.inflate(-width * 3, -width * 3)

        pygame.draw.ellipse(
            self.screen,
            (8, 50, 37),
            center_rect
        )

        pygame.draw.arc(
            self.screen,
            EMERALD,
            center_rect,
            self.animation % math.tau,
            (self.animation % math.tau) + math.pi * 1.5,
            max(2, width)
        )

    def draw_particles(self):
        for particle in self.particles:
            particle[1] -= particle[2]

            if particle[1] < 0:
                particle[1] = HEIGHT
                particle[0] = random.randint(0, VIEW_WIDTH)

            x, y = int(particle[0]), int(particle[1])

            pygame.draw.circle(
                self.screen,
                (55, 125, 91),
                (x, y),
                1
            )

    def draw_objects(self):
        # Draw distant objects first
        objects = []

        for key in self.keys:
            distance = math.hypot(
                key[0] - self.player_x,
                key[1] - self.player_y
            )
            objects.append((distance, "key", key))

        portal = (13 * TILE + 32, 9 * TILE + 32)
        distance = math.hypot(
            portal[0] - self.player_x,
            portal[1] - self.player_y
        )
        objects.append((distance, "portal", portal))

        objects.sort(reverse=True)

        for _, kind, position in objects:
            if kind == "key":
                self.draw_key_sprite(*position)
            else:
                self.draw_portal()

    def draw_hud(self):
        panel = pygame.Rect(VIEW_WIDTH, 0, HUD_WIDTH, HEIGHT)

        pygame.draw.rect(self.screen, (7, 19, 20), panel)
        pygame.draw.line(
            self.screen,
            (27, 104, 75),
            (VIEW_WIDTH, 0),
            (VIEW_WIDTH, HEIGHT),
            2
        )

        x = VIEW_WIDTH + 25

        title = self.font_large.render("CYBER", True, PALE_GOLD)
        subtitle = self.font_medium.render("MAZE ESCAPE", True, EMERALD)

        self.screen.blit(title, (x, 38))
        self.screen.blit(subtitle, (x, 82))

        pygame.draw.line(
            self.screen,
            GOLD,
            (x, 124),
            (WIDTH - 25, 124),
            1
        )

        # Player status
        label = self.font_small.render(
            "PLAYER STATUS",
            True,
            (155, 180, 160)
        )
        self.screen.blit(label, (x, 151))

        health_text = self.font_medium.render(
            f"HEALTH  {self.health}%",
            True,
            WHITE
        )
        self.screen.blit(health_text, (x, 184))

        pygame.draw.rect(
            self.screen,
            (35, 55, 48),
            (x, 220, 245, 13),
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            EMERALD,
            (x, 220, int(245 * self.health / 100), 13),
            border_radius=6
        )

        # Keys
        self.screen.blit(
            self.font_small.render("ANCIENT KEYS", True, GOLD),
            (x, 268)
        )

        self.screen.blit(
            self.font_large.render(
                f"{self.collected} / 3",
                True,
                PALE_GOLD
            ),
            (x, 296)
        )

        # Score and time
        self.screen.blit(
            self.font_small.render("SCORE", True, (155, 180, 160)),
            (x, 365)
        )

        self.screen.blit(
            self.font_medium.render(
                str(self.score),
                True,
                GOLD
            ),
            (x, 390)
        )

        self.screen.blit(
            self.font_small.render("TIME", True, (155, 180, 160)),
            (x, 440)
        )

        minutes = int(self.elapsed) // 60
        seconds = int(self.elapsed) % 60

        self.screen.blit(
            self.font_medium.render(
                f"{minutes:02}:{seconds:02}",
                True,
                WHITE
            ),
            (x, 465)
        )

        pygame.draw.line(
            self.screen,
            (27, 104, 75),
            (x, 515),
            (WIDTH - 25, 515),
            1
        )

        self.screen.blit(
            self.font_small.render("CONTROLS", True, GOLD),
            (x, 536)
        )

        controls = [
            "WASD  - Move",
            "MOUSE - Look around",
            "ESC   - Release mouse",
            "Find all 3 keys to escape",
        ]

        for i, line in enumerate(controls):
            text = self.font_small.render(
                line,
                True,
                (170, 190, 175)
            )
            self.screen.blit(text, (x, 565 + i * 23))

    def draw_crosshair(self):
        cx = VIEW_WIDTH // 2
        cy = HEIGHT // 2

        pygame.draw.circle(
            self.screen,
            (210, 195, 135),
            (cx, cy),
            5,
            1
        )

        pygame.draw.line(
            self.screen,
            (210, 195, 135),
            (cx - 10, cy),
            (cx - 5, cy),
            1
        )

        pygame.draw.line(
            self.screen,
            (210, 195, 135),
            (cx + 5, cy),
            (cx + 10, cy),
            1
        )

        pygame.draw.line(
            self.screen,
            (210, 195, 135),
            (cx, cy - 10),
            (cx, cy - 5),
            1
        )

        pygame.draw.line(
            self.screen,
            (210, 195, 135),
            (cx, cy + 5),
            (cx, cy + 10),
            1
        )

    def draw_victory(self):
        overlay = pygame.Surface((VIEW_WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 12, 9, 210))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render(
            "MAZE ESCAPED!",
            True,
            PALE_GOLD
        )

        message = self.font_medium.render(
            "THE ANCIENT PORTAL HAS ACCEPTED YOU",
            True,
            EMERALD
        )

        score = self.font_medium.render(
            f"FINAL SCORE: {self.score}",
            True,
            WHITE
        )

        self.screen.blit(
            title,
            title.get_rect(center=(VIEW_WIDTH // 2, 260))
        )

        self.screen.blit(
            message,
            message.get_rect(center=(VIEW_WIDTH // 2, 325))
        )

        self.screen.blit(
            score,
            score.get_rect(center=(VIEW_WIDTH // 2, 385))
        )

    def draw(self, dt):
        self.animation += dt

        self.draw_environment()
        self.cast_rays()
        self.draw_objects()
        self.draw_particles()
        self.check_exit()
        self.draw_hud()
        self.draw_crosshair()

        if self.won:
            self.draw_victory()

        pygame.display.update()
