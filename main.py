"""
Gravity Wells v2.0 - A spaceship slingshotting game
Navigate through gravitational fields, wormholes, and black holes!

New in v2.0:
  - Wormhole teleportation mechanic
  - Star rating system (1-3 stars per level)
  - Animated starfield background with shooting stars
  - Screen shake effects on collisions
  - Explosion particle effects
  - Time dilation near black holes
  - Level select screen (press M)
  - 3 new levels featuring wormholes
  - 12 total levels
"""

import pygame
import sys
from game.engine import GameEngine

def main():
    """Main entry point for the game"""
    pygame.init()

    # Initialize the game engine
    game = GameEngine()

    try:
        # Run the game
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
