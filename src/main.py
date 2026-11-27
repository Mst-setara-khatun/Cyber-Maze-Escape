import pygame
import sys
import random
import math
from pathlib import Path

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 700
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON SHADOWS | Escape the Cyber Maze")
clock = pygame.time.Clock()

ROOT = Path(__file__).resolve().parent.parent
ASSET = ROOT / "Assets" / "Backgrounds"

WHITE = (240, 245, 255)
CYAN = (0, 225, 255)
PURPLE = (175, 75, 255)
PINK = (255, 75, 190)
DARK = (7, 10, 25)
GREEN = (80, 255, 150)
RED = (255, 75, 90)
MUTED = (145, 160, 190)

font_big = pygame.font.SysFont("arial", 48, bold=True)
font_title = pygame.font.SysFont("arial", 32, bold=True)
font = pygame.font.SysFont("arial", 22, bold=True)
font_small = pygame.font.SysFont("arial", 17)

try:
    menu_image = pygame.image.load(
        str(ASSET / "main_menu_design.png")
    ).convert()
    menu_image = pygame.transform.smoothscale(menu_image, (1200, 675))
except Exception:
    menu_image = pygame.Surface((1200, 675))
    menu_image.fill(DARK)

music_on = True
try:
    pygame.mixer.music.load(str(ASSET / "fantasy_music.wav"))
    pygame.mixer.music.set_volume(0.22)
    pygame.mixer.music.play(-1)
except Exception:
    pass

questions = [
    ("Which language is used in this game?", ["Python", "Java", "C++", "PHP"], 0),
    ("What does CPU stand for?", ["Computer Personal Unit", "Central Processing Unit", "Control Program Unit", "Central Power Unit"], 1),
    ("Which one is an input device?", ["Monitor", "Printer", "Keyboard", "Speaker"], 2),
    ("Which data structure uses FIFO?", ["Stack", "Queue", "Tree", "Graph"], 1),
    ("What does HTML stand for?", ["HyperText Markup Language", "HighText Machine Language", "Hyper Transfer Main Link", "Home Tool Markup Language"], 0),
    ("Which symbol is used for Python comments?", ["//", "<!-- -->", "#", "**"], 2),
    ("Which one is an operating system?", ["Python", "Windows", "HTML", "MySQL"], 1),
    ("What is the brain of a computer?", ["RAM", "Hard Disk", "CPU", "Monitor"], 2),
    ("Which protocol secures websites?", ["HTTP", "FTP", "HTTPS", "SMTP"], 2),
    ("What is binary form of decimal 2?", ["10", "11", "01", "100"], 0),
]

screen_name = "home"
buttons = []
score = 0
lives = 3
level = 1
question_number = 0
quiz_active = False
question_start = 0
message = ""
message_until = 0
particles = [[random.randrange(WIDTH), random.randrange(HEIGHT),
              random.uniform(.3, 1.2)] for _ in range(55)]

# Maze geometry: 25 columns x 13 rows
COLS, ROWS = 25, 13
TILE = 40
OX, OY = 100, 95
maze = []
player = [1, 1]
terminal = (23, 11)
exit_cell = (23, 1)
terminal_unlocked = False
exit_unlocked = False
move_cooldown = 0

coins = []
enemy_path = []
enemy_index = 0
enemy_direction = 1
enemy_pos = None
enemy_last_move = 0
enemy_hit_until = 0
collected_coins = 0


def text(value, f, color, center):
    surf = f.render(str(value), True, color)
    screen.blit(surf, surf.get_rect(center=center))


def make_maze():
    global maze, player, terminal_unlocked, exit_unlocked
    global coins, enemy_path, enemy_index, enemy_direction
    global enemy_pos, enemy_last_move, enemy_hit_until

    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    visited = set()

    def carve(cx, cy):
        visited.add((cx, cy))
        gx, gy = 2 * cx + 1, 2 * cy + 1
        maze[gy][gx] = 0
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 12 and 0 <= ny < 6 and (nx, ny) not in visited:
                maze[gy + dy][gx + dx] = 0
                carve(nx, ny)

    carve(0, 0)
    maze[11][23] = 0
    maze[1][23] = 0
    player = [1, 1]
    terminal_unlocked = False
    exit_unlocked = False

    for x in range(1, 24):
        if x % 2 == 1:
            maze[11][x] = 0
            maze[1][x] = 0
    for y in range(1, 12):
        if y % 2 == 1:
            maze[y][23] = 0

    # Find all maze cells reachable from the player.
    start = (1, 1)
    queue = [start]
    previous = {start: None}
    for cell in queue:
        x, y = cell
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nxt = (x + dx, y + dy)
            if (0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS
                    and maze[nxt[1]][nxt[0]] == 0 and nxt not in previous):
                previous[nxt] = cell
                queue.append(nxt)

    reachable = list(previous.keys())

    # Build a short enemy patrol route using connected maze cells.
    enemy_path = []
    candidates = [
        c for c in reachable
        if c not in (start, terminal, exit_cell)
        and abs(c[0] - start[0]) + abs(c[1] - start[1]) >= 5
    ]
    for _ in range(35):
        if len(candidates) < 2:
            break
        a, b = random.sample(candidates, 2)
        q = [a]
        came_from = {a: None}
        for cell in q:
            if cell == b:
                break
            x, y = cell
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nxt = (x + dx, y + dy)
                if (0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS
                        and maze[nxt[1]][nxt[0]] == 0 and nxt not in came_from):
                    came_from[nxt] = cell
                    q.append(nxt)
        if b in came_from:
            path = []
            cur = b
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            if 5 <= len(path) <= 13:
                enemy_path = path
                break

    enemy_index = 0
    enemy_direction = 1
    enemy_pos = enemy_path[0] if enemy_path else None
    enemy_last_move = pygame.time.get_ticks()
    enemy_hit_until = 0

    # Place six collectibles on reachable cells away from important objects.
    coin_spots = [
        c for c in reachable
        if c not in (start, terminal, exit_cell)
        and c not in enemy_path
    ]
    coins = random.sample(coin_spots, min(6, len(coin_spots)))

def start_game():
    global score, lives, level, question_number, screen_name, collected_coins
    score, lives, level, question_number = 0, 3, 1, 0
    collected_coins = 0
    make_maze()
    screen_name = "game"

def draw_menu(mouse):
    screen.fill(DARK)
    screen.blit(menu_image, (0, 12))
    for p in particles:
        p[1] -= p[2]
        if p[1] < 0:
            p[0], p[1] = random.randrange(WIDTH), HEIGHT
        pygame.draw.circle(screen, (75, 150, 220), (int(p[0]), int(p[1])), 1)

    global buttons
    buttons = [
        ("PLAY GAME", pygame.Rect(145, 334, 390, 59)),
        ("LEVEL SELECT", pygame.Rect(168, 397, 347, 43)),
        ("HOW TO PLAY", pygame.Rect(168, 450, 347, 43)),
        ("SETTINGS", pygame.Rect(168, 503, 347, 43)),
        ("EXIT GAME", pygame.Rect(168, 556, 347, 47)),
    ]
    for label, rect in buttons:
        if rect.collidepoint(mouse):
            pygame.draw.rect(screen, (210, 100, 255), rect, 2, border_radius=8)

def panel(title):
    pygame.draw.rect(screen, (8, 13, 34), (75, 55, 1050, 590), border_radius=18)
    pygame.draw.rect(screen, CYAN, (75, 55, 1050, 590), 2, border_radius=18)
    text(title, font_big, CYAN, (600, 100))


def draw_maze():
    now = pygame.time.get_ticks()
    pulse = (math.sin(now * 0.004) + 1) / 2

    screen.fill((3, 6, 19))

    # Neon maze tiles
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(OX + x*TILE, OY + y*TILE, TILE, TILE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, (15, 24, 49), rect)
                pygame.draw.rect(screen, (25, 54, 91), rect, 1)
                if (x + y) % 3 == 0:
                    pygame.draw.line(screen, (23, 39, 69),
                                     rect.topleft, rect.bottomright, 1)
            else:
                pygame.draw.rect(screen, (7, 13, 29), rect)
                pygame.draw.rect(screen, (12, 28, 48), rect, 1)

    # Animated terminal
    tx, ty = terminal
    tcx, tcy = OX + tx*TILE + 20, OY + ty*TILE + 20
    terminal_color = GREEN if terminal_unlocked else PURPLE
    pygame.draw.circle(screen, (*terminal_color,), (tcx, tcy),
                       19 + int(pulse * 4), 2)
    pygame.draw.rect(screen, terminal_color,
                     (tcx-11, tcy-11, 22, 22), border_radius=5)
    pygame.draw.circle(screen, WHITE, (tcx, tcy), 4)

    # Pulsing exit door
    ex, ey = exit_cell
    ecx, ecy = OX + ex*TILE + 20, OY + ey*TILE + 20
    door_color = GREEN if exit_unlocked else RED
    pygame.draw.circle(screen, door_color, (ecx, ecy),
                       20 + int(pulse * 5), 2)
    pygame.draw.rect(screen, door_color,
                     (ecx-12, ecy-15, 24, 30), border_radius=5)
    pygame.draw.circle(screen, WHITE, (ecx+5, ecy), 2)

    # Energy coins
    for index, (cx, cy) in enumerate(coins):
        x, y = OX + cx*TILE + 20, OY + cy*TILE + 20
        glow = 12 + int((math.sin(now * 0.006 + index) + 1) * 3)
        pygame.draw.circle(screen, (100, 75, 25), (x, y), glow)
        pygame.draw.circle(screen, (255, 205, 55), (x, y), 9)
        pygame.draw.circle(screen, (255, 245, 170), (x, y), 5)
        pygame.draw.circle(screen, WHITE, (x-2, y-3), 2)

    # Moving enemy
    if enemy_pos is not None:
        ax, ay = enemy_pos
        exx, eyy = OX + ax*TILE + 20, OY + ay*TILE + 20
        pygame.draw.circle(screen, (85, 15, 35), (exx, eyy), 20)
        pygame.draw.circle(screen, RED, (exx, eyy), 14)
        pygame.draw.circle(screen, WHITE, (exx-5, eyy-3), 3)
        pygame.draw.circle(screen, WHITE, (exx+5, eyy-3), 3)
        pygame.draw.line(screen, (70, 0, 20),
                         (exx-5, eyy+6), (exx+5, eyy+6), 2)

    # Animated player glow
    px, py = player
    pcx, pcy = OX + px*TILE + 20, OY + py*TILE + 20
    radius = 15 + int(pulse * 4)
    pygame.draw.circle(screen, (0, 65, 95), (pcx, pcy), radius + 7)
    pygame.draw.circle(screen, CYAN, (pcx, pcy), radius, 2)
    pygame.draw.circle(screen, CYAN, (pcx, pcy), 11)
    pygame.draw.circle(screen, WHITE, (pcx, pcy), 5)

    text("NEON SHADOWS  |  CYBER MAZE", font, WHITE, (600, 30))
    text(f"LEVEL {level}/10", font, CYAN, (145, 635))
    text(f"SCORE: {score}", font, WHITE, (330, 635))
    text(f"LIVES: {'♥ ' * lives}", font, PINK, (510, 635))
    text(f"COINS: {collected_coins}", font, (255, 210, 75), (700, 635))
    text("WASD / ARROWS: MOVE     E: TERMINAL     ENTER: EXIT",
         font_small, MUTED, (950, 635))

    if not terminal_unlocked:
        text("PURPLE TERMINAL: REACH AND PRESS E",
             font_small, PURPLE, (600, 670))
    else:
        text("EXIT UNLOCKED! REACH THE GREEN DOOR",
             font_small, GREEN, (600, 670))

def draw_quiz():
    panel("CYBER TERMINAL CHALLENGE")
    q, options, correct = questions[question_number]
    elapsed = (pygame.time.get_ticks() - question_start) / 1000
    remaining = max(0, 10 - elapsed)

    text(f"CHALLENGE {question_number+1}/10     SCORE: {score}     LIVES: {lives}",
         font, WHITE, (600, 165))
    bar = pygame.Rect(280, 205, 640, 15)
    pygame.draw.rect(screen, (45, 55, 80), bar, border_radius=7)
    pygame.draw.rect(screen, RED if remaining < 3 else CYAN,
                     (bar.x, bar.y, int(bar.width*remaining/10), bar.height),
                     border_radius=7)
    text(f"{remaining:.1f} SECONDS", font_small, WHITE, (600, 240))
    text(q, font_title, WHITE, (600, 300))

    global buttons
    buttons = []
    for i, option in enumerate(options):
        rect = pygame.Rect(300, 355+i*58, 600, 45)
        buttons.append((str(i+1)+". "+option, rect))
        color = PURPLE if rect.collidepoint(pygame.mouse.get_pos()) else (25, 38, 70)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, CYAN, rect, 1, border_radius=8)
        text(str(i+1)+". "+option, font, WHITE, rect.center)

    if remaining <= 0:
        lose_life()

def lose_life():
    global lives, quiz_active, message, message_until, screen_name
    lives -= 1
    quiz_active = False
    screen_name = "game"
    message = "TIME OUT! ONE LIFE LOST"
    message_until = pygame.time.get_ticks() + 1400
    if lives <= 0:
        finish_game(False)

def answer_question(index):
    global score, question_number, quiz_active, terminal_unlocked
    global message, message_until, screen_name
    if index == questions[question_number][2]:
        score += 10
        question_number += 1
        terminal_unlocked = True
        message = "CORRECT! EXIT DOOR UNLOCKED"
    else:
        global lives
        lives -= 1
        message = "WRONG ANSWER! LIFE LOST"
    quiz_active = False
    screen_name = "game"
    message_until = pygame.time.get_ticks() + 1600
    if lives <= 0:
        finish_game(False)

def finish_game(won):
    global screen_name
    screen_name = "victory" if won else "gameover"

def next_level():
    global level, question_number, quiz_active, screen_name
    if level >= 10:
        finish_game(True)
        return
    level += 1
    make_maze()
    screen_name = "game"
    quiz_active = False

def draw_result(won):
    screen.fill(DARK)
    panel("MAZE ESCAPED!" if won else "GAME OVER")
    text("CONGRATULATIONS! YOU ESCAPED THE CYBER MAZE!" if won
         else "THE CYBER MAZE WON THIS TIME!", font_title,
         GREEN if won else RED, (600, 270))
    text(f"FINAL SCORE: {score} / 100", font_title, CYAN, (600, 345))
    text(f"LEVEL REACHED: {level}/10", font, WHITE, (600, 395))
    global buttons
    buttons = [
        ("PLAY AGAIN", pygame.Rect(300, 475, 260, 55)),
        ("MAIN MENU", pygame.Rect(640, 475, 260, 55))
    ]
    for label, rect in buttons:
        pygame.draw.rect(screen, (20, 35, 65), rect, border_radius=9)
        pygame.draw.rect(screen, CYAN, rect, 2, border_radius=9)
        text(label, font, WHITE, rect.center)


def move_player(dx, dy):
    global player, coins, score, collected_coins, message, message_until
    nx, ny = player[0] + dx, player[1] + dy
    if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
        player = [nx, ny]
        if (nx, ny) in coins:
            coins.remove((nx, ny))
            collected_coins += 1
            score = min(100, score + 2)
            message = "ENERGY COIN COLLECTED! +2 BONUS"
            message_until = pygame.time.get_ticks() + 1100

def click_button(pos):
    global screen_name, music_on, quiz_active
    for i, (label, rect) in enumerate(buttons):
        if rect.collidepoint(pos):
            if screen_name == "home":
                if i == 0:
                    start_game()
                elif i == 1:
                    screen_name = "levels"
                elif i == 2:
                    screen_name = "info"
                elif i == 3:
                    screen_name = "settings"
                else:
                    pygame.quit()
                    sys.exit()
            elif screen_name == "quiz":
                answer_question(i)
            elif screen_name in ("victory", "gameover"):
                if i == 0:
                    start_game()
                else:
                    screen_name = "home"
            elif screen_name in ("info", "levels", "settings"):
                if screen_name == "settings" and i == 0:
                    music_on = not music_on
                    pygame.mixer.music.set_volume(.22 if music_on else 0)
                else:
                    screen_name = "home"

def draw_simple_page(title, lines):
    panel(title)
    for i, line in enumerate(lines):
        text(line, font, WHITE, (600, 250+i*55))
    global buttons
    buttons = [("BACK TO HOME", pygame.Rect(450, 520, 300, 55))]
    pygame.draw.rect(screen, (20, 35, 65), buttons[0][1], border_radius=8)
    pygame.draw.rect(screen, CYAN, buttons[0][1], 2, border_radius=8)
    text("BACK TO HOME", font, WHITE, buttons[0][1].center)

running = True

def keep_background_music_playing():
    try:
        if music_on:
            pygame.mixer.music.set_volume(0.25)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.set_volume(0.0)
    except pygame.error:
        pass


def update_enemy():
    global enemy_index, enemy_direction, enemy_pos, enemy_last_move
    global lives, player, message, message_until, enemy_hit_until

    if not enemy_path:
        return

    now = pygame.time.get_ticks()
    if now - enemy_last_move >= 430:
        enemy_index += enemy_direction
        if enemy_index >= len(enemy_path) - 1:
            enemy_index = len(enemy_path) - 1
            enemy_direction = -1
        elif enemy_index <= 0:
            enemy_index = 0
            enemy_direction = 1
        enemy_pos = enemy_path[enemy_index]
        enemy_last_move = now

    if enemy_pos == tuple(player) and now >= enemy_hit_until:
        lives -= 1
        player = [1, 1]
        enemy_hit_until = now + 1500
        message = "ENEMY ATTACK! ONE LIFE LOST"
        message_until = now + 1400
        if lives <= 0:
            finish_game(False)

while running:
    keep_background_music_playing()
    dt = clock.tick(FPS)
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if screen_name != "home":
                    screen_name = "home"
                    quiz_active = False

            if screen_name == "game" and not quiz_active:
                if event.key in (pygame.K_UP, pygame.K_w):
                    move_player(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    move_player(0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    move_player(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    move_player(1, 0)
                elif event.key == pygame.K_e:
                    if tuple(player) == terminal and not terminal_unlocked:
                        if question_number < 10:
                            quiz_active = True
                            question_start = pygame.time.get_ticks()
                            screen_name = "quiz"
                elif event.key == pygame.K_RETURN:
                    if tuple(player) == exit_cell and exit_unlocked:
                        next_level()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_button(event.pos)

    if screen_name == "home":
        draw_menu(mouse)

    elif screen_name == "game":
        update_enemy()
        draw_maze()
        if tuple(player) == terminal and not terminal_unlocked:
            text("PRESS E TO ACCESS TERMINAL", font_small, PURPLE, (600, 60))
        if tuple(player) == exit_cell:
            if exit_unlocked:
                text("PRESS ENTER TO ENTER NEXT LEVEL", font_small, GREEN, (600, 60))
            else:
                text("EXIT LOCKED - SOLVE THE TERMINAL", font_small, RED, (600, 60))
        if terminal_unlocked:
            exit_unlocked = True
        if message and pygame.time.get_ticks() < message_until:
            text(message, font, GREEN if "CORRECT" in message else RED, (600, 75))

    elif screen_name == "quiz":
        draw_quiz()

    elif screen_name == "info":
        draw_simple_page("HOW TO PLAY", [
            "Explore the maze using WASD or Arrow Keys.",
            "Find the purple terminal and press E.",
            "Answer the question within 10 seconds.",
            "Correct answers unlock the green exit.",
            "Reach the exit and press ENTER for next level.",
            "You have 3 lives. Complete all 10 levels!"
        ])

    elif screen_name == "levels":
        draw_simple_page("LEVEL SELECT", [
            f"CURRENT PROGRESS: LEVEL {level}/10",
            "Complete each maze to unlock the next one.",
            "Press BACK TO HOME to continue."
        ])

    elif screen_name == "settings":
        draw_simple_page("SETTINGS", [
            "Click the music toggle below to change volume.",
            "Music: " + ("ON" if music_on else "OFF")
        ])
        buttons = [
            ("TOGGLE MUSIC", pygame.Rect(450, 440, 300, 50)),
            ("BACK TO HOME", pygame.Rect(450, 520, 300, 55))
        ]
        for label, rect in buttons:
            pygame.draw.rect(screen, (20, 35, 65), rect, border_radius=8)
            pygame.draw.rect(screen, CYAN, rect, 2, border_radius=8)
            text(label, font, WHITE, rect.center)

    elif screen_name == "victory":
        draw_result(True)

    elif screen_name == "gameover":
        draw_result(False)

    pygame.display.flip()

pygame.quit()
sys.exit()
