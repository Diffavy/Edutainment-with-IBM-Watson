import pygame
import sys
import os
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 60
GRID_WIDTH, GRID_HEIGHT = 8, 8
CURRENT_SOURCE_POS = (0, 4)
TARGET_POS = (7, 7)
CURRENT = 2  # Amps
REQUIRED_FORCE = 324  # N
MAX_PATH_LENGTH = 12  # Optional challenge

# Colors
LIGHT_BLUE = (173, 216, 230)
BLUE = (100, 149, 237)
DARK_BLUE = (50, 60, 190)
PURPLE = (138, 43, 226)
GRAY = (120, 120, 120)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 105, 180)
BLACK = (0, 0, 0)

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level 10 - Magnetic Mayhem")
font = pygame.font.SysFont(None, 28)

# Load images
try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    rocket_img = pygame.image.load(os.path.join(base_path, 'rocketbroken.png'))
    rocket_img = pygame.transform.scale(rocket_img, (220, 250))

    space_bg = pygame.image.load(os.path.join(base_path, 'openspace.jpg'))
    space_bg = pygame.transform.scale(space_bg, (800, 600))

    rocket_solenoid_img = pygame.image.load(os.path.join(base_path, 'rocketsolenoid.png'))
    rocket_solenoid_img = pygame.transform.scale(rocket_solenoid_img, (800, 600))

    legend = pygame.image.load(os.path.join(base_path, 'legendb.png'))
    legend = pygame.transform.scale(legend, (300, 240))
    img_low = pygame.image.load(os.path.join(base_path, "tilelow.png"))
    img_stable = pygame.image.load(os.path.join(base_path, "tilestable.png"))
    img_strong = pygame.image.load(os.path.join(base_path, "tilestrong.png"))
    img_unstable = pygame.image.load(os.path.join(base_path, "tileunstable.png"))
    img_wall = pygame.image.load(os.path.join(base_path, "tilewall.png"))
    img_reverse = pygame.image.load(os.path.join(base_path, "tilerev.png"))
    weapon = pygame.image.load(os.path.join(base_path, "weapon.png"))
    source = pygame.image.load(os.path.join(base_path, "source.png"))
except Exception as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

img_low = pygame.transform.scale(img_low, (TILE_SIZE, TILE_SIZE))
img_stable = pygame.transform.scale(img_stable, (TILE_SIZE, TILE_SIZE))
img_strong = pygame.transform.scale(img_strong, (TILE_SIZE, TILE_SIZE))
img_unstable = pygame.transform.scale(img_unstable, (TILE_SIZE, TILE_SIZE))
img_reverse = pygame.transform.scale(img_reverse, (TILE_SIZE, TILE_SIZE))
img_wall = pygame.transform.scale(img_wall, (TILE_SIZE, TILE_SIZE)) 
weapon = pygame.transform.scale(weapon, (80,60))
source = pygame.transform.scale(source,(62, 62))
# Grid setup
tile_images = {
    'low': img_low,
    'stable': img_stable,
    'strong': img_strong,
    'unstable': img_unstable,
    'reverse': img_reverse,
    'wall': img_wall,
    'weapon' : weapon,
    'source' : source
}

# Magnetic field values (used for physics)
tile_types = {
    'low': {'B': 0.5},
    'stable': {'B': 1},
    'strong': {'B': 2},
    'unstable': {'B': 10},
    'reverse': {'B': -1},
    'wall': {'B': 0},
    'weapon': {'B': 0},
    'source' : {'B': 0}
}


# Use hardcoded grid design
grid_design = [
    'wwwbblrk',
    'wlwulwlk',
    'ullrbwlk',
    'sbkbwwlb',
    'blwlbblr',
    'bwkukwuu',
    'lwrukbll',
    'lurubblt'
]

char_map = {
    'l': 'low',
    'b': 'stable',
    'k': 'strong',
    'u': 'unstable',
    'w': 'wall',
    'r': 'reverse',
    's': 'source',  # Start
    't': 'weapon'   # Goal
}

grid = []
for y, row in enumerate(grid_design):
    grid_row = []
    for x, char in enumerate(row):
        tile_type = char_map[char]
        grid_row.append(tile_type)
        if char == 's':
            CURRENT_SOURCE_POS = (x, y)
        elif char == 't':
            TARGET_POS = (x, y)
    grid.append(grid_row)


selected_path = []
game_state = 'start'

def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def calculate_force(path):
    total_B = 0
    L = 0
    for x, y in path:
        if (x, y) != CURRENT_SOURCE_POS and (x, y) != TARGET_POS:
            total_B += tile_types[grid[y][x]]['B']
            L += 1
    return total_B * CURRENT * L, total_B, L

def draw_grid():
    screen.blit(space_bg, (0, 0))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile_type = grid[y][x]
            if tile_type in tile_images:
                screen.blit(tile_images[tile_type], rect.topleft)
            else:
                pygame.draw.rect(screen, tile_types[tile_type]['color'], rect)
            if tile_type != 'weapon' and tile_type != 'source':
                pygame.draw.rect(screen, BLACK, rect, 2)
            


            if (x, y) == CURRENT_SOURCE_POS:
                
                draw_text("I = 2A", x * TILE_SIZE + 5, y * TILE_SIZE + 15)
            elif (x, y) in selected_path:
                pygame.draw.circle(screen, GREEN, rect.center, 10)

    F, B, L = calculate_force(selected_path)
    draw_text(f"F = B × I × L", 10, SCREEN_HEIGHT - 120)
    draw_text(f"B = {B:.2f} T, I = {CURRENT} A, L = {L}, F = {F:.2f} N", 10, SCREEN_HEIGHT - 90)
    draw_text(f"Target F = {REQUIRED_FORCE} N", 490, SCREEN_HEIGHT - 120)
    draw_text(f"Max Steps Allowed = {MAX_PATH_LENGTH}", 490, SCREEN_HEIGHT - 350)
    draw_text(f"Clue : You will need 3 Strong Field Areas", 10, SCREEN_HEIGHT - 50)

def handle_grid_click(pos):
    global game_state
    x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
    if x >= GRID_WIDTH or y >= GRID_HEIGHT:
        return
    if grid[y][x] == 'wall':
        return
    if not selected_path:
        if (x, y) == CURRENT_SOURCE_POS:
            selected_path.append((x, y))
    else:
        last_x, last_y = selected_path[-1]
        if abs(x - last_x) + abs(y - last_y) == 1 and (x, y) not in selected_path:
            selected_path.append((x, y))
            if len(selected_path) > MAX_PATH_LENGTH + 2:  
                return  # Too long
            if (x, y) == TARGET_POS:
                F, _, _ = calculate_force(selected_path)
                if F == REQUIRED_FORCE:
                    game_state = 'end'

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'start':
                rocket_rect = rocket_img.get_rect(topleft=(280, 260))
                if rocket_rect.collidepoint(event.pos):
                    game_state = 'grid'
            elif game_state == 'grid':
                handle_grid_click(pygame.mouse.get_pos())

    if game_state == 'start':
        screen.blit(space_bg, (0, 0))
        screen.blit(rocket_img, (280, 240))
        draw_text("Click the rocket to begin repairs", 250, 520)
    elif game_state == 'grid':
        draw_grid()
        screen.blit(legend, (490, 5))
    elif game_state == 'end':
        screen.blit(space_bg, (0, 0))
        screen.blit(rocket_solenoid_img, (0, 0))
        draw_text("Weapon activated! Level complete.", 250, 70)

    pygame.display.flip()
    clock.tick(60)