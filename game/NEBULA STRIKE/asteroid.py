"""
NEBULA STRIKE - Asteroids System
Procedurally generated asteroids with irregular jagged geometry, surface craters,
realistic tumbling rotation, and a cascading splitting system (Large -> Medium -> Small).
"""

import random
import math
import pygame
from settings import (
    WIDTH, HEIGHT, WHITE,
    SCORE_ASTEROID_SMALL, SCORE_ASTEROID_MED, SCORE_ASTEROID_LARGE
)


class Asteroid:
    """An individual tumbling asteroid with procedural jagged geometry."""
    SIZE_LARGE = "large"
    SIZE_MEDIUM = "medium"
    SIZE_SMALL = "small"

    def __init__(self, x=None, y=None, size_tier=None, vx=None, vy=None):
        self.size_tier = size_tier or random.choice([self.SIZE_LARGE, self.SIZE_MEDIUM, self.SIZE_SMALL])
        
        # Configure tier properties
        if self.size_tier == self.SIZE_LARGE:
            self.base_radius = random.randint(46, 56)
            self.max_hp = 4
            self.score_value = SCORE_ASTEROID_LARGE
            base_speed = random.uniform(1.0, 2.2)
        elif self.size_tier == self.SIZE_MEDIUM:
            self.base_radius = random.randint(26, 34)
            self.max_hp = 2
            self.score_value = SCORE_ASTEROID_MED
            base_speed = random.uniform(1.8, 3.2)
        else:  # Small
            self.base_radius = random.randint(14, 18)
            self.max_hp = 1
            self.score_value = SCORE_ASTEROID_SMALL
            base_speed = random.uniform(2.5, 4.5)

        self.hp = self.max_hp
        self.x = float(x if x is not None else random.randint(self.base_radius, WIDTH - self.base_radius))
        self.y = float(y if y is not None else -self.base_radius * 2)
        
        self.vx = float(vx if vx is not None else random.uniform(-0.8, 0.8))
        self.vy = float(vy if vy is not None else base_speed)

        # Rotation
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2.5, 2.5)
        self.hit_flash_timer = 0
        self.alive = True

        # Generate procedural irregular polygon vertices
        self.vertex_count = random.randint(10, 16)
        self.vertices = []
        for i in range(self.vertex_count):
            theta = (i / self.vertex_count) * (math.pi * 2)
            # Irregular radius variation
            r = self.base_radius * random.uniform(0.78, 1.22)
            self.vertices.append((math.cos(theta) * r, math.sin(theta) * r))

        # Craters on surface
        self.craters = []
        crater_count = random.randint(2, 5) if self.size_tier != self.SIZE_SMALL else 1
        for _ in range(crater_count):
            crater_angle = random.uniform(0, math.pi * 2)
            crater_dist = random.uniform(0, self.base_radius * 0.6)
            crater_radius = random.uniform(self.base_radius * 0.12, self.base_radius * 0.28)
            cx = math.cos(crater_angle) * crater_dist
            cy = math.sin(crater_angle) * crater_dist
            self.craters.append((cx, cy, crater_radius))

        # Pre-render base surface
        self.base_surface = self._build_base_surface()
        self.image = self.base_surface
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _build_base_surface(self):
        """Draw the procedural asteroid polygon, craters, and shading to a surface."""
        surf_size = int(self.base_radius * 2.8)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        center = (surf_size // 2, surf_size // 2)

        # Shift vertices to surface center
        shifted_verts = [(center[0] + vx, center[1] + vy) for vx, vy in self.vertices]

        # Base rock color
        base_color = (95, 105, 125)
        edge_highlight = (145, 160, 185)
        dark_shade = (60, 68, 85)

        # Draw main rock body
        pygame.draw.polygon(surf, base_color, shifted_verts)

        # Draw craters
        for cx, cy, cr in self.craters:
            c_pos = (int(center[0] + cx), int(center[1] + cy))
            pygame.draw.circle(surf, dark_shade, c_pos, int(cr))
            # Crater rim
            pygame.draw.circle(surf, edge_highlight, c_pos, int(cr), 1)

        # Outlines & highlights
        pygame.draw.polygon(surf, edge_highlight, shifted_verts, 2)

        return surf

    def update(self):
        """Update coordinates, tumbling angle, and collision rect."""
        self.x += self.vx
        self.y += self.vy
        self.angle = (self.angle + self.rot_speed) % 360

        # Rotate surface
        self.image = pygame.transform.rotate(self.base_surface, self.angle)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        # Check off-screen
        if self.y - self.base_radius > HEIGHT + 60:
            self.alive = False

    def take_damage(self, amount=1):
        """Apply damage and trigger hit flash."""
        self.hp -= amount
        self.hit_flash_timer = 4
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def split(self):
        """Splits large asteroid into 2 medium, and medium into 2 small."""
        if self.size_tier == self.SIZE_LARGE:
            a1 = Asteroid(self.x - 14, self.y, self.SIZE_MEDIUM, vx=self.vx - 1.2, vy=self.vy * 1.1)
            a2 = Asteroid(self.x + 14, self.y, self.SIZE_MEDIUM, vx=self.vx + 1.2, vy=self.vy * 1.1)
            return [a1, a2]
        elif self.size_tier == self.SIZE_MEDIUM:
            a1 = Asteroid(self.x - 10, self.y, self.SIZE_SMALL, vx=self.vx - 1.6, vy=self.vy * 1.2)
            a2 = Asteroid(self.x + 10, self.y, self.SIZE_SMALL, vx=self.vx + 1.6, vy=self.vy * 1.2)
            return [a1, a2]
        return []

    def draw(self, surface):
        """Render the tumbling asteroid with hit-flash support."""
        if not self.alive:
            return

        if self.hit_flash_timer > 0:
            # Render white silhouette flash
            flash_surf = self.image.copy()
            flash_surf.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(flash_surf, self.rect)
        else:
            surface.blit(self.image, self.rect)
