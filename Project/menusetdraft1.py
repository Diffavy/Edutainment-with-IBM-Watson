import pygame
import sys
import os
import importlib  # For reloading modules (if necessary)


pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Edutainment")


try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    space_bg = pygame.image.load(os.path.join(base_path, 'openspace.jpg'))
    space_bg = pygame.transform.scale(space_bg, (WIDTH, HEIGHT))

    
    rocket_image = pygame.image.load(os.path.join(base_path, '1Rocket_Image.png'))
    rocket_image = pygame.transform.scale(rocket_image, (100, 150))

    # Load and scale planet 
    planet_images = [
        pygame.image.load(os.path.join(base_path, 'earth3.png')),
        pygame.image.load(os.path.join(base_path, 'mars2.png')),
        pygame.image.load(os.path.join(base_path, 'saturn2.png')),
        pygame.image.load(os.path.join(base_path, 'neptuno2.png')),
        pygame.image.load(os.path.join(base_path, 'alienplanet2.png'))
    ]
    planet_images = [pygame.transform.scale(planet, (120, 120)) for planet in planet_images]  # Larger size
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Fonts
font = pygame.font.Font(r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\high-orbit.ttf', 48)
small_font = pygame.font.Font(None, 36)

# Planet positions
planet_positions = [
    (WIDTH // 2 - 250, HEIGHT // 2 - 200),  # Top left
    (WIDTH // 2 + 150, HEIGHT // 2 - 200),  # Top right
    (WIDTH // 2 - 300, HEIGHT // 2 + 100),  # Bottom left
    (WIDTH // 2 + 200, HEIGHT // 2 + 100),  # Bottom right
    (WIDTH // 2 - 50, HEIGHT // 2 + 150),   # Center bottom
]

# Game states
STATE_MENU = "Menu"
STATE_LEVEL_SELECTION = "LevelSelection"
current_state = STATE_MENU
current_difficulty = None

# Game loop
running = True
while running:
    screen.blit(space_bg, (0, 0))
    for i, planet_pos in enumerate(planet_positions):
        screen.blit(planet_images[i], planet_pos)
    
    rocket_x = WIDTH // 2 - rocket_image.get_width() // 2
    rocket_y = HEIGHT // 2 - 250
    screen.blit(rocket_image, (rocket_x, rocket_y))
    
    if current_state == STATE_MENU:
        title_text = font.render("Race Across the Galaxy", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 200))

        easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        medium_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        hard_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)

        pygame.draw.rect(screen, GREEN, easy_button)
        pygame.draw.rect(screen, GREEN, medium_button)
        pygame.draw.rect(screen, GREEN, hard_button)

        easy_text = small_font.render("Easy", True, WHITE)
        medium_text = small_font.render("Medium", True, WHITE)
        hard_text = small_font.render("Hard", True, WHITE)

        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2 + 10))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 70))
    
    elif current_state == STATE_LEVEL_SELECTION:
        level1_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        level2_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        level3_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
        
        pygame.draw.rect(screen, GREEN, level1_button)
        pygame.draw.rect(screen, GREEN, level2_button)
        pygame.draw.rect(screen, GREEN, level3_button)

        level1_text = small_font.render("Level 1", True, WHITE)
        level2_text = small_font.render("Minigame 3", True, WHITE)
        level3_text = small_font.render("Level 4", True, WHITE)
        
        screen.blit(level1_text, (WIDTH // 2 - level1_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(level2_text, (WIDTH // 2 - level2_text.get_width() // 2, HEIGHT // 2 + 10))
        screen.blit(level3_text, (WIDTH // 2 - level3_text.get_width() // 2, HEIGHT // 2 + 70))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if current_state == STATE_MENU:
                if easy_button.collidepoint(mouse_pos):
                    current_difficulty = "Easy"
                    current_state = STATE_LEVEL_SELECTION
            elif current_state == STATE_LEVEL_SELECTION:
                if level1_button.collidepoint(mouse_pos):
                    import level1_circuitfix
                    importlib.reload(level1_circuitfix)
                    level1_circuitfix.run_level1()
                elif level2_button.collidepoint(mouse_pos):
                    import mazeP2
                    importlib.reload(mazeP2)
                    mazeP2.run_minigame()
                elif level3_button.collidepoint(mouse_pos):
                    import level4_selection
                    importlib.reload(level4_selection)
                    level4_selection.run_level4()

pygame.quit()
