import pygame
import sys
import os
import importlib
# this is first draft in menu design, colours, theme ,etc 
pygame.init()

# Screen dimensions to be modified
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Edutainment")

# Load Images 
try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    # Load and scale the background (Open Space)
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

# Planet positions (manually distributed evenly around the buttons)
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

# Current difficulty
current_difficulty = None

# Game loop
running = True
while running:
    
    screen.blit(space_bg, (0, 0))  # Draw the space background

    # Draw planets
    for i, planet_pos in enumerate(planet_positions):
        screen.blit(planet_images[i], planet_pos)

    # Draw rocket in the center of the screen
    rocket_x = WIDTH // 2 - rocket_image.get_width() // 2
    rocket_y = HEIGHT // 2 - 250
    screen.blit(rocket_image, (rocket_x, rocket_y))

    # Event 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if current_state == STATE_MENU:
                easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
                medium_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
                hard_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
                if easy_button.collidepoint(mouse_pos):
                    current_difficulty = "Easy"
                    current_state = STATE_LEVEL_SELECTION
                elif medium_button.collidepoint(mouse_pos):
                    current_difficulty = "Medium"
                    current_state = STATE_LEVEL_SELECTION
                elif hard_button.collidepoint(mouse_pos):
                    current_difficulty = "Hard"
                    current_state = STATE_LEVEL_SELECTION
            elif current_state == STATE_LEVEL_SELECTION:
                level1_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
                if level1_button.collidepoint(mouse_pos):
                    # Import and run the Level 1 circuit file for Easy difficulty
                    if current_difficulty == "Easy":
                        import level1_circuit
                        importlib.reload(level1_circuit)  # Reload the module if needed
                        level1_circuit.run_level1()  # Run level
                        current_state = STATE_MENU  # Return to the main menu after the level ends
                    else:
                        print(f"Level 1 for {current_difficulty} not implemented yet")

    # Draw menu
    if current_state == STATE_MENU:
        title_text = font.render("Race Across the Galaxy", True, WHITE)  # Title in white
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

        pygame.draw.rect(screen, GREEN, level1_button)
        pygame.draw.rect(screen, GREEN, level2_button)

        level1_text = small_font.render("Level 1", True, WHITE)
        level2_text = small_font.render("Level 2", True, WHITE)

        screen.blit(level1_text, (WIDTH // 2 - level1_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(level2_text, (WIDTH // 2 - level2_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()

# Quit Pygame
pygame.quit()
