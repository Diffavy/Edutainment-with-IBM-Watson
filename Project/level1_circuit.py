import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Reassembly - Level 1")

# Load resources
try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    control_room_bg = pygame.image.load(os.path.join(base_path, 'cr3.jpg'))
    control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

    zoomed_background = pygame.image.load(os.path.join(base_path, 'cr4.jpg'))
    zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

    resistor_100k_image = pygame.image.load(os.path.join(base_path, '100kr.png'))
    resistor_100k_image = pygame.transform.scale(resistor_100k_image, (60, 30))

    resistor_100_image = pygame.image.load(os.path.join(base_path, '100r.png'))
    resistor_100_image = pygame.transform.scale(resistor_100_image, (60, 30))

    resistor_10k_image = pygame.image.load(os.path.join(base_path, '10kres.png'))
    resistor_10k_image = pygame.transform.scale(resistor_10k_image, (60, 30))

    resistor_47_image = pygame.image.load(os.path.join(base_path, '47kres.png'))
    resistor_47_image = pygame.transform.scale(resistor_47_image, (60, 30))

    switchoff_image = pygame.image.load(os.path.join(base_path, 'switchoff.png'))
    switchoff_image = pygame.transform.scale(switchoff_image, (80, 40))

    switchon_image = pygame.image.load(os.path.join(base_path, 'switchon.png'))
    switchon_image = pygame.transform.scale(switchon_image, (80, 40))

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

# Fonts
font = pygame.font.Font(None, 36)
label_font = pygame.font.Font(None, 24)

# Circuit Board area
circuit_board_rect = pygame.Rect(150, 300, 600, 150)


components = {
    "resistor_100": {"image": resistor_100_image, "rect": resistor_100_image.get_rect(topleft=(150, 50)), "label": "100Ω", "placed": False},  
    "resistor_10k": {"image": resistor_10k_image, "rect": resistor_10k_image.get_rect(topleft=(250, 50)), "label": "10kΩ", "placed": False},  
    "resistor_47k": {"image": resistor_47_image, "rect": resistor_47_image.get_rect(topleft=(350, 50)), "label": "4.7kΩ", "placed": False},  
    "resistor_100k": {"image": resistor_100k_image, "rect": resistor_100k_image.get_rect(topleft=(50, 50)), "label": "100kΩ", "placed": False},  
    "led": {"image": led_off_image, "rect": led_off_image.get_rect(topleft=(650, 360)), "label": "LED", "placed": False},
    "battery": {"image": battery_image, "rect": battery_image.get_rect(topleft=(450, 50)), "label": "Power", "placed": False} 
}

# Switches
switches = [
    {"image": switchoff_image, "alt_image": switchon_image, "rect": switchoff_image.get_rect(topleft=(280, 340)), "state": False},  # For first resistor
    {"image": switchoff_image, "alt_image": switchon_image, "rect": switchoff_image.get_rect(topleft=(280, 390)), "state": False}   # For second resistor
]

# Game States
STATE_OVERVIEW = "overview"
STATE_ZOOM = "zoom"
current_state = STATE_OVERVIEW

# Dragging logic
selected_component = None
mouse_offset = (0, 0)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    if current_state == STATE_OVERVIEW:
        screen.blit(control_room_bg, (0, 0))
        #pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

    elif current_state == STATE_ZOOM:
        screen.blit(zoomed_background, (0, 0))
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)

        # Draw wires
        pygame.draw.line(screen, WHITE, (200, 380), (280, 380), 5)  # Power to parallel branches
        pygame.draw.line(screen, WHITE, (280, 380), (280, 350), 5)  # Vertical to first switch
        pygame.draw.line(screen, WHITE, (280, 380), (280, 420), 5)  # Vertical to second switch

        pygame.draw.line(screen, WHITE, (360, 350), (450, 350), 5)  # First resistor to series
        pygame.draw.line(screen, WHITE, (360, 420), (450, 420), 5)  # Second resistor to series

        pygame.draw.line(screen, WHITE, (450, 350), (450, 420), 5)  # Connect both parallel paths
        pygame.draw.line(screen, WHITE, (450, 400), (650, 400), 5)  # Series resistor to LED
        

        # Draw switches
        for switch in switches:
            screen.blit(switch["alt_image"] if switch["state"] else switch["image"], switch["rect"])

        for comp in components.values():
            screen.blit(comp["image"], comp["rect"])
            
            #labels
            label_surface = label_font.render(comp["label"], True, WHITE)
            label_rect = label_surface.get_rect(midtop=(comp["rect"].centerx, comp["rect"].bottom + 5))
            screen.blit(label_surface, label_rect)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if current_state == STATE_OVERVIEW:
                if circuit_board_rect.collidepoint(mouse_pos):
                    current_state = STATE_ZOOM

            elif current_state == STATE_ZOOM:
                # Check switches
                for switch in switches:
                    if switch["rect"].collidepoint(mouse_pos):
                        switch["state"] = not switch["state"]  # Toggle switch

                # Check component selection
                for name, comp in components.items():
                    if comp["rect"].collidepoint(mouse_pos) and not comp["placed"]:
                        selected_component = name
                        mouse_offset = (mouse_pos[0] - comp["rect"].x, mouse_pos[1] - comp["rect"].y)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_component and circuit_board_rect.collidepoint(event.pos):
                comp = components[selected_component]
                comp["rect"].topleft = (max(min(event.pos[0] - mouse_offset[0], circuit_board_rect.right - comp["rect"].width), circuit_board_rect.left),
                                        max(min(event.pos[1] - mouse_offset[1], circuit_board_rect.bottom - comp["rect"].height), circuit_board_rect.top))
                comp["placed"] = True
            selected_component = None

        elif event.type == pygame.MOUSEMOTION and selected_component:
            comp = components[selected_component]
            comp["rect"].x = event.pos[0] - mouse_offset[0]
            comp["rect"].y = event.pos[1] - mouse_offset[1]

    if current_state == STATE_ZOOM and all(components[res]["placed"] for res in ["resistor_100", "resistor_10k", "resistor_47k"]) and all(switch["state"] for switch in switches):
        components["led"]["image"] = led_on_image  # Correct three resistors used

    pygame.display.flip()
pygame.quit()
sys.exit()

def run_level1():
    main()

if __name__ == "__main__":
    main()
