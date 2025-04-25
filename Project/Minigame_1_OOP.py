import pygame
import os
import random
from typing import List
import asyncio

"=== MINIGAME 1 ==="

class Game:
    """Main game class that handles initialization and the game loop."""
    
    def __init__(self):
        pygame.init()
        
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = int(0.8 * self.SCREEN_WIDTH)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.FONT = 'Arial'

        # Names the window
        pygame.display.set_caption('Rocket Level 1')
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        
        # Game physics
        self.GRAVITY = 0.5
        self.THRUSTER_POWER = 0.15
        self.MAX_THRUST = 1.2
        self.MAX_FALL_SPEED = 10
        self.MAX_RISE_SPEED = 15
        self.FLOOR_Y = self.SCREEN_HEIGHT - 50
        self.SCROLL_THRESH = 150
        
        # Game timing
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.ANIMATION_COOLDOWN = 100
        self.METEOR_SPAWN_INTERVAL = 1500
        
        # Game state
        self.screen_scroll = 0
        self.bg_scroll = 0
        self.running = True
        self.level_complete = False
        self.meteor_spawn_timer = 0
        self.hint_count = 0
        
        # Sprite groups
        self.meteor_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        # Load assets
        self.load_assets()
        
        # Create game objects
        self.player = Rocket(self, 200, self.FLOOR_Y - 100)
        self.all_sprites.add(self.player)
        
        # Create finish line
        self.finish_line = FinishLine(self, 0, -10000)
        self.all_sprites.add(self.finish_line)
        
        # Spawn initial meteors with guaranteed hints
        self.spawn_initial_objects()

    def load_assets(self):
        """Load all game assets with forced hint visibility"""
        # Background
        self.moving_background = self.load_image('../Project/Background/level_1.png')
        
        # Hint images with fallback
        try:
            self.hint_images = [
                pygame.image.load('../Project/Meteor/Hint/Hint1.png').convert_alpha(),
                pygame.image.load('../Project/Meteor/Hint/Hint2.png').convert_alpha()
            ]
            # Scale hint images larger for better visibility
            self.hint_images = [pygame.transform.scale(img, (80, 80)) for img in self.hint_images]
        except:
            # Create bright placeholder if images fail to load
            self.hint_images = []
            for _ in range(2):
                surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                surf.fill((0, 255, 0, 200))  # Semi-transparent green
                pygame.draw.circle(surf, (255, 255, 0), (40, 40), 30)  # Yellow center
                self.hint_images.append(surf)

    def load_image(self, path: str, scale: float = 1.0) -> pygame.Surface:
        """Load and scale an image with error handling"""
        # Tries to load images using the given path, if that fails it loads a magenta colour of the same size
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale != 1.0:
                new_size = (int(image.get_width() * scale), 
                           int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            return image
        except:
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            surf.fill((255, 0, 255))  # Magenta error color
            return surf

    def spawn_initial_objects(self):
        """Spawn objects with guaranteed hint meteors"""
        # Clear existing meteors
        self.meteor_group.empty()
        
        # Spawn regular enemies (5 total)
        for _ in range(5):
            x = random.randint(0, self.SCREEN_WIDTH)
            y = random.randint(-500, -100)
            meteor = Meteor(self, 'Enemy', x, y, random.uniform(0.05, 0.1))
            meteor.spawn()
            self.meteor_group.add(meteor)
            self.all_sprites.add(meteor)
        
        # Spawn exactly two guaranteed hint meteors
        hint_positions = [-800, -1500, -2800, -4400, -6000, -7500]  # Fixed vertical positions
        for y_pos in hint_positions:
            x = random.randint(100, self.SCREEN_WIDTH - 100)
            hint = Meteor(self, 'Hint', x, y_pos, 0.2)
            self.meteor_group.add(hint)
            self.all_sprites.add(hint)

    def draw_background(self):
        """Draw scrolling background"""
        rel_y = self.bg_scroll % self.moving_background.get_height()
        if rel_y > 0:
            self.screen.blit(self.moving_background, (0, rel_y - self.moving_background.get_height()))
        self.screen.blit(self.moving_background, (0, rel_y))
        
        # Draw floor
        floor_y = self.FLOOR_Y + self.bg_scroll
        if 0 <= floor_y <= self.SCREEN_HEIGHT:
            pygame.draw.line(self.screen, self.RED, (0, floor_y), (self.SCREEN_WIDTH, floor_y))

    def draw_health_bar(self, x: int, y: int, health: int, max_health: int):
        """Draw player health bar"""
        if max_health <= 0:
            return
            
        ratio = health / max_health # Used to change the colour of the health bar
        color = self.GREEN if ratio > 0.6 else self.YELLOW if ratio > 0.3 else self.RED
        
        pygame.draw.rect(self.screen, color, (x, y, 100 * ratio, 10))
        pygame.draw.rect(self.screen, self.WHITE, (x, y, 100, 10), 2)

    def draw_progress(self):
        """Draw progress toward finish line"""
        total_dist = abs(self.finish_line.rect.y - self.FLOOR_Y)
        progress = min(abs(self.bg_scroll) / total_dist, 1)
        
        # Progress bar
        bar_width = 200
        pygame.draw.rect(self.screen, self.WHITE, (self.SCREEN_WIDTH//2 - bar_width//2, 20, bar_width, 10), 1)
        pygame.draw.rect(self.screen, self.GREEN, (self.SCREEN_WIDTH//2 - bar_width//2, 20, bar_width * progress, 10))
        
        # Displays the progress as a percentage of how close the rocket is to finishing
        font = pygame.font.SysFont(self.FONT, 16)
        text = font.render(f"{int(progress * 100)}%", True, self.WHITE)
        self.screen.blit(text, (self.SCREEN_WIDTH//2 - text.get_width()//2, 35))

    def clear_meteors(self):
        """Remove all meteors from the game"""
        for meteor in self.meteor_group:
            meteor.kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player.moving_left = True
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.moving_right = True
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.player.fly = True
                elif event.key == pygame.K_r and not self.player.alive:
                    self.reset_level()
                elif event.key == pygame.K_SPACE and self.level_complete:
                    self.reset_level()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.player.fly = False

    def update(self):
        if self.player.alive and not self.level_complete:
            # Player movement
            self.screen_scroll = self.player.move()
            self.bg_scroll += self.screen_scroll
            
            # Meteor collisions
            hits = pygame.sprite.spritecollide(self.player, self.meteor_group, False)
            for meteor in hits:
                if meteor.meteor_type == 'Hint':
                    self.hint_count += 1
                    meteor.kill()
                else:
                    self.player.health -= 10
                    meteor.kill()  # Add this line to remove enemy meteor on collision
                    if self.player.health <= 0:
                        self.player.alive = False
            
            # Spawn new meteors
            current_time = pygame.time.get_ticks()
            if current_time - self.meteor_spawn_timer > self.METEOR_SPAWN_INTERVAL:
                self.meteor_spawn_timer = current_time
                x = random.randint(0, self.SCREEN_WIDTH)
                y = random.randint(-100, -50) + self.bg_scroll
                meteor = Meteor(self, 'Enemy', x, y, random.uniform(0.05, 0.1))
                meteor.spawn()
                self.meteor_group.add(meteor)
                self.all_sprites.add(meteor)
            
            # Check level completion
            if abs(self.bg_scroll) >= abs(self.finish_line.rect.y - self.FLOOR_Y):
                self.level_complete = True
        
        self.all_sprites.update()

    def render(self):
        self.draw_background()
        self.all_sprites.draw(self.screen)
        
        # UI elements
        self.draw_health_bar(10, 10, self.player.health, self.player.max_health)
        self.draw_progress()
        
        # Hint counter
        font = pygame.font.SysFont(self.FONT, 24)
        text = font.render(f"Hints: {self.hint_count}", True, self.WHITE)
        self.screen.blit(text, (self.SCREEN_WIDTH - 120, 10))
        
        # Game state messages
        if not self.player.alive:
            self.show_game_over()
        elif self.level_complete:
            self.show_level_complete()
        
        pygame.display.update()

    def reset_level(self):
        """Reset level state"""
        self.level_complete = False
        self.bg_scroll = 0
        self.hint_count = 0
        self.clear_meteors()
        self.player.reset()
        self.spawn_initial_objects()

    def show_game_over(self):
        """Display game over screen"""
        font = pygame.font.SysFont(self.FONT, 64)
        text = font.render("GAME OVER", True, self.RED)
        self.screen.blit(text, (self.SCREEN_WIDTH//2 - text.get_width()//2, 
                               self.SCREEN_HEIGHT//2 - text.get_height()//2))
        
        font_small = pygame.font.SysFont(self.FONT, 24)
        prompt = font_small.render("Press R to restart", True, self.WHITE)
        self.screen.blit(prompt, (self.SCREEN_WIDTH//2 - prompt.get_width()//2,
                                 self.SCREEN_HEIGHT//2 + 50))

    def show_level_complete(self):
        """Display level complete screen"""
        font = pygame.font.SysFont(self.FONT, 72)
        text = font.render("LEVEL COMPLETE!", True, self.GREEN)
        self.screen.blit(text, (self.SCREEN_WIDTH//2 - text.get_width()//2,
                               self.SCREEN_HEIGHT//2 - 50))
        
        font_small = pygame.font.SysFont(self.FONT, 36)
        prompt = font_small.render("Press SPACE to continue", True, self.WHITE)
        self.screen.blit(prompt, (self.SCREEN_WIDTH//2 - prompt.get_width()//2,
                                 self.SCREEN_HEIGHT//2 + 50))

    async def run(self):
        """Async main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.FPS)
            await asyncio.sleep(0)

class Rocket(pygame.sprite.Sprite):
    """Player controlled rocket"""
    
    def __init__(self, game: Game, x: int, y: int):
        super().__init__()
        self.game = game
        self.alive = True
        self.health = 100
        self.max_health = 100
        self.speed = 5
        self.vel_y = 0
        self.rocket_thrust = 0
        self.moving_left = False
        self.moving_right = False
        self.fly = False
        self.grounded = False
        
        # Load animations - uses dictionary
        self.animations = {
            'Idle': self.load_animation_frames('../Project/Idle', 0.04),
            'Flying': self.load_animation_frames('../Project/Flying', 0.04),
            'Death': self.load_animation_frames('../Project/Death', 0.04)
        }
        self.action = 0  # Start with Idle
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.rotation_angle = 0
        
        self.image = self.animations['Idle'][0]
        self.rect = self.image.get_rect(center=(x, y))
    
    def load_animation_frames(self, folder_path: str, scale: float) -> List[pygame.Surface]:
        """Load animation frames from folder"""
        frames = []
        # Tries to find a image in the file directory provided, if that fails a placeholder is used
        try:
            for file in sorted(os.listdir(folder_path)):
                if file.endswith('.png'):
                    frames.append(self.game.load_image(os.path.join(folder_path, file), scale))
        except:
            frames.append(pygame.Surface((50, 80), pygame.SRCALPHA))
        return frames
    
    def move(self) -> int:
        """Handle movement and return scroll amount"""
        dx = 0
        dy = 0
        
        # Horizontal movement - rotates the rocket slightly in the direction of motion
        if self.moving_left:
            dx = -self.speed
            self.rotation_angle = 10
        elif self.moving_right:
            dx = self.speed
            self.rotation_angle = -10
        else:
            self.rotation_angle = 0
        
        # Vertical movement - accelerates the rocket up to a maximum velocity
        if self.fly:
            self.rocket_thrust = min(self.rocket_thrust + self.game.THRUSTER_POWER, 
                                self.game.MAX_THRUST)
            self.vel_y = max(self.vel_y - self.rocket_thrust, -self.game.MAX_RISE_SPEED)
            self.update_action(1)  # Flying animation
        else:
            self.rocket_thrust = 0.0
            if not self.moving_left and not self.moving_right:
                self.update_action(0)  # Idle animation
        
        # Apply gravity if not grounded
        if not self.grounded:
            self.vel_y = min(self.vel_y + self.game.GRAVITY, self.game.MAX_FALL_SPEED)
        
        
        
        # Cap vertical velocity
        self.vel_y = max(-self.game.MAX_RISE_SPEED, 
                        min(self.game.MAX_FALL_SPEED, self.vel_y))
        
        dy += self.vel_y
        
        # Screen scrolling
        screen_scroll = 0
        if self.rect.top < self.game.SCROLL_THRESH:
            screen_scroll = self.game.SCROLL_THRESH - self.rect.top
            self.rect.top = self.game.SCROLL_THRESH
        elif self.rect.bottom > self.game.SCREEN_HEIGHT - self.game.SCROLL_THRESH:
            screen_scroll = (self.game.SCREEN_HEIGHT - self.game.SCROLL_THRESH) - self.rect.bottom
            self.rect.bottom = self.game.SCREEN_HEIGHT - self.game.SCROLL_THRESH
        
        # Floor collision
        floor_y = self.game.FLOOR_Y + self.game.bg_scroll
        if self.rect.bottom + dy >= floor_y:
            dy = floor_y - self.rect.bottom
            self.vel_y = 0
            self.grounded = True
        else:
            self.grounded = False
        
        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        return screen_scroll
    
    def update_animation(self):
        """Update current animation frame"""
        animation = list(self.animations.values())[self.action]
        if pygame.time.get_ticks() - self.update_time > self.game.ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(animation)
        
        # Apply rotation
        base_image = animation[self.frame_index]
        if self.rotation_angle != 0:
            self.image = pygame.transform.rotate(base_image, self.rotation_angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = base_image
    
    def update_action(self, new_action: int):
        """Change animation state"""
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def update(self):
        """Update sprite state"""
        # Add another condition like self.update_action(3) to add another animation (ensure there is a respective dictionary element)
        if not self.alive:
            self.update_action(2)  # Death animation
        elif self.fly:
            self.update_action(1)  # Flying
        elif not self.moving_left and not self.moving_right:
            self.update_action(0)  # Idle
        
        self.update_animation()
        
        # Check health - no negative health values
        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def reset(self):
        """Reset player to initial state"""
        self.rect.center = (200, self.game.FLOOR_Y - 100)
        self.health = self.max_health
        self.alive = True
        self.vel_y = 0
        self.rocket_thrust = 0
        self.update_action(0)

class Meteor(pygame.sprite.Sprite):
    """Meteor sprite with both enemy and hint variants"""
    
    def __init__(self, game: Game, meteor_type: str, x: int, y: int, scale: float):
        super().__init__()
        self.game = game
        self.meteor_type = meteor_type
        self.scale = scale
        
        if self.meteor_type == 'Hint':
            # Use random hint image
            self.image = random.choice(self.game.hint_images)
            self.rect = self.image.get_rect(center=(x, y))
            self.speed = 0
            self.direction = 0
        else:
            # Enemy meteor setup
            self.direction = random.choice([-1, 1])
            self.speed = random.uniform(4, 16)  # Change these arguments for min and max meteor speeds respectively
            self.animations = {
                'Idle': self.load_animation_frames('../Project/Meteor/Asteroid 1/Idle'),
                'Moving': self.load_animation_frames('../Project/Meteor/Asteroid 1/Moving')
            }
            self.action = 1  # Always moving for enemies
            self.image = self.animations['Moving'][0]
            self.rect = self.image.get_rect(center=(x, y))
        
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
    def load_animation_frames(self, folder_path: str) -> List[pygame.Surface]:
        """Load animation frames for enemy meteors"""
        frames = []
        try:
            for file in sorted(os.listdir(folder_path)):
                if file.endswith('.png'):
                    frames.append(self.game.load_image(os.path.join(folder_path, file), self.scale))
        except:
            frames.append(pygame.Surface((50, 50), pygame.SRCALPHA))
        return frames
    
    def spawn(self):
        """Initialize meteor starting position (enemies only)"""
        if self.meteor_type == 'Enemy':
            if self.direction == -1:
                self.rect.x = self.game.SCREEN_WIDTH
            elif self.direction == 1:
                self.rect.x = -self.rect.width
            else:
                self.rect.x = random.randint(0, self.game.SCREEN_WIDTH // 2)
            
            self.rect.y = random.randint(200, self.game.SCREEN_HEIGHT // 2)
    
    def update_animation(self):
        """Update enemy meteor animation"""
        if self.meteor_type == 'Hint':
            return
            
        if pygame.time.get_ticks() - self.update_time > self.game.ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.animations['Moving'])
        
        base_image = self.animations['Moving'][self.frame_index]
        
        # Apply rotation based on direction
        if self.direction == -1:
            self.image = pygame.transform.rotate(base_image, 250)
        elif self.direction == 1:
            self.image = pygame.transform.rotate(base_image, 70)
        else:
            self.image = pygame.transform.rotate(base_image, 70)
    
    def update(self):
        """Update meteor position and animation"""
        # Move with screen scroll
        self.rect.y += self.game.screen_scroll
        
        # Enemy meteors move horizontally
        if self.meteor_type == 'Enemy':
            self.rect.x += self.direction * self.speed
            
            # Remove if off-screen (enemies only)
            if (self.rect.right < 0 or self.rect.left > self.game.SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > self.game.SCREEN_HEIGHT):
                self.kill()
        
        self.update_animation()

class FinishLine(pygame.sprite.Sprite):
    """Finish line sprite"""
    
    def __init__(self, game: Game, x: int, y: int):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((800, 10), pygame.SRCALPHA)
        self.image.fill((0, 255, 0, 128))
        
        # Add text
        font = pygame.font.SysFont(game.FONT, 24)
        text = font.render("FINISH LINE", True, self.game.WHITE)
        self.image.blit(text, (self.image.get_width()//2 - text.get_width()//2, 
                              self.image.get_height()//2 - text.get_height()//2))
        
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self):
        """Finish line doesn't move with scrolling"""
        pass

async def async_main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    game = Game()
    asyncio.run(async_main())
    pygame.quit()