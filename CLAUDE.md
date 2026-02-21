# CLAUDE.md — Gravity Wells v2.0

## Project Overview

Gravity Wells is a physics-based 2D puzzle game built with Python and pygame. Players slingshot a spaceship through gravitational fields, wormholes, and past obstacles to reach a goal. It uses an Angry Birds-style drag-to-launch mechanic with Newtonian gravity simulation.

**Tech stack:** Python 3.8+, pygame, numpy

## Running the Game

```bash
pip install -r requirements.txt
python main.py
```

Or use `./run_game.sh` (auto-detects virtualenv).

No test suite exists. To verify changes don't break imports:
```bash
python -c "from game.engine import GameEngine; print('OK')"
```

## Project Structure

```
main.py              # Entry point — creates GameEngine and calls run()
game/
  engine.py          # Game loop, input handling, rendering, UI, all game states
  physics.py         # Vector2D class, gravity calculations, trajectory prediction
  objects.py         # All game entities (GameObject subclasses) + visual effects
  level.py           # Level loading from JSON, progression, star ratings, unlocks
levels/
  level_01.json      # 12 level files loaded alphabetically by LevelManager
  ...
  level_12.json
progress.json        # Auto-generated at runtime — player save data (gitignored)
```

## Architecture

**Game loop:** `GameEngine.run()` calls `handle_events()` → `update(dt)` → `draw()` at 60 FPS.

**Game states** (`GameState` enum in `engine.py`): `AIMING` (2), `FLYING` (3), `LEVEL_COMPLETE` (4), `GAME_OVER` (5), `LEVEL_SELECT` (6). States 0-1 (MENU, PLAYING) are unused.

**Object hierarchy** — all game entities inherit from `GameObject` (`objects.py`):
- `Spaceship` — player ship with fuel, trail, glow
- `Planet` — color-based gravity multiplier (red=2x, blue=1x, green=0.7x, yellow=1.5x, purple=2.5x, white=1.2x)
- `BlackHole` — extreme gravity, causes time dilation when ship is within 200px
- `AntiGravityWell` — repulsive force (`anti_gravity = True` flag checked in physics)
- `Goal` — level completion target (mass=0)
- `Obstacle` — deadly collision hazard (mass=0)
- `Wormhole` — teleportation portal, paired via `link_partner()`

**Standalone classes** in `objects.py`: `ExplosionEffect` (particle burst), `Starfield` (background).

**Physics** (`physics.py`): `PhysicsEngine` computes gravity with `F = G * m1 * m2 / r^2` using `Vector2D`. Gravity constant = 5000, max range = 500px. Anti-gravity sources have force inverted. Trajectory prediction uses Euler integration (60 steps, dt=0.15).

**Level system** (`level.py`): `LevelManager` loads all `levels/*.json` alphabetically, tracks completion and star ratings in `progress.json`. Levels unlock sequentially. Star ratings: 3 stars = used ≤1/3 of max shots, 2 = ≤2/3, 1 = completed.

## Code Conventions

- **Classes:** PascalCase (`GameEngine`, `BlackHole`)
- **Methods/variables:** snake_case (`calculate_gravity_force`, `screen_width`)
- **Constants:** UPPER_CASE or module-level (`VERSION = "2.0"`, gravity values in `PhysicsEngine.__init__`)
- **Positions/velocities:** Always use `Vector2D` (from `physics.py`), never raw tuples for math
- **Drawing:** Each `GameObject` subclass has its own `draw(screen)` method
- **State updates:** Objects with behavior implement `update(dt)`
- **Imports:** `from game.module import Class` style

## Key Constants

| Constant | Value | Location |
|---|---|---|
| VERSION | "2.0" | `engine.py` |
| Screen size | 1024x768 | `engine.py` |
| FPS | 60 | `engine.py` |
| Gravity constant | 5000 | `physics.py` |
| Max gravity distance | 500px | `physics.py` |
| Max slingshot pull | 120px | `engine.py` |
| Launch speed multiplier | 350 | `engine.py` |
| Spaceship fuel | 100 | `objects.py` |

## Adding New Levels

Create a JSON file in `levels/` (naming: `level_NN.json`, loaded alphabetically):

```json
{
  "name": "Level Name",
  "description": "Shown in level select",
  "max_shots": 3,
  "spaceship_start": {"x": 100, "y": 300},
  "objects": [
    {"type": "planet", "x": 400, "y": 300, "mass": 80, "radius": 25, "color": [50, 50, 255]},
    {"type": "black_hole", "x": 500, "y": 400, "mass": 400},
    {"type": "anti_gravity", "x": 300, "y": 200, "mass": 60},
    {"type": "obstacle", "x": 350, "y": 350, "radius": 15},
    {"type": "wormhole", "x": 200, "y": 500, "partner_x": 600, "partner_y": 200},
    {"type": "goal", "x": 800, "y": 300}
  ]
}
```

Wormholes must be added in pairs (consecutive in the objects array) to be linked automatically.

## Adding New Game Objects

1. Create a subclass of `GameObject` in `objects.py` with `draw(screen)` and optionally `update(dt)`
2. Add an `elif obj_type == "your_type"` branch in `Level.create_object_from_data()` in `level.py`
3. If it has gravity: ensure `mass > 0` (auto-added to `gravity_sources`)
4. If it needs special collision handling: add logic in `GameEngine.check_collisions()` in `engine.py`
