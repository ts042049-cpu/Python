"""
NEBULA STRIKE - Projectiles System
Handles player and enemy projectiles: standard lasers, spread shots, fast needle bolts,
piercing laser beams, and tracking missiles with glowing visual effects.
"""

import math
import pygame
from settings import (
    WIDTH, HEIGHT, CYAN, WHITE, RED, ORANGE, PURPLE, YELLOW,
    PLAYER_BULLET_SPEED, ENEMY_BULLET_NORMAL_SPEED, ENEMY_BULLET_FAST_SPEED, ENEMY_BULLET_TRACKING_SPEED
)


class Bullet:
    """Base class for all game projectiles."""
    def __init__(self, x, y, vx, vy, damage=1, color=CYAN, radius=4):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.damage = damage
        self.color = color
        self.radius = radius
        self.alive = True
        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        if self.is_off_screen():
            self.alive = False

    def is_off_screen(self):
        return (self.y < -50 or self.y > HEIGHT + 50 or
                self.x < -50 or self.x > WIDTH + 50)

    def draw(self, surface):
        """Draw projectile with a glowing aura."""
        # Outer glow
        glow_radius = self.radius * 2 + 2
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (self.color[0], self.color[1], self.color[2], 90)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)), special_flags=pygame.BLEND_ADD)
        
        # Inner projectile
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Core white highlight
        if self.radius >= 3:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), max(1, self.radius // 2))


class PlayerBullet(Bullet):
    """Standard player laser bolt moving upward."""
    def __init__(self, x, y, vx=0, vy=-PLAYER_BULLET_SPEED, damage=25, is_double=False):
        color = CYAN if not is_double else YELLOW
        super().__init__(x, y, vx, vy, damage=damage, color=color, radius=4)
        self.length = 16
        self.is_double = is_double
        self.rect = pygame.Rect(int(self.x - 3), int(self.y - self.length // 2), 6, self.length)

    def update(self):
        super().update()
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        # Draw elongated glowing laser capsule
        glow_surf = pygame.Surface((20, self.length + 12), pygame.SRCALPHA)
        glow_color = (self.color[0], self.color[1], self.color[2], 90)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, 20, self.length + 12), border_radius=6)
        surface.blit(glow_surf, (int(self.x - 10), int(self.y - (self.length + 12) // 2)), special_flags=pygame.BLEND_ADD)

        # Main laser bolt
        pygame.draw.rect(surface, self.color, (int(self.x - 2), int(self.y - self.length // 2), 4, self.length), border_radius=2)
        # White hot center
        pygame.draw.rect(surface, WHITE, (int(self.x - 1), int(self.y - (self.length - 4) // 2), 2, self.length - 4), border_radius=1)


class LaserBeam(Bullet):
    """High-powered piercing laser beam fired in laser power-up mode."""
    def __init__(self, x, y, damage=65):
        super().__init__(x, y, 0, -22, damage=damage, color=(0, 255, 200), radius=7)
        self.length = 36
        self.rect = pygame.Rect(int(self.x - 5), int(self.y - self.length // 2), 10, self.length)
        self.piercing = True

    def update(self):
        super().update()
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        glow_surf = pygame.Surface((28, self.length + 16), pygame.SRCALPHA)
        glow_color = (0, 255, 200, 110)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, 28, self.length + 16), border_radius=10)
        surface.blit(glow_surf, (int(self.x - 14), int(self.y - (self.length + 16) // 2)), special_flags=pygame.BLEND_ADD)

        # Outer beam
        pygame.draw.rect(surface, (0, 255, 220), (int(self.x - 4), int(self.y - self.length // 2), 8, self.length), border_radius=4)
        # Inner beam
        pygame.draw.rect(surface, WHITE, (int(self.x - 2), int(self.y - self.length // 2), 4, self.length), border_radius=2)


class EnemyBullet(Bullet):
    """Standard enemy energy projectile."""
    def __init__(self, x, y, vx=0, vy=ENEMY_BULLET_NORMAL_SPEED, damage=15, color=RED):
        super().__init__(x, y, vx, vy, damage=damage, color=color, radius=5)


class FastEnemyBullet(Bullet):
    """Fast needle laser fired by snipers and high-tier fighters."""
    def __init__(self, x, y, vx=0, vy=ENEMY_BULLET_FAST_SPEED, damage=20):
        super().__init__(x, y, vx, vy, damage=damage, color=ORANGE, radius=3)
        self.length = 14
        self.rect = pygame.Rect(int(self.x - 3), int(self.y - self.length // 2), 6, self.length)

    def update(self):
        super().update()
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        glow_surf = pygame.Surface((16, self.length + 8), pygame.SRCALPHA)
        glow_color = (ORANGE[0], ORANGE[1], ORANGE[2], 100)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, 16, self.length + 8), border_radius=4)
        surface.blit(glow_surf, (int(self.x - 8), int(self.y - (self.length + 8) // 2)), special_flags=pygame.BLEND_ADD)

        pygame.draw.rect(surface, ORANGE, (int(self.x - 2), int(self.y - self.length // 2), 4, self.length), border_radius=2)
        pygame.draw.rect(surface, WHITE, (int(self.x - 1), int(self.y - self.length // 2), 2, self.length), border_radius=1)


class TrackingEnemyBullet(Bullet):
    """Homing missile that turns toward the player's current position."""
    def __init__(self, x, y, target_player, speed=ENEMY_BULLET_TRACKING_SPEED, damage=22):
        super().__init__(x, y, 0, speed, damage=damage, color=PURPLE, radius=6)
        self.target = target_player
        self.speed = speed
        self.angle = math.pi / 2  # Facing downwards
        self.turn_rate = 0.045     # Maximum angular turn speed (radians/frame)
        self.life = 240           # Dissipates after some time

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
            return

        # Calculate target angle
        if self.target and self.target.alive:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            target_angle = math.atan2(dy, dx)
            
            # Smoothly rotate toward target angle
            diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) < self.turn_rate:
                self.angle = target_angle
            else:
                self.angle += math.copysign(self.turn_rate, diff)

        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        super().update()

    def draw(self, surface):
        # Draw missile with purple glowing aura
        glow_radius = self.radius * 2 + 4
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (PURPLE[0], PURPLE[1], PURPLE[2], 120), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)), special_flags=pygame.BLEND_ADD)

        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 180, 255), (int(self.x), int(self.y)), max(1, self.radius - 2))
