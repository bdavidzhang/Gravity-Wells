"""
Game objects: spaceship, planets, goals, obstacles, wormholes
Gravity Wells v2.0
"""

import pygame
import math
import random
import time
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


class Wormhole(GameObject):
    """Teleportation portal - links two wormholes together"""

    def __init__(self, x, y, partner_x=0, partner_y=0):
        super().__init__(x, y, mass=0)
        self.radius = 22
        self.color = (0, 200, 255)
        self.partner_pos = Vector2D(partner_x, partner_y)
        self.partner = None  # Will be linked after creation
        self.cooldown = 0  # Prevent instant re-teleport
        self.spin_angle = 0
        self.warp_particles = []

    def link_partner(self, partner):
        """Link this wormhole to its partner"""
        self.partner = partner

    def teleport(self, spaceship):
        """Teleport the spaceship to the partner wormhole"""
        if self.partner and self.cooldown <= 0:
            spaceship.position = Vector2D(
                self.partner.position.x,
                self.partner.position.y
            )
            # Keep velocity but slightly randomize direction
            speed = spaceship.velocity.magnitude()
            angle = math.atan2(spaceship.velocity.y, spaceship.velocity.x)
            angle += random.uniform(-0.3, 0.3)
            spaceship.velocity = Vector2D(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            self.cooldown = 0.5
            self.partner.cooldown = 0.5
            return True
        return False

    def update(self, dt):
        """Update wormhole animation"""
        self.spin_angle += dt * 200
        if self.cooldown > 0:
            self.cooldown -= dt

        # Update warp particles
        if random.random() < 0.4:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(15, 35)
            self.warp_particles.append({
                'angle': angle,
                'dist': dist,
                'life': 1.0,
                'speed': random.uniform(1, 3)
            })

        for p in self.warp_particles[:]:
            p['angle'] += p['speed'] * dt * 3
            p['dist'] -= dt * 20
            p['life'] -= dt * 1.5
            if p['life'] <= 0 or p['dist'] <= 0:
                self.warp_particles.remove(p)

    def draw(self, screen):
        """Draw wormhole with swirling portal effect"""
        cx, cy = int(self.position.x), int(self.position.y)

        # Draw swirling particles being sucked in
        for p in self.warp_particles:
            px = cx + int(math.cos(p['angle']) * p['dist'])
            py = cy + int(math.sin(p['angle']) * p['dist'])
            intensity = p['life']
            color = (0, int(180 * intensity), int(255 * intensity))
            pygame.draw.circle(screen, color, (px, py), 2)

        # Draw outer swirl rings
        for i in range(6):
            angle = math.radians(self.spin_angle + i * 60)
            ring_r = self.radius + 8 + math.sin(time.time() * 3 + i) * 4
            rx = cx + int(math.cos(angle) * ring_r * 0.3)
            ry = cy + int(math.sin(angle) * ring_r * 0.3)
            ring_color = (0, int(150 + 50 * math.sin(time.time() * 2 + i)), 255)
            pygame.draw.circle(screen, ring_color, (rx, ry), 3)

        # Draw portal ring
        pulse = abs(math.sin(time.time() * 3)) * 0.2 + 0.8
        pygame.draw.circle(screen, (0, 180, 255), (cx, cy), int(self.radius * pulse), 3)

        # Draw inner gradient
        for r in range(self.radius - 2, 0, -3):
            ratio = r / self.radius
            color = (int(20 * ratio), int(50 + 100 * (1 - ratio)), int(200 + 55 * (1 - ratio)))
            pygame.draw.circle(screen, color, (cx, cy), r)

        # Bright center
        pygame.draw.circle(screen, (150, 255, 255), (cx, cy), 4)

        # Draw connection line to partner (faint)
        if self.partner:
            mid_x = (self.position.x + self.partner.position.x) / 2
            mid_y = (self.position.y + self.partner.position.y) / 2
            # Dashed line effect
            steps = 12
            for s in range(steps):
                if s % 2 == 0:
                    t1 = s / steps
                    t2 = (s + 1) / steps
                    x1 = int(self.position.x + (self.partner.position.x - self.position.x) * t1)
                    y1 = int(self.position.y + (self.partner.position.y - self.position.y) * t1)
                    x2 = int(self.position.x + (self.partner.position.x - self.position.x) * t2)
                    y2 = int(self.position.y + (self.partner.position.y - self.position.y) * t2)
                    pygame.draw.line(screen, (0, 80, 120), (x1, y1), (x2, y2), 1)


class ExplosionEffect:
    """Particle explosion effect when spaceship is destroyed"""

    def __init__(self, x, y, color=(0, 255, 255)):
        self.particles = []
        self.active = True
        self.lifetime = 1.5
        self.timer = 0

        # Create burst of particles
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 250)
            size = random.uniform(2, 6)
            life = random.uniform(0.5, 1.5)

            # Mix colors
            r = min(255, color[0] + random.randint(-30, 80))
            g = min(255, color[1] + random.randint(-30, 80))
            b = min(255, color[2] + random.randint(-30, 80))

            self.particles.append({
                'x': float(x),
                'y': float(y),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'max_life': life,
                'color': (r, g, b)
            })

    def update(self, dt):
        """Update all explosion particles"""
        self.timer += dt
        if self.timer >= self.lifetime:
            self.active = False
            return

        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vx'] *= 0.96  # Drag
            p['vy'] *= 0.96
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)

        if not self.particles:
            self.active = False

    def draw(self, screen):
        """Draw explosion particles"""
        for p in self.particles:
            ratio = max(0, p['life'] / p['max_life'])
            r = int(p['color'][0] * ratio)
            g = int(p['color'][1] * ratio)
            b = int(p['color'][2] * ratio)
            size = max(1, int(p['size'] * ratio))
            pygame.draw.circle(screen, (r, g, b), (int(p['x']), int(p['y'])), size)


class Starfield:
    """Animated starfield background with twinkling and parallax layers"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []

        # Create 3 parallax layers (far, mid, near)
        layer_configs = [
            {'count': 80, 'min_size': 1, 'max_size': 1, 'speed': 0.1, 'brightness': 120},
            {'count': 40, 'min_size': 1, 'max_size': 2, 'speed': 0.3, 'brightness': 180},
            {'count': 20, 'min_size': 2, 'max_size': 3, 'speed': 0.6, 'brightness': 255},
        ]

        for config in layer_configs:
            stars = []
            for _ in range(config['count']):
                stars.append({
                    'x': random.randint(0, width),
                    'y': random.randint(0, height),
                    'size': random.randint(config['min_size'], config['max_size']),
                    'brightness': config['brightness'],
                    'twinkle_speed': random.uniform(1, 5),
                    'twinkle_offset': random.uniform(0, math.pi * 2),
                })
            self.layers.append({'stars': stars, 'speed': config['speed']})

        # Occasional shooting star
        self.shooting_stars = []

    def update(self, dt):
        """Update starfield animation"""
        # Random shooting stars
        if random.random() < 0.003:
            self.shooting_stars.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, int(self.height * 0.6)),
                'vx': random.uniform(300, 600),
                'vy': random.uniform(100, 200),
                'life': 1.0,
                'trail': []
            })

        for star in self.shooting_stars[:]:
            star['trail'].append((star['x'], star['y']))
            if len(star['trail']) > 8:
                star['trail'].pop(0)
            star['x'] += star['vx'] * dt
            star['y'] += star['vy'] * dt
            star['life'] -= dt * 2
            if star['life'] <= 0 or star['x'] > self.width or star['y'] > self.height:
                self.shooting_stars.remove(star)

    def draw(self, screen):
        """Draw the starfield"""
        t = time.time()

        for layer in self.layers:
            for star in layer['stars']:
                # Twinkle effect
                twinkle = abs(math.sin(t * star['twinkle_speed'] + star['twinkle_offset']))
                brightness = int(star['brightness'] * (0.4 + 0.6 * twinkle))

                # Slight blue/white color variation
                r = min(255, brightness + random.randint(-5, 5))
                g = min(255, brightness + random.randint(-5, 5))
                b = min(255, brightness + random.randint(0, 20))

                pygame.draw.circle(screen, (r, g, b),
                                 (int(star['x']), int(star['y'])),
                                 star['size'])

        # Draw shooting stars
        for ss in self.shooting_stars:
            intensity = ss['life']
            if len(ss['trail']) > 1:
                for i in range(1, len(ss['trail'])):
                    alpha = (i / len(ss['trail'])) * intensity
                    color = (int(255 * alpha), int(255 * alpha), int(200 * alpha))
                    pygame.draw.line(screen, color,
                                   (int(ss['trail'][i-1][0]), int(ss['trail'][i-1][1])),
                                   (int(ss['trail'][i][0]), int(ss['trail'][i][1])), 2)
            # Bright head
            pygame.draw.circle(screen, (int(255 * intensity), int(255 * intensity), int(220 * intensity)),
                             (int(ss['x']), int(ss['y'])), 2)
