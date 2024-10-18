import pygame
from pygame.locals import *
import math

# Initialize pygame
pygame.init()

# Create a display surface object for the rocket animation
window = pygame.display.set_mode((800, 800))

# Load and resize the rocket images
image_Rocket = [
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket1.png"), (400, 600)),
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket2.png"), (400, 600)),
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket3.png"), (400, 600))
]

# Create a clock object to control the framerate
clock = pygame.time.Clock()

# Initialize the sprite list iterator
value = 0

# Run loop control
run = True

# Main loop for the rocket animation
while run:
    # Handle the window close event
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    # Set the framerate
    clock.tick(9)

    # Reset the sprite iterator if it exceeds the list length
    if value >= len(image_Rocket):
        value = 0

    # Get the current rocket image
    image = image_Rocket[value]

    # Fill the window with black color
    window.fill((0, 0, 0))

    # Display the current image at coordinates (150, 200)
    window.blit(image, (150, 200))

    # Update the display surface
    pygame.display.update()

    # Move to the next image in the list
    value += 1

# Create a new clock object for the scrolling background
clock = pygame.time.Clock()

# Frame size for scrolling background
FrameHeight = 600
FrameWidth = 1200

# Create a new display for the scrolling background
pygame.display.set_caption("Endless Scrolling in pygame")
screen = pygame.display.set_mode((FrameWidth, FrameHeight))

# Load the background image and convert it
bg = pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Background.png").convert()

# Variables for scrolling
scroll = 0
tiles = math.ceil(FrameWidth / bg.get_width()) + 1

# Main loop for the scrolling background
while True:
    # Control the scrolling speed
    clock.tick(33)

    # Draw the background image repeatedly to create scrolling
    for i in range(tiles):
        screen.blit(bg, (bg.get_width() * i + scroll, 0))

    # Update the scroll position
    scroll -= 6

    # Reset the scroll if it goes off-screen
    if abs(scroll) > bg.get_width():
        scroll = 0

    # Handle the window close event
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

    # Update the display
    pygame.display.update()

# Quit pygame
pygame.quit()