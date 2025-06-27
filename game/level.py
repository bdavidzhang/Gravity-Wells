"""
Level management and loading system
"""

import json
import os
from game.objects import *
from game.physics import Vector2D

class Level:
    """Represents a single game level"""
    
    def __init__(self, level_data=None):
        self.spaceship_start = Vector2D(100, 300)
        self.objects = []
        self.gravity_sources = []
        self.goal = None
        self.name = "Untitled Level"
        self.description = "Complete the level by reaching the goal!"
        self.max_shots = 3
        self.shots_used = 0
        
        if level_data:
            self.load_from_data(level_data)
    
    def load_from_data(self, data):
        """Load level from dictionary data"""
        self.name = data.get("name", "Untitled Level")
        self.description = data.get("description", "")
        self.max_shots = data.get("max_shots", 3)
        
        # Load spaceship starting position
        start_pos = data.get("spaceship_start", {"x": 100, "y": 300})
        self.spaceship_start = Vector2D(start_pos["x"], start_pos["y"])
        
        # Load objects
        self.objects = []
        self.gravity_sources = []
        
        for obj_data in data.get("objects", []):
            obj = self.create_object_from_data(obj_data)
            if obj:
                self.objects.append(obj)
                
                # Add to gravity sources if it has gravitational effect
                if hasattr(obj, 'mass') and obj.mass > 0:
                    self.gravity_sources.append(obj)
                
                # Set goal reference
                if isinstance(obj, Goal):
                    self.goal = obj
    
    def create_object_from_data(self, obj_data):
        """Create game object from data dictionary"""
        obj_type = obj_data.get("type")
        x = obj_data.get("x", 0)
        y = obj_data.get("y", 0)
        
        if obj_type == "planet":
            mass = obj_data.get("mass", 100)
            radius = obj_data.get("radius", 30)
            color = obj_data.get("color", [100, 100, 200])
            return Planet(x, y, mass, radius, tuple(color))
        
        elif obj_type == "black_hole":
            mass = obj_data.get("mass", 200)
            return BlackHole(x, y, mass)
        
        elif obj_type == "anti_gravity":
            mass = obj_data.get("mass", 50)
            return AntiGravityWell(x, y, mass)
        
        elif obj_type == "goal":
            return Goal(x, y)
        
        elif obj_type == "obstacle":
            radius = obj_data.get("radius", 15)
            return Obstacle(x, y, radius)
        
        return None
    
    def reset(self):
        """Reset level state"""
        self.shots_used = 0
        
        # Reset all objects to initial state
        for obj in self.objects:
            if hasattr(obj, 'active'):
                obj.active = True

class LevelManager:
    """Manages level loading and progression"""
    
    def __init__(self):
        self.levels = []
        self.current_level_index = 0
        self.levels_dir = "levels"
        self.load_all_levels()
    
    def load_all_levels(self):
        """Load all available levels"""
        # Create default levels if no level files exist
        if not os.path.exists(self.levels_dir):
            os.makedirs(self.levels_dir)
            self.create_default_levels()
        
        # Load levels from files
        self.levels = []
        for filename in sorted(os.listdir(self.levels_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(self.levels_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        level_data = json.load(f)
                        level = Level(level_data)
                        self.levels.append(level)
                except Exception as e:
                    print(f"Error loading level {filename}: {e}")
        
        # Ensure we have at least one level
        if not self.levels:
            self.levels.append(self.create_tutorial_level())
    
    def create_default_levels(self):
        """Create default level files with enhanced variety and all object types"""
        levels_data = [
            {
                "name": "Tutorial: Color-Based Gravity",
                "description": "Blue=Normal, Red=Heavy, Green=Light gravity. Use the blue planet!",
                "max_shots": 3,
                "spaceship_start": {"x": 100, "y": 300},
                "objects": [
                    {
                        "type": "planet",
                        "x": 400,
                        "y": 300,
                        "mass": 80,
                        "radius": 25,
                        "color": [50, 50, 255]  # Blue - Normal gravity
                    },
                    {
                        "type": "goal",
                        "x": 700,
                        "y": 300
                    }
                ]
            },
            {
                "name": "Heavy Red Planet Challenge",
                "description": "Red planets have 2x gravity! Use the heavy pull to slingshot around.",
                "max_shots": 2,
                "spaceship_start": {"x": 100, "y": 400},
                "objects": [
                    {
                        "type": "planet",
                        "x": 400,
                        "y": 300,
                        "mass": 100,
                        "radius": 35,
                        "color": [255, 30, 30]  # Red - Heavy gravity (2x)
                    },
                    {
                        "type": "goal",
                        "x": 400,
                        "y": 150
                    }
                ]
            },
            {
                "name": "Anti-Gravity Introduction",
                "description": "Pink anti-gravity wells push you away! Use them to avoid obstacles.",
                "max_shots": 3,
                "spaceship_start": {"x": 100, "y": 300},
                "objects": [
                    {
                        "type": "obstacle",
                        "x": 350,
                        "y": 300,
                        "radius": 20
                    },
                    {
                        "type": "anti_gravity",
                        "x": 400,
                        "y": 250,
                        "mass": 60
                    },
                    {
                        "type": "planet",
                        "x": 600,
                        "y": 350,
                        "mass": 80,
                        "radius": 25,
                        "color": [50, 255, 50]  # Green - Light gravity
                    },
                    {
                        "type": "goal",
                        "x": 750,
                        "y": 300
                    }
                ]
            },
            {
                "name": "Black Hole Gauntlet",
                "description": "Navigate past the deadly black hole! One wrong move and you're space dust.",
                "max_shots": 2,
                "spaceship_start": {"x": 100, "y": 500},
                "objects": [
                    {
                        "type": "black_hole",
                        "x": 400,
                        "y": 300,
                        "mass": 400
                    },
                    {
                        "type": "planet",
                        "x": 250,
                        "y": 200,
                        "mass": 60,
                        "radius": 20,
                        "color": [50, 255, 50]  # Green - Light gravity helper
                    },
                    {
                        "type": "goal",
                        "x": 650,
                        "y": 150
                    }
                ]
            },
            {
                "name": "Multi-Color Gravity Maze",
                "description": "Purple=Super Heavy, Yellow=Variable, Green=Light. Navigate the maze!",
                "max_shots": 4,
                "spaceship_start": {"x": 50, "y": 300},
                "objects": [
                    {
                        "type": "planet",
                        "x": 200,
                        "y": 150,
                        "mass": 80,
                        "radius": 28,
                        "color": [200, 50, 200]  # Purple - Super heavy (2.5x)
                    },
                    {
                        "type": "planet",
                        "x": 450,
                        "y": 400,
                        "mass": 90,
                        "radius": 30,
                        "color": [255, 255, 50]  # Yellow - Variable (1.5x)
                    },
                    {
                        "type": "planet",
                        "x": 650,
                        "y": 200,
                        "mass": 100,
                        "radius": 25,
                        "color": [50, 255, 50]  # Green - Light (0.7x)
                    },
                    {
                        "type": "obstacle",
                        "x": 400,
                        "y": 250,
                        "radius": 15
                    },
                    {
                        "type": "goal",
                        "x": 800,
                        "y": 300
                    }
                ]
            },
            {
                "name": "The Obstacle Course",
                "description": "Dodge red obstacles while using gravity wells to reach the goal!",
                "max_shots": 3,
                "spaceship_start": {"x": 80, "y": 400},
                "objects": [
                    {
                        "type": "obstacle",
                        "x": 200,
                        "y": 350,
                        "radius": 18
                    },
                    {
                        "type": "obstacle",
                        "x": 350,
                        "y": 250,
                        "radius": 15
                    },
                    {
                        "type": "obstacle",
                        "x": 500,
                        "y": 400,
                        "radius": 20
                    },
                    {
                        "type": "planet",
                        "x": 300,
                        "y": 500,
                        "mass": 100,
                        "radius": 30,
                        "color": [50, 50, 255]  # Blue - Normal gravity
                    },
                    {
                        "type": "anti_gravity",
                        "x": 450,
                        "y": 150,
                        "mass": 70
                    },
                    {
                        "type": "goal",
                        "x": 700,
                        "y": 200
                    }
                ]
            },
            {
                "name": "Push and Pull Chaos",
                "description": "Master anti-gravity wells and heavy planets in this chaotic level!",
                "max_shots": 4,
                "spaceship_start": {"x": 100, "y": 100},
                "objects": [
                    {
                        "type": "anti_gravity",
                        "x": 250,
                        "y": 200,
                        "mass": 80
                    },
                    {
                        "type": "planet",
                        "x": 400,
                        "y": 300,
                        "mass": 120,
                        "radius": 35,
                        "color": [255, 30, 30]  # Red - Heavy gravity
                    },
                    {
                        "type": "anti_gravity",
                        "x": 550,
                        "y": 150,
                        "mass": 60
                    },
                    {
                        "type": "planet",
                        "x": 300,
                        "y": 450,
                        "mass": 90,
                        "radius": 25,
                        "color": [255, 255, 50]  # Yellow - Variable gravity
                    },
                    {
                        "type": "obstacle",
                        "x": 450,
                        "y": 200,
                        "radius": 12
                    },
                    {
                        "type": "goal",
                        "x": 750,
                        "y": 400
                    }
                ]
            },
            {
                "name": "Black Hole Binary System",
                "description": "Two black holes create extreme gravitational chaos! Expert level only.",
                "max_shots": 3,
                "spaceship_start": {"x": 50, "y": 400},
                "objects": [
                    {
                        "type": "black_hole",
                        "x": 300,
                        "y": 200,
                        "mass": 350
                    },
                    {
                        "type": "black_hole",
                        "x": 500,
                        "y": 400,
                        "mass": 350
                    },
                    {
                        "type": "planet",
                        "x": 150,
                        "y": 250,
                        "mass": 60,
                        "radius": 20,
                        "color": [50, 255, 50]  # Green - Light gravity escape helper
                    },
                    {
                        "type": "anti_gravity",
                        "x": 650,
                        "y": 300,
                        "mass": 100
                    },
                    {
                        "type": "goal",
                        "x": 800,
                        "y": 100
                    }
                ]
            },
            {
                "name": "The Final Challenge",
                "description": "Everything you've learned! All object types in one epic level.",
                "max_shots": 5,
                "spaceship_start": {"x": 80, "y": 500},
                "objects": [
                    {
                        "type": "planet",
                        "x": 200,
                        "y": 400,
                        "mass": 100,
                        "radius": 30,
                        "color": [200, 50, 200]  # Purple - Super heavy
                    },
                    {
                        "type": "obstacle",
                        "x": 300,
                        "y": 300,
                        "radius": 18
                    },
                    {
                        "type": "anti_gravity",
                        "x": 400,
                        "y": 200,
                        "mass": 80
                    },
                    {
                        "type": "black_hole",
                        "x": 500,
                        "y": 350,
                        "mass": 400
                    },
                    {
                        "type": "planet",
                        "x": 350,
                        "y": 500,
                        "mass": 70,
                        "radius": 22,
                        "color": [50, 255, 50]  # Green - Light gravity
                    },
                    {
                        "type": "obstacle",
                        "x": 600,
                        "y": 250,
                        "radius": 15
                    },
                    {
                        "type": "planet",
                        "x": 700,
                        "y": 400,
                        "mass": 90,
                        "radius": 28,
                        "color": [255, 30, 30]  # Red - Heavy gravity
                    },
                    {
                        "type": "anti_gravity",
                        "x": 750,
                        "y": 150,
                        "mass": 60
                    },
                    {
                        "type": "goal",
                        "x": 850,
                        "y": 300
                    }
                ]
            }
        ]
        
        for i, level_data in enumerate(levels_data):
            filename = f"level_{i+1:02d}.json"
            filepath = os.path.join(self.levels_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(level_data, f, indent=2)
    
    def create_tutorial_level(self):
        """Create a simple tutorial level"""
        return Level({
            "name": "Tutorial",
            "description": "Reach the green goal!",
            "max_shots": 5,
            "spaceship_start": {"x": 100, "y": 300},
            "objects": [
                {
                    "type": "planet",
                    "x": 400,
                    "y": 300,
                    "mass": 80,
                    "radius": 25
                },
                {
                    "type": "goal",
                    "x": 700,
                    "y": 300
                }
            ]
        })
    
    def get_current_level(self):
        """Get the current level"""
        if 0 <= self.current_level_index < len(self.levels):
            return self.levels[self.current_level_index]
        return None
    
    def next_level(self):
        """Advance to next level"""
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            return True
        return False
    
    def previous_level(self):
        """Go to previous level"""
        if self.current_level_index > 0:
            self.current_level_index -= 1
            return True
        return False
    
    def restart_level(self):
        """Restart current level"""
        current_level = self.get_current_level()
        if current_level:
            current_level.reset()
    
    def get_level_progress(self):
        """Get current level progress info"""
        return {
            "current": self.current_level_index + 1,
            "total": len(self.levels),
            "name": self.get_current_level().name if self.get_current_level() else "Unknown"
        }
