# Gravity Wells - Spaceship Slingshotting Game

A physics-based puzzle game where you navigate a spaceship through gravitational fields to reach your destination!

## 🚀 Game Overview

In Gravity Wells, you control a spaceship that must reach the goal by using the gravitational pull of planets and other celestial bodies. Plan your trajectory carefully, as you have limited shots per level!

## 🎮 How to Play

### Controls
- **Mouse**: Click and drag from the spaceship to aim and set power (Angry Birds style)
- **Mouse (Aiming)**: Drag to dynamically adjust slingshot direction and power before launch
- **SPACE**: Use thruster for speed boost while flying (consumes fuel)
- **SHIFT**: Use brake to slow down while flying (consumes fuel)
- **R**: Restart current level
- **N**: Next level (when level is complete)
- **P**: Previous level
- **ESC**: Quit game

### Gameplay
1. **Aim**: Click near your spaceship and drag to pull back the slingshot (like Angry Birds)
2. **Adjust**: Move your mouse to dynamically adjust direction and power
3. **Launch**: Release the mouse button to launch your spaceship
4. **Control**: Use SPACE to boost forward or SHIFT to brake/slow down
5. **Navigate**: Use gravitational forces to slingshot around planets
6. **Reach Goal**: Hit the pulsing green goal to complete the level

### Game Elements

#### 🛸 Spaceship (Cyan)
- Your controllable vessel
- Has limited fuel for mid-flight corrections
- Leaves a trail showing its path

#### 🪐 Planets (Blue/Purple)
- Create gravitational fields that pull your spaceship
- Use them to change direction and gain speed
- Different sizes have different gravitational strength

#### 🕳️ Black Holes (Dark Purple)
- Extremely strong gravity
- Deadly to touch - avoid the event horizon!

#### 🔴 Anti-Gravity Wells (Red)
- Push objects away instead of pulling
- Useful for avoiding obstacles or changing trajectory

#### 🎯 Goal (Green, Pulsing)
- Your target destination
- Complete the level by reaching it

#### ⚠️ Obstacles (Red)
- Destroy your spaceship on contact
- Plan your route to avoid them

## 🎯 Strategy Tips

1. **Study the Level**: Look at all gravitational sources before launching
2. **Use Prediction**: The yellow trajectory line shows where you'll go
3. **Save Fuel**: Use gravity assists instead of thrusters when possible
4. **Chain Slingshots**: Use multiple planets for complex maneuvers
5. **Timing Matters**: Some objects move - wait for the right moment

## 🚀 Installation & Running

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup
1. Clone or download this repository
2. Navigate to the game directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python main.py
   ```
   
   Or use the convenience script:
   ```bash
   ./run_game.sh
   ```

## 🎨 Game Features

### Current Features
- ✅ Realistic gravity physics simulation
- ✅ Trajectory prediction system
- ✅ Multiple level progression
- ✅ Different celestial body types
- ✅ Fuel management system
- ✅ Visual effects and trails
- ✅ Level editor-friendly JSON format

### Level Progression
The game includes several built-in levels:

1. **Tutorial: Basic Gravity** - Learn the fundamentals
2. **Slingshot Challenge** - Navigate around a planet
3. **Double Trouble** - Complex multi-body gravity fields

## 🛠️ Technical Details

### Architecture
- **Main Game Loop**: `main.py` - Entry point
- **Game Engine**: `game/engine.py` - Core game logic and state management
- **Physics**: `game/physics.py` - Gravity calculations and trajectory prediction
- **Objects**: `game/objects.py` - All game entities (spaceship, planets, etc.)
- **Level System**: `game/level.py` - Level loading and management

### Adding New Levels
Levels are stored as JSON files in the `levels/` directory. Each level defines:
- Starting position for the spaceship
- Positions and properties of all objects
- Maximum number of shots allowed
- Level name and description

Example level structure:
```json
{
  "name": "My Level",
  "description": "A challenging level!",
  "max_shots": 3,
  "spaceship_start": {"x": 100, "y": 300},
  "objects": [
    {
      "type": "planet",
      "x": 400,
      "y": 300,
      "mass": 100,
      "radius": 30,
      "color": [100, 150, 200]
    },
    {
      "type": "goal",
      "x": 700,
      "y": 300
    }
  ]
}
```

## 🎯 Future Enhancements

Potential additions to make the game even better:
- Moving/orbiting planets
- Collectible items
- Time-based challenges
- Sound effects and music
- Level editor GUI
- Multiplayer challenges
- Steam Workshop integration
- Mobile version

## 🐛 Troubleshooting

### Common Issues

**Game won't start**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.8+

**Poor performance**
- The game is designed to run at 60 FPS
- On slower systems, trajectory prediction might cause lag

**Levels not loading**
- Ensure the `levels/` directory exists
- Check that level JSON files are properly formatted

## 🎮 Have Fun!

Enjoy exploring the physics of space and mastering the art of gravitational navigation! Each level presents a unique puzzle that requires both planning and precision.

Remember: In space, momentum is everything! 🌌
