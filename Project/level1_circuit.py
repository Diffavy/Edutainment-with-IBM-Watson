import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Reassembly - Level 1")

# Load resources
try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'
# if running from github:
#def load_image(filename):
    #base_path = os.path.join(os.getcwd(), 'Project', 'Idle')
    #return pygame.image.load(os.path.join(base_path, filename))

    control_room_bg = pygame.image.load(os.path.join(base_path, 'cr1.jpg'))
    control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

    zoomed_background = pygame.image.load(os.path.join(base_path, 'cr2.jpg'))
    zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

    resistor_100k_image = pygame.image.load(os.path.join(base_path, '100kr.png'))
    resistor_100k_image = pygame.transform.scale(resistor_100k_image, (80, 40))

    resistor_100_image = pygame.image.load(os.path.join(base_path, '100r.png'))
    resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 40))

    led_off_image = pygame.image.load(os.path.join(base_path, 'LEDOFF.png'))
    led_off_image = pygame.transform.scale(led_off_image, (70, 70))

    led_on_image = pygame.image.load(os.path.join(base_path, 'LEDON.png'))
    led_on_image = pygame.transform.scale(led_on_image, (70, 70))

    battery_image = pygame.image.load(os.path.join(base_path, 'Power.png'))
    battery_image = pygame.transform.scale(battery_image, (100, 100))
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
label_font = pygame.font.Font(None, 24)

# Circuit Components Dictionary
components = {
    "resistor_100k": {
        "image": resistor_100k_image,
        "rect": resistor_100k_image.get_rect(topleft=(50, 50)),
        "label": "100k",
        "placed": False
    },
    "resistor_100": {
        "image": resistor_100_image,
        "rect": resistor_100_image.get_rect(topleft=(150, 50)),
        "label": "100",
        "placed": False
    },
    "led": {
        "image": led_off_image,
        "rect": led_off_image.get_rect(topleft=(250, 50)),
        "label": "LED",
        "placed": False
    },
    "battery": {
        "image": battery_image,
        "rect": battery_image.get_rect(topleft=(350, 50)),
        "label": "Battery",
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
mouse_offset = (0, 0)  # Offset for dragging components

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if current_state == STATE_OVERVIEW:
                if circuit_board_rect.collidepoint(mouse_pos):
                    current_state = STATE_ZOOM

            elif current_state == STATE_ZOOM:
                for comp_name, comp in components.items():
                    if comp["rect"].collidepoint(mouse_pos) and not comp["placed"]:
                        selected_component = comp_name
                        mouse_offset = (mouse_pos[0] - comp["rect"].x, mouse_pos[1] - comp["rect"].y)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_component and circuit_board_rect.collidepoint(event.pos):
                comp = components[selected_component]
                comp["rect"].topleft = (
                    min(max(event.pos[0] - mouse_offset[0], circuit_board_rect.left),
                        circuit_board_rect.right - comp["rect"].width),
                    min(max(event.pos[1] - mouse_offset[1], circuit_board_rect.top),
                        circuit_board_rect.bottom - comp["rect"].height)
                )
                comp["placed"] = True
            selected_component = None

    if event.type == pygame.MOUSEMOTION and selected_component:
        comp = components[selected_component]
        comp["rect"].x = event.pos[0] - mouse_offset[0]
        comp["rect"].y = event.pos[1] - mouse_offset[1]

    # Draw
    if current_state == STATE_OVERVIEW:
        screen.blit(control_room_bg, (0, 0))
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

    elif current_state == STATE_ZOOM:
        screen.blit(zoomed_background, (0, 0))
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

        for comp_name, comp in components.items():
            screen.blit(comp["image"], comp["rect"])
            label_surface = label_font.render(comp["label"], True, WHITE)
            label_rect = label_surface.get_rect(center=(comp["rect"].centerx, comp["rect"].bottom + 15))
            screen.blit(label_surface, label_rect)

        if all(comp["placed"] for comp in components.values()):
            components["led"]["image"] = led_on_image

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
