"""
NEBULA STRIKE - Boss Battles System
Implements the Level 5 Sector Boss and the epic Final Boss "VOID DESTROYER",
featuring multi-phase combat AI, spiral bullet hell attacks, asteroid barrages,
enrage states, and cinematic destruction sequences.
"""

import math
import random
import pygame
from settings import (
    WIDTH, HEIGHT, RED, ORANGE, PURPLE, YELLOW, CYAN, WHITE, GREEN, MAGENTA,
    SCORE_BOSS, SCORE_FINAL_BOSS
)
from bullet import EnemyBullet, FastEnemyBullet, TrackingEnemyBullet


class Boss:
    """Base class for colossal boss starships."""
    def __init__(self, name, hp, score_value, width, height):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.score_value = score_value
        self.width = width
        self.height = height

        self.x = WIDTH // 2
        self.y = -height  # Start off-screen and descend
        self.target_y = 130
        self.vx = 2.0
        self.alive = True
        self.is_entering = True
        self.phase = 1
        self.hit_flash_timer = 0
        self.attack_timer = 0
        self.attack_mode = 0
        self.bullet_angle_offset = 0.0
        self.enraged = False
        self.rect = pygame.Rect(int(self.x - width // 2), int(self.y - height // 2), width, height)

    def take_damage(self, amount):
        """Apply damage, update phases, and trigger hit flash."""
        if self.is_entering:
            return False  # Invulnerable during entrance
        self.hp -= amount
        self.hit_flash_timer = 4
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def is_phase_two(self):
        return self.hp <= self.max_hp * 0.5


class SectorBoss(Boss):
    """Level 5 Sector Guardian Cruiser with 2 combat phases and varied bullet attacks."""
    def __init__(self, level=5, difficulty_mult=1.0):
        base_hp = int(1200 * difficulty_mult + (level - 5) * 400)
        super().__init__("SECTOR GUARDIAN", hp=base_hp, score_value=SCORE_BOSS, width=160, height=110)
        self.vx = 2.5

    def update(self, player, current_time, particle_system=None):
        # Entrance descent
        if self.is_entering:
            self.y += 2.0
            if self.y >= self.target_y:
                self.y = self.target_y
                self.is_entering = False
            self.rect.center = (int(self.x), int(self.y))
            return

        # Phase 2 Transition Check
        if not self.enraged and self.is_phase_two():
            self.enraged = True
            self.phase = 2
            self.vx = 3.8
            if particle_system:
                particle_system.create_shockwave(self.x, self.y, RED, max_radius=120, duration=35)
                particle_system.add_floating_text(self.x, self.y - 40, "PHASE 2: ENRAGED!", RED, font_size=24)

        # Horizontal patrol
        self.x += self.vx
        if self.x < self.width // 2 + 30:
            self.x = self.width // 2 + 30
            self.vx *= -1
        elif self.x > WIDTH - self.width // 2 - 30:
            self.x = WIDTH - self.width // 2 - 30
            self.vx *= -1

        self.rect.center = (int(self.x), int(self.y))
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        # Enrage smoke / fire particles
        if particle_system and self.enraged:
            if random.random() < 0.35:
                particle_system.create_explosion(
                    self.x + random.randint(-50, 50),
                    self.y + random.randint(-30, 30),
                    RED, count=6, speed_max=3.0, radius_max=2
                )

    def attack(self, player, current_time):
        """Generates bullet patterns based on attack mode and active phase."""
        if self.is_entering or not self.alive:
            return []

        self.attack_timer += 1
        bullets = []

        # Switch attack mode every 180 frames (~3 seconds)
        if self.attack_timer % 180 == 0:
            self.attack_mode = (self.attack_mode + 1) % 4

        # Attack 1: Straight rapid volleys from wing cannons
        if self.attack_mode == 0:
            if self.attack_timer % (18 if self.enraged else 26) == 0:
                bullets.append(EnemyBullet(self.x - 55, self.y + 40, vx=0, vy=7, damage=18, color=RED))
                bullets.append(EnemyBullet(self.x + 55, self.y + 40, vx=0, vy=7, damage=18, color=RED))

        # Attack 2: Triple / Quintuple spread shot
        elif self.attack_mode == 1:
            if self.attack_timer % (45 if self.enraged else 65) == 0:
                angles = [-0.4, -0.2, 0.0, 0.2, 0.4] if self.enraged else [-0.3, 0.0, 0.3]
                for ang in angles:
                    vx = math.sin(ang) * 5.5
                    vy = math.cos(ang) * 5.5
                    bullets.append(EnemyBullet(self.x, self.y + 50, vx=vx, vy=vy, damage=16, color=ORANGE))

        # Attack 3: Circular / spiral bullet hell
        elif self.attack_mode == 2:
            if self.attack_timer % (10 if self.enraged else 18) == 0:
                self.bullet_angle_offset += 0.35
                for i in range(4):
                    ang = self.bullet_angle_offset + (i * math.pi / 2)
                    vx = math.cos(ang) * 4.8
                    vy = math.sin(ang) * 4.8
                    bullets.append(EnemyBullet(self.x, self.y + 20, vx=vx, vy=vy, damage=15, color=PURPLE))

        # Attack 4: Homing missile + aimed fast snipes
        elif self.attack_mode == 3:
            if self.attack_timer % 50 == 0:
                if player and player.alive:
                    bullets.append(TrackingEnemyBullet(self.x, self.y + 35, player, speed=4.5, damage=22))
                bullets.append(FastEnemyBullet(self.x - 40, self.y + 30, vx=-1, vy=7, damage=18))
                bullets.append(FastEnemyBullet(self.x + 40, self.y + 30, vx=1, vy=7, damage=18))

        return bullets

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        # Colossal warship geometry
        pts = [
            (px, py + 55),
            (px + 45, py + 35),
            (px + 78, py + 15),
            (px + 80, py - 35),
            (px + 40, py - 52),
            (px, py - 35),
            (px - 40, py - 52),
            (px - 80, py - 35),
            (px - 78, py + 15),
            (px - 45, py + 35)
        ]

        main_color = (255, 60, 60) if self.enraged else (200, 40, 70)
        if self.hit_flash_timer > 0:
            main_color = WHITE

        # Main hull
        pygame.draw.polygon(surface, (35, 12, 22), pts)
        pygame.draw.polygon(surface, main_color, pts, 3)

        # Dual heavy weapon pods
        pod_left = (px - 55, py + 25)
        pod_right = (px + 55, py + 25)
        pygame.draw.circle(surface, (50, 15, 25), pod_left, 14)
        pygame.draw.circle(surface, main_color, pod_left, 14, 2)
        pygame.draw.circle(surface, (50, 15, 25), pod_right, 14)
        pygame.draw.circle(surface, main_color, pod_right, 14, 2)

        # Glowing central power reactor
        reactor_color = (255, 50, 50) if self.enraged else (255, 170, 0)
        pygame.draw.circle(surface, reactor_color, (px, py), 16)
        pygame.draw.circle(surface, WHITE, (px, py), 8)


class VoidDestroyer(Boss):
    """Epic Final Boss: VOID DESTROYER.
    Features 3 phases, devastating multi-spiral bullet patterns, seismic lasers,
    and heavy tracking salvos.
    """
    def __init__(self, difficulty_mult=1.0):
        super().__init__("VOID DESTROYER", hp=int(2600 * difficulty_mult), score_value=SCORE_FINAL_BOSS, width=220, height=140)
        self.target_y = 145
        self.vx = 2.0
        self.phase = 1
        self.spiral_step = 0

    def update(self, player, current_time, particle_system=None):
        if self.is_entering:
            self.y += 1.8
            if self.y >= self.target_y:
                self.y = self.target_y
                self.is_entering = False
            self.rect.center = (int(self.x), int(self.y))
            return

        # Multi-phase progression
        hp_ratio = self.hp / self.max_hp
        if hp_ratio <= 0.33 and self.phase < 3:
            self.phase = 3
            self.vx = 4.2
            if particle_system:
                particle_system.create_shockwave(self.x, self.y, MAGENTA, max_radius=180, duration=45)
                particle_system.add_floating_text(self.x, self.y - 50, "FINAL PHASE: VOID COLLAPSE!", MAGENTA, font_size=26)
        elif hp_ratio <= 0.66 and self.phase < 2:
            self.phase = 2
            self.vx = 3.0
            if particle_system:
                particle_system.create_shockwave(self.x, self.y, PURPLE, max_radius=140, duration=35)
                particle_system.add_floating_text(self.x, self.y - 50, "PHASE 2: MAXIMUM FIREPOWER!", PURPLE, font_size=24)

        # Sweeping movement
        self.x += self.vx
        if self.x < self.width // 2 + 25:
            self.x = self.width // 2 + 25
            self.vx *= -1
        elif self.x > WIDTH - self.width // 2 - 25:
            self.x = WIDTH - self.width // 2 - 25
            self.vx *= -1

        self.rect.center = (int(self.x), int(self.y))
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        if particle_system and self.phase >= 2:
            if random.random() < 0.4:
                p_color = MAGENTA if self.phase == 3 else PURPLE
                particle_system.create_explosion(
                    self.x + random.randint(-80, 80),
                    self.y + random.randint(-40, 40),
                    p_color, count=8, speed_max=3.5, radius_max=3
                )

    def attack(self, player, current_time):
        if self.is_entering or not self.alive:
            return []

        self.attack_timer += 1
        bullets = []

        # Phase 1: Quad-cannon streams & fan sweeps
        if self.phase == 1:
            if self.attack_timer % 20 == 0:
                bullets.append(EnemyBullet(self.x - 75, self.y + 45, vx=-0.5, vy=6.5, damage=18, color=MAGENTA))
                bullets.append(EnemyBullet(self.x - 30, self.y + 60, vx=0, vy=7.0, damage=20, color=MAGENTA))
                bullets.append(EnemyBullet(self.x + 30, self.y + 60, vx=0, vy=7.0, damage=20, color=MAGENTA))
                bullets.append(EnemyBullet(self.x + 75, self.y + 45, vx=0.5, vy=6.5, damage=18, color=MAGENTA))

            if self.attack_timer % 65 == 0:
                for ang in [-0.5, -0.25, 0.0, 0.25, 0.5]:
                    bullets.append(EnemyBullet(self.x, self.y + 65, vx=math.sin(ang) * 5.8, vy=math.cos(ang) * 5.8, damage=18, color=ORANGE))

        # Phase 2: Dual spiral storms + tracking missiles
        elif self.phase == 2:
            if self.attack_timer % 8 == 0:
                self.spiral_step += 0.32
                for i in range(3):
                    ang = self.spiral_step + (i * math.pi * 2 / 3)
                    bullets.append(EnemyBullet(self.x - 50, self.y + 35, vx=math.cos(ang) * 5.0, vy=math.sin(ang) * 5.0, damage=16, color=PURPLE))
                    bullets.append(EnemyBullet(self.x + 50, self.y + 35, vx=-math.cos(ang) * 5.0, vy=math.sin(ang) * 5.0, damage=16, color=CYAN))

            if self.attack_timer % 70 == 0 and player and player.alive:
                bullets.append(TrackingEnemyBullet(self.x - 80, self.y + 20, player, speed=4.8, damage=24))
                bullets.append(TrackingEnemyBullet(self.x + 80, self.y + 20, player, speed=4.8, damage=24))

        # Phase 3: Void Collapse (all-out bullet hell)
        elif self.phase == 3:
            if self.attack_timer % 6 == 0:
                self.spiral_step += 0.28
                for i in range(4):
                    ang = self.spiral_step + (i * math.pi / 2)
                    bullets.append(EnemyBullet(self.x, self.y + 45, vx=math.cos(ang) * 5.5, vy=math.sin(ang) * 5.5, damage=18, color=MAGENTA))

            if self.attack_timer % 32 == 0:
                # Fast aimed cluster
                if player and player.alive:
                    dx = player.x - self.x
                    dy = player.y - self.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        vx = (dx / dist) * 7.5
                        vy = (dy / dist) * 7.5
                        bullets.append(FastEnemyBullet(self.x - 40, self.y + 50, vx=vx, vy=vy, damage=22))
                        bullets.append(FastEnemyBullet(self.x + 40, self.y + 50, vx=vx, vy=vy, damage=22))

            if self.attack_timer % 80 == 0 and player and player.alive:
                bullets.append(TrackingEnemyBullet(self.x, self.y + 60, player, speed=5.2, damage=28))

        return bullets

    def draw(self, surface):
        if not self.alive:
            return
        px, py = int(self.x), int(self.y)
        # Giant mothership geometry
        pts = [
            (px, py + 70),
            (px + 50, py + 45),
            (px + 105, py + 25),
            (px + 110, py - 40),
            (px + 60, py - 70),
            (px, py - 45),
            (px - 60, py - 70),
            (px - 110, py - 40),
            (px - 105, py + 25),
            (px - 50, py + 45)
        ]

        main_color = (255, 0, 180) if self.phase == 3 else ((180, 50, 255) if self.phase == 2 else (130, 20, 220))
        if self.hit_flash_timer > 0:
            main_color = WHITE

        pygame.draw.polygon(surface, (20, 8, 30), pts)
        pygame.draw.polygon(surface, main_color, pts, 4)

        # Heavy armor wings
        pygame.draw.line(surface, main_color, (px - 90, py), (px + 90, py), 3)

        # Dual massive plasma pods
        pygame.draw.circle(surface, (40, 12, 50), (px - 75, py + 25), 18)
        pygame.draw.circle(surface, main_color, (px - 75, py + 25), 18, 2)
        pygame.draw.circle(surface, (40, 12, 50), (px + 75, py + 25), 18)
        pygame.draw.circle(surface, main_color, (px + 75, py + 25), 18, 2)

        # Central Pulsing Void Core
        pulse_r = int(20 + 4 * math.sin(self.attack_timer * 0.1))
        core_color = MAGENTA if self.phase == 3 else PURPLE
        pygame.draw.circle(surface, core_color, (px, py), pulse_r)
        pygame.draw.circle(surface, WHITE, (px, py), pulse_r // 2)
