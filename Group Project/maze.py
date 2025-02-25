import pygame
from random import choice, randrange

## Constants for screen dimensions and tile size
RES = width, height = 1202, 902
TILE = 100
cols, rows = width // TILE, height // TILE

#Add pitfalls, don't have coins come in rng


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        ## Walls represent the boundaries of the cell
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False
        self.thickness = 4

    ## Draw the cell's walls
    def draw(self, sc):
        x, y = self.x * TILE, self.y * TILE
        if self.walls["top"]:
            pygame.draw.line(
                sc, pygame.Color("grey75"), (x, y), (x + TILE, y), self.thickness
            )
        if self.walls["right"]:
            pygame.draw.line(
                sc,
                pygame.Color("grey75"),
                (x + TILE, y),
                (x + TILE, y + TILE),
                self.thickness,
            )
        if self.walls["bottom"]:
            pygame.draw.line(
                sc,
                pygame.Color("grey75"),
                (x + TILE, y + TILE),
                (x, y + TILE),
                self.thickness,
            )
        if self.walls["left"]:
            pygame.draw.line(
                sc, pygame.Color("grey75"), (x, y + TILE), (x, y), self.thickness
            )

    ## Get the rectangles representing each wall of the cell
    def get_rects(self):
        rects = []
        x, y = self.x * TILE, self.y * TILE
        if self.walls["top"]:
            rects.append(pygame.Rect((x, y), (TILE, self.thickness)))
        if self.walls["right"]:
            rects.append(pygame.Rect((x + TILE, y), (self.thickness, TILE)))
        if self.walls["bottom"]:
            rects.append(pygame.Rect((x, y + TILE), (TILE, self.thickness)))
        if self.walls["left"]:
            rects.append(pygame.Rect((x, y), (self.thickness, TILE)))
        return rects

    ## Check if a neighboring cell exists
    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return self.grid_cells[find_index(x, y)]

    ## Get neighboring cells that have not been visited
    def check_neighbors(self, grid_cells):
        self.grid_cells = grid_cells
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

## Function to remove walls between two adjacent cells
def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls["left"] = False
        next.walls["right"] = False
    elif dx == -1:
        current.walls["right"] = False
        next.walls["left"] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls["top"] = False
        next.walls["bottom"] = False
    elif dy == -1:
        current.walls["bottom"] = False
        next.walls["top"] = False


## Function to generate the maze
def generate_maze():
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    array = []
    break_count = 1

    while break_count != len(grid_cells):
        current_cell.visited = True
        next_cell = current_cell.check_neighbors(grid_cells)
        if next_cell:
            next_cell.visited = True
            break_count += 1
            array.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif array:
            current_cell = array.pop()
    return grid_cells


class coin:
    def __init__(self):
        ## Load the coin image
        self.img = pygame.image.load(f'..\\Group Project\\Maze\\coin.png').convert_alpha()
        self.img = pygame.transform.scale(self.img, (TILE - 10, TILE - 10))
        self.rect = self.img.get_rect()
        self.set_pos()

    ## Set the position of the coin randomly
    def set_pos(self):
        self.rect.topleft = randrange(cols) * TILE + 5, randrange(rows) * TILE + 5

    ## Draw the coin on the screen
    def draw(self):
        game_surface.blit(self.img, self.rect)

class Pitfall:
    def __init__(self, x, y):
        # Load the pitfall image
        self.img = pygame.image.load(f'..\\Group Project\\Maze\\pitfall.png').convert_alpha()
        self.img = pygame.transform.scale(self.img, (TILE - 10, TILE - 10))
        # Set the position of the pitfall
        self.rect = self.img.get_rect()
        self.rect.topleft = x * TILE + 5, y * TILE + 5

    def draw(self):
        # Draw the pitfall on the game surface
        game_surface.blit(self.img, self.rect)

# Predefined pitfall positions (adjust based on the maze's layout)
pitfall_positions = [
    (2, 2),  # Near the top-left corner
    (cols - 3, 2),  # Near the top-right corner
    (2, rows - 3),  # Near the bottom-left corner
    (cols - 3, rows - 3),  # Near the bottom-right corner
]

def check_pitfall():
    for pitfall in pitfall_list:
        if player_rect.colliderect(pitfall.rect):
            return True
    return False

## Check if the player has eaten any coin
def eat_coin():
    for coin in coin_list:
        if player_rect.collidepoint(coin.rect.center):
            coin.set_pos()
            return True
    return False

def is_collide(x, y):
    tmp_rect = player_rect.move(x, y)
    if tmp_rect.collidelist(walls_collide_list) == -1:
        return False
    return True

## Check if the game is over (time runs out)
def is_game_over():
    global time, score, record, FPS
    if time < 0:
        pygame.time.wait(700)
        player_rect.center = TILE // 2, TILE // 2
        [coin.set_pos() for coin in coin_list]
        set_record(record, score)
        record = get_record()
        time, score, FPS = 60, 0, 60


## Function to get the current record from a file
def get_record():
    try:
        with open("record") as f:
            return f.readline()
    except FileNotFoundError:
        with open("record", "w") as f:
            f.write("0")
            return "0"

## Function to set and update the record in a file
def set_record(record, score):
    rec = max(int(record), score)
    with open("record", "w") as f:
        f.write(str(rec))


## Initialize Pygame and set up the game window
FPS = 60
pygame.init()
game_surface = pygame.Surface(RES)
surface = pygame.display.set_mode((width + 300, height))
clock = pygame.time.Clock()

# Create pitfalls at these predefined positions
pitfall_list = [Pitfall(x, y) for x, y in pitfall_positions]

## Load background images
bg_game = pygame.image.load(f'..\\Group Project\\Maze\\main_BG.png').convert()
bg = pygame.image.load(f'..\\Group Project\\Maze\\side_BG.png').convert() 

## Generate the maze
maze = generate_maze()

## Player settings
player_speed = 5
player_img = pygame.image.load(f'..\\Group Project\\Maze\\astronaut.png').convert_alpha() 
player_img = pygame.transform.scale(
    player_img, (TILE - 2 * maze[0].thickness, TILE - 2 * maze[0].thickness)
)
player_rect = player_img.get_rect()
player_rect.center = TILE // 2, TILE // 2
directions = {
    "a": (-player_speed, 0),
    "d": (player_speed, 0),
    "w": (0, -player_speed),
    "s": (0, player_speed),
}
keys = {"a": pygame.K_LEFT, "d": pygame.K_RIGHT, "w": pygame.K_UP, "s": pygame.K_DOWN}
direction = (0, 0)

## coin settings
coin_list = [coin() for i in range(3)]

## Create a list of rectangles representing walls for collision detection
walls_collide_list = sum([cell.get_rects() for cell in maze], [])

## Timer, score, and record
pygame.time.set_timer(pygame.USEREVENT, 1000)
time = 60
score = 0
record = get_record()

## Fonts
font = pygame.font.SysFont("Impact", 150)
text_font = pygame.font.SysFont("Impact", 80)

while True:
    ## Blit background images
    surface.blit(bg, (width, 0))
    surface.blit(game_surface, (0, 0))
    game_surface.blit(bg_game, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.USEREVENT:
            time -= 1

    ## Handle player controls and movement
    pressed_key = pygame.key.get_pressed()
    for key, key_value in keys.items():
        if pressed_key[key_value] and not is_collide(*directions[key]):
            direction = directions[key]
            break
    if not is_collide(*direction):
        player_rect.move_ip(direction)

    ## Draw the maze
    [cell.draw(game_surface) for cell in maze]
    print(game_surface)
    ## Gameplay: Check if the player has eaten coin and if the game is over
    if eat_coin():
        FPS += 10
        score += 1
    is_game_over()

    # Check for pitfall collision
    if check_pitfall():
        # Reset the game or penalize the player
        print("Game Over! Fell into a pitfall!")
        pygame.time.wait(1000)
        player_rect.center = TILE // 2, TILE // 2  # Reset player position
        time, score, FPS = 60, 0, 60  # Reset game variables

    ## Draw the player
    game_surface.blit(player_img, player_rect)

    ## Draw coin items
    [coin.draw() for coin in coin_list]

    [pitfall.draw() for pitfall in pitfall_list]  # Draw pitfalls
    
    surface.blit(
        text_font.render("TIME", True, pygame.Color("cyan"), True), (width + 70, 30)
    )
    surface.blit(font.render(f"{time}", True, pygame.Color("cyan")), (width + 70, 130))
    surface.blit(
        text_font.render("score:", True, pygame.Color("forestgreen"), True),
        (width + 50, 350),
    )
    surface.blit(
        font.render(f"{score}", True, pygame.Color("forestgreen")), (width + 70, 430)
    )
    surface.blit(
        text_font.render("record:", True, pygame.Color("magenta"), True),
        (width + 30, 620),
    )
    surface.blit(
        font.render(f"{record}", True, pygame.Color("magenta")), (width + 70, 700)
    )

    pygame.display.flip()
    clock.tick(FPS)