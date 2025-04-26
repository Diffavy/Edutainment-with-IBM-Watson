import pygame
import sys
import os


pygame.init()


WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Reassembly - Level 1")


try:
    base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\images'

    control_room_bg = pygame.image.load(os.path.join(base_path, 'cr3.jpg'))
    control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

    zoomed_background = pygame.image.load(os.path.join(base_path, 'cr4.jpg'))
    zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

    resistor_100k_image = pygame.image.load(os.path.join(base_path, '100kr.png'))
    resistor_100k_image = pygame.transform.scale(resistor_100k_image, (80, 50))

    resistor_100_image = pygame.image.load(os.path.join(base_path, '100r.png'))
    resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 50))

    resistor_270_image = pygame.image.load(os.path.join(base_path, '270r.png'))
    resistor_270_image = pygame.transform.scale(resistor_270_image, (80, 50))

    resistor_330_image = pygame.image.load(os.path.join(base_path, '330r.png'))
    resistor_330_image = pygame.transform.scale(resistor_330_image, (80, 50))

    resistor_100_image = pygame.image.load(os.path.join(base_path, '100r.png'))
    resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 50))

    resistor_470_image = pygame.image.load(os.path.join(base_path, '47kres.png'))
    resistor_470_image = pygame.transform.scale(resistor_470_image, (80, 50))

    led_off_image = pygame.image.load(os.path.join(base_path, 'LEDOFF.png'))
    led_off_image = pygame.transform.scale(led_off_image, (60, 70))

    led_on_image = pygame.image.load(os.path.join(base_path, 'LEDON.png'))
    led_on_image = pygame.transform.scale(led_on_image, (60, 70))

    battery_image = pygame.image.load(os.path.join(base_path, 'source.png'))
    battery_image = pygame.transform.scale(battery_image, (100, 100))
    legend = pygame.image.load(os.path.join(base_path, 'legendr.png'))
    legend = pygame.transform.scale(legend, (400, 300))

except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()


WHITE = (255, 255, 255)
DBLUE = (100, 0, 255)


font = pygame.font.Font(None, 36)
label_font = pygame.font.Font(None, 24)

# Circuit Board area
circuit_board_rect = pygame.Rect(110, 340, 670, 110)

components = {
    "resistor_270": {"image": resistor_270_image, "rect": resistor_270_image.get_rect(topleft=(100, 50)), "resistance": 270, "placed": False},
    "resistor_330": {"image": resistor_330_image, "rect": resistor_330_image.get_rect(topleft=(200, 100)), "resistance": 330, "placed": False},
    "resistor_470": {"image": resistor_470_image, "rect": resistor_470_image.get_rect(topleft=(300, 50)), "resistance": 470, "placed": False},
    "resistor_1k": {"image": resistor_100k_image, "rect": resistor_100k_image.get_rect(topleft=(100, 150)), "resistance": 1000, "placed": False},
    "resistor_100": {"image": resistor_100_image, "rect": resistor_100_image.get_rect(topleft=(300, 150)), "resistance": 100, "placed": False},
    "led": {"image": led_off_image, "rect": led_off_image.get_rect(topleft=(650, 365)), "placed": True, "label": "LED 3V"},
    "battery": {"image": battery_image, "rect": battery_image.get_rect(topleft=(120, 350)), "placed": True, "label": "Battery 9V"}
    
}

STATE_OVERVIEW = "overview"
STATE_ZOOM = "zoom"
current_state = STATE_OVERVIEW


selected_component = None
mouse_offset = (0, 0)

# Game loop
running = True

while running:
    screen.fill(WHITE)

    if current_state == STATE_OVERVIEW:
        screen.blit(control_room_bg, (0, 0))
        msg_rect = pygame.Rect(90, 130, 620, 60)
        s = pygame.Surface((msg_rect.width, msg_rect.height))
        s.set_alpha(180)  #transparency (0 = invisible, 255 = solid)
        s.fill((0, 0, 0))  
        screen.blit(s, msg_rect.topleft)
        init_msg = font.render("The control board is not working! Click to fix it", True, WHITE)
        screen.blit(init_msg, (110, 140))

    elif current_state == STATE_ZOOM:
        screen.blit(zoomed_background, (0, 0))
        pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)


        pygame.draw.line(screen, WHITE, (components["battery"]["rect"].centerx + 50, components["battery"]["rect"].centery), (components["led"]["rect"].centerx - 35, components["led"]["rect"].centery), 5)

     
        ohms_text = font.render("Source 9V - LED 3V = 6V drop across resistors", True, WHITE)
        screen.blit(ohms_text, (50, 500))
        ohms_law = font.render("Current needed is  I = 0.01A ,   Use Ohm's Law: R = V / I ", True, WHITE)
        hint = font.render("What resistors do we need to get to the R value?", True, WHITE)
        screen.blit(ohms_law, (50, 530))
        screen.blit(hint, (50, 560))
        screen.blit(legend, (400, 0))

        for name, comp in components.items():
            screen.blit(comp["image"], comp["rect"])
            if name in ("battery", "led") and "label" in comp:
                label_surface = label_font.render(comp["label"], True, WHITE)
                label_rect = label_surface.get_rect(midtop=(comp["rect"].centerx, comp["rect"].bottom ))
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

    # Check if the circuit is correctly assembled
    placed_resistors = [name for name in components if "resistor" in name and components[name]["placed"]]
    total_resistance = sum(components[name]["resistance"] for name in placed_resistors)

    if (len(placed_resistors) == 2 and abs(total_resistance - 600) <= 10):
        components["led"]["image"] = led_on_image

    pygame.display.flip()

pygame.quit()
sys.exit()
