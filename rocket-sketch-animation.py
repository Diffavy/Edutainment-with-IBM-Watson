# Importing the pygame module
import pygame
from pygame.locals import *

# Initiate pygame and give permission
# to use pygame's functionality
pygame.init()

# Create a display surface object
# of specific dimension
window = pygame.display.set_mode((800, 800))

# Load the rocket images and resize them to a smaller size
image_Rocket = [
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket1.png"), (400, 600)),
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket2.png"), (400, 600)),
    pygame.transform.scale(pygame.image.load(r"C:\Users\hanna\Pictures\Coursework\Year 4\Group csw ideas\Rocket3.png"), (400, 600))
]

# Creating a new clock object to track the amount of time
clock = pygame.time.Clock()

# Creating a new variable to iterate over the sprite list
value = 0

# Creating a boolean variable to control the while loop
run = True

# Creating an infinite loop to run the game
while run:

    # Handling the window close event
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False  # Set run to False to exit the loop

    # Setting the framerate to 3fps just to see the result properly
    clock.tick(9)

    # Setting 0 in value variable if its value is greater than the length of the sprite list
    if value >= len(image_Rocket):
        value = 0

    # Storing the sprite image in an image variable
    image = image_Rocket[value]

    # Creating a variable to store the starting x and y coordinates
    x = 150

    # Changing the y coordinate according to the value stored in our value variable
    if value == 0:
        y = 200
    else:
        y = 200

    # Filling the window with black color
    window.fill((0, 0, 0))

    # Displaying the image in the game window
    window.blit(image, (x, y))

    # Updating the display surface
    pygame.display.update()

    # Increasing the value of the value variable by 1 after every iteration
    value += 1

# Quit pygame when the loop ends
pygame.quit()
