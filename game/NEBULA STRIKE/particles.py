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
    """Animated floating combat text with bounce, outline, and alpha fade."""
    def __init__(self, x, y, text, color, duration=48, rise_speed=1.4, font_size=20, is_crit=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.life = duration
        self.rise_speed = rise_speed
        self.is_crit = is_crit
        
        # Pre-render text with drop shadow / dark outline
        actual_size = int(font_size * 1.25) if is_crit else font_size
        self.font = pygame.font.SysFont("Arial", actual_size, bold=True)
        self.text_surf = self.font.render(self.text, True, self.color)
        self.shadow_surf = self.font.render(self.text, True, (0, 0, 0))

    def update(self):
        self.y -= self.rise_speed
        self.rise_speed = max(0.4, self.rise_speed * 0.96)
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = self.life / self.duration
        alpha = int(255 * min(1.0, progress * 1.6))
        
        # Pop scale during first 6 frames
        scale = 1.0
        elapsed = self.duration - self.life
        if elapsed < 6:
            scale = 1.0 + (6 - elapsed) * 0.05
        
        surf = self.text_surf
        shadow = self.shadow_surf
        if scale != 1.0:
            w = max(1, int(surf.get_width() * scale))
            h = max(1, int(surf.get_height() * scale))
            surf = pygame.transform.smoothscale(surf, (w, h))
            shadow = pygame.transform.smoothscale(shadow, (w, h))
            
        surf = surf.copy()
        surf.set_alpha(alpha)
        shadow = shadow.copy()
        shadow.set_alpha(int(alpha * 0.7))

        ix, iy = int(self.x), int(self.y)
        rect = surf.get_rect(center=(ix, iy))
        shadow_rect = shadow.get_rect(center=(ix + 1, iy + 2))
        
        surface.blit(shadow, shadow_rect)
        surface.blit(surf, rect)


class SmokeParticle:
    """Soft billowing smoke / flame puff for ship damage trails."""
    def __init__(self, x, y, is_fire=False):
        self.x = x
        self.y = y
        self.is_fire = is_fire
        angle = random.uniform(math.pi * 0.25, math.pi * 0.75)  # Drift upward & outward
        speed = random.uniform(0.5, 2.0)
        self.vx = math.cos(angle) * speed * random.choice([-1, 1])
        self.vy = random.uniform(0.5, 2.5)  # Drift down relative to ship movement
        self.radius = random.uniform(3, 6) if not is_fire else random.uniform(2, 4)
        self.max_life = random.randint(20, 36)
        self.life = self.max_life
        if is_fire:
            self.color = random.choice([(255, 100, 20), (255, 60, 20), (255, 180, 40)])
        else:
            shade = random.randint(70, 120)
            self.color = (shade, shade, shade)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius += 0.15
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(160 * (self.life / self.max_life))
        size = int(self.radius * 2) + 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(surf, c, (size // 2, size // 2), int(self.radius))
        surface.blit(surf, (int(self.x - size // 2), int(self.y - size // 2)))


class ParticleSystem:
    """Central particle manager for the entire game."""
    def __init__(self):
        self.sparks = []
        self.shockwaves = []
        self.floating_texts = []
        self.smoke_particles = []

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

        for s in self.smoke_particles:
            s.update()
        self.smoke_particles = [s for s in self.smoke_particles if s.is_alive()]

    def draw(self, surface):
        """Draw all shockwaves, smoke, sparks, and floating text."""
        for s in self.smoke_particles:
            s.draw(surface)
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
        self.shockwaves.append(Shockwave(x, y, color, max_radius=int(speed_max * 12), duration=22))
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
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
        
        p_color = random.choice([color, WHITE, (200, 240, 255)])
        self.sparks.append(
            SparkParticle(x, y, vx, vy, p_color, radius=random.randint(1, 3), max_life=random.randint(8, 16), friction=0.92)
        )

    def create_damage_smoke(self, x, y, is_fire=False):
        """Spawns trailing smoke puff and fire sparks from damaged player hull."""
        self.smoke_particles.append(SmokeParticle(x, y, is_fire=is_fire))
        if is_fire and random.random() < 0.4:
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(1.5, 3.5)
            self.sparks.append(SparkParticle(x, y, math.cos(angle) * spd, math.sin(angle) * spd, (255, 120, 0), radius=2, max_life=14))

    def create_warp_in_effect(self, x, y, color=CYAN):
        """Spawns converging hyperdrive warp particles and glowing rings for respawn."""
        self.shockwaves.append(Shockwave(x, y, color, max_radius=80, duration=28, line_width=4))
        self.shockwaves.append(Shockwave(x, y, WHITE, max_radius=45, duration=18, line_width=2))
        for _ in range(32):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(40, 110)
            target_x = x + math.cos(angle) * dist
            target_y = y + math.sin(angle) * dist
            vx = (x - target_x) / 14.0
            vy = (y - target_y) / 14.0
            self.sparks.append(SparkParticle(target_x, target_y, vx, vy, color, radius=3, max_life=16))

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

    def add_floating_text(self, x, y, text, color=YELLOW, font_size=20, is_crit=False):
        """Spawns floating text at (x, y)."""
        self.floating_texts.append(FloatingText(x, y, text, color, font_size=font_size, is_crit=is_crit))

    def add_damage_popup(self, x, y, amount, is_crit=False, is_player=False, is_shield=False, shield_color=CYAN):
        """Creates stylized popups for combat damage and shield absorption."""
        # Slight random jitter so multiple numbers don't overlap completely
        jx = x + random.uniform(-10, 10)
        jy = y + random.uniform(-6, 6)
        if is_shield:
            txt = f"SHIELD -{int(amount)}"
            col = shield_color
            self.add_floating_text(jx, jy, txt, color=col, font_size=18, is_crit=False)
        elif is_player:
            txt = f"-{int(amount)}"
            col = (255, 60, 60)
            self.add_floating_text(jx, jy, txt, color=col, font_size=22, is_crit=True)
        elif is_crit:
            txt = f"-{int(amount)} CRIT!"
            col = (255, 215, 0)
            self.add_floating_text(jx, jy, txt, color=col, font_size=22, is_crit=True)
        else:
            txt = f"-{int(amount)}"
            col = (255, 240, 200)
            self.add_floating_text(jx, jy, txt, color=col, font_size=18, is_crit=False)

    def clear(self):
        """Clear all active particles."""
        self.sparks.clear()
        self.shockwaves.clear()
        self.floating_texts.clear()
        self.smoke_particles.clear()
