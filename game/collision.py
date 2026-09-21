"""
NEBULA STRIKE - Centralized Collision System
Handles all intersection checks and damage resolution between players, bullets,
asteroids, enemies, bosses, and collectible power-ups.
"""

import random
import pygame
from settings import (
    POWERUP_DROP_CHANCE, WHITE, YELLOW, CYAN, RED, GREEN, MAGENTA, ORANGE
)
from powerup import PowerUp


class CollisionManager:
    """Detects and resolves all combat interactions."""
    def __init__(self, game):
        self.game = game

    def update(self):
        player = self.game.player
        particles = self.game.particle_system
        sounds = self.game.sound_manager
        current_time = pygame.time.get_ticks()

        # 1. PLAYER BULLETS VS ASTEROIDS
        for bullet in list(self.game.player_bullets):
            if not bullet.alive:
                continue
            for asteroid in list(self.game.asteroids):
                if not asteroid.alive:
                    continue
                if bullet.rect.colliderect(asteroid.rect):
                    # Damage asteroid
                    is_destroyed = asteroid.take_damage(bullet.damage)
                    particles.create_hit_spark(bullet.x, bullet.y, WHITE, count=4)
                    sounds.play("hit")

                    if not getattr(bullet, "piercing", False):
                        bullet.alive = False

                    if is_destroyed:
                        # Asteroid destroyed
                        self.game.add_score(asteroid.score_value)
                        particles.create_asteroid_debris(asteroid.x, asteroid.y, count=14)
                        sounds.play("explosion")

                        # Split asteroid
                        new_pieces = asteroid.split()
                        self.game.asteroids.extend(new_pieces)

                        # Drop powerup
                        if random.random() < POWERUP_DROP_CHANCE:
                            self.game.powerups.append(PowerUp(asteroid.x, asteroid.y))
                    break

        # 2. PLAYER BULLETS VS ENEMIES
        for bullet in list(self.game.player_bullets):
            if not bullet.alive:
                continue
            for enemy in list(self.game.enemies):
                if not enemy.alive:
                    continue
                if bullet.rect.colliderect(enemy.rect):
                    is_destroyed = enemy.take_damage(bullet.damage)
                    particles.create_hit_spark(bullet.x, bullet.y, WHITE, count=5)
                    sounds.play("hit")

                    if not getattr(bullet, "piercing", False):
                        bullet.alive = False

                    if is_destroyed:
                        self.game.add_score(enemy.score_value)
                        particles.create_explosion(enemy.x, enemy.y, ORANGE, count=24, speed_max=6.5)
                        particles.add_floating_text(enemy.x, enemy.y, f"+{enemy.score_value}", YELLOW)
                        sounds.play("explosion")
                        self.game.trigger_screen_shake(6)

                        if random.random() < POWERUP_DROP_CHANCE:
                            self.game.powerups.append(PowerUp(enemy.x, enemy.y))
                    break

        # 3. PLAYER BULLETS VS BOSS
        if self.game.boss and self.game.boss.alive and not self.game.boss.is_entering:
            boss = self.game.boss
            for bullet in list(self.game.player_bullets):
                if not bullet.alive:
                    continue
                if bullet.rect.colliderect(boss.rect):
                    is_destroyed = boss.take_damage(bullet.damage)
                    particles.create_hit_spark(bullet.x, bullet.y, (255, 200, 100), count=6)
                    sounds.play("hit")

                    if not getattr(bullet, "piercing", False):
                        bullet.alive = False

                    if is_destroyed:
                        self.game.add_score(boss.score_value)
                        # Cascading boss destruction sequence
                        for _ in range(12):
                            rx = boss.x + random.randint(-boss.width // 2, boss.width // 2)
                            ry = boss.y + random.randint(-boss.height // 2, boss.height // 2)
                            particles.create_explosion(rx, ry, random.choice([RED, ORANGE, MAGENTA]), count=32, speed_max=9.0)

                        particles.add_floating_text(boss.x, boss.y, f"+{boss.score_value} BOSS DESTROYED!", YELLOW, font_size=28)
                        sounds.play("explosion")
                        self.game.trigger_screen_shake(18)
                        self.game.on_boss_defeated()
                    break

        # If player is not alive or currently respawning, skip player collision checks
        if not player.alive:
            return

        # 4. ENEMY BULLETS VS PLAYER
        for bullet in list(self.game.enemy_bullets):
            if not bullet.alive:
                continue
            if bullet.rect.colliderect(player.rect):
                bullet.alive = False
                died = player.take_damage(bullet.damage, current_time, particles)
                sounds.play("player_damage")
                self.game.trigger_screen_shake(8)

                if died:
                    self._handle_player_death(player, particles, sounds)
                break

        # 5. ASTEROIDS VS PLAYER (Ramming Collision)
        for asteroid in list(self.game.asteroids):
            if not asteroid.alive:
                continue
            if asteroid.rect.colliderect(player.rect):
                asteroid.alive = False
                particles.create_asteroid_debris(asteroid.x, asteroid.y, count=18)
                sounds.play("explosion")
                died = player.take_damage(40, current_time, particles)
                sounds.play("player_damage")
                self.game.trigger_screen_shake(12)

                if died:
                    self._handle_player_death(player, particles, sounds)
                break

        # 6. ENEMIES VS PLAYER (Ship Crash)
        for enemy in list(self.game.enemies):
            if not enemy.alive:
                continue
            if enemy.rect.colliderect(player.rect):
                enemy.alive = False
                particles.create_explosion(enemy.x, enemy.y, ORANGE, count=22)
                sounds.play("explosion")
                died = player.take_damage(50, current_time, particles)
                sounds.play("player_damage")
                self.game.trigger_screen_shake(14)

                if died:
                    self._handle_player_death(player, particles, sounds)
                break

        # 7. PLAYER VS POWER-UPS
        for powerup in list(self.game.powerups):
            if not powerup.alive:
                continue
            if powerup.rect.colliderect(player.rect):
                powerup.alive = False
                player.apply_powerup(powerup.powerup_type)
                sounds.play("powerup")

                label = PowerUp.LABELS.get(powerup.powerup_type, "BUFF")
                color = PowerUp.COLORS.get(powerup.powerup_type, YELLOW)
                particles.add_floating_text(player.x, player.y - 30, f"{label}!", color, font_size=22)
                particles.create_shockwave(player.x, player.y, color, max_radius=50, duration=18)

    def _handle_player_death(self, player, particles, sounds):
        """Execute player destruction sequence and decrement lives."""
        particles.create_explosion(player.x, player.y, CYAN, count=36, speed_max=8.5)
        sounds.play("explosion")
        self.game.trigger_screen_shake(16)
        player.lose_life()
        if not player.alive:
            self.game.on_game_over()
