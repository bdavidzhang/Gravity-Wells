"""
Main game engine - handles game loop, input, and state management
"""

import pygame
import math
from game.physics import PhysicsEngine, Vector2D
from game.objects import Spaceship
from game.level import LevelManager

class GameState:
    """Game state enumeration"""
    MENU = 0
    PLAYING = 1
    AIMING = 2
    FLYING = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5

class GameEngine:
    """Main game engine"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen settings
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Gravity Wells - Spaceship Slingshotting Game")
        
        # Game components
        self.clock = pygame.time.Clock()
        self.physics = PhysicsEngine()
        self.level_manager = LevelManager()
        
        # Game state
        self.state = GameState.AIMING
        self.running = True
        self.spaceship = None
        self.current_level = None
        
        # Input handling
        self.mouse_pos = Vector2D(0, 0)
        self.mouse_pressed = False
        self.aim_start = Vector2D(0, 0)
        self.aim_power = 0
        
        # UI settings
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load first level
        self.load_current_level()
    
    def load_current_level(self):
        """Load the current level"""
        self.current_level = self.level_manager.get_current_level()
        if self.current_level:
            # Create spaceship at starting position
            start_pos = self.current_level.spaceship_start
            self.spaceship = Spaceship(start_pos.x, start_pos.y)
            self.state = GameState.AIMING
            
            # Update objects
            for obj in self.current_level.objects:
                if hasattr(obj, 'pulse_timer'):
                    obj.pulse_timer = 0
    
    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.handle_mouse_down()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.handle_mouse_up()
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = Vector2D(event.pos[0], event.pos[1])
    
    def handle_key_press(self, key):
        """Handle keyboard input"""
        if key == pygame.K_r:
            # Restart level
            self.restart_level()
        
        elif key == pygame.K_n:
            # Next level
            if self.level_manager.next_level():
                self.load_current_level()
        
        elif key == pygame.K_p:
            # Previous level
            if self.level_manager.previous_level():
                self.load_current_level()
        
        elif key == pygame.K_SPACE:
            # Use thruster (if spaceship is flying)
            if self.state == GameState.FLYING and self.spaceship.fuel > 0:
                # Apply small thrust in direction of mouse
                thrust_dir = self.mouse_pos - self.spaceship.position
                self.spaceship.use_thruster(thrust_dir.normalize(), 30)
        
        elif key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_mouse_down(self):
        """Handle mouse button down"""
        if self.state == GameState.AIMING:
            self.mouse_pressed = True
            self.aim_start = Vector2D(self.mouse_pos.x, self.mouse_pos.y)
    
    def handle_mouse_up(self):
        """Handle mouse button up"""
        if self.state == GameState.AIMING and self.mouse_pressed:
            self.mouse_pressed = False
            self.launch_spaceship()
    
    def launch_spaceship(self):
        """Launch the spaceship with calculated velocity"""
        if self.spaceship and not self.spaceship.launched:
            # Calculate launch velocity based on mouse drag
            aim_vector = self.aim_start - self.spaceship.position
            power_factor = min(aim_vector.magnitude() / 100.0, 3.0)  # Cap the power
            
            if power_factor > 0.1:  # Minimum power threshold
                launch_velocity = aim_vector.normalize() * power_factor * 100
                self.spaceship.launch(launch_velocity)
                self.state = GameState.FLYING
                self.current_level.shots_used += 1
    
    def update(self, dt):
        """Update game state"""
        if self.state == GameState.AIMING:
            self.update_aiming()
        
        elif self.state == GameState.FLYING:
            self.update_flying(dt)
        
        # Update level objects
        if self.current_level:
            for obj in self.current_level.objects:
                if hasattr(obj, 'update'):
                    obj.update(dt)
    
    def update_aiming(self):
        """Update aiming state"""
        # Calculate aim direction and power for preview
        if self.mouse_pressed and self.spaceship:
            aim_vector = self.aim_start - self.spaceship.position
            self.aim_power = min(aim_vector.magnitude() / 100.0, 3.0)
            
            # Set spaceship velocity for trajectory prediction
            if self.aim_power > 0.1:
                self.spaceship.velocity = aim_vector.normalize() * self.aim_power * 100
            else:
                self.spaceship.velocity = Vector2D(0, 0)
    
    def update_flying(self, dt):
        """Update flying state"""
        if self.spaceship and self.spaceship.launched:
            # Update spaceship physics
            self.physics.update_object_physics(
                self.spaceship, 
                self.current_level.gravity_sources, 
                dt
            )
            
            # Update spaceship
            self.spaceship.update(dt)
            
            # Check collisions
            self.check_collisions()
            
            # Check if spaceship is off screen or moving too slowly
            if (self.spaceship.position.x < -100 or 
                self.spaceship.position.x > self.screen_width + 100 or
                self.spaceship.position.y < -100 or 
                self.spaceship.position.y > self.screen_height + 100):
                self.reset_for_next_shot()
    
    def check_collisions(self):
        """Check for collisions between spaceship and objects"""
        if not self.spaceship or not self.spaceship.launched:
            return
        
        for obj in self.current_level.objects:
            if self.spaceship.collides_with(obj):
                if isinstance(obj, type(self.current_level.goal)) and obj == self.current_level.goal:
                    # Level completed!
                    self.state = GameState.LEVEL_COMPLETE
                    break
                else:
                    # Hit obstacle or planet - reset
                    self.reset_for_next_shot()
                    break
    
    def reset_for_next_shot(self):
        """Reset spaceship for next shot"""
        if self.current_level.shots_used >= self.current_level.max_shots:
            self.state = GameState.GAME_OVER
        else:
            # Reset spaceship
            start_pos = self.current_level.spaceship_start
            self.spaceship = Spaceship(start_pos.x, start_pos.y)
            self.state = GameState.AIMING
    
    def restart_level(self):
        """Restart the current level"""
        self.level_manager.restart_level()
        self.load_current_level()
    
    def draw(self):
        """Render everything to screen"""
        # Clear screen with cool space gradient effect
        self.screen.fill((2, 0, 15))  # Deep space purple-black background
        
        # Draw level objects
        if self.current_level:
            for obj in self.current_level.objects:
                obj.draw(self.screen)
        
        # Draw spaceship
        if self.spaceship:
            self.spaceship.draw(self.screen)
        
        # Draw trajectory prediction when aiming
        if self.state == GameState.AIMING and self.spaceship and self.aim_power > 0.1:
            self.draw_trajectory_prediction()
        
        # Draw aiming line
        if self.state == GameState.AIMING and self.mouse_pressed:
            self.draw_aiming_line()
        
        # Draw UI
        self.draw_ui()
        
        # Draw gravity information
        self.draw_gravity_info()
        
        # Update display
        pygame.display.flip()
    
    def draw_trajectory_prediction(self):
        """Draw predicted trajectory with enhanced visual effects"""
        if self.spaceship and self.spaceship.velocity.magnitude() > 0:
            trajectory = self.physics.predict_trajectory(
                self.spaceship.position,
                self.spaceship.velocity,
                self.spaceship.mass,
                self.current_level.gravity_sources,
                steps=60,
                dt=0.15
            )
            
            # Draw trajectory with gradient and glow effect
            for i, point in enumerate(trajectory[::2]):  # Every 2nd point
                progress = 1.0 - (i / len(trajectory))
                
                # Create gradient from bright cyan to purple
                color = (
                    int(100 + 155 * progress),  # Cyan to magenta
                    int(255 * progress),        # Bright to dim
                    int(255)                    # Always full blue
                )
                
                # Size decreases along trajectory
                size = max(1, int(4 * progress))
                pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])), size)
    
    def draw_aiming_line(self):
        """Draw enhanced aiming line and power indicator"""
        if self.spaceship:
            # Draw line from spaceship to mouse with gradient
            pygame.draw.line(self.screen, (255, 255, 100),
                           self.spaceship.position.to_tuple(),
                           self.aim_start.to_tuple(), 4)
            
            # Draw power indicator with cool effects
            power_length = self.aim_power * 60
            if power_length > 5:
                end_pos = self.spaceship.position + (self.aim_start - self.spaceship.position).normalize() * power_length
                
                # Power bar with color based on strength
                if self.aim_power < 1.0:
                    power_color = (0, 255, 100)  # Green for low power
                elif self.aim_power < 2.0:
                    power_color = (255, 200, 0)  # Yellow for medium power
                else:
                    power_color = (255, 50, 50)  # Red for high power
                
                pygame.draw.line(self.screen, power_color,
                               self.spaceship.position.to_tuple(),
                               end_pos.to_tuple(), 6)
                
                # Draw power level indicator
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 (int(end_pos.x), int(end_pos.y)), 4)
    
    def draw_ui(self):
        """Draw enhanced user interface with cool colors"""
        # Level info with enhanced styling
        if self.current_level:
            progress = self.level_manager.get_level_progress()
            level_text = f"Level {progress['current']}/{progress['total']}: {progress['name']}"
            text_surface = self.font.render(level_text, True, (100, 255, 255))  # Bright cyan
            self.screen.blit(text_surface, (10, 10))
            
            # Shots info with color coding
            shots_text = f"Shots: {self.current_level.shots_used}/{self.current_level.max_shots}"
            if self.current_level.shots_used >= self.current_level.max_shots:
                shots_color = (255, 100, 100)  # Red when out of shots
            elif self.current_level.shots_used >= self.current_level.max_shots - 1:
                shots_color = (255, 255, 100)  # Yellow when almost out
            else:
                shots_color = (100, 255, 100)  # Green when plenty left
            
            shots_surface = self.small_font.render(shots_text, True, shots_color)
            self.screen.blit(shots_surface, (10, 50))
            
            # Fuel info with gradient based on fuel level
            if self.spaceship:
                fuel_ratio = self.spaceship.fuel / self.spaceship.max_fuel
                fuel_color = (
                    int(255 * (1 - fuel_ratio)),  # More red as fuel decreases
                    int(255 * fuel_ratio),        # More green as fuel increases
                    100
                )
                fuel_text = f"Fuel: {self.spaceship.fuel}/{self.spaceship.max_fuel}"
                fuel_surface = self.small_font.render(fuel_text, True, fuel_color)
                self.screen.blit(fuel_surface, (10, 75))
        
        # Game state messages with enhanced styling
        if self.state == GameState.LEVEL_COMPLETE:
            msg = "*** LEVEL COMPLETE! ***"
            msg_surface = self.font.render(msg, True, (100, 255, 150))
            rect = msg_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20))
            self.screen.blit(msg_surface, rect)
            
            next_msg = "Press N for next level, R to restart"
            next_surface = self.small_font.render(next_msg, True, (200, 200, 255))
            next_rect = next_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 10))
            self.screen.blit(next_surface, next_rect)
        
        elif self.state == GameState.GAME_OVER:
            msg = ">>> MISSION FAILED <<<"
            msg_surface = self.font.render(msg, True, (255, 100, 100))
            rect = msg_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20))
            self.screen.blit(msg_surface, rect)
            
            retry_msg = "Press R to restart level"
            retry_surface = self.small_font.render(retry_msg, True, (255, 200, 200))
            retry_rect = retry_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 10))
            self.screen.blit(retry_surface, retry_rect)
        
        elif self.state == GameState.AIMING:
            msg = ">> Click and drag to aim, then release to launch! <<"
            msg_surface = self.small_font.render(msg, True, (255, 255, 150))
            self.screen.blit(msg_surface, (10, self.screen_height - 30))
        
        # Controls help with better formatting
        help_text = "Controls: R=Restart | N=Next | P=Previous | SPACE=Thruster | ESC=Quit"
        help_surface = self.small_font.render(help_text, True, (180, 180, 255))
        self.screen.blit(help_surface, (10, self.screen_height - 60))
    
    def draw_gravity_info(self):
        """Draw information about gravity types with enhanced styling"""
        if not self.current_level:
            return
        
        # Find planets in the level
        planets = [obj for obj in self.current_level.objects if hasattr(obj, 'color_type')]
        
        if planets:
            info_y = 100
            info_text = "*** Gravity Types ***"
            info_surface = self.small_font.render(info_text, True, (255, 255, 150))
            self.screen.blit(info_surface, (10, info_y))
            info_y += 25
            
            # Show unique gravity types in this level
            shown_types = set()
            for planet in planets:
                if planet.color_type not in shown_types:
                    gravity_strength = planet.mass / planet.base_mass
                    color = planet.color
                    
                    # Add symbol based on gravity type
                    if "Heavy" in planet.color_type:
                        symbol = "[R]"  # Red
                    elif "Super Heavy" in planet.color_type:
                        symbol = "[P]"  # Purple
                    elif "Light" in planet.color_type:
                        symbol = "[G]"  # Green
                    elif "Variable" in planet.color_type:
                        symbol = "[Y]"  # Yellow
                    elif "Normal" in planet.color_type:
                        symbol = "[B]"  # Blue
                    else:
                        symbol = "[*]"  # Default
                    
                    type_text = f"  {symbol} {planet.color_type}: {gravity_strength:.1f}x"
                    # Enhance color brightness for better visibility
                    enhanced_color = (min(255, color[0] + 50), 
                                    min(255, color[1] + 50), 
                                    min(255, color[2] + 50))
                    type_surface = self.small_font.render(type_text, True, enhanced_color)
                    self.screen.blit(type_surface, (10, info_y))
                    info_y += 20
                    shown_types.add(planet.color_type)

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
