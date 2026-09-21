"""
NEBULA STRIKE - Player Spaceship
Handles player input, smooth movement, screen boundaries, combat systems,
shields, lives, power-ups, glowing engine trails, and procedural spaceship rendering.
"""

import math
import pygame
from settings import (
    WIDTH, HEIGHT, CYAN, WHITE, YELLOW,
    MAGENTA, GREEN, RED, PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_MAX_SHIELD,
    PLAYER_INITIAL_LIVES, PLAYER_SHOOT_COOLDOWN, PLAYER_RAPID_COOLDOWN,
    PLAYER_INVINCIBILITY_TIME, POWERUP_DURATION_SHIELD, POWERUP_DURATION_RAPID,
    POWERUP_DURATION_DOUBLE, POWERUP_DURATION_LASER
)
from bullet import PlayerBullet, LaserBeam


class Player:
    """The player-controlled futuristic combat starfighter."""
    def __init__(self, x=WIDTH // 2, y=HEIGHT - 120):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = PLAYER_SPEED
        self.width = 48
        self.height = 54
        self.rect = pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)

        # Combat & Health Stats
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.max_shield = PLAYER_MAX_SHIELD
        self.shield = self.max_shield
        self.lives = PLAYER_INITIAL_LIVES
        self.alive = True

        # Timers & Cooldowns (milliseconds)
        self.last_shot_time = 0
        self.invincible_until = 0
        self.shield_recharge_cooldown = 0

        # Power-Up Status Timers (seconds remaining)
        self.powerups = {
            "shield": 0.0,
            "rapid_fire": 0.0,
            "double_shot": 0.0,
            "laser": 0.0
        }

        # Visuals & Animation
        self.tilt = 0.0  # -1.0 (left) to 1.0 (right)
        self.engine_timer = 0
        self.shield_pulse = 0.0

    def handle_input(self, keys):
        """Process keyboard inputs (WASD and Arrow keys)."""
        move_x = 0
        move_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        # Normalize diagonal movement speed
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        # Smooth velocity interpolation
        target_vx = move_x * self.speed
        target_vy = move_y * self.speed
        self.vx += (target_vx - self.vx) * 0.35
        self.vy += (target_vy - self.vy) * 0.35

        # Banking tilt for left/right turns
        target_tilt = 0.0
        if move_x < -0.1:
            target_tilt = -1.0
        elif move_x > 0.1:
            target_tilt = 1.0
        self.tilt += (target_tilt - self.tilt) * 0.25

    def update(self, dt_sec, particle_system=None):
        """Update position, bounds, timers, and particle trails."""
        # Update coordinates
        self.x += self.vx
        self.y += self.vy

        # Screen Boundary Enforcement (clamping with margin)
        half_w = self.width // 2
        half_h = self.height // 2
        margin = 10
        self.x = max(half_w + margin, min(WIDTH - half_w - margin, self.x))
        self.y = max(half_h + margin, min(HEIGHT - half_h - margin, self.y))
        self.rect.center = (int(self.x), int(self.y))

        # Update Power-Up timers
        for power_name in list(self.powerups.keys()):
            if self.powerups[power_name] > 0:
                self.powerups[power_name] = max(0.0, self.powerups[power_name] - dt_sec)

        # Passive shield recharge if shield power-up or after cooldown
        current_time = pygame.time.get_ticks()
        if self.powerups["shield"] > 0:
            self.shield = self.max_shield
        elif current_time > self.shield_recharge_cooldown and self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + 12 * dt_sec)

        # Thruster particle exhaust
        if particle_system and self.alive:
            self.engine_timer += 1
            if self.engine_timer % 2 == 0:
                # Left engine
                lx = self.x - 12 + self.tilt * 3
                ly = self.y + 22
                particle_system.create_thruster_trail(lx, ly, direction_deg=90, color=CYAN, speed=4.0)
                # Right engine
                rx = self.x + 12 - self.tilt * 3
                ry = self.y + 22
                particle_system.create_thruster_trail(rx, ry, direction_deg=90, color=CYAN, speed=4.0)

        # Shield pulse animation
        self.shield_pulse = (self.shield_pulse + dt_sec * 4) % (math.pi * 2)

    def can_shoot(self, current_time):
        """Check if firing cooldown has elapsed."""
        cooldown = PLAYER_RAPID_COOLDOWN if self.powerups["rapid_fire"] > 0 else PLAYER_SHOOT_COOLDOWN
        return current_time - self.last_shot_time >= cooldown

    def shoot(self, current_time):
        """Generates bullet(s) based on active power-ups."""
        if not self.can_shoot(current_time):
            return []

        self.last_shot_time = current_time
        bullets = []

        if self.powerups["laser"] > 0:
            # High-damage piercing laser beam
            bullets.append(LaserBeam(self.x, self.y - 25))
        elif self.powerups["double_shot"] > 0:
            # Twin cannons
            bullets.append(PlayerBullet(self.x - 16, self.y - 12, is_double=True))
            bullets.append(PlayerBullet(self.x + 16, self.y - 12, is_double=True))
        else:
            # Standard single laser
            bullets.append(PlayerBullet(self.x, self.y - 25))

        return bullets

    def take_damage(self, amount, current_time, particle_system=None):
        """Apply damage prioritizing shield, then HP with invincibility period."""
        if current_time < self.invincible_until or not self.alive:
            return False

        # Shield absorbs damage first
        if self.shield > 0:
            absorbed = min(self.shield, amount)
            self.shield -= absorbed
            amount -= absorbed
            self.shield_recharge_cooldown = current_time + 4000  # 4s recharge delay
            if particle_system:
                particle_system.create_shockwave(self.x, self.y, (0, 200, 255), max_radius=40, duration=15)

        if amount > 0:
            self.hp -= amount
            self.invincible_until = current_time + PLAYER_INVINCIBILITY_TIME
            if particle_system:
                particle_system.create_explosion(self.x, self.y, RED, count=16, speed_max=5)

            if self.hp <= 0:
                self.hp = 0
                return True  # Player killed
        return False

    def lose_life(self):
        """Deduct a life and reset position/health if lives remain."""
        self.lives -= 1
        if self.lives > 0:
            self.respawn()
        else:
            self.alive = False

    def respawn(self):
        """Reset player state after losing a life."""
        self.x = WIDTH // 2
        self.y = HEIGHT - 120
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.max_hp
        self.shield = self.max_shield
        self.invincible_until = pygame.time.get_ticks() + 3000
        # Reset offensive powerups on death
        self.powerups["rapid_fire"] = 0.0
        self.powerups["double_shot"] = 0.0
        self.powerups["laser"] = 0.0
        self.powerups["shield"] = 0.0

    def apply_powerup(self, powerup_type):
        """Activate power-up effects."""
        if powerup_type == "shield":
            self.powerups["shield"] = POWERUP_DURATION_SHIELD
            self.shield = self.max_shield
        elif powerup_type == "rapid_fire":
            self.powerups["rapid_fire"] = POWERUP_DURATION_RAPID
        elif powerup_type == "double_shot":
            self.powerups["double_shot"] = POWERUP_DURATION_DOUBLE
        elif powerup_type == "laser":
            self.powerups["laser"] = POWERUP_DURATION_LASER
        elif powerup_type == "health":
            self.hp = min(self.max_hp, self.hp + 40)

    def draw(self, surface):
        """Render the sleek futuristic spaceship with banking tilt and glowing cockpit."""
        if not self.alive:
            return

        current_time = pygame.time.get_ticks()
        # Invincibility flashing
        if current_time < self.invincible_until:
            if (current_time // 100) % 2 == 0:
                return  # Skip drawing frame for flashing effect

        # Render Active Energy Shield Dome
        if self.shield > 0 or self.powerups["shield"] > 0:
            shield_radius = int(self.height * 0.68)
            pulse_alpha = int(45 + 25 * math.sin(self.shield_pulse))
            if self.powerups["shield"] > 0:
                pulse_alpha = int(80 + 35 * math.sin(self.shield_pulse * 2))

            shield_surf = pygame.Surface((shield_radius * 2 + 8, shield_radius * 2 + 8), pygame.SRCALPHA)
            s_color = (0, 240, 255, pulse_alpha)
            pygame.draw.circle(shield_surf, s_color, (shield_radius + 4, shield_radius + 4), shield_radius)
            pygame.draw.circle(shield_surf, (150, 255, 255, pulse_alpha + 50), (shield_radius + 4, shield_radius + 4), shield_radius, 2)
            surface.blit(shield_surf, (int(self.x - shield_radius - 4), int(self.y - shield_radius - 4)), special_flags=pygame.BLEND_ADD)

        # Procedural Spaceship Geometry with banking offset
        px, py = int(self.x), int(self.y)
        tilt_px = int(self.tilt * 6)

        # Outer Wings / Body
        nose = (px, py - 26)
        left_wing = (px - 22 + tilt_px, py + 18)
        left_intake = (px - 10, py + 12)
        tail_left = (px - 8, py + 22)
        engine_mid = (px, py + 16)
        tail_right = (px + 8, py + 22)
        right_intake = (px + 10, py + 12)
        right_wing = (px + 22 + tilt_px, py + 18)

        # Main hull polygon
        hull_points = [nose, right_wing, right_intake, tail_right, engine_mid, tail_left, left_intake, left_wing]
        pygame.draw.polygon(surface, (25, 35, 60), hull_points)
        pygame.draw.polygon(surface, CYAN, hull_points, 2)

        # Wing glow accents
        pygame.draw.line(surface, (0, 255, 240), nose, right_wing, 2)
        pygame.draw.line(surface, (0, 255, 240), nose, left_wing, 2)

        # Cockpit canopy (glowing cyan glass)
        cockpit_points = [
            (px, py - 18),
            (px + 4 + tilt_px // 2, py - 2),
            (px, py + 5),
            (px - 4 + tilt_px // 2, py - 2)
        ]
        pygame.draw.polygon(surface, (0, 240, 255), cockpit_points)
        pygame.draw.polygon(surface, WHITE, cockpit_points, 1)

        # Dual weapon pods on wingtips
        wp_left = (px - 18 + tilt_px, py + 4)
        wp_right = (px + 18 + tilt_px, py + 4)
        pygame.draw.circle(surface, (180, 230, 255), wp_left, 3)
        pygame.draw.circle(surface, (180, 230, 255), wp_right, 3)
