import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Choose Your Planet")


background = pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/deepspace.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


planets = {
    "Mars": pygame.transform.scale(pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/mars2.png"), (130, 130)),
    "Saturn": pygame.transform.scale(pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/saturn2.png"), (140, 130)),
    "Uranus": pygame.transform.scale(pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/urano2.png"), (150, 130)),
    "Alien Planet": pygame.transform.scale(pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/alienplanet2.png"), (130, 130)),
    "Neptune": pygame.transform.scale(pygame.image.load("C:/Users/luuxm/OneDrive/Escritorio/CLASSES/groupproject/images/neptuno2.png"), (135, 125)),
}

# Define planet positions (centered in the middle of the screen)
planet_positions = {
    "Mars": (50, 450),
    "Saturn": (200, 200),
    "Uranus": (350, 400),
    "Alien Planet": (500, 150),
    "Neptune": (650, 350)
}

# Text properties
font = pygame.font.Font(None, 24)
text_color = (255, 255, 255)
green = (0, 255, 0)

# Fuel properties
fuel_available = "Methane & Liquid Oxygen"
total_fuel = 10000  # Arbitrary fuel units
fuel_per_unit_distance = 2  # Fuel consumption per distance unit

# Distance from Earth (starting planet) to each planet
distances = {
    "Mars": 4000,
    "Saturn": 8000,
    "Uranus": 10000,  
    "Alien Planet": 12000,
    "Neptune": 15000,
}


gravity_and_d = {
    "Mars": "Gravity: 3.71 m/s² | Distance: 5000L",
    "Saturn": "Gravity: 10.44 m/s² | Distance: 15000L",
    "Uranus": "Gravity: 9.81 m/s² | Distance: 8000L",
    "Alien Planet": "Gravity: 7.2 m/s² | Distance: 11000L",
    "Neptune": "Gravity: 11.15 m/s² | Distance: 13000L",
}

display_info = None
selected_planet = None

dragging = None
text_positions = {
    "Mars": [100, 50], "Saturn": [450, 50], "Uranus": [250, 50], "Alien Planet": [550, 50], "Neptune": [350, 50]
}
matched = {name: False for name in planets}

def draw_screen():
    screen.blit(background, (0, 0))
    # Display fuel information
    fuel_text = font.render(f"Fuel Type: {fuel_available} | Total Fuel: {total_fuel} units", True, text_color)
    screen.blit(fuel_text, (20, 120))
    fuel_usage_text = font.render(f"Fuel Consumption: {fuel_per_unit_distance} units per distance", True, text_color)
    screen.blit(fuel_usage_text, (20, 150))
    for name, pos in planet_positions.items():
        screen.blit(planets[name], pos)
    for name, pos in text_positions.items():
        color = green if matched[name] else text_color
        text = font.render(name, True, color)
        screen.blit(text, pos)
    if display_info:
        info_text = font.render(display_info, True, text_color)
        screen.blit(info_text, (WIDTH // 2 - 100, HEIGHT - 50))
    pygame.display.flip()
    
    
    

def check_matching():
    for name in planets:
        if abs(text_positions[name][0] - planet_positions[name][0]) < 80 and abs(text_positions[name][1] - planet_positions[name][1]) < 80:
            matched[name] = True
            text_positions[name] = [planet_positions[name][0], planet_positions[name][1] - 40]

def handle_mouse_down(pos):
    global dragging, selected_planet
    for name, (x, y) in text_positions.items():
        if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 30:
            dragging = name
    for name, (x, y) in planet_positions.items():
        if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 100:
            selected_planet = name
            required_fuel = distances[name] * fuel_per_unit_distance
            if required_fuel <= total_fuel:
                show_popup(f"Setting course to {name}!")
            else:
                show_popup("Not enough fuel to reach this planet!")

def handle_mouse_up():
    global dragging
    if dragging:
        check_matching()
    dragging = None

def handle_mouse_motion(pos):
    global display_info
    display_info = None
    if dragging:
        text_positions[dragging] = [pos[0] - 50, pos[1] - 15]
    else:
        for name, (x, y) in planet_positions.items():
            if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 100:
                display_info = f"Distance: {distances[name]} units"
                break

def show_popup(message):
    popup = pygame.Surface((350, 100))
    popup.fill((0, 0, 0))
    border_rect = pygame.Rect(0, 0, 350, 100)
    pygame.draw.rect(popup, (255, 255, 255), border_rect, 2)
    text = font.render(message, True, text_color)
    popup.blit(text, (20, 40))
    screen.blit(popup, (WIDTH//2 - 175, HEIGHT//2 - 50))
    pygame.display.flip()
    pygame.time.delay(2000)

def main():
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_screen()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event.pos)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

def run_level4():
    main()

if __name__ == "__main__":
    main()