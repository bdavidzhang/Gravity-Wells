"""
Physics engine for gravity simulation and movement calculations
"""

import numpy as np
import math

class Vector2D:
    """2D Vector class for position and velocity calculations"""
    
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def to_tuple(self):
        return (self.x, self.y)

class PhysicsEngine:
    """Handles all physics calculations including gravity and movement"""
    
    def __init__(self):
        self.gravity_constant = 5000  # Significantly increased for stronger gravity
        self.max_gravity_distance = 500  # Increased range for more dramatic effects
    
    def calculate_gravity_force(self, obj1_pos, obj1_mass, obj2_pos, obj2_mass):
        """Calculate gravitational force between two objects"""
        # Vector from obj1 to obj2
        direction = obj2_pos - obj1_pos
        distance = direction.magnitude()
        
        # Avoid division by zero and extremely close objects
        if distance < 5:
            return Vector2D(0, 0)
        
        # Don't calculate gravity for very distant objects
        if distance > self.max_gravity_distance:
            return Vector2D(0, 0)
        
        # F = G * m1 * m2 / r^2
        force_magnitude = (self.gravity_constant * obj1_mass * obj2_mass) / (distance ** 2)
        force_direction = direction.normalize()
        
        return force_direction * force_magnitude
    
    def calculate_total_gravity(self, position, mass, gravity_sources):
        """Calculate total gravitational force from all sources"""
        total_force = Vector2D(0, 0)
        
        for source in gravity_sources:
            force = self.calculate_gravity_force(
                position, mass, 
                source.position, source.mass
            )
            
            # Handle anti-gravity sources
            if hasattr(source, 'anti_gravity') and source.anti_gravity:
                force = force * -1
            
            total_force = total_force + force
        
        return total_force
    
    def update_object_physics(self, obj, gravity_sources, dt):
        """Update an object's position and velocity based on physics"""
        # Calculate gravitational acceleration
        gravity_force = self.calculate_total_gravity(obj.position, obj.mass, gravity_sources)
        acceleration = gravity_force / obj.mass
        
        # Update velocity (Euler integration)
        obj.velocity = obj.velocity + acceleration * dt
        
        # Update position
        obj.position = obj.position + obj.velocity * dt
    
    def predict_trajectory(self, start_pos, start_vel, mass, gravity_sources, steps=100, dt=0.1):
        """Predict trajectory for visualization"""
        trajectory = []
        pos = Vector2D(start_pos.x, start_pos.y)
        vel = Vector2D(start_vel.x, start_vel.y)
        
        for _ in range(steps):
            trajectory.append((pos.x, pos.y))
            
            # Calculate forces
            gravity_force = self.calculate_total_gravity(pos, mass, gravity_sources)
            acceleration = gravity_force / mass
            
            # Update
            vel = vel + acceleration * dt
            pos = pos + vel * dt
            
            # Stop prediction if object goes too far off screen
            if pos.x < -500 or pos.x > 1500 or pos.y < -500 or pos.y > 1200:
                break
        
        return trajectory
