import pygame
import os
import numpy as np
import scipy
import matplotlib
import random

pygame.init()

screen_width = 800
screen_height = int(screen_width*0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Rocket Level 1')

#Set Framerate
clock = pygame.time.Clock()
FPS = 60

#Define game variables
GRAVITY = 0.5         # Gravity strength, adjust for desired falling speed
THRUSTER_POWER = 0.1  # Thrust power applied each frame
MAX_THRUST = 1.0      # Maximum upward thrust
MAX_FALL_SPEED = 10   # Maximum downward speed
MAX_RISE_SPEED = 15    # Maximum upward speed (negative velocity)
FLOOR_Y = 550         # Y-coordinate of the floor
SCROLL_THRESH = 100

#Background scroll
screen_scroll = 0
bg_scroll = 0
#Meteor
meteor_img = pygame.image.load(f'../Project/Meteor/Idle/0Meteor_Image.png').convert_alpha()
meteor_frequency = 2000 #Value in miliseconds

#Define Colours
background_colour = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

moving_background = pygame.image.load(f'../Project/Background/level_1.png')


def draw_background(bg_scroll):
    # print(f"bg_scroll: {bg_scroll}") #debug
    # Calculate relative y-position for background wrapping
    rel_y = bg_scroll % screen_height
    screen.blit(moving_background, (0, rel_y - screen_height))  # Draw image above
    screen.blit(moving_background, (0, rel_y))  # Draw main image

    floor_y = FLOOR_Y + bg_scroll
    pygame.draw.line(screen, RED, (0, floor_y), (screen_width, floor_y))

# Spawn a meteor function




# Spawn a meteor variables
meteor_spawn_timer = 0
meteor_spawn_interval = 2000 # 2000 ms = 2 seconds

# Game over display function
def show_game_over():
    font = pygame.font.SysFont('Arial', 64)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.update()

# Health Bar display
def draw_health_bar(x, y, health, max_health):
    bar_width = 100
    bar_height = 10
    fill = (health / max_health) * bar_width
    border_colour = WHITE
    fill_colour = GREEN
    pygame.draw.rect(screen, fill_colour, (x, y, fill, bar_height))
    pygame.draw.rect(screen, border_colour, (x, y, bar_width, bar_height), 2)

class Rocket(pygame.sprite.Sprite):
    def __init__(self, character_type, x, y, rocket_scale, speed, health=100):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.character_type = character_type
        self.speed = speed
        self.direction = 1
        self.health = health
        self.max_health = self.health
        self.vel_y = 0.0
        self.rocket_thrust = 0.0
        self.fly = False
        self.flip = False
        self.grounded = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        
        #Load all images for players
        animation_types = ['Idle', 'Flying', 'Death']
        for animation in animation_types:    
            #Get all .png files in the folder sorted by name
            folder_path = f'../Project/{animation}'

            image_files = sorted([file for file in os.listdir(folder_path) if file.endswith('.png')])
            
            #Reset temporary list of images
            temp_list = [
            pygame.transform.scale(
            pygame.image.load(os.path.join(folder_path, image_file)).convert_alpha(),
            (int(pygame.image.load(os.path.join(folder_path, image_file)).get_width() * rocket_scale), 
             int(pygame.image.load(os.path.join(folder_path, image_file)).get_height() * rocket_scale))
            )
            for image_file in image_files
            ]
            
            self.animation_list.append(temp_list)
            #Count the number of files in the folder
            # num_of_frames = len(os.listdir(f'../Project/{animation}'))

            
        self.image = self.animation_list[self.action][self.frame_index]
        
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        self.update_animation()
        self.check_alive()

    def move(self, moving_left, moving_right):
        global bg_scroll
        screen_scroll = 0
        #Reset movement variables
        dx = 0
        dy = 0

        #Assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.direction = 1
        
        if self.fly:
            # Apply thrust and limit its maximum effect
            self.rocket_thrust = min(self.rocket_thrust + THRUSTER_POWER, MAX_THRUST)
            self.vel_y -= self.rocket_thrust  # Thrust decreases downward velocity
        else:
            self.rocket_thrust = 0.0

        # Apply gravity (always acting downward)
        if not self.grounded:
            self.vel_y += GRAVITY

        if self.rect.top < SCROLL_THRESH:
            screen_scroll = SCROLL_THRESH - self.rect.top
            if screen_scroll > 0:
                self.rect.top += screen_scroll
            else:
                self.rect.top = SCROLL_THRESH
        elif self.rect.bottom > screen_height - SCROLL_THRESH:
            screen_scroll = (screen_height - SCROLL_THRESH) - self.rect.bottom
            self.rect.bottom = screen_height - SCROLL_THRESH

        # Cap vertical velocity to prevent excessive speed
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        elif self.vel_y < -MAX_RISE_SPEED:
            self.vel_y = -MAX_RISE_SPEED

        # Update vertical position
        dy += self.vel_y

        # Collision with the floor
        if self.rect.bottom + dy > FLOOR_Y + bg_scroll:
            dy = (FLOOR_Y + bg_scroll) - self.rect.bottom
            self.vel_y = 0  # Reset velocity when hitting the floor
            self.grounded = True
        else:
            self.grounded = False

        #Update Rectangle Position
        self.rect.x += dx
        self.rect.y += dy

        return screen_scroll


    def update_animation(self):
        #Update animation
        ANIMATION_COOLDOWN = 100
        #Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        
        #Check if enough time has passed since the last update:
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #If animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
        #Rotate image
        if moving_right:
            self.image = pygame.transform.rotate(self.animation_list[self.action][self.frame_index], -10)

        if moving_left:
            self.image = pygame.transform.rotate(self.animation_list[self.action][self.frame_index], 10)

    def update_action(self, new_action):
        #Check if new action is different to previous action
        if new_action != self.action:
            self.action = new_action
            #Update animation settings
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)
            

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, False, self.flip), self.rect)


class Meteor(pygame.sprite.Sprite):
    def __init__(self, meteor_type, x, y, meteor_scale, direction=None, speed=None):
        pygame.sprite.Sprite.__init__(self)
        self.meteor_type = meteor_type
        self.meteor_scale = meteor_scale
        self.min_speed = 2
        self.max_speed = 4
        # If direction is None, assign a random direction (-1, 0, or 1)
        self.direction = direction if direction is not None else random.choice([-1, 0, 1])
        self.speed = speed
        self.image = pygame.transform.scale(meteor_img, (int(meteor_img.get_width() * self.meteor_scale), int(meteor_img.get_height() * self.meteor_scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def spawn_meteor(self):
        
        # Spawn Logic
        if self.direction == -1: 
            self.rect.x = screen_width  
            self.speed = random.uniform(self.min_speed, self.max_speed)  # Lower speed for left-moving meteors
        elif self.direction == 1:  # Moving right
            self.rect.x = -self.rect.width  # Spawn off-screen to the left
            self.speed = random.uniform(self.min_speed, self.max_speed)  # Speed for right-moving meteors
        else:  # Direction is 0 (no horizontal movement)
            self.rect.x = random.randint(0, screen_width // 2)  # Center horizontally
            self.speed = random.uniform(1, 2)  # Speed for meteors not moving horizontally
        
        # Set Y-coordinate for meteor
        self.rect.y = random.randint(200, screen_height // 2)  # Avoid spawning near the floor

        

    def update(self):
        # Meteor moves with the background
        self.rect.y += screen_scroll
        if self.speed is not None and self.direction != 0:  # Only move horizontally if direction is not 0
            self.rect.x += self.direction * self.speed
            

        # Check if meteor has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

        # Check collision with rockets
        if pygame.sprite.spritecollide(player, meteor_group, False):
            if player.alive:
                player.health -= 5
                if player.health <= 0:
                    player.alive = False
                self.kill()


        

#create sprite groups
meteor_group = pygame.sprite.Group()



player = Rocket('Rocket', 200, 200, 0.04, 3)

run = True

moving_right = False
moving_left = False
moving_up = False
moving_down = False

meteor = Meteor('Enemy',400, screen_height/2, 0.2)

meteor_group.add(meteor)

# GAME LOOP
while run:
    
    clock.tick(FPS)
    
    screen_scroll = player.move(moving_left, moving_right)

    # print(f'screen_scroll: {screen_scroll}') Debug

    bg_scroll += screen_scroll

    draw_background(bg_scroll)

    #Update player actions
    if player.alive:
        if player.fly:
            player.update_action(1) #1 means Flying
        else:
            player.update_action(0) #0 means Idle
    else:    
        show_game_over()

    

    player.update()
    player.draw()

    draw_health_bar(10, 10, player.health, player.max_health)

    current_time = pygame.time.get_ticks()
    if current_time - meteor_spawn_timer > meteor_spawn_interval:
        meteor_spawn_timer = current_time
        new_meteor = Meteor('Enemy', 0, 0, random.uniform(0.05, 0.1))
        new_meteor.spawn_meteor()
        meteor_group.add(new_meteor)

    #update and draw groups
    meteor_group.update()
    meteor_group.draw(screen)



    

    for event in pygame.event.get():
        #Quit Game
        if event.type == pygame.QUIT:
            run = False
        #Keyboard Presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.fly = True
            if event.key == pygame.K_ESCAPE:
                run = False
        #Keyboard Button Released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                player.fly = False
            
    pygame.display.update()

pygame.quit()