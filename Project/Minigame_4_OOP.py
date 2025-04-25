import pygame
import pymunk
import pymunk.pygame_util
import asyncio
import random
from typing import List, Tuple, Optional

"=== MINIGAME 4 ==="

def simulate_trajectory_in_temp_space(
    init_position: Tuple[float, float],
    init_velocity: pymunk.Vec2d,
    planets: List['Planet'],  # Now takes full Planet objects
    projectile_mass: float = 0.2,
    projectile_radius: float = 10,
    dt: float = 1/60.0,
    max_steps: int = 300,
    screen_bounds: Tuple[int, int] = (800, 640)
) -> List[Tuple[int, int]]:
    """Simulates a projectile trajectory in a temporary Pymunk space with multiple gravity fields."""
    temp_space = pymunk.Space()
    temp_space.gravity = (0, 0)

    moment = pymunk.moment_for_circle(projectile_mass, 0, projectile_radius)
    dummy_body = pymunk.Body(projectile_mass, moment)
    dummy_body.position = init_position
    dummy_body.velocity = init_velocity
    dummy_shape = pymunk.Circle(dummy_body, projectile_radius)
    dummy_shape.elasticity = 0.6
    dummy_shape.friction = 0.4
    temp_space.add(dummy_body, dummy_shape)

    points = []
    for _ in range(max_steps):
        total_force = pymunk.Vec2d(0, 0)

        for planet in planets:
            direction = planet.body.position - dummy_body.position
            distance = direction.length
            min_distance = planet.radius
            max_distance = planet.gravity_field_radius

            if min_distance <= distance < max_distance:
                force = direction.normalized() * max(planet.gravitational_field_strength / (distance ** 2), 5)
                total_force += force
            elif distance < min_distance:
                dummy_body.velocity *= 0.87

        dummy_body.apply_force_at_world_point(total_force, dummy_body.position)
        dummy_body.angular_velocity *= 0.8
        temp_space.step(dt)

        x, y = dummy_body.position
        points.append((int(x), int(y)))

        if x < 0 or x > screen_bounds[0] or y < 0 or y > screen_bounds[1] or dummy_body.velocity.length < 10:
            break

    return points

class GameConstants:
    """Centralized game constants"""
    def __init__(self):
        # Screen dimensions
        self.WIDTH = 800
        self.HEIGHT = 640
        self.FONT = "Arial"
        self.MAX_PROJECTILES = 5
        
        # Physics parameters
        self.PLANET_RADIUS = 50
        self.GRAVITY_FIELD_RADIUS = 3 * self.PLANET_RADIUS
        self.GRAVITY_STRENGTH = 1000000
        self.PLANET_POS = pymunk.Vec2d(600, 600)
        self.SLINGSHOT_POS = pymunk.Vec2d(100, 500)

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.SLINGSHOT_COLOR = (66, 73, 73)
        self.TRAJECTORY_COLOR = (255, 255, 255, 100)

class PhysicsObject:
    """Base class for physics objects with safe initialization"""
    def __init__(self, space: pymunk.Space, position: Tuple[float, float]):
        self.space = space
        self.body = None
        self.shape = None
        self._initialize_physics(position)
    
    def _initialize_physics(self, position: Tuple[float, float]):
        """Initialize physics properties - to be overridden by subclasses"""
        pass
    
    def add_to_space(self):
        """Add to physics space if not already added"""
        if self.body and self.shape and self.body not in self.space.bodies:
            self.space.add(self.body, self.shape)
    
    def remove_from_space(self):
        """Remove from physics space if present"""
        if self.body and self.shape and self.body in self.space.bodies:
            self.space.remove(self.body, self.shape)
    
    def draw(self, surface: pygame.Surface):
        """Draw the object - to be overridden by subclasses"""
        pass

class Planet(PhysicsObject):
    """Planetary body with gravity"""
    def __init__(self, space: pymunk.Space, constants: GameConstants, position: pymunk.Vec2d, gravitational_field_strength: float, radius: int):
        self.constants = constants
        # Scale gravity strength by radius (using inverse square law)
        self.gravitational_field_strength = gravitational_field_strength * (radius**2) / (constants.PLANET_RADIUS**2)
        self.radius = radius
        self.gravity_field_radius = radius * 3
        super().__init__(space, position)
    
    def _initialize_physics(self, position: Tuple[float, float]):
        """Initialize planet physics"""
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.8
        self.shape.friction = 0.4
        self.add_to_space()
    
    def draw(self, surface: pygame.Surface):
        if not self.body:
            return
            
        pos = (int(self.body.position.x), int(self.body.position.y))
        
        # Draw gravity field - USE THE PLANET'S OWN FIELD RADIUS
        pygame.draw.circle(surface, self.constants.WHITE, pos, self.gravity_field_radius)
        pygame.draw.circle(surface, self.constants.BLACK, pos, self.gravity_field_radius - 2)
        
        # Draw planet
        pygame.draw.circle(surface, self.constants.GREEN, pos, self.radius)

class Projectile(PhysicsObject):
    """Projectile that can be launched with velocity-based physics"""
    def __init__(self, space: pymunk.Space, position: Tuple[float, float]):
        self.radius = 5
        self.mass = 0.2
        self.launched = False
        self.should_remove = False
        super().__init__(space, position)
    
    def _initialize_physics(self, position: Tuple[float, float]):
        """Initialize projectile physics"""
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.4
    
    def launch(self, velocity: pymunk.Vec2d):
        """Launch with exact velocity (matches prediction)"""
        if not self.launched:
            self.add_to_space()
            self.body.velocity = velocity  # Set velocity directly
            self.launched = True
    
    def draw(self, surface: pygame.Surface):
        """Draw the projectile"""
        if self.body:
            pygame.draw.circle(
                surface, 
                (255, 255, 255),
                (int(self.body.position.x), int(self.body.position.y)), 
                self.radius
            )

class Slingshot:
    """Slingshot for launching projectiles"""
    def __init__(self, constants: GameConstants, physics_world):
        self.constants = constants
        self.physics_world = physics_world
        self.width = 30
        self.height = 100
        self.position = constants.SLINGSHOT_POS
        self.loaded_projectile = None
        self.dragging = False
        
        # Physics tuning
        self.min_launch_speed = 300  # pixels/sec
        self.max_launch_speed = 1000
        self.pull_to_speed_ratio = 0.8
        self.min_pull = 15  # pixels
        self.max_pull = 100
    
    def load_projectile(self, projectile: Projectile):
        """Load projectile only if under limit"""
        if self.physics_world.active_projectiles <= self.physics_world.constants.MAX_PROJECTILES:
            if self.loaded_projectile:
                self.loaded_projectile.remove_from_space()
            self.loaded_projectile = projectile
            self.dragging = False
        else:
            # Immediately remove the new projectile if over limit
            projectile.remove_from_space()
    
    def _calculate_launch_velocity(self, pull_vector: pymunk.Vec2d):
        """Core physics used by both release() and predict_trajectory()"""
        pull_distance = max(pull_vector.length - self.min_pull, 0)
        # Enforce maximum pull distance
        pull_distance = min(pull_distance, self.max_pull)
        speed = min(pull_distance * self.pull_to_speed_ratio, self.max_launch_speed)
        speed = max(speed, self.min_launch_speed)
        return pull_vector.normalized() * speed

    def release(self):
        """Launch projectile with velocity matching prediction"""
        if not self.loaded_projectile:
            return None
            
        pull_vector = self.position - self.loaded_projectile.body.position
        velocity = self._calculate_launch_velocity(pull_vector)
        self.loaded_projectile.launch(velocity)
        
        launched = self.loaded_projectile
        self.loaded_projectile = None
        return launched
    
    def draw(self, surface: pygame.Surface):
        """Draw the slingshot and its loaded projectile"""
        # Draw base
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x, self.position.y + self.height * 1/3, 
             self.width, self.height * 2/3)
        )
        
        # Draw frame
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x - self.width/4, self.position.y, 
             self.width/2, self.height/3), 
            5
        )
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x + self.width - self.width/4, self.position.y, 
             self.width/2, self.height/3), 
            5
        )
        
        # Draw bands if loaded
        if self.loaded_projectile and self.loaded_projectile.body:
            band_start_left = (self.position.x - self.width/4, self.position.y + self.height/6)
            band_start_right = (self.position.x + self.width, self.position.y + self.height/6)
            projectile_pos = (int(self.loaded_projectile.body.position.x), 
                             int(self.loaded_projectile.body.position.y))
            
            pygame.draw.line(
                surface, 
                (100, 30, 22), 
                band_start_left, 
                projectile_pos, 
                5
            )
            pygame.draw.line(
                surface, 
                (100, 30, 22), 
                band_start_right, 
                projectile_pos, 
                5
            )
    
    def predict_trajectory(self, surface: pygame.Surface):
        """Accurate prediction using temporary pymunk simulation"""
        if not self.loaded_projectile or not self.loaded_projectile.body:
            return

        # Compute initial velocity based on slingshot pull
        pull_vector = self.position - self.loaded_projectile.body.position
        velocity = self._calculate_launch_velocity(pull_vector)

        points = simulate_trajectory_in_temp_space(
            init_position=self.loaded_projectile.body.position,
            init_velocity=velocity,
            planets=self.physics_world.planets,  # Pass the full planet objects
            projectile_mass=self.loaded_projectile.mass,
            projectile_radius=self.loaded_projectile.radius,
            screen_bounds=(self.constants.WIDTH, self.constants.HEIGHT)
        )

        # Draw trajectory
        if len(points) > 1:
            pygame.draw.lines(surface, (255, 255, 255, 150), False, points, 2)

class PhysicsWorld:
    """Manages the physics simulation and objects"""
    def __init__(self, constants: GameConstants):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # We'll handle gravity manually
        self.constants = constants
        self.active_projectiles = 0
        self.objects: List[PhysicsObject] = []
        self.planets: List[Planet] = []
        self._create_boundaries()
    
    def _create_boundaries(self):
        """Create walls around the screen"""
        width, height = self.constants.WIDTH, self.constants.HEIGHT
        rects = [
            [(width/2, height - 10), (width, 20)],
            [(width/2, 10), (width, 20)],
            [(10, height/2), (20, height)],
            [(width - 10, height/2), (20, height)]
        ]

        for pos, size in rects:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            shape = pymunk.Poly.create_box(body, size)
            shape.elasticity = 0.4
            shape.friction = 0.5
            self.space.add(body, shape)
    
    def add_object(self, obj: PhysicsObject):
        """Add object with projectile limit enforcement"""
        if isinstance(obj, Projectile):
            # Remove oldest projectile if at limit
            if self.active_projectiles >= self.constants.MAX_PROJECTILES:
                self._remove_oldest_projectile()
            
            self.active_projectiles += 1
        
        self.objects.append(obj)
        obj.add_to_space()
    
    def add_planet(self, position: Optional[pymunk.Vec2d] = None, gravitational_field_strength: Optional[float] = None, radius: Optional[int] = None) -> Planet:
        if position is None:
            position = self.constants.PLANET_POS
        if gravitational_field_strength is None:
            gravitational_field_strength = self.constants.GRAVITY_STRENGTH
        if radius is None:
            radius = self.constants.PLANET_RADIUS
        planet = Planet(self.space, self.constants, position, gravitational_field_strength, radius)
        self.planets.append(planet)
        self.objects.append(planet)
        return planet
    
    def _remove_oldest_projectile(self):
        """Finds and removes the oldest projectile"""
        for obj in self.objects:
            if isinstance(obj, Projectile):
                obj.remove_from_space()
                self.objects.remove(obj)
                self.active_projectiles -= 1
                break
    

    def apply_gravity(self):
        """Apply gravity forces from all planets"""
        for obj in self.objects:
            if isinstance(obj, Projectile) and obj.body:
                for planet in self.planets:
                    self._apply_radial_gravity(obj.body, planet)

    
    def _apply_radial_gravity(self, body: pymunk.Body, planet: Planet):
        """Apply radial gravity from a single planet"""
        direction = planet.body.position - body.position
        distance = direction.length
        min_distance = planet.radius
        max_distance = planet.gravity_field_radius

        if min_distance <= distance < max_distance:
            force = direction.normalized() * max(planet.gravitational_field_strength / (distance ** 2), 5)
            body.apply_force_at_world_point(force, body.position)
        elif distance < min_distance:
            body.velocity *= 0.87
        body.angular_velocity *= 0.8

    def update(self, dt: float):
        """Update physics without auto-removal"""
        self.apply_gravity()
        self.space.step(dt)
    
    def draw(self, surface: pygame.Surface):
        """Draw all physics objects"""
        for obj in self.objects:
            obj.draw(surface)

class Game:
    """Main game class"""
    def __init__(self):
        pygame.init()
        self.constants = GameConstants()
        self.screen = pygame.display.set_mode(
            (self.constants.WIDTH, self.constants.HEIGHT))
        pygame.display.set_caption("Orbital Physics Game")
        
        # Setup physics
        self.physics_world = PhysicsWorld(self.constants)
        
        # Create slingshot
        self.slingshot = Slingshot(self.constants, self.physics_world)
        
        # Game state
        self.running = False
        self.dragging = False
        self.projectiles: List[Projectile] = []
        
        # Setup drawing
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Stages
        self.stages = {
            1: {
                "planets": [
                    {"pos": pymunk.Vec2d(400, 320), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            2: {
                "planets": [
                    {"pos": pymunk.Vec2d(400, 400), "gravity": 2e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": pymunk.Vec2d(200, 300), "gravity": 1.5e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            3: {
                "planets": [
                    {"pos": pymunk.Vec2d(300, 500), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": pymunk.Vec2d(700, 200), "gravity": 2e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": pymunk.Vec2d(500, 100), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            4: {
                "planets": [
                    {"pos": pymunk.Vec2d(400, 300), "gravity": 1e7, "radius": 30},
                    {"pos": pymunk.Vec2d(500, 500), "gravity": 3e6, "radius": 25}
                ]
            },
            5: {
                "planets": [
                    {"pos": pymunk.Vec2d(600, 300), "gravity": 3e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": pymunk.Vec2d(300, 600), "gravity": 2e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
        }
        self.current_stage = 1
        self.max_stages = len(self.stages)
        self.load_stage(self.current_stage)


    async def run(self):
        """Main game loop"""
        self.running = True
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            await self._handle_events()
            
            # Update physics
            self.physics_world.update(1/60.0)
            
            # Draw everything
            self._draw_frame()
            
            # Cap the frame rate
            await asyncio.sleep(1/60.0)
            clock.tick(60)
        
        pygame.quit()
    
    async def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:  # Reset projectile
                    self.reset_level()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    await self._handle_mouse_down(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    await self._handle_mouse_up()
    
    async def _handle_mouse_down(self, pos: Tuple[int, int]):
        """Handle mouse button down event"""
        if not self.slingshot.loaded_projectile:
            # Check projectile limit before creating new one
            if self.physics_world.active_projectiles < self.physics_world.constants.MAX_PROJECTILES:
                projectile = Projectile(self.physics_world.space, pos)
                self.physics_world.add_object(projectile)
                self.slingshot.load_projectile(projectile)
                self.dragging = True
    
    async def _handle_mouse_up(self):
        """Handle mouse button up event"""
        if self.dragging and self.slingshot.loaded_projectile:
            launched_projectile = self.slingshot.release()
            if launched_projectile:
                self.projectiles.append(launched_projectile)
            self.dragging = False

    def _draw_frame(self):
        """Draw the current frame"""
        self.screen.fill(self.constants.BLACK)
        
        # Draw physics objects
        self.physics_world.draw(self.screen)
        
        # Draw slingshot and trajectory
        self.slingshot.draw(self.screen)
        # Update projectile position if dragging
        if self.slingshot.loaded_projectile and self.dragging and self.slingshot.loaded_projectile.body:
            mouse_pos = pygame.mouse.get_pos()
            pull_vector = pymunk.Vec2d(*mouse_pos) - self.slingshot.position
        
            # Enforce maximum pull distance visually
            if pull_vector.length > self.slingshot.max_pull:
                pull_vector = pull_vector.normalized() * self.slingshot.max_pull
                mouse_pos = (self.slingshot.position + pull_vector).int_tuple
            
            self.slingshot.loaded_projectile.body.position = mouse_pos
            self.slingshot.predict_trajectory(self.screen)
            self.slingshot.loaded_projectile.body.position = mouse_pos
        
        font = pygame.font.SysFont(self.constants.FONT, 24)
        counter_text = font.render(
            f"Projectiles: {self.physics_world.active_projectiles}/{self.constants.MAX_PROJECTILES}",
            True, 
            (255, 255, 255)
        )
        self.screen.blit(counter_text, (10, 10))

        if self.physics_world.active_projectiles >= self.physics_world.constants.MAX_PROJECTILES:
            font = pygame.font.SysFont(self.constants.FONT, 32)
            warning = font.render("MAX PROJECTILES REACHED! Press R to reset", True, (255, 0, 0))
            self.screen.blit(warning, (self.constants.WIDTH//2 - 350, 50))

        self.check_stage_complete()
        
        pygame.draw.rect(
            self.screen,
            (255, 255, 0),
            pygame.Rect(700, 100, 50, 50),
            width=2
        )
        pygame.draw.circle(
            self.screen, 
            (*self.constants.SLINGSHOT_COLOR, 50),  # Semi-transparent
            (int(self.slingshot.position.x), int(self.slingshot.position.y)), 
            self.slingshot.max_pull,
            1  # Thin outline
        )
        font = pygame.font.SysFont(self.constants.FONT, 16)
        goal_text = font.render("GOAL", True, (255, 255, 0))
        self.screen.blit(goal_text, (705, 105))

        pygame.display.flip()
    
    def load_stage(self, stage_num: int):
        print(f"Loading Stage {stage_num}")
        
        # Reset physics world
        self.physics_world = PhysicsWorld(self.constants)
        self.slingshot = Slingshot(self.constants, self.physics_world)
        self.projectiles.clear()
        self.dragging = False

        # Load planet config
        stage_config = self.stages.get(stage_num)
        if not stage_config:
            print("All stages complete!")
            self.running = False
            return

        for planet_data in stage_config["planets"]:
            self.physics_world.add_planet(
                position=planet_data["pos"],
                gravitational_field_strength=planet_data["gravity"],
                radius=planet_data["radius"]
            )
        if self.current_stage == stage_num:
            return
    
    def check_stage_complete(self):
        for proj in self.projectiles:
            if 700 < proj.body.position.x < 750 and 100 < proj.body.position.y < 150:
                self.current_stage += 1
                if self.current_stage <= self.max_stages:
                    self.load_stage(self.current_stage)
                else:
                    print("Game complete!")
                    self.running = False

    def reset_level(self):
        """Reset the current level completely"""
        # Clear all projectiles
        for obj in self.physics_world.objects[:]:  # Make a copy for safe iteration
            if isinstance(obj, Projectile):
                obj.remove_from_space()
                self.physics_world.objects.remove(obj)
        
        # Reset projectile count
        self.physics_world.active_projectiles = 0
        
        # Reset slingshot state
        self.slingshot.loaded_projectile = None
        self.dragging = False
        
        # Reload the current stage
        self.load_stage(self.current_stage)        

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())