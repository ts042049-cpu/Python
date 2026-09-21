"""
NEBULA STRIKE - Parallax Starfield & Nebula Atmosphere
Provides a multi-layered moving starfield with twinkling stars and procedural cosmic nebulae.
"""

import random
import math
import pygame
from settings import WIDTH, HEIGHT


class Star:
    """Represents an individual star in the starfield."""
    def __init__(self, layer, screen_width=WIDTH, screen_height=HEIGHT):
        self.layer = layer
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.uniform(0, self.screen_width)
        self.y = random.uniform(0, self.screen_height)
        
        if layer == 0:  # Distant background stars
            self.base_speed = random.uniform(0.4, 0.8)
            self.size = 1
            self.color = random.choice([
                (180, 200, 255),
                (200, 220, 255),
                (255, 230, 200),
                (150, 170, 220)
            ])
            self.twinkle_speed = random.uniform(0.02, 0.05)
            self.twinkle_offset = random.uniform(0, math.pi * 2)
        elif layer == 1:  # Midground stars
            self.base_speed = random.uniform(1.2, 2.0)
            self.size = 2
            self.color = random.choice([
                (220, 240, 255),
                (255, 255, 255),
                (190, 255, 240),
                (255, 220, 230)
            ])
            self.twinkle_speed = random.uniform(0.04, 0.08)
            self.twinkle_offset = random.uniform(0, math.pi * 2)
        else:  # Foreground bright stars
            self.base_speed = random.uniform(2.6, 3.8)
            self.size = 3
            self.color = (255, 255, 255)
            self.twinkle_speed = random.uniform(0.06, 0.12)
            self.twinkle_offset = random.uniform(0, math.pi * 2)

    def update(self, speed_mult=1.0):
        """Move star downward, wrapping around the bottom."""
        self.y += self.base_speed * speed_mult
        if self.y > self.screen_height:
            self.y = 0
            self.x = random.uniform(0, self.screen_width)

    def draw(self, surface, time_sec):
        """Draw star with twinkling brightness and flare for foreground stars."""
        twinkle = 0.7 + 0.3 * math.sin(time_sec * 5 * self.twinkle_speed + self.twinkle_offset)
        r = int(min(255, max(0, self.color[0] * twinkle)))
        g = int(min(255, max(0, self.color[1] * twinkle)))
        b = int(min(255, max(0, self.color[2] * twinkle)))
        star_color = (r, g, b)

        ix, iy = int(self.x), int(self.y)
        if self.layer == 0:
            surface.set_at((ix, iy), star_color)
        elif self.layer == 1:
            pygame.draw.circle(surface, star_color, (ix, iy), 1)
        else:
            # Foreground star with slight cross-flare
            pygame.draw.circle(surface, star_color, (ix, iy), 2)
            if twinkle > 0.85:
                flare_color = (r // 2, g // 2, b // 2)
                surface.set_at((ix - 2, iy), flare_color)
                surface.set_at((ix + 2, iy), flare_color)
                surface.set_at((ix, iy - 2), flare_color)
                surface.set_at((ix, iy + 2), flare_color)


class NebulaCloud:
    """Procedurally rendered soft glowing nebula cloud drifting in deep space."""
    def __init__(self, x, y, radius, color_rgb, speed=0.25):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = color_rgb
        self.surface = self._create_nebula_surface()

    def _create_nebula_surface(self):
        """Generate a soft radial alpha gradient surface."""
        size = self.radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (self.radius, self.radius)
        r, g, b = self.color

        steps = 14
        for i in range(steps, 0, -1):
            current_r = int(self.radius * (i / steps))
            # Smooth falloff alpha
            norm = 1.0 - (i / steps)
            alpha = int(24 * (norm ** 1.6))
            pygame.draw.circle(surf, (r, g, b, alpha), center, current_r)

        return surf

    def update(self, speed_mult=1.0, screen_height=HEIGHT):
        """Move nebula downward slowly."""
        self.y += self.speed * speed_mult
        if self.y - self.radius > screen_height:
            self.y = -self.radius
            self.x = random.uniform(100, WIDTH - 100)

    def draw(self, surface):
        """Render the pre-baked nebula surface with additive blending."""
        rect = self.surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.surface, rect, special_flags=pygame.BLEND_ADD)


class Starfield:
    """Manages the full parallax starfield and nebula layers."""
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.stars = []
        
        # Populate stars across 3 layers
        for _ in range(85):
            self.stars.append(Star(0, self.width, self.height))
        for _ in range(50):
            self.stars.append(Star(1, self.width, self.height))
        for _ in range(25):
            self.stars.append(Star(2, self.width, self.height))

        # Cosmic nebulae
        self.nebulae = [
            NebulaCloud(WIDTH * 0.25, HEIGHT * 0.2, 280, (40, 10, 80), speed=0.2),
            NebulaCloud(WIDTH * 0.75, HEIGHT * 0.6, 320, (10, 45, 85), speed=0.25),
            NebulaCloud(WIDTH * 0.50, HEIGHT * 1.1, 300, (60, 20, 70), speed=0.22)
        ]
        self.time_sec = 0.0

    def update(self, dt=1/60, speed_mult=1.0):
        """Update stars, nebulae, and animation clock."""
        self.time_sec += dt
        for nebula in self.nebulae:
            nebula.update(speed_mult, self.height)
        for star in self.stars:
            star.update(speed_mult)

    def draw(self, surface):
        """Draw nebulae and all stars onto the destination surface."""
        # Draw nebulae first
        for nebula in self.nebulae:
            nebula.draw(surface)
        # Draw stars
        for star in self.stars:
            star.draw(surface, self.time_sec)
