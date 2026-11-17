import pygame
import sys
import math
from pathlib import Path
from game_engine import CyberMaze

pygame.init()

WIDTH, HEIGHT = 1200, 675
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Maze Escape | Cinematic Edition")

clock = pygame.time.Clock()

BASE = Path(__file__).resolve().parent
BG_PATH = BASE / "Assets" / "Backgrounds" / "cinematic_menu.png"
MUSIC_PATH = BASE / "Assets" / "Backgrounds" / "fantasy_music.wav"

background = pygame.image.load(str(BG_PATH)).convert()
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

# Original artwork button positions preserved
buttons = {
    "start": pygame.Rect(135, 286, 370, 70),
    "help": pygame.Rect(155, 366, 345, 65),
    "settings": pygame.Rect(155, 428, 345, 65),
    "exit": pygame.Rect(155, 490, 345, 65),
}

# Additional About button
about_button = pygame.Rect(1060, 22, 115, 38)

WHITE = (245, 240, 220)
GOLD = (230, 190, 115)
DARK = (5, 18, 12)
EMERALD = (35, 150, 95)
MUTED = (175, 190, 180)

font_title = pygame.font.SysFont("arial", 34, bold=True)
font_text = pygame.font.SysFont("arial", 19)
font_small = pygame.font.SysFont("arial", 15)
font_button = pygame.font.SysFont("arial", 16, bold=True)

# Music initialization
music_available = False
music_enabled = True
music_volume = 0.35

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(str(MUSIC_PATH))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
    music_available = True

except pygame.error as error:
    print("Music could not start:", error)

game = None
game_started = False
running = True
active_panel = None

panel = pygame.Rect(340, 175, 520, 320)

music_toggle_rect = pygame.Rect(465, 275, 270, 42)
volume_rect = pygame.Rect(460, 365, 280, 12)
close_rect = pygame.Rect(490, 445, 220, 32)

yes_rect = pygame.Rect(445, 370, 125, 42)
no_rect = pygame.Rect(630, 370, 125, 42)


def draw_text_center(text, font, color, position):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=position))


def draw_menu():
    # Preserve original cinematic artwork
    screen.blit(background, (0, 0))

    mouse = pygame.mouse.get_pos()

    for rect in buttons.values():
        if rect.collidepoint(mouse):
            glow = pygame.Surface(
                (rect.width, rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow, (255, 220, 130, 35),
                glow.get_rect(), border_radius=12
            )
            screen.blit(glow, rect.topleft)

    # Additional About button
    about_color = GOLD if about_button.collidepoint(mouse) else WHITE

    pygame.draw.rect(
        screen, (5, 18, 12, 210),
        about_button, border_radius=8
    )
    pygame.draw.rect(
        screen, GOLD,
        about_button, 1, border_radius=8
    )

    draw_text_center(
        "ABOUT",
        font_button,
        about_color,
        about_button.center
    )

    if active_panel:
        draw_panel()


def draw_panel():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, DARK, panel, border_radius=16)
    pygame.draw.rect(screen, GOLD, panel, 2, border_radius=16)

    pygame.draw.line(
        screen, EMERALD,
        (panel.left + 35, panel.top + 65),
        (panel.right - 35, panel.top + 65), 2
    )

    if active_panel == "help":

        draw_text_center(
            "HOW TO PLAY",
            font_title, GOLD, (600, 220)
        )

        lines = [
            "W / UP       - Move Forward",
            "S / DOWN     - Move Backward",
            "A / D        - Move Sideways",
            "LEFT / RIGHT - Rotate View",
            "MOUSE        - Look Around",
            "",
            "COLLECT ALL 3 KEYS TO UNLOCK THE EXIT",
            "Each key gives 100 points."
        ]

        for i, line in enumerate(lines):
            draw_text_center(
                line, font_text, WHITE,
                (600, 275 + i * 24)
            )

    elif active_panel == "settings":

        draw_text_center(
            "SETTINGS",
            font_title, GOLD, (600, 220)
        )

        music_status = (
            "MUSIC: ON" if music_enabled else "MUSIC: OFF"
        )

        pygame.draw.rect(
            screen, EMERALD,
            music_toggle_rect, border_radius=8
        )
        pygame.draw.rect(
            screen, GOLD,
            music_toggle_rect, 1, border_radius=8
        )

        draw_text_center(
            music_status,
            font_text, WHITE,
            music_toggle_rect.center
        )

        draw_text_center(
            f"MUSIC VOLUME: {int(music_volume * 100)}%",
            font_text, WHITE, (600, 335)
        )

        pygame.draw.rect(
            screen, (75, 85, 75),
            (volume_rect.x, volume_rect.y,
             volume_rect.width, volume_rect.height),
            border_radius=6
        )

        fill_width = int(volume_rect.width * music_volume)

        pygame.draw.rect(
            screen, GOLD,
            (volume_rect.x, volume_rect.y,
             fill_width, volume_rect.height),
            border_radius=6
        )

        knob_x = volume_rect.x + fill_width

        pygame.draw.circle(
            screen, WHITE,
            (knob_x, volume_rect.centery), 10
        )

        if not music_available:
            draw_text_center(
                "Audio device unavailable",
                font_small, MUTED, (600, 405)
            )

    elif active_panel == "about":

        draw_text_center(
            "ABOUT THE GAME",
            font_title, GOLD, (600, 220)
        )

        lines = [
            "PROJECT: CYBER MAZE ESCAPE",
            "TYPE: 3D MAZE ADVENTURE GAME",
            "DEVELOPER: MST. SETARA KHATUN",
            "TECHNOLOGY: PYTHON + PYGAME-CE",
            "",
            "Explore the maze, collect keys and escape!",
            "PROJECT VERSION: 1.0"
        ]

        for i, line in enumerate(lines):
            draw_text_center(
                line, font_text, WHITE,
                (600, 275 + i * 27)
            )

    elif active_panel == "exit":

        draw_text_center(
            "EXIT GAME?",
            font_title, GOLD, (600, 245)
        )

        draw_text_center(
            "Are you sure you want to leave?",
            font_text, WHITE, (600, 310)
        )

        pygame.draw.rect(
            screen, (100, 35, 30),
            yes_rect, border_radius=8
        )

        pygame.draw.rect(
            screen, EMERALD,
            no_rect, border_radius=8
        )

        draw_text_center(
            "YES", font_button, WHITE, yes_rect.center
        )

        draw_text_center(
            "NO", font_button, WHITE, no_rect.center
        )

    if active_panel != "exit":
        pygame.draw.rect(
            screen, EMERALD,
            close_rect, border_radius=8
        )

        draw_text_center(
            "CLOSE",
            font_button, WHITE,
            close_rect.center
        )


def set_music_volume(value):
    global music_volume

    music_volume = max(0.0, min(1.0, value))

    if music_available:
        pygame.mixer.music.set_volume(
            music_volume if music_enabled else 0
        )


def handle_volume_click(mouse_x):
    relative = mouse_x - volume_rect.x
    value = relative / volume_rect.width
    set_music_volume(value)


while running:

    dt = clock.tick(60) / 1000

    if game_started:
        game.draw(dt)
    else:
        draw_menu()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_started:

            game.mouse_control(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_started = False
                    game = None
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)

        else:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if active_panel:
                        active_panel = None
                    else:
                        active_panel = "exit"

                elif event.key == pygame.K_F1:
                    active_panel = "about"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if active_panel == "settings":

                    if music_toggle_rect.collidepoint(event.pos):

                        music_enabled = not music_enabled

                        if music_available:
                            pygame.mixer.music.set_volume(
                                music_volume if music_enabled else 0
                            )

                    elif volume_rect.inflate(0, 25).collidepoint(event.pos):
                        handle_volume_click(event.pos[0])

                    elif close_rect.collidepoint(event.pos):
                        active_panel = None

                    else:
                        pass

                elif active_panel == "exit":

                    if yes_rect.collidepoint(event.pos):
                        running = False

                    elif no_rect.collidepoint(event.pos):
                        active_panel = None

                elif active_panel:

                    if close_rect.collidepoint(event.pos):
                        active_panel = None

                elif about_button.collidepoint(event.pos):
                    active_panel = "about"

                elif buttons["start"].collidepoint(event.pos):

                    game = CyberMaze(screen)
                    game.mouse_locked = True
                    game_started = True

                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    pygame.mouse.get_rel()

                elif buttons["help"].collidepoint(event.pos):
                    active_panel = "help"

                elif buttons["settings"].collidepoint(event.pos):
                    active_panel = "settings"

                elif buttons["exit"].collidepoint(event.pos):
                    active_panel = "exit"

            if event.type == pygame.MOUSEMOTION:
                if active_panel == "settings" and pygame.mouse.get_pressed()[0]:
                    if volume_rect.inflate(0, 25).collidepoint(event.pos):
                        handle_volume_click(event.pos[0])

    if game_started and not game.won:
        game.movement(dt)

    pygame.display.flip()

pygame.mouse.set_visible(True)
pygame.event.set_grab(False)

if music_available:
    pygame.mixer.music.stop()

pygame.quit()
sys.exit()
