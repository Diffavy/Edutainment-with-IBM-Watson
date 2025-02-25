import pygame
import numpy as np
import scipy
import matplotlib

pygame.init()

screen_width = 1000
screen_height = int(screen_width*0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Rocket Level 1')

# Set Framerate
clock = pygame.time.Clock()
FPS = 60

# Define Colours
background_colour = (0, 0, 0)

def draw_background():
    screen.fill(background_colour)


class Rocket(pygame.sprite.Sprite):
    def __init__(self, character_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.character_type = character_type
        self.speed = speed
        self.direction = 1
        self.fly = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'..\\Group Project\\Idle\\{i}Rocket_Image.png')
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'..\\Group Project\\Idle\\{i}Rocket_Image.png')
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right, moving_up, moving_down):
        # Reset movement variables
        dx = 0
        dy = 0

        # Assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.direction = 1
        if moving_down:
            dy = self.speed
            self.flip = True
        if moving_up:
            dy = -self.speed
            self.flip = False

        # Update Rectangle Position
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # Update animation
        ANIMATION_COOLDOWN = 100
        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]      
        # Check if enough time has passed since the last update:
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # If animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # Check if new action is different to previous action
        if new_action != self.action:
            self.action = new_action
            # Update animation settings
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, False, self.flip), self.rect)


player = Rocket('Rocket', 200, 200, 1, 3)

run = True

moving_right = False
moving_left = False
moving_up = False
moving_down = False

while run:
    
    clock.tick(FPS)

    draw_background()

    player.update_animation()
    player.draw()

    # Update player actions
    if player.alive:
        if moving_up or moving_down:
            player.update_action(1)  # 1 means Flying
        else:
            player.update_action(0)  # 0 means Idle

    player.move(moving_left, moving_right, moving_up, moving_down)

    # Event Handler
    for event in pygame.event.get():
        # Quit Game
        if event.type == pygame.QUIT:
            run = False
        # Keyboard Presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True  # Moving up
            if event.key == pygame.K_s:
                moving_down = True  # Moving down
            if event.key == pygame.K_ESCAPE:
                run = False
        # Keyboard Button Released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False  # Stop moving up
            if event.key == pygame.K_s:
                moving_down = False  # Stop moving down

    pygame.display.update()


pygame.quit()