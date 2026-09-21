"""
NEBULA STRIKE - Enemy Spaceships
Implements 4 distinct enemy archetypes with unique AI patterns, procedural ship designs,
custom weapon behaviors, and health indicators:
1. Scout   - Agile, fast sinusoidal swooper
2. Fighter - Tactical strafer with aimed projectiles
3. Tank    - Armored battle-cruiser firing triple spread salvos with mini health bar
4. Hunter  - Aggressive interceptor tracking the player's position
"""

import random
import math
import pygame
from settings import (
    WIDTH, HEIGHT, RED, ORANGE, PURPLE, YELLOW, CYAN, WHITE, GREEN,
    SCORE_SCOUT, SCORE_FIGHTER, SCORE_TANK, SCORE_HUNTER
)
from bullet import EnemyBullet, FastEnemyBullet, TrackingEnemyBullet


class Enemy:
    """Base class for all enemy starships."""
    def __init__(self, x, y, hp, score_value, speed):
        self.x = float(x)
        self.y = float(y)
        self.max_hp = hp
        self.hp = hp
        self.score_value = score_value
        self.speed = speed
        self.alive = True
        self.hit_flash_timer = 0
        self.shoot_timer = random.randint(30, 90)
        self.engine_timer = 0

    def take_damage(self, amount):
        """Apply damage and set hit flash."""
        self.hp -= amount
        self.hit_flash_timer = 4
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def is_off_screen(self):
        return self.y > HEIGHT + 80 or self.x < -100 or self.x > WIDTH + 100

    def draw_health_bar(self, surface, x, y, width=40, height=5):
        """Draw mini health bar above the enemy."""
        if self.hp < self.max_hp:
            ratio = max(0.0, self.hp / self.max_hp)
            bg_rect = pygame.Rect(x - width // 2, y, width, height)
            fill_rect = pygame.Rect(x - width // 2, y, int(width * ratio), height)
            pygame.draw.rect(surface, (40, 10, 10), bg_rect)
            hp_color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
            pygame.draw.rect(surface, hp_color, fill_rect)
            pygame.draw.rect(surface, WHITE, bg_rect, 1)


class Scout(Enemy):
    """Fast, agile scout executing sinusoidal swoop maneuvers."""
    def __init__(self, x=None, y=None, speed_mult=1.0, hp_mult=1.0):
        init_x = x if x is not None else random.randint(60, WIDTH - 60)
        init_y = y if y is not None else -40
        super().__init__(init_x, init_y, hp=int(22 * hp_mult), score_value=SCORE_SCOUT, speed=3.6 * speed_mult)
        
        self.width = 34
        self.height = 36
        self.rect = pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)
        self.sine_freq = random.uniform(0.04, 0.07)
        self.sine_amp = random.uniform(3.5, 6.0)
        self.time_step = random.uniform(0, 100)

    def update(self, player, current_time, particle_system=None):
        self.time_step += 1
        self.y += self.speed
        self.x += math.sin(self.time_step * self.sine_freq) * self.sine_amp
        self.rect.center = (int(self.x), int(self.y))

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        if self.is_off_screen():
            self.alive = False

        # Thruster trail
        if particle_system and self.alive:
            self.engine_timer += 1
            if self.engine_timer % 3 == 0:
                particle_system.create_thruster_trail(self.x, self.y - 12, direction_deg=270, color=ORANGE, speed=2.5)

    def shoot(self, current_time, player=None):
        """Scouts fire infrequent light bolts."""
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(90, 160)
            if self.y > 0 and self.y < HEIGHT - 150:
                return [EnemyBullet(self.x, self.y + 16, vx=0, vy=5.5, damage=12, color=ORANGE)]
        return []

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        # Fast needle-winged scout
        nose = (px, py + 18)
        left_wing = (px - 16, py - 12)
        tail = (px, py - 6)
        right_wing = (px + 16, py - 12)
        pts = [nose, right_wing, tail, left_wing]

        color = WHITE if self.hit_flash_timer > 0 else (255, 120, 20)
        pygame.draw.polygon(surface, (45, 20, 10), pts)
        pygame.draw.polygon(surface, color, pts, 2)
        # Glowing cockpit
        pygame.draw.circle(surface, YELLOW, (px, py), 3)


class Fighter(Enemy):
    """Tactical fighter that strafes downward and aims shots directly at player."""
    def __init__(self, x=None, y=None, speed_mult=1.0, hp_mult=1.0):
        init_x = x if x is not None else random.randint(80, WIDTH - 80)
        init_y = y if y is not None else -50
        super().__init__(init_x, init_y, hp=int(50 * hp_mult), score_value=SCORE_FIGHTER, speed=2.2 * speed_mult)

        self.width = 44
        self.height = 42
        self.rect = pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)
        self.strafe_vx = random.choice([-1.2, 1.2]) * speed_mult
        self.shoot_timer = random.randint(45, 90)

    def update(self, player, current_time, particle_system=None):
        self.y += self.speed
        self.x += self.strafe_vx
        if self.x < 70 or self.x > WIDTH - 70:
            self.strafe_vx *= -1

        self.rect.center = (int(self.x), int(self.y))
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.is_off_screen():
            self.alive = False

        if particle_system and self.alive:
            self.engine_timer += 1
            if self.engine_timer % 3 == 0:
                particle_system.create_thruster_trail(self.x - 8, self.y - 14, direction_deg=270, color=RED, speed=3.0)
                particle_system.create_thruster_trail(self.x + 8, self.y - 14, direction_deg=270, color=RED, speed=3.0)

    def shoot(self, current_time, player=None):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(80, 130)
            if self.y > 20 and self.y < HEIGHT - 180:
                bullets = []
                if player and player.alive:
                    # Aimed shot
                    dx = player.x - self.x
                    dy = player.y - self.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        spd = 6.0
                        vx = (dx / dist) * spd
                        vy = (dy / dist) * spd
                        bullets.append(FastEnemyBullet(self.x, self.y + 18, vx=vx, vy=vy, damage=16))
                else:
                    bullets.append(FastEnemyBullet(self.x, self.y + 18, vx=0, vy=6.0, damage=16))
                return bullets
        return []

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        nose = (px, py + 20)
        wing_r = (px + 22, py - 10)
        fin_r = (px + 10, py - 16)
        engine_mid = (px, py - 8)
        fin_l = (px - 10, py - 16)
        wing_l = (px - 22, py - 10)
        pts = [nose, wing_r, fin_r, engine_mid, fin_l, wing_l]

        color = WHITE if self.hit_flash_timer > 0 else RED
        pygame.draw.polygon(surface, (50, 12, 18), pts)
        pygame.draw.polygon(surface, color, pts, 2)
        pygame.draw.circle(surface, (255, 60, 60), (px, py + 2), 4)


class Tank(Enemy):
    """Heavily armored dreadnought firing triple spread salvos with mini health bar."""
    def __init__(self, x=None, y=None, speed_mult=1.0, hp_mult=1.0):
        init_x = x if x is not None else random.randint(120, WIDTH - 120)
        init_y = y if y is not None else -80
        super().__init__(init_x, init_y, hp=int(160 * hp_mult), score_value=SCORE_TANK, speed=1.1 * speed_mult)

        self.width = 68
        self.height = 62
        self.rect = pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)
        self.shoot_timer = random.randint(60, 110)

    def update(self, player, current_time, particle_system=None):
        self.y += self.speed
        self.rect.center = (int(self.x), int(self.y))
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.is_off_screen():
            self.alive = False

        if particle_system and self.alive:
            self.engine_timer += 1
            if self.engine_timer % 2 == 0:
                particle_system.create_thruster_trail(self.x - 18, self.y - 24, direction_deg=270, color=PURPLE, speed=3.5)
                particle_system.create_thruster_trail(self.x + 18, self.y - 24, direction_deg=270, color=PURPLE, speed=3.5)

    def shoot(self, current_time, player=None):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(100, 150)
            if self.y > 30 and self.y < HEIGHT - 200:
                # Triple spread salvo
                return [
                    EnemyBullet(self.x - 18, self.y + 24, vx=-2.0, vy=5.0, damage=20, color=PURPLE),
                    EnemyBullet(self.x, self.y + 28, vx=0.0, vy=5.5, damage=24, color=PURPLE),
                    EnemyBullet(self.x + 18, self.y + 24, vx=2.0, vy=5.0, damage=20, color=PURPLE)
                ]
        return []

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        # Heavy battlecruiser polygon
        pts = [
            (px, py + 30),
            (px + 28, py + 12),
            (px + 34, py - 18),
            (px + 14, py - 28),
            (px - 14, py - 28),
            (px - 34, py - 18),
            (px - 28, py + 12)
        ]
        color = WHITE if self.hit_flash_timer > 0 else (170, 70, 240)
        pygame.draw.polygon(surface, (38, 15, 55), pts)
        pygame.draw.polygon(surface, color, pts, 3)
        # Heavy armor plates
        pygame.draw.line(surface, color, (px - 20, py), (px + 20, py), 2)
        pygame.draw.circle(surface, (255, 100, 255), (px, py - 4), 6)
        # Health bar
        self.draw_health_bar(surface, px, py - 38, width=54, height=5)


class Hunter(Enemy):
    """Aggressive interceptor that dynamically seeks the player's position and fires tracking missiles."""
    def __init__(self, x=None, y=None, speed_mult=1.0, hp_mult=1.0):
        init_x = x if x is not None else random.randint(100, WIDTH - 100)
        init_y = y if y is not None else -60
        super().__init__(init_x, init_y, hp=int(80 * hp_mult), score_value=SCORE_HUNTER, speed=2.5 * speed_mult)

        self.width = 46
        self.height = 48
        self.rect = pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)
        self.tracking_speed = 3.2 * speed_mult
        self.shoot_timer = random.randint(40, 80)

    def update(self, player, current_time, particle_system=None):
        self.y += self.speed * 0.75
        
        # Intercept player horizontally
        if player and player.alive:
            dx = player.x - self.x
            if abs(dx) > 10:
                self.x += math.copysign(min(abs(dx), self.tracking_speed), dx)

        self.rect.center = (int(self.x), int(self.y))
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.is_off_screen():
            self.alive = False

        if particle_system and self.alive:
            self.engine_timer += 1
            if self.engine_timer % 2 == 0:
                particle_system.create_thruster_trail(self.x, self.y - 20, direction_deg=270, color=CYAN, speed=3.2)

    def shoot(self, current_time, player=None):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(70, 110)
            if self.y > 40 and self.y < HEIGHT - 180:
                # Fire homing missile
                if player and player.alive and random.random() < 0.6:
                    return [TrackingEnemyBullet(self.x, self.y + 20, player, speed=4.2, damage=22)]
                else:
                    return [
                        FastEnemyBullet(self.x - 12, self.y + 18, vx=-1.0, vy=6.5, damage=16),
                        FastEnemyBullet(self.x + 12, self.y + 18, vx=1.0, vy=6.5, damage=16)
                    ]
        return []

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        # Sharp forward-swept hunter wings
        pts = [
            (px, py + 24),
            (px + 12, py + 14),
            (px + 24, py + 22),
            (px + 16, py - 18),
            (px, py - 10),
            (px - 16, py - 18),
            (px - 24, py + 22),
            (px - 12, py + 14)
        ]
        color = WHITE if self.hit_flash_timer > 0 else (0, 240, 255)
        pygame.draw.polygon(surface, (10, 35, 50), pts)
        pygame.draw.polygon(surface, color, pts, 2)
        pygame.draw.circle(surface, (0, 255, 200), (px, py + 2), 4)
        self.draw_health_bar(surface, px, py - 26, width=42, height=4)
