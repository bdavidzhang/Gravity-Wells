"""
Game objects: spaceship, planets, goals, obstacles
"""

import pygame
import math
from game.physics import Vector2D

class GameObject:
    """Base class for all game objects"""
    
    def __init__(self, x, y, mass=1.0):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.mass = mass
        self.radius = 10
        self.color = (255, 255, 255)
        self.active = True
    
    def draw(self, screen):
        """Draw the object on screen"""
        if self.active:
            pygame.draw.circle(screen, self.color, 
                             (int(self.position.x), int(self.position.y)), 
                             self.radius)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.position.x - self.radius, 
                          self.position.y - self.radius,
                          self.radius * 2, self.radius * 2)
    
    def collides_with(self, other):
        """Check collision with another object"""
        distance = (self.position - other.position).magnitude()
        return distance < (self.radius + other.radius)

class Spaceship(GameObject):
    """Player-controlled spaceship"""
    
    def __init__(self, x, y):
        super().__init__(x, y, mass=1.0)
        self.radius = 8
        self.color = (0, 255, 255)  # Bright cyan
        self.fuel = 100
        self.max_fuel = 100
        self.launched = False
        self.trail = []  # For visual trail
        self.max_trail_length = 50
        self.glow_color = (100, 255, 255)  # Cyan glow
    
    def launch(self, velocity):
        """Launch the spaceship with given velocity"""
        self.velocity = velocity
        self.launched = True
        self.trail = []
    
    def use_thruster(self, direction, power=50):
        """Use thruster for course correction"""
        if self.fuel > 0 and self.launched:
            thrust = direction.normalize() * power
            self.velocity = self.velocity + thrust
            self.fuel -= 5
    
    def update(self, dt):
        """Update spaceship state"""
        if self.launched:
            # Add current position to trail
            self.trail.append((self.position.x, self.position.y))
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
    
    def draw(self, screen):
        """Draw spaceship with enhanced glow effect and trail"""
        # Draw trail with gradient effect
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = i / len(self.trail)
                # Gradient from bright cyan to purple
                color = (int(100 * alpha), int(255 * alpha), int(255 * alpha))
                start_pos = self.trail[i-1]
                end_pos = self.trail[i]
                # Draw thicker trail segments at the beginning
                thickness = max(1, int(3 * alpha))
                pygame.draw.line(screen, color, start_pos, end_pos, thickness)
        
        # Draw spaceship glow effect
        glow_radius = self.radius + 6
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.glow_color, 30), 
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, 
                   (self.position.x - glow_radius, self.position.y - glow_radius),
                   special_flags=pygame.BLEND_ADD)
        
        # Draw spaceship core
        super().draw(screen)
        
        # Draw inner bright core
        pygame.draw.circle(screen, (255, 255, 255),
                          (int(self.position.x), int(self.position.y)), 3)
        
        # Draw direction indicator if not launched
        if not self.launched:
            # Draw bright arrow pointing in velocity direction
            if self.velocity.magnitude() > 0:
                end_x = self.position.x + self.velocity.x * 0.1
                end_y = self.position.y + self.velocity.y * 0.1
                pygame.draw.line(screen, (255, 255, 0), 
                               (self.position.x, self.position.y),
                               (end_x, end_y), 4)
                # Arrow tip
                pygame.draw.circle(screen, (255, 255, 100),
                                 (int(end_x), int(end_y)), 3)

class Planet(GameObject):
    """Gravitational body with color-based gravity strength"""
    
    def __init__(self, x, y, mass=100, radius=30, color=(100, 100, 200)):
        # Calculate effective mass based on color
        effective_mass = self.calculate_color_based_mass(mass, color)
        super().__init__(x, y, effective_mass)
        self.base_mass = mass  # Store original mass
        self.radius = radius
        self.color = color
        self.gravity_field_radius = self.mass * 1.5  # Visual representation based on effective mass
        self.color_type = self.determine_color_type(color)
    
    def calculate_color_based_mass(self, base_mass, color):
        """Calculate effective gravitational mass based on color"""
        r, g, b = color
        
        # Color-based gravity multipliers
        if r > 150 and g < 100 and b < 100:  # Red planets - Heavy gravity
            return base_mass * 2.0
        elif b > 150 and r < 100 and g < 100:  # Blue planets - Normal gravity
            return base_mass * 1.0
        elif g > 150 and r < 100 and b < 100:  # Green planets - Light gravity
            return base_mass * 0.7
        elif r > 150 and g > 150 and b < 100:  # Yellow planets - Variable gravity
            return base_mass * 1.5
        elif r > 100 and g < 100 and b > 100:  # Purple planets - Super heavy
            return base_mass * 2.5
        elif r > 150 and g > 150 and b > 150:  # White planets - Moderate gravity
            return base_mass * 1.2
        else:  # Default colors get normal gravity
            return base_mass * 1.0
    
    def determine_color_type(self, color):
        """Determine the dominant color type for display purposes"""
        r, g, b = color
        if r > 150 and g < 100 and b < 100:
            return "Heavy (Red)"
        elif b > 150 and r < 100 and g < 100:
            return "Normal (Blue)"
        elif g > 150 and r < 100 and b < 100:
            return "Light (Green)"
        elif r > 150 and g > 150 and b < 100:
            return "Variable (Yellow)"
        elif r > 100 and g < 100 and b > 100:
            return "Super Heavy (Purple)"
        elif r > 150 and g > 150 and b > 150:
            return "Moderate (White)"
        else:
            return "Standard"
    
    def draw(self, screen):
        """Draw planet with enhanced gamey visual effects"""
        # Draw animated gravity field with pulsing rings
        field_color = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        
        # Get gravity strength for visual effects
        gravity_strength = self.mass / self.base_mass
        num_rings = min(int(gravity_strength * 3), 6)  # More rings for stronger gravity
        
        # Animated pulsing effect
        import time
        pulse = abs(math.sin(time.time() * 2)) * 0.3 + 0.7
        
        for i in range(num_rings):
            ring_radius = int(self.gravity_field_radius * (0.4 + i * 0.15) * pulse)
            alpha_factor = (num_rings - i) / num_rings
            ring_color = (int(field_color[0] * alpha_factor * 1.5), 
                         int(field_color[1] * alpha_factor * 1.5), 
                         int(field_color[2] * alpha_factor * 1.5))
            pygame.draw.circle(screen, ring_color,
                              (int(self.position.x), int(self.position.y)),
                              ring_radius, 2)
        
        # Draw planet with gradient effect
        super().draw(screen)
        
        # Enhanced visual effects based on gravity strength
        if gravity_strength > 1.5:
            # High-gravity planets get pulsing cores and particle effects
            pulse_intensity = math.sin(time.time() * 4) * 0.2 + 0.8
            pulse_radius = max(3, int(self.radius * 0.7 * pulse_intensity))
            pulse_color = (min(255, int(self.color[0] * 1.4)), 
                          min(255, int(self.color[1] * 1.4)), 
                          min(255, int(self.color[2] * 1.4)))
            pygame.draw.circle(screen, pulse_color,
                              (int(self.position.x), int(self.position.y)),
                              pulse_radius)
            
            # Add bright core for high-gravity planets
            pygame.draw.circle(screen, (255, 255, 255),
                              (int(self.position.x), int(self.position.y)), 4)
        else:
            # Normal planets get subtle inner glow
            inner_radius = max(3, self.radius - 8)
            inner_color = (min(255, self.color[0] + 80), 
                          min(255, self.color[1] + 80), 
                          min(255, self.color[2] + 80))
            pygame.draw.circle(screen, inner_color,
                              (int(self.position.x), int(self.position.y)),
                              inner_radius)
            
            # Bright center dot
            pygame.draw.circle(screen, (255, 255, 255),
                              (int(self.position.x), int(self.position.y)), 2)

class BlackHole(GameObject):
    """Deadly gravitational body with extreme gravity and cool effects"""
    
    def __init__(self, x, y, mass=500):  # Increased mass for stronger gravity
        super().__init__(x, y, mass)
        self.radius = 15
        self.color = (20, 0, 40)  # Deep purple
        self.event_horizon = 30
        self.accretion_disk_radius = 45
    
    def draw(self, screen):
        """Draw black hole with dramatic visual effects"""
        import time
        
        # Draw accretion disk with spinning effect
        spin_offset = time.time() * 5
        for i in range(8):
            angle = (i * 45 + spin_offset) * math.pi / 180
            disk_radius = self.accretion_disk_radius + math.sin(spin_offset + i) * 5
            x_offset = math.cos(angle) * disk_radius * 0.7
            y_offset = math.sin(angle) * disk_radius * 0.3  # Flatten to look like disk
            
            # Gradient colors from orange to red
            intensity = (math.sin(spin_offset + i) + 1) / 2
            color = (int(255 * intensity), int(100 * intensity), int(20 * intensity))
            
            pygame.draw.circle(screen, color,
                              (int(self.position.x + x_offset), int(self.position.y + y_offset)), 3)
        
        # Draw event horizon with pulsing danger effect
        pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
        horizon_color = (int(150 * pulse), 0, int(200 * pulse))
        pygame.draw.circle(screen, horizon_color,
                          (int(self.position.x), int(self.position.y)),
                          int(self.event_horizon * pulse), 3)
        
        # Draw the black hole itself
        pygame.draw.circle(screen, self.color,
                          (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw ultra-dark center
        pygame.draw.circle(screen, (0, 0, 0),
                          (int(self.position.x), int(self.position.y)), self.radius - 5)

class AntiGravityWell(GameObject):
    """Repulsive gravitational body with cool energy effects"""
    
    def __init__(self, x, y, mass=50):
        super().__init__(x, y, mass)
        self.radius = 20
        self.color = (255, 50, 100)  # Hot pink/magenta
        self.anti_gravity = True
        self.energy_field_radius = 60
    
    def draw(self, screen):
        """Draw anti-gravity well with energy field effects"""
        import time
        
        # Draw pulsing energy field
        pulse = abs(math.sin(time.time() * 4)) * 0.4 + 0.6
        
        # Draw multiple energy rings
        for i in range(4):
            ring_radius = int(self.energy_field_radius * (0.3 + i * 0.2) * pulse)
            ring_intensity = (4 - i) / 4
            ring_color = (int(255 * ring_intensity), 
                         int(100 * ring_intensity), 
                         int(150 * ring_intensity))
            pygame.draw.circle(screen, ring_color,
                              (int(self.position.x), int(self.position.y)),
                              ring_radius, 2)
        
        # Draw repulsion particles
        for i in range(12):
            angle = (i * 30 + time.time() * 50) * math.pi / 180
            distance = 30 + math.sin(time.time() * 3 + i) * 10
            x_offset = math.cos(angle) * distance
            y_offset = math.sin(angle) * distance
            
            particle_color = (255, 100, 200)
            pygame.draw.circle(screen, particle_color,
                              (int(self.position.x + x_offset), int(self.position.y + y_offset)), 2)
        
        # Draw anti-gravity well core
        super().draw(screen)
        
        # Draw bright pulsing center
        center_pulse = abs(math.sin(time.time() * 6)) * 0.5 + 0.5
        center_color = (255, int(255 * center_pulse), int(255 * center_pulse))
        pygame.draw.circle(screen, center_color,
                          (int(self.position.x), int(self.position.y)), 8)

class Goal(GameObject):
    """Level completion target with enhanced visual effects"""
    
    def __init__(self, x, y):
        super().__init__(x, y, mass=0)  # No gravitational effect
        self.radius = 25
        self.color = (0, 255, 100)  # Bright green
        self.pulse_timer = 0
        self.particles = []  # For particle effects
    
    def update(self, dt):
        """Animate the goal with particles"""
        self.pulse_timer += dt * 3
        pulse = math.sin(self.pulse_timer) * 0.3 + 1.0
        self.current_radius = int(self.radius * pulse)
        
        # Update particles
        import random
        if random.random() < 0.3:  # Add new particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 30)
            self.particles.append({
                'x': self.position.x,
                'y': self.position.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0
            })
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 2
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Draw animated goal with particle effects"""
        import time
        
        # Draw success particles
        for particle in self.particles:
            intensity = particle['life']
            color = (0, int(255 * intensity), int(100 * intensity))
            pygame.draw.circle(screen, color,
                              (int(particle['x']), int(particle['y'])), 3)
        
        # Draw multiple pulsing rings
        pulse_offset = time.time() * 4
        for i in range(3):
            ring_pulse = abs(math.sin(pulse_offset + i * 0.5)) * 0.4 + 0.6
            ring_radius = int(self.current_radius * (1 + i * 0.3) * ring_pulse)
            ring_intensity = (3 - i) / 3
            ring_color = (0, int(255 * ring_intensity), int(150 * ring_intensity))
            pygame.draw.circle(screen, ring_color,
                              (int(self.position.x), int(self.position.y)),
                              ring_radius, 3)
        
        # Draw bright core
        pygame.draw.circle(screen, (100, 255, 200),
                          (int(self.position.x), int(self.position.y)),
                          self.radius // 2)
        
        # Draw ultra-bright center
        pygame.draw.circle(screen, (255, 255, 255),
                          (int(self.position.x), int(self.position.y)), 5)

class Obstacle(GameObject):
    """Static obstacle with danger visual effects"""
    
    def __init__(self, x, y, radius=15):
        super().__init__(x, y, mass=0)  # No gravitational effect
        self.radius = radius
        self.color = (255, 0, 50)  # Bright red
        self.warning_radius = radius + 8
    
    def draw(self, screen):
        """Draw obstacle with warning effects"""
        import time
        
        # Draw pulsing danger field
        pulse = abs(math.sin(time.time() * 5)) * 0.5 + 0.5
        warning_color = (int(255 * pulse), 0, int(100 * pulse))
        
        # Draw multiple warning rings
        for i in range(3):
            ring_radius = int(self.warning_radius * (1 + i * 0.2) * pulse)
            ring_intensity = (3 - i) / 3 * pulse
            color = (int(255 * ring_intensity), 0, int(50 * ring_intensity))
            pygame.draw.circle(screen, color,
                              (int(self.position.x), int(self.position.y)),
                              ring_radius, 2)
        
        # Draw obstacle core
        super().draw(screen)
        
        # Draw danger center
        pygame.draw.circle(screen, (255, 100, 100),
                          (int(self.position.x), int(self.position.y)),
                          self.radius - 3)
