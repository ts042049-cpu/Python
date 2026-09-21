"""
NEBULA STRIKE - Collectible Power-Ups System
Implements floating glowing power-up capsules dropped by destroyed enemies and asteroids:
- SHIELD      (🛡 Energy barrier protection)
- RAPID_FIRE  (⚡ High fire rate overdrive)
- HEALTH      (❤️ Nanite hull repair)
- LASER       (💥 Penetrating plasma laser beam)
- DOUBLE_SHOT (🔥 Dual wing-mounted heavy cannons)
"""

import math
import random
import pygame
from settings import (
    WIDTH, HEIGHT, CYAN, YELLOW, GREEN, MAGENTA, ORANGE, WHITE
)


class PowerUp:
    """Floating collectible power-up capsule."""
    TYPE_SHIELD = "shield"
    TYPE_RAPID_FIRE = "rapid_fire"
    TYPE_HEALTH = "health"
    TYPE_LASER = "laser"
    TYPE_DOUBLE_SHOT = "double_shot"

    TYPES = [TYPE_SHIELD, TYPE_RAPID_FIRE, TYPE_HEALTH, TYPE_LASER, TYPE_DOUBLE_SHOT]

    COLORS = {
        TYPE_SHIELD: CYAN,
        TYPE_RAPID_FIRE: YELLOW,
        TYPE_HEALTH: GREEN,
        TYPE_LASER: MAGENTA,
        TYPE_DOUBLE_SHOT: ORANGE
    }

    LABELS = {
        TYPE_SHIELD: "SHIELD",
        TYPE_RAPID_FIRE: "RAPID FIRE",
        TYPE_HEALTH: "+HP",
        TYPE_LASER: "LASER",
        TYPE_DOUBLE_SHOT: "DOUBLE SHOT"
    }

    ICONS = {
        TYPE_SHIELD: "S",
        TYPE_RAPID_FIRE: "R",
        TYPE_HEALTH: "+",
        TYPE_LASER: "L",
        TYPE_DOUBLE_SHOT: "D"
    }

    def __init__(self, x, y, powerup_type=None):
        self.x = float(x)
        self.y = float(y)
        self.powerup_type = powerup_type or random.choice(self.TYPES)
        self.color = self.COLORS[self.powerup_type]
        self.radius = 16
        self.vy = random.uniform(1.4, 2.0)
        self.vx = random.uniform(-0.5, 0.5)
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.time_sec = 0.0
        self.alive = True
        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt_sec=1/60):
        self.time_sec += dt_sec
        self.y += self.vy
        self.x += self.vx + math.sin(self.time_sec * 3 + self.bob_offset) * 0.4
        self.rect.center = (int(self.x), int(self.y))

        if self.y - self.radius > HEIGHT + 40 or self.x < -40 or self.x > WIDTH + 40:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return

        px, py = int(self.x), int(self.y)
        pulse = 0.8 + 0.2 * math.sin(self.time_sec * 6 + self.bob_offset)

        # Outer glowing aura
        glow_size = int(self.radius * 2.5 * pulse)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_col = (self.color[0], self.color[1], self.color[2], int(70 * pulse))
        pygame.draw.circle(glow_surf, glow_col, (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (px - glow_size, py - glow_size), special_flags=pygame.BLEND_ADD)

        # Hexagonal badge
        hex_points = []
        for i in range(6):
            ang = (i / 6) * math.pi * 2 + (self.time_sec * 1.5)
            hx = px + math.cos(ang) * (self.radius * 1.1)
            hy = py + math.sin(ang) * (self.radius * 1.1)
            hex_points.append((hx, hy))

        pygame.draw.polygon(surface, (15, 20, 35), hex_points)
        pygame.draw.polygon(surface, self.color, hex_points, 2)

        # Core symbol
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.ICONS[self.powerup_type], True, WHITE)
        t_rect = txt.get_rect(center=(px, py))
        surface.blit(txt, t_rect)
