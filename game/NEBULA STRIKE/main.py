"""
NEBULA STRIKE 🚀
Advanced 2D Python Space Shooter

Entry point of the game.
Run with:
    python main.py
"""

import sys
import pygame
from settings import WIDTH, HEIGHT, TITLE
from game import Game


def create_window_icon():
    """Generate a sharp, glowing spaceship icon for the window titlebar."""
    icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Spaceship triangle
    pts = [(16, 2), (28, 28), (16, 22), (4, 28)]
    pygame.draw.polygon(icon_surf, (0, 240, 255), pts)
    pygame.draw.polygon(icon_surf, (255, 255, 255), pts, 1)
    # Cockpit dot
    pygame.draw.circle(icon_surf, (255, 0, 128), (16, 14), 3)
    return icon_surf


def main():
    """Initializes Pygame, creates window, and starts NEBULA STRIKE."""
    # Initialize core Pygame systems
    pygame.init()

    # Set window icon and title
    try:
        icon = create_window_icon()
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Window icon note: {e}")

    # Launch game engine
    game = Game()
    game.run()

    sys.exit(0)


if __name__ == "__main__":
    main()
