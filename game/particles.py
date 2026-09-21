"""
NEBULA STRIKE - Particle System
Handles high-performance sparks, shockwaves, engine trails, asteroid debris,
and floating combat text with smooth alpha fades.
"""

import random
import math
import pygame
from settings import CYAN, MAGENTA, YELLOW, ORANGE, RED, WHITE, GREEN


class SparkParticle:
    """A glowing spark or debris particle with velocity, decay, and color fade."""
    def __init__(self, x, y, vx, vy, color, radius=3, max_life=30, friction=0.96):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.max_life = max_life
        self.life = max_life
        self.friction = friction

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = self.life / self.max_life
        current_radius = max(1, int(self.radius * progress))
        alpha = int(255 * progress)
        
        # Draw on an alpha surface for glowing effect
        size = current_radius * 4
        p_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(p_surf, c, (size // 2, size // 2), current_radius)
        
        # Center hot spot
        if current_radius > 1:
            pygame.draw.circle(p_surf, (255, 255, 255, alpha), (size // 2, size // 2), max(1, current_radius // 2))
            
        surface.blit(p_surf, (int(self.x - size // 2), int(self.y - size // 2)), special_flags=pygame.BLEND_ADD)


class Shockwave:
    """An expanding energy ring that radiates outward and fades out."""
    def __init__(self, x, y, color, max_radius=60, duration=24, line_width=3):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.life = duration
        self.line_width = line_width

    def update(self):
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = 1.0 - (self.life / self.duration)
        current_radius = int(self.max_radius * progress)
        if current_radius <= 0:
            return
            
        alpha = int(255 * (1.0 - progress))
        size = (current_radius + 4) * 2
        wave_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        
        pygame.draw.circle(
            wave_surf,
            c,
            (size // 2, size // 2),
            current_radius,
            max(1, int(self.line_width * (1.0 - progress * 0.5)))
        )
        surface.blit(wave_surf, (int(self.x - size // 2), int(self.y - size // 2)), special_flags=pygame.BLEND_ADD)


class FloatingText:
    """Animated floating combat text (e.g. +100, SHIELD UP!, CRITICAL)."""
    def __init__(self, x, y, text, color, duration=50, rise_speed=1.2, font_size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.life = duration
        self.rise_speed = rise_speed
        
        # Pre-render text
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.text_surf = self.font.render(self.text, True, self.color)

    def update(self):
        self.y -= self.rise_speed
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = self.life / self.duration
        alpha = int(255 * min(1.0, progress * 1.5))
        
        surf = self.text_surf.copy()
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(surf, rect)


class ParticleSystem:
    """Central particle manager for the entire game."""
    def __init__(self):
        self.sparks = []
        self.shockwaves = []
        self.floating_texts = []

    def update(self):
        """Update all particles and prune dead ones."""
        for p in self.sparks:
            p.update()
        self.sparks = [p for p in self.sparks if p.is_alive()]

        for w in self.shockwaves:
            w.update()
        self.shockwaves = [w for w in self.shockwaves if w.is_alive()]

        for t in self.floating_texts:
            t.update()
        self.floating_texts = [t for t in self.floating_texts if t.is_alive()]

    def draw(self, surface):
        """Draw all shockwaves, sparks, and floating text."""
        for w in self.shockwaves:
            w.draw(surface)
        for p in self.sparks:
            p.draw(surface)
        for t in self.floating_texts:
            t.draw(surface)

    def create_shockwave(self, x, y, color=CYAN, max_radius=60, duration=24, line_width=3):
        """Spawns an expanding glowing energy ring."""
        self.shockwaves.append(Shockwave(x, y, color, max_radius=max_radius, duration=duration, line_width=line_width))

    def create_explosion(self, x, y, color=ORANGE, count=28, speed_max=7.0, radius_max=4):
        """Spawns an explosive burst of radial sparks and an energy shockwave."""
        # Shockwave
        self.shockwaves.append(Shockwave(x, y, color, max_radius=int(speed_max * 12), duration=22))
        
        # Sparks
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Palette variation for rich explosion look
            spark_color = random.choice([color, YELLOW, WHITE, ORANGE])
            p_radius = random.randint(2, radius_max)
            p_life = random.randint(18, 42)
            
            self.sparks.append(SparkParticle(x, y, vx, vy, spark_color, radius=p_radius, max_life=p_life))

    def create_thruster_trail(self, x, y, direction_deg=90, color=CYAN, speed=3.0):
        """Spawns engine exhaust particles trailing behind a moving ship."""
        angle = math.radians(direction_deg + random.uniform(-25, 25))
        spd = random.uniform(speed * 0.6, speed * 1.3)
        vx = math.cos(angle) * spd
        vy = math.sin(angle) * spd
        
        p_color = random.choice([color, WHITE, CYAN])
        self.sparks.append(
            SparkParticle(x, y, vx, vy, p_color, radius=random.randint(1, 3), max_life=random.randint(8, 16), friction=0.92)
        )

    def create_asteroid_debris(self, x, y, count=16):
        """Spawns tumbling rocky asteroid fragments."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 5.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            debris_color = random.choice([
                (170, 180, 200),
                (120, 130, 150),
                (90, 100, 120),
                (200, 210, 230)
            ])
            self.sparks.append(
                SparkParticle(x, y, vx, vy, debris_color, radius=random.randint(2, 4), max_life=random.randint(20, 45), friction=0.95)
            )

    def create_hit_spark(self, x, y, color=WHITE, count=6):
        """Spawns small sparks when a bullet impacts an entity."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2.0, 6.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.sparks.append(
                SparkParticle(x, y, vx, vy, color, radius=random.randint(1, 2), max_life=random.randint(8, 18), friction=0.9)
            )

    def add_floating_text(self, x, y, text, color=YELLOW, font_size=20):
        """Spawns floating text at (x, y)."""
        self.floating_texts.append(FloatingText(x, y, text, color, font_size=font_size))

    def clear(self):
        """Clear all active particles."""
        self.sparks.clear()
        self.shockwaves.clear()
        self.floating_texts.clear()
