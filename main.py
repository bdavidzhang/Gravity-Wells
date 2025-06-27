"""
Gravity Wells - A spaceship slingshotting game
Navigate through gravitational fields to reach your destination!
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
