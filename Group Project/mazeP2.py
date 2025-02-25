import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
TILE = 40
WIDTH, HEIGHT = 800, 640
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()

player_img = pygame.image.load(f'..\\Group Project\\Maze\\astronaut.png').convert_alpha() 
coin_img = pygame.image.load(f'..\\Group Project\\Maze\\coin.png').convert_alpha()
pitfall_img = pygame.image.load(f'..\\Group Project\\Maze\\pitfall.png').convert_alpha()
wall_img = pygame.image.load(f'..\\Group Project\\Maze\\wall.jpg').convert_alpha()
chatbot_img = pygame.image.load(f'..\\Group Project\\Maze\\chatbot.png').convert_alpha()
hint1_img = pygame.image.load(f'..\\Group Project\\Maze\\Hint1.png').convert_alpha()
hint2_img = pygame.image.load(f'..\\Group Project\\Maze\\Hint2.png').convert_alpha()

player_img = pygame.transform.scale(player_img, (TILE, TILE))
coin_img = pygame.transform.scale(coin_img, (TILE, TILE))
pitfall_img = pygame.transform.scale(pitfall_img, (TILE, TILE))
wall_img = pygame.transform.scale(wall_img, (TILE, TILE))
chatbot_img = pygame.transform.scale(chatbot_img, (TILE, TILE))
hint1_img = pygame.transform.scale(hint1_img, (TILE, TILE))
hint2_img = pygame.transform.scale(hint2_img, (TILE, TILE))

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.image = player_img
        self.speed = 4

    def move(self, walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed

        # Move the player and check collisions
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x -= dx

        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.y -= dy

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# Goal class
class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
        self.color = GREEN

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Chatbot
class Chatbot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
        self.image = chatbot_img

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


# Load a room
def load_room(index):
    global walls, pitfalls, coins, goal, hints1, hints2, chatbot
    walls, pitfalls, coins, hints1, hints2 = [], [], [], [], []
    maze = mazes[index]

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "W":
                walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
            elif cell == "C":
                coins.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
            elif cell == "P":
                pitfalls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
            elif cell == "G":
                goal = Goal(x, y)
            elif cell == "R":
                chatbot = Chatbot(x,y)
            elif cell == "A":
                hints1.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
            elif cell == "B":
                hints2.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))

# Define mazes for three rooms
mazes = [
    # Room 1
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W.WW.....C.......CPW",
        "W....WWWWW.WWWWCWWWW",
        "WWWW.WWWWW....W..WWW",
        "WP.......WW.W.WW..WW",
        "WW.W.WWW.WW.W.WWW.WW",
        "W..W..C.PW.CW.....CW",
        "W.WW.WWW...WWPWWW.WW",
        "W.WW.WWWWW.WW.WWW.WW",
        "WAW....CP.C....WW..W",
        "WPWWWWWWWW.WWW.WWW.W",
        "WWWWPB.WWW..WW.WWW.W",
        "WWWWWW..P...WW...W.W",
        "WW.....WWWW.WWWWCW.W",
        "WA.WWW....C......W.W",
        "WWWWWWWWWWWWWWWW...G",
        "W.WWWWWWWWWWWWWWWWWWW",
    ],
    # Room 2
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W.......WWWWWWWWWWWW",
        "W.WWWWW............W",
        "W.WWWWWCWWW.WWWW.W.W",
        "W.........W....W.W.W",
        "WWW.WWWWW.WWWW.WP..W",
        "WWW....WW...WW.WWW.W",
        "WWW.WW..WWWCWW.WWW.W",
        "WPC.WWW.WWW.WWC..WCW",
        "WWW.WWW.WWW..WWW.WWW",
        "WWW.WWWC.....WWWC.WW",
        "W...WWW.WWWW.WWWW.WW",
        "WCWWWWWP.CWW.C.PW.WW",
        "W.WWWWWWW.WWWWW.W.WW",
        "WP....C............W",
        "WWWWWWWWWWWWWWWWWW.G",
    ],
    # Room 3
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W...C..WWWWW....CWWWW",
        "W.WWWW....C..WWWP..WW",
        "W.WWWWCWWWWW..WWWW.WW",
        "WC.WWW.....WWW..CWCWW",
        "WW...W.WWW.WWWWW.W.WW",
        "WW.WPC.WWW.....W...WW",
        "WW.WWW...WWWWW.WWW.WW",
        "WW..WW.W...WWWC..W..W",
        "WWW.WW.WWW.WWWWW.WWPW",
        "WW..WW.WWW...P....WCW",
        "WW.WWWC..WW.WWWWW...W",
        "WWCWWWWWPWWP.C.WWW.WW",
        "WW.WWWC..WWWWW.WWW.WW",
        "WWP....W...C.......WW",
        "WWWWWWWWWWWWWWWWWW.R",
    ],
]

# Initialize game variables
current_room_index = 0
walls, pitfalls, coins, hints1, hints2, goal, chatbot = [], [], [], [], [], None, None
player = Player(1 * TILE, 1 * TILE)

# Load the first room
load_room(current_room_index)

# Main game loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    player.move(walls)

    # Check for coin collection
    for coin in coins[:]:
        if player.rect.colliderect(coin):
            coins.remove(coin)  # Remove coin on collision

    for hint1 in hints1[:]:
        if player.rect.colliderect(hint1):
            hints1.remove(hint1)  # Remove coin on collision

    for hint2 in hints2[:]:
        if player.rect.colliderect(hint2):
            hints2.remove(hint2)  # Remove coin on collision

    # Check for pitfalls
    for pitfall in pitfalls:
        if player.rect.colliderect(pitfall):
            print("You fell into a pitfall!")
            running = False  # End game if player hits a pitfall
    
    if goal != None:
        # Check if player reaches the goal
        if player.rect.colliderect(goal.rect):
            current_room_index += 1
            if current_room_index < len(mazes):
                load_room(current_room_index)
                player.rect.topleft = (1 * TILE, 1 * TILE)  # Reset player position
            elif player.rect.colliderect(chatbot.rect):
                print("You completed all rooms!")
                running = False  # End the game
    else:
        if player.rect.colliderect(chatbot.rect):
            print("You completed all rooms!")
            running = False  # End the game

    
    # Draw everything
    for wall in walls:
        screen.blit(wall_img, (wall.x, wall.y))
    for coin in coins:
        screen.blit(coin_img, (coin.x, coin.y))
    for hint1 in hints1:
        screen.blit(hint1_img, (hint1.x, hint1.y))
    for hint2 in hints2:
        screen.blit(hint2_img, (hint2.x, hint2.y))
    for pitfall in pitfalls:
        screen.blit(pitfall_img, (pitfall.x, pitfall.y))
    
    player.draw(screen)
    
    if goal != None and chatbot == None:
        goal.draw(screen)
    else:
        chatbot.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
#sys.exit()
