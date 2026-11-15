import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Maze Escape: A 3D Maze Adventure Game")

clock = pygame.time.Clock()

# Colors
BG = (5, 7, 20)
CYAN = (0, 220, 255)
BLUE = (35, 100, 255)
PURPLE = (150, 60, 255)
WHITE = (240, 245, 255)
MUTED = (120, 145, 180)

# Fonts
logo_font = pygame.font.SysFont("consolas", 25, bold=True)
title_font = pygame.font.SysFont("arial", 66, bold=True)
subtitle_font = pygame.font.SysFont("arial", 23)
button_font = pygame.font.SysFont("arial", 22, bold=True)
small_font = pygame.font.SysFont("consolas", 14)

# Particles
particles = [
    [random.randrange(WIDTH), random.randrange(HEIGHT),
     random.uniform(0.3, 1.2), random.randint(1, 3)]
    for _ in range(90)
]

def text_center(text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=(x, y)))

def draw_background():
    screen.fill(BG)

    # Gradient background
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (5 + int(5*t), 7 + int(8*t), 20 + int(20*t))
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    # Background grid
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (12, 25, 48), (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (12, 25, 48), (0, y), (WIDTH, y))

    # Moving particles
    for p in particles:
        p[1] -= p[2]
        if p[1] < 0:
            p[1] = HEIGHT
            p[0] = random.randrange(WIDTH)

        pygame.draw.circle(
            screen, (0, 115, 175),
            (int(p[0]), int(p[1])), p[3]
        )

    # Scan line
    scan_y = int((pygame.time.get_ticks() * 0.08) % HEIGHT)
    pygame.draw.line(
        screen, (10, 35, 65),
        (0, scan_y), (WIDTH, scan_y), 2
    )

def draw_portal():
    cx, cy = 870, 365
    pulse = math.sin(pygame.time.get_ticks() * 0.003)

    # Portal glow rings
    for i in range(5, 0, -1):
        radius = 145 + i * 12 + int(pulse * 4)
        pygame.draw.circle(
            screen, (12, 20 + i*3, 55 + i*5),
            (cx, cy), radius, 2
        )

    # Portal
    pygame.draw.ellipse(
        screen, (15, 35, 80),
        (cx-110, cy-145, 220, 290)
    )

    pygame.draw.ellipse(
        screen, PURPLE,
        (cx-110, cy-145, 220, 290), 3
    )

    pygame.draw.ellipse(
        screen, CYAN,
        (cx-95, cy-130, 190, 260), 2
    )

    # Inner portal
    pygame.draw.ellipse(
        screen, (8, 20, 55),
        (cx-80, cy-115, 160, 230)
    )

    # Futuristic maze illustration
    maze_lines = [
        ((cx-55, cy-75), (cx+55, cy-75)),
        ((cx-55, cy-75), (cx-55, cy+70)),
        ((cx-55, cy), (cx+35, cy)),
        ((cx+35, cy), (cx+35, cy+75)),
        ((cx-55, cy+70), (cx+35, cy+70)),
        ((cx+35, cy+35), (cx+65, cy+35)),
    ]

    for start, end in maze_lines:
        pygame.draw.line(screen, CYAN, start, end, 4)

    # Portal core
    pygame.draw.circle(screen, BLUE, (cx, cy), 12)
    pygame.draw.circle(screen, WHITE, (cx, cy), 5)

    # Floating energy dots
    for i in range(8):
        angle = pygame.time.get_ticks() * 0.001 + i * math.pi / 4
        x = cx + math.cos(angle) * 165
        y = cy + math.sin(angle) * 190
        pygame.draw.circle(screen, CYAN, (int(x), int(y)), 3)

def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    hover = rect.collidepoint(pygame.mouse.get_pos())

    color = CYAN if hover else BLUE
    fill = (12, 42, 72) if hover else (10, 20, 45)

    pygame.draw.rect(screen, fill, rect, border_radius=9)
    pygame.draw.rect(screen, color, rect, 2, border_radius=9)

    label = button_font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))

    return rect

def draw_interface():
    draw_background()

    # Header
    pygame.draw.line(screen, (20, 70, 110),
                     (45, 75), (1155, 75), 1)

    pygame.draw.circle(screen, CYAN, (65, 42), 14, 3)
    text_center("CM", logo_font, WHITE, 65, 42)

    logo = logo_font.render("CYBER MAZE", True, WHITE)
    screen.blit(logo, (95, 29))

    text_center("MAIN MENU", small_font, CYAN, 1050, 42)

    # Left content
    text_center("WELCOME TO THE FUTURE", small_font,
                CYAN, 310, 160)

    title = title_font.render("CYBER MAZE", True, WHITE)
    screen.blit(title, (95, 220))

    title2 = title_font.render("ESCAPE", True, CYAN)
    screen.blit(title2, (95, 290))

    pygame.draw.rect(screen, PURPLE, (100, 380, 65, 4))

    description = [
        "A 3D MAZE ADVENTURE GAME",
        "Enter a mysterious cyber world.",
        "Solve the maze, collect keys,",
        "and discover the path to freedom."
    ]

    for i, line in enumerate(description):
        color = CYAN if i == 0 else MUTED
        font = subtitle_font if i == 0 else small_font
        screen.blit(font.render(line, True, color),
                    (100, 410 + i * 30))

    # Buttons
    start = draw_button("START ADVENTURE", 100, 570, 270, 58)
    exit_btn = draw_button("EXIT GAME", 390, 570, 170, 58)

    # Right portal illustration
    draw_portal()

    text_center("THE MAZE IS WAITING", small_font,
                CYAN, 870, 590)

    text_center("EXPLORE  |  SURVIVE  |  ESCAPE",
                small_font, MUTED, 870, 620)

    # Footer
    pygame.draw.line(screen, (20, 70, 110),
                     (45, 690), (1155, 690), 1)

    screen.blit(
        small_font.render("GAME PROJECT  |  VERSION 1.0",
                          True, MUTED), (50, 710)
    )

    screen.blit(
        small_font.render("POWERED BY PYGAME",
                          True, CYAN), (1000, 710)
    )

    return start, exit_btn

running = True
game_started = False

while running:
    start_button, exit_button = draw_interface()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not game_started:
                if start_button.collidepoint(event.pos):
                    game_started = True

                elif exit_button.collidepoint(event.pos):
                    running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_started:
                    game_started = False
                else:
                    running = False

    if game_started:
        screen.fill(BG)
        text_center("ADVENTURE INITIALIZING",
                    title_font, CYAN, WIDTH//2, 310)
        text_center("3D MAZE ENVIRONMENT - COMING NEXT",
                    subtitle_font, WHITE, WIDTH//2, 380)
        text_center("PRESS ESC TO RETURN",
                    small_font, MUTED, WIDTH//2, 440)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
