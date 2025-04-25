import pygame
import os
import random
from typing import List, Tuple, Dict, Optional, Literal
import math
from enum import Enum, auto
import asyncio

"=== MINIGAME 5 ==="

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
        self.BLUE = (0, 0, 255)
        
        # Game physics and settings
        self.GRAVITY = 0.5
        self.THRUSTER_POWER = 0.15
        self.MAX_THRUST = 1.2
        self.MAX_FALL_SPEED = 10
        self.MAX_RISE_SPEED = 15
        self.FLOOR_Y = self.SCREEN_HEIGHT - 50
        self.TOP_SCROLL_THRESH = 220  # Larger value = more space at top
        self.BOTTOM_SCROLL_THRESH = 160  # Smaller value = less space at bottom
        self.ENEMY_SPAWN_INTERVAL = 3000  # milliseconds
        
        # Game variables
        self.firing = False
        self.firing_backwards = False
        self.enemy_spawn_timer = 0
        
        # Game timing
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.ANIMATION_COOLDOWN = 100
        
        # Game state
        self.screen_scroll = 0
        self.bg_scroll = 0
        self.running = True
        self.level_complete = False
        self.hint_count = 0
        
        # Sprite groups
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        # Load assets
        self.load_assets()
        
        # Create game objects
        self.player = Rocket(self, 200, self.FLOOR_Y - 100)
        self.all_sprites.add(self.player)
        
        # Create finish line
        self.finish_line = FinishLine(self, 0, -10000)
        self.all_sprites.add(self.finish_line)

    def load_assets(self):
        """Load all game assets with forced hint visibility"""
        # Background
        self.moving_background = self.load_image('../Project/Background/level_1.png')

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
        
    def spawn_enemy(self, enemy_type=None):
        if enemy_type is None:
            enemy_type = random.choice(['chaser', 'shooter', 'patroller'])

        player_pos = pygame.math.Vector2(self.player.rect.center)
        safe_distance = 250  # Minimum distance from player (adjust as needed)

        max_attempts = 10
        for _ in range(max_attempts):
            x = random.randint(50, self.SCREEN_WIDTH - 50)
            y = random.randint(-self.bg_scroll - 600, -self.bg_scroll - 100)
            spawn_pos = pygame.math.Vector2(x, y)

            if spawn_pos.distance_to(player_pos) >= safe_distance:
                enemy = EnemyAI(self, x, y, enemy_type)
                self.enemy_group.add(enemy)
                self.all_sprites.add(enemy)
                break

    def spawn_wave(self, wave_size=3):
        player_pos = pygame.math.Vector2(self.player.rect.center)
        safe_distance = 250

        for i in range(wave_size):
            for _ in range(10):  # Try 10 times to get a valid position
                x = random.randint(50, self.SCREEN_WIDTH - 50)
                y = random.randint(self.bg_scroll - 600, self.bg_scroll - 100) - (i * 100)
                spawn_pos = pygame.math.Vector2(x, y)

                if spawn_pos.distance_to(player_pos) >= safe_distance:
                    enemy_type = random.choice(['chaser', 'shooter', 'patroller'])
                    enemy = EnemyAI(self, x, y, enemy_type)
                    self.enemy_group.add(enemy)
                    self.all_sprites.add(enemy)
                    break

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
            
        ratio = health / max_health
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
        
        # Percentage text
        font = pygame.font.SysFont(self.FONT, 16)
        text = font.render(f"{int(progress * 100)}%", True, self.WHITE)
        self.screen.blit(text, (self.SCREEN_WIDTH//2 - text.get_width()//2, 35))

    def clear_enemies(self):
        """Remove all enemies from the game"""
        for enemy in self.enemy_group:
            enemy.kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.moving_left = True
                elif event.key == pygame.K_d:
                    self.player.moving_right = True
                elif event.key == pygame.K_w:
                    self.player.fly = True
                elif event.key == pygame.K_r and not self.player.alive:
                    self.reset_level()
                elif event.key == pygame.K_SPACE and self.level_complete:
                    self.reset_level()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f: 
                    self.firing = True
                elif event.key == pygame.K_g: 
                    self.firing_backwards = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.player.moving_left = False
                elif event.key == pygame.K_d:
                    self.player.moving_right = False
                elif event.key == pygame.K_w:
                    self.player.fly = False
                elif event.key == pygame.K_f:
                    self.firing = False
                elif event.key == pygame.K_g: 
                    self.firing_backwards = False

    def update(self):
        if self.player.alive and not self.level_complete:
            
            # Player movement
            self.screen_scroll = self.player.move()
            self.bg_scroll += self.screen_scroll
            
            if self.firing:
                self.player.fire()
            
            if self.firing_backwards:
                self.player.fire_backwards()

            if abs(self.bg_scroll) in [1000, 3000, 6000]:
                self.spawn_wave(random.randint(2, 4))

            # Check level completion
            if abs(self.bg_scroll) >= abs(self.finish_line.rect.y - self.FLOOR_Y):
                self.level_complete = True
        
            # Enemy spawning
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_spawn_timer > self.ENEMY_SPAWN_INTERVAL:
                self.enemy_spawn_timer = current_time
                self.spawn_enemy()
                
            # Enemy collision with player
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemy_group, False)
            for enemy in enemy_hits:
                self.player.health -= 10
                enemy.health -= 20  # Enemy takes damage from collision
                if enemy.health <= 0:
                    enemy.kill()
                if self.player.health <= 0:
                    self.player.alive = False
                    
            # Bullet collision with enemies
            for bullet in self.bullet_group:
                if hasattr(bullet, 'owner'):  # Only check non-owned bullets
                    enemy_hits = pygame.sprite.spritecollide(bullet, self.enemy_group, False)
                    for enemy in enemy_hits:
                        # Skip collision if enemy is the owner of this bullet
                        if enemy is bullet.owner:
                            continue
                            
                        enemy.take_damage(25)
                        bullet.kill()
                        if enemy.health <= 0:
                            enemy.kill()

        self.all_sprites.update()

    def render(self):
        self.draw_background()
        self.all_sprites.draw(self.screen)
        
        for enemy in self.enemy_group:
            enemy.draw_health_bar(self.screen)

        # UI elements
        self.draw_health_bar(10, 10, self.player.health, self.player.max_health)
        self.draw_progress()
        
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
        self.clear_enemies()
        # self.clear_meteors()
        self.player.reset()
        # self.spawn_initial_objects()

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
            await asyncio.sleep(0)  # This yields control to the event loop

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
        self.last_shot = 0
        self.shot_cooldown = 300 # milliseconds
        
        # Load animations
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
        
        # Horizontal movement
        if self.moving_left:
            dx = -self.speed
            self.rotation_angle = 10
        elif self.moving_right:
            dx = self.speed
            self.rotation_angle = -10
        else:
            self.rotation_angle = 0
        
        # Vertical movement
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
        if self.rect.top < self.game.TOP_SCROLL_THRESH:
            screen_scroll = self.game.TOP_SCROLL_THRESH - self.rect.top
            self.rect.top = self.game.TOP_SCROLL_THRESH
        elif self.rect.bottom > self.game.SCREEN_HEIGHT - self.game.BOTTOM_SCROLL_THRESH:
            screen_scroll = (self.game.SCREEN_HEIGHT - self.game.BOTTOM_SCROLL_THRESH) - self.rect.bottom
            self.rect.bottom = self.game.SCREEN_HEIGHT - self.game.BOTTOM_SCROLL_THRESH
        
        # Floor collision (working version from previous iteration)
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
    
    def fire(self):
        """Fire a bullet upwards from the rocket"""
        now = pygame.time.get_ticks()
        if self.alive and now - self.last_shot > self.shot_cooldown:  # Only fire if alive and after the cooldown has finished
            # This always fires bullets upwards
            self.last_shot = now
            bullet = Bullet(self.game, self.rect.centerx, self.rect.top, 'up')
            self.game.bullet_group.add(bullet)
            self.game.all_sprites.add(bullet)
    
    def fire_backwards(self):
        """Fire a bullet upwards from the rocket"""
        now = pygame.time.get_ticks()
        if self.alive and now - self.last_shot > self.shot_cooldown:  # Only fire if alive and after the cooldown has finished
            # This always fires bullets upwards
            self.last_shot = now
            bullet = Bullet(self.game, self.rect.centerx, self.rect.bottom, 'down')
            self.game.bullet_group.add(bullet)
            self.game.all_sprites.add(bullet)
        
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
        if not self.alive:
            self.update_action(2)  # Death animation
        elif self.fly:
            self.update_action(1)  # Flying
        elif not self.moving_left and not self.moving_right:
            self.update_action(0)  # Idle
        
        self.update_animation()
        
        # Check health
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game: Game, x: int, y: int, direction: str):
        pygame.sprite.Sprite.__init__(self)
        self.game = game  
        self.speed = 15  
        self.direction = direction
        
        self.image = pygame.Surface((2, 10), pygame.SRCALPHA)  
        self.image.fill(self.game.YELLOW)
        
        self.rect = self.image.get_rect()
        
        if direction == 'up':
            self.rect.midbottom = (x, y)  
        elif direction == 'down':
            self.rect.midtop = (x, y)  

    def update(self):
        """Move bullet and handle collisions"""
        # Movement based on direction
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
            
        # Remove if off-screen
        if (self.rect.bottom < 0 or 
            self.rect.top > self.game.SCREEN_HEIGHT or
            self.rect.right < 0 or 
            self.rect.left > self.game.SCREEN_WIDTH):
            self.kill()
            
        # Only check for enemy collisions now
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemy_group, False)
        for enemy in enemy_hits:
            enemy.take_damage(25)
            self.kill()
            break

class EnemyState(Enum):
    PATROL = auto()
    CHASE = auto()
    ATTACK = auto()

class EnemyAI(pygame.sprite.Sprite):
    # Class-level constants
    DETECTION_RADIUS = 300
    ATTACK_RADIUS = 200
    PATROL_DIRECTION_CHANGE_CHANCE = 0.02
    BASE_SPEED = 3
    FRICTION = 0.95

    def __init__(self, game: 'Game', x: int, y: int, enemy_type: Literal['chaser', 'shooter', 'patroller']):
        super().__init__()
        self.game = game
        self.ENEMY_HEALTH = {
            'chaser': 25,
            'shooter': 50,
            'patroller': 100
        }
        self.type = enemy_type
        self.max_health = self.ENEMY_HEALTH[enemy_type]
        self.health = self.max_health
        self.speed = self.BASE_SPEED

        # Position
        self.x = x
        self.y = y  # World Y

        # Movement
        self.direction = pygame.math.Vector2(1, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # Combat
        self.state = EnemyState.PATROL
        self.last_shot = 0
        self.shot_cooldown = random.randint(800, 1200)
        self.hit_flash_timer = 0
        self.hit_flash_duration = 200

        # Visual
        self._create_enemy_image()
        self.rect = self.image.get_rect(center=(self.x, self.y - self.game.bg_scroll))

    def _create_enemy_image(self):
        size = 30
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = {
            'chaser': pygame.Color('red'),
            'shooter': pygame.Color('blue'),
            'patroller': pygame.Color('green')
        }
        self.image.fill(colors.get(self.type, pygame.Color('white')))
        pygame.draw.polygon(self.image, pygame.Color('black'), [(15, 0), (0, 30), (30, 30)])
        self.original_image = self.image.copy()

    def update(self):
        self._update_state()
        self._execute_behavior()
        self._update_movement()
        self._update_attack()
        self._update_hit_flash()
        self._check_offscreen()

        # Sync rect with world position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y + self.game.bg_scroll)

    def _update_state(self):
        if not hasattr(self.game, 'player') or not self.game.player:
            self.state = EnemyState.PATROL
            return
        player_pos = pygame.math.Vector2(self.game.player.rect.center)
        distance = player_pos.distance_to(pygame.math.Vector2(self.rect.center))
        if self.type == 'shooter' and distance < self.ATTACK_RADIUS:
            self.state = EnemyState.ATTACK
        elif self.type == 'chaser' and distance < self.DETECTION_RADIUS:
            self.state = EnemyState.CHASE
        else:
            self.state = EnemyState.PATROL

    def _execute_behavior(self):
        if self.state == EnemyState.PATROL:
            self._patrol_behavior()
        elif self.state == EnemyState.CHASE:
            self._chase_behavior()
        elif self.state == EnemyState.ATTACK:
            self._attack_behavior()

    def _patrol_behavior(self):
        if random.random() < self.PATROL_DIRECTION_CHANGE_CHANCE:
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), 0)
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
        self.acceleration = self.direction * 0.1

    def _chase_behavior(self):
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        direction = pygame.math.Vector2(self.game.player.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
        self.acceleration = direction * 0.2

    def _attack_behavior(self):
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        direction = pygame.math.Vector2(self.game.player.rect.center) - pygame.math.Vector2(self.rect.center)
        desired_distance = 150
        if direction.length() > desired_distance:
            if direction.length() > 0:
                direction = direction.normalize()
            self.acceleration = direction * 0.15
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

    def _update_movement(self):
        self.velocity += self.acceleration
        self.velocity *= self.FRICTION
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.x = max(0, min(self.game.SCREEN_WIDTH - self.rect.width, self.x))

    def _update_attack(self):
        if self.type == 'shooter' and self.state == EnemyState.ATTACK:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_cooldown:
                self.last_shot = now
                self.fire()

    def fire(self):
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        direction = pygame.math.Vector2(self.game.player.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
        start_pos = (
            self.rect.centerx + direction.x * 20,
            self.rect.centery + direction.y * 20
        )
        bullet = EnemyBullet(self.game, *start_pos, direction, owner=self)  # Pass self as owner
        self.game.bullet_group.add(bullet)
        self.game.all_sprites.add(bullet)

    def take_damage(self, amount: int):
        self.health -= amount
        self.hit_flash_timer = pygame.time.get_ticks()
        self.image.fill(pygame.Color('red'))
        if self.health <= 0:
            self.kill()

    def _update_hit_flash(self):
        if pygame.time.get_ticks() - self.hit_flash_timer > self.hit_flash_duration:
            self.image = self.original_image.copy()

    def _check_offscreen(self):
        screen_rect = self.game.screen.get_rect()
        # Only kill if COMPLETELY off the screen in BOTH directions
        if self.rect.right < 0 or self.rect.left > screen_rect.width:# "or self.rect.bottom < 0 or self.rect.top > screen_rect.height:"
            self.kill()

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        bar_width = self.rect.width
        bar_height = 6
        fill_width = max(2, int(bar_width * health_ratio))
        outline_rect = pygame.Rect(self.rect.left, self.rect.top - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top - 10, fill_width, bar_height)
        pygame.draw.rect(surface, (0, 0, 0), outline_rect)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect, 1)
        color = (0, 255, 0) if health_ratio > 0.6 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(surface, color, fill_rect)

class EnemyBullet(pygame.sprite.Sprite):
    """Projectile fired by enemy AI"""
    
    def __init__(self, game: Game, x: int, y: int, direction: pygame.math.Vector2, owner=None):
        super().__init__()
        self.game = game
        self.speed = 7
        self.direction = direction
        self.damage = 10
        self.owner = owner  # Store reference to the enemy that fired this bullet
        
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        self.image.fill(self.game.RED)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Rotate bullet to face direction
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        self.image = pygame.transform.rotate(self.image, angle)
    
    def update(self):
        """Move bullet with opposite effect of background scroll"""
        # Standard movement (direction * speed)
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # Counteract background scroll (move opposite to scroll direction)
        self.rect.y += self.game.screen_scroll  # Add scroll to oppose movement
        
        # Remove if off-screen
        if (self.rect.right < 0 or self.rect.left > self.game.SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > self.game.SCREEN_HEIGHT):
            self.kill()
        
        # Check for player collision (player's position is already scroll-adjusted)
        if pygame.sprite.collide_rect(self, self.game.player):
            self.game.player.health -= self.damage
            self.kill()

async def async_main():
    """Async entry point for the game"""
    game = Game()
    await game.run()

if __name__ == "__main__":
    game = Game()
    asyncio.run(async_main())
    pygame.quit()