import pygame
import sys
# this is first draft in menu design, colours, theme ,etc 
pygame.init()

# Screen dimensions to be modified
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Edutainment")

# Colours Used (add backgroud from hannah)
DGREY = (155, 155, 155)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)

# Game states
STATE_MENU = "Menu"
STATE_DIFFICULTY = "Difficulty"
STATE_LEVEL = "Level"
current_state = STATE_MENU

#  i.c. variables 
gravity = 0.98  # Constant gravity force
thrust_power = -0.2  # Rocket thrust
rocket_pos = [WIDTH // 2, HEIGHT - 50]
rocket_speed = 0
fuel = 100

# Difficulty setting will be updated 
difficulty = None

# Arrow button positions
arrow_buttons = {
    "up": pygame.Rect(700, 400, 50, 50),
    "down": pygame.Rect(700, 500, 50, 50),
}

# Game loop
running = True
while running:
    screen.fill(DGREY if current_state != STATE_LEVEL else GREY)

    # currentv event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Menu state
            if current_state == STATE_MENU:
                easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
                if easy_button.collidepoint(mouse_pos):
                    current_state = STATE_DIFFICULTY

            # Difficulty state
            elif current_state == STATE_DIFFICULTY:
                level1_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
                if level1_button.collidepoint(mouse_pos):
                    current_state = STATE_LEVEL
                    difficulty = "Easy"

            # idea of level , arrow button interactions
            elif current_state == STATE_LEVEL:
                if arrow_buttons["up"].collidepoint(mouse_pos):
                    rocket_pos[1] -= 10
                elif arrow_buttons["down"].collidepoint(mouse_pos):
                    rocket_pos[1] += 10

    # Set menu
    if current_state == STATE_MENU:
        menu_text = font.render("Edutainment IBM", True, BLACK)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 - 150))

        easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        pygame.draw.rect(screen, GREEN, easy_button)
        easy_text = small_font.render("Easy", True, BLACK)
        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 50))

    # Set difficulty selection
    elif current_state == STATE_DIFFICULTY:
        level1_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        pygame.draw.rect(screen, GREEN, level1_button)
        level1_text = small_font.render("Level 1", True, BLACK)
        screen.blit(level1_text, (WIDTH // 2 - level1_text.get_width() // 2, HEIGHT // 2 - 50))

    # Start level level
    elif current_state == STATE_LEVEL:
        # rocket (currently a dot)
        pygame.draw.circle(screen, BLACK, (rocket_pos[0], int(rocket_pos[1])), 5)

        # arrow buttons
        for direction, rect in arrow_buttons.items():
            pygame.draw.rect(screen, RED, rect)
            arrow_text = "^" if direction == "up" else "v"
            arrow_render = font.render(arrow_text, True, BLACK)
            screen.blit(arrow_render, (rect.x + 10, rect.y + 5))

    # Update screen
    pygame.display.flip()

# Quit Pygame
pygame.quit()
