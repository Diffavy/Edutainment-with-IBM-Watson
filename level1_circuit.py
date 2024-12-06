import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Reassembly - Level 2")


try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    # Load and scale the background (Control Room)
    control_room_bg = pygame.image.load(os.path.join(base_path, 'cr1.jpg'))
    control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

    # Load zoomed background image for solving the circuit
    zoomed_background = pygame.image.load(os.path.join(base_path, 'cr2.jpg'))
    zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

    # Load and scale component images
    resistor_100k_image = pygame.image.load(os.path.join(base_path, '100kr.png'))
    resistor_100k_image = pygame.transform.scale(resistor_100k_image, (80, 40))  # Standardize size

    resistor_100_image = pygame.image.load(os.path.join(base_path, '100r.png'))
    resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 40))  # Standardize size

    led_off_image = pygame.image.load(os.path.join(base_path, 'LEDOFF.png'))
    led_off_image = pygame.transform.scale(led_off_image, (70, 70))  # Standardize size

    led_on_image = pygame.image.load(os.path.join(base_path, 'LEDON.png'))
    led_on_image = pygame.transform.scale(led_on_image, (70, 70))  # Standardize size

    battery_image = pygame.image.load(os.path.join(base_path, 'Power.png'))
    battery_image = pygame.transform.scale(battery_image, (60, 120))  # Standardize size
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Circuit Components Dictionary
components = {
    "resistor_100k": {
        "image": resistor_100k_image,
        "rect": resistor_100k_image.get_rect(topleft=(50, 50)),
        "placed": False
    },
    "resistor_100": {
        "image": resistor_100_image,
        "rect": resistor_100_image.get_rect(topleft=(150, 50)),
        "placed": False
    },
    "led": {
        "image": led_off_image,
        "rect": led_off_image.get_rect(topleft=(250, 50)),
        "placed": False
    },
    "battery": {
        "image": battery_image,
        "rect": battery_image.get_rect(topleft=(350, 50)),
        "placed": False
    }
}

# Circuit Board area
circuit_board_rect = pygame.Rect(200, 400, 400, 100)

# Game State Variables
STATE_OVERVIEW = "overview"
STATE_ZOOM = "zoom"
current_state = STATE_OVERVIEW
selected_component = None

# Game Loop
running = True

while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # In Overview State, click to zoom in on the circuit board
            if current_state == STATE_OVERVIEW:
                if circuit_board_rect.collidepoint(mouse_pos):
                    current_state = STATE_ZOOM

            # In Zoom State, handle component selection and placement
            elif current_state == STATE_ZOOM:
                #
                for comp_name, comp in components.items():
                    if comp["rect"].collidepoint(mouse_pos) and not comp["placed"]:
                        selected_component = comp_name
                        break

                
                if selected_component and circuit_board_rect.collidepoint(mouse_pos):
                    # Place the component sin the circuit board area
                    comp_rect = components[selected_component]["rect"]
                    comp_rect.topleft = (
                        min(max(mouse_pos[0] - comp_rect.width // 2, circuit_board_rect.left),
                            circuit_board_rect.right - comp_rect.width),
                        min(max(mouse_pos[1] - comp_rect.height // 2, circuit_board_rect.top),
                            circuit_board_rect.bottom - comp_rect.height)
                    )
                    components[selected_component]["placed"] = True
                    selected_component = None

    # Draw the appropriate screen based on the current state
    if current_state == STATE_OVERVIEW:
        # the broad control room view
        screen.blit(control_room_bg, (0, 0))
        #  the outline of the circuit board area for clicking
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

    elif current_state == STATE_ZOOM:
        # Zoomed in on the circuit board 
        screen.blit(zoomed_background, (0, 0))

        # outline only)
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

        # Draw Components
        for comp in components.values():
            screen.blit(comp["image"], comp["rect"])

        # Check if all components are placed correctly to complete the circuit
        if all(comp["placed"] for comp in components.values()):
            # All components are placed, change LED image to "on"
            components["led"]["image"] = led_on_image

    # Update the Screen
    pygame.display.flip()

# Quit Pygame
pygame.quit()
