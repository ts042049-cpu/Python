"""
NEBULA STRIKE - Core Game Engine & State Machine
Coordinates game loop, states, audio synthesis fallback, level progression,
procedural wave spawning, screen shake, and local persistence.
"""

import os
import math
import struct
import wave
import random
import datetime
import pygame

from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BG_COLOR, CYAN, MAGENTA, RED, YELLOW, WHITE,
    GREEN, ORANGE, PURPLE, GRAY,
    load_settings, save_settings, load_highscores, save_highscores,
    DIFFICULTY_PRESETS, SOUNDS_DIR
)
from starfield import Starfield
from particles import ParticleSystem
from player import Player
from asteroid import Asteroid
from enemy import Scout, Fighter, Tank, Hunter
from boss import SectorBoss, VoidDestroyer
from collision import CollisionManager
from ui import UI, Button


class SoundManager:
    """Manages sound effects and procedural retro audio synthesis."""
    def __init__(self, settings_data):
        self.settings = settings_data
        self.sounds = {}
        self.mixer_initialized = False

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
        except Exception as e:
            print(f"Audio Warning: Mixer failed to initialize: {e}")

        if self.mixer_initialized:
            self._ensure_sound_effects()

    def _ensure_sound_effects(self):
        """Loads WAV files from disk or synthesizes retro arcade WAVs using pure Python."""
        sound_names = ["shoot", "explosion", "hit", "powerup", "boss_warning", "player_damage", "game_over"]
        for name in sound_names:
            wav_path = os.path.join(SOUNDS_DIR, f"{name}.wav")
            if not os.path.exists(wav_path):
                self._synthesize_retro_wav(name, wav_path)

            if os.path.exists(wav_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(wav_path)
                    self.sounds[name].set_volume(0.4)
                except Exception as e:
                    print(f"Could not load sound {name}: {e}")

    def _synthesize_retro_wav(self, name, filepath):
        """Synthesizes retro 8-bit/16-bit sound effects using pure standard library wave & math."""
        sample_rate = 22050
        samples = []

        if name == "shoot":
            # Fast downward frequency laser sweep
            duration = 0.14
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 950 - (t / duration) * 650
                val = math.sin(2 * math.pi * freq * t)
                # Exponential decay envelope
                val *= math.exp(-t * 16)
                samples.append(int(val * 16000))

        elif name == "explosion":
            # Noise burst with exponential decay
            duration = 0.45
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                noise = random.uniform(-1.0, 1.0)
                env = math.exp(-t * 7.5)
                samples.append(int(noise * env * 18000))

        elif name == "hit":
            # Short metallic click
            duration = 0.06
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 600 + random.uniform(-50, 50)
                val = math.sin(2 * math.pi * freq * t) * math.exp(-t * 50)
                samples.append(int(val * 14000))

        elif name == "powerup":
            # Ascending 3-note chime arpeggio
            duration = 0.32
            num_samples = int(sample_rate * duration)
            notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
            for i in range(num_samples):
                t = i / sample_rate
                note_idx = min(len(notes) - 1, int((t / duration) * len(notes)))
                freq = notes[note_idx]
                val = math.sin(2 * math.pi * freq * t) * 0.8
                samples.append(int(val * 15000))

        elif name == "boss_warning":
            # Pulsing low siren alarm
            duration = 0.6
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 280 + 120 * math.sin(2 * math.pi * 5 * t)
                val = math.sin(2 * math.pi * freq * t)
                samples.append(int(val * 17000))

        elif name == "player_damage":
            # Heavy impact buzz
            duration = 0.22
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 140 - (t / duration) * 50
                noise = random.uniform(-0.3, 0.3)
                val = (math.sin(2 * math.pi * freq * t) + noise) * math.exp(-t * 12)
                samples.append(int(val * 19000))

        elif name == "game_over":
            # Descending sad tone
            duration = 0.7
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 420 - (t / duration) * 260
                val = math.sin(2 * math.pi * freq * t) * math.exp(-t * 3.5)
                samples.append(int(val * 15000))

        try:
            with wave.open(filepath, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                raw_data = struct.pack(f"<{len(samples)}h", *samples)
                wav_file.writeframes(raw_data)
        except Exception as e:
            print(f"Failed to write synthesized sound {name}: {e}")

    def play(self, sound_name):
        """Safely trigger sound effect if SFX is enabled."""
        if not self.settings.get("sfx_on", True) or not self.mixer_initialized:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass


class Game:
    """Master controller for NEBULA STRIKE."""
    STATE_MENU = "MENU"
    STATE_PLAYING = "PLAYING"
    STATE_PAUSED = "PAUSED"
    STATE_BOSS = "BOSS_FIGHT"
    STATE_GAME_OVER = "GAME_OVER"
    STATE_VICTORY = "VICTORY"
    STATE_SETTINGS = "SETTINGS"
    STATE_HIGHSCORES = "HIGH_SCORES"

    def __init__(self, headless=False):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        self.headless = headless
        if not self.headless:
            pygame.display.set_caption(TITLE)
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        else:
            self.screen = pygame.Surface((WIDTH, HEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True

        # Systems & Managers
        self.settings = load_settings()
        self.highscores = load_highscores()
        self.sound_manager = SoundManager(self.settings)
        self.starfield = Starfield(WIDTH, HEIGHT)
        self.particle_system = ParticleSystem()
        self.collision_manager = CollisionManager(self)
        self.ui = UI(self)

        # Game State
        self.state = self.STATE_MENU
        self.score = 0
        self.level = 1
        self.level_transition_timer = 0
        self.screen_shake = 0.0

        # Entity Collections
        self.player = None
        self.player_bullets = []
        self.enemy_bullets = []
        self.asteroids = []
        self.enemies = []
        self.boss = None
        self.powerups = []

        # Wave Spawning Parameters
        self.wave_timer = 0
        self.spawn_interval = 100
        self.level_enemies_defeated = 0
        self.level_enemies_needed = 15

        # Initialize Menus
        self._init_menu_buttons()

    def _init_menu_buttons(self):
        """Create buttons for all menu states."""
        btn_w, btn_h = 240, 52
        cx = (WIDTH - btn_w) // 2

        # Main Menu
        self.menu_buttons = [
            Button(cx, 310, btn_w, btn_h, "▶  PLAY", 22, CYAN, WHITE),
            Button(cx, 380, btn_w, btn_h, "⚙  SETTINGS", 22, CYAN, WHITE),
            Button(cx, 450, btn_w, btn_h, "🏆  HIGH SCORES", 22, CYAN, WHITE),
            Button(cx, 520, btn_w, btn_h, "❌  EXIT", 22, RED, WHITE)
        ]

        # Pause Menu
        self.pause_buttons = [
            Button(cx, 280, btn_w, btn_h, "▶  RESUME", 22, CYAN, WHITE),
            Button(cx, 350, btn_w, btn_h, "⚙  SETTINGS", 22, CYAN, WHITE),
            Button(cx, 420, btn_w, btn_h, "🏠  MAIN MENU", 22, MAGENTA, WHITE)
        ]

        # Game Over Menu
        self.game_over_buttons = [
            Button(cx, 370, btn_w, btn_h, "▶  PLAY AGAIN", 22, GREEN, WHITE),
            Button(cx, 440, btn_w, btn_h, "🏠  MAIN MENU", 22, CYAN, WHITE)
        ]

        # Victory Menu
        self.victory_buttons = [
            Button(cx, 360, btn_w, btn_h, "▶  PLAY AGAIN", 22, GREEN, WHITE),
            Button(cx, 430, btn_w, btn_h, "🏠  MAIN MENU", 22, CYAN, WHITE)
        ]

        # Settings Menu
        self.settings_buttons = [
            Button(cx, 480, btn_w, btn_h, "TOGGLE MUSIC", 18, CYAN, WHITE),
            Button(cx, 545, btn_w, btn_h, "TOGGLE SFX", 18, CYAN, WHITE),
            Button(cx, 610, btn_w, btn_h, "TOGGLE SHAKE", 18, CYAN, WHITE),
            Button(cx - 130, 610, 120, btn_h, "DIFFICULTY", 18, YELLOW, WHITE),
            Button(cx + 250, 610, 120, btn_h, "◀  BACK", 18, MAGENTA, WHITE)
        ]

        # High Scores Menu
        self.highscore_buttons = [
            Button(cx, 580, btn_w, btn_h, "◀  BACK", 22, MAGENTA, WHITE)
        ]

    def reset_game(self):
        """Reset all game variables to start fresh from Level 1."""
        self.score = 0
        self.level = 1
        self.player = Player()
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.asteroids.clear()
        self.enemies.clear()
        self.boss = None
        self.powerups.clear()
        self.particle_system.clear()

        self.level_enemies_defeated = 0
        self.level_enemies_needed = 12
        self.spawn_interval = 90
        self.level_transition_timer = 120  # Show "LEVEL 1" banner
        self.state = self.STATE_PLAYING

    def add_score(self, points):
        """Add points to score."""
        self.score += points

    def trigger_screen_shake(self, intensity=10):
        """Triggers trauma for screen shake effect."""
        if self.settings.get("screen_shake", True):
            self.screen_shake = min(22.0, self.screen_shake + intensity)

    def on_boss_defeated(self):
        """Handles sector boss or final boss defeat."""
        if self.boss and isinstance(self.boss, VoidDestroyer):
            # Final Boss beaten!
            self.state = self.STATE_VICTORY
            self._record_high_score()
        else:
            # Sector Boss beaten -> Advance to next level
            self.boss = None
            self.level += 1
            self.level_enemies_defeated = 0
            self.level_enemies_needed = 12 + self.level * 3
            self.level_transition_timer = 120
            self.state = self.STATE_PLAYING

    def on_game_over(self):
        """Triggers Game Over state and records high score."""
        self.state = self.STATE_GAME_OVER
        self.sound_manager.play("game_over")
        self._record_high_score()

    def _record_high_score(self):
        """Appends new score entry and saves to JSON."""
        today = datetime.date.today().isoformat()
        entry = {"score": self.score, "level": self.level, "date": today}
        self.highscores.append(entry)
        self.highscores = sorted(self.highscores, key=lambda x: x.get("score", 0), reverse=True)[:10]
        save_highscores(self.highscores)

    def spawn_wave(self):
        """Spawns enemies and asteroids based on current level & difficulty."""
        diff_name = self.settings.get("difficulty", "NORMAL")
        preset = DIFFICULTY_PRESETS.get(diff_name, DIFFICULTY_PRESETS["NORMAL"])
        hp_m = preset["hp_mult"]
        spd_m = preset["speed_mult"]

        # Level 1: Asteroids only
        if self.level == 1:
            self.asteroids.append(Asteroid())

        # Level 2: Asteroids + Scouts
        elif self.level == 2:
            if random.random() < 0.5:
                self.asteroids.append(Asteroid())
            else:
                self.enemies.append(Scout(speed_mult=spd_m, hp_mult=hp_m))

        # Level 3: Scouts + Fighters
        elif self.level == 3:
            choice = random.random()
            if choice < 0.4:
                self.asteroids.append(Asteroid())
            elif choice < 0.7:
                self.enemies.append(Scout(speed_mult=spd_m, hp_mult=hp_m))
            else:
                self.enemies.append(Fighter(speed_mult=spd_m, hp_mult=hp_m))

        # Level 4: Fighters + Tanks + Hunters
        elif self.level == 4:
            choice = random.random()
            if choice < 0.25:
                self.asteroids.append(Asteroid())
            elif choice < 0.5:
                self.enemies.append(Fighter(speed_mult=spd_m, hp_mult=hp_m))
            elif choice < 0.75:
                self.enemies.append(Tank(speed_mult=spd_m, hp_mult=hp_m))
            else:
                self.enemies.append(Hunter(speed_mult=spd_m, hp_mult=hp_m))

        # Level 5: Boss Fight
        elif self.level == 5:
            if not self.boss:
                self.boss = SectorBoss(level=5, difficulty_mult=hp_m)
                self.sound_manager.play("boss_warning")
                self.state = self.STATE_BOSS

        # Level 6-9: All enemy types with scaling density
        elif 6 <= self.level < 10:
            choice = random.random()
            if choice < 0.2:
                self.asteroids.append(Asteroid())
            elif choice < 0.4:
                self.enemies.append(Scout(speed_mult=spd_m * 1.1, hp_mult=hp_m * 1.1))
            elif choice < 0.65:
                self.enemies.append(Fighter(speed_mult=spd_m * 1.1, hp_mult=hp_m * 1.1))
            elif choice < 0.85:
                self.enemies.append(Hunter(speed_mult=spd_m * 1.1, hp_mult=hp_m * 1.1))
            else:
                self.enemies.append(Tank(speed_mult=spd_m * 1.1, hp_mult=hp_m * 1.1))

        # Level 10: Epic Final Boss VOID DESTROYER
        elif self.level >= 10:
            if not self.boss:
                self.boss = VoidDestroyer(difficulty_mult=hp_m)
                self.sound_manager.play("boss_warning")
                self.state = self.STATE_BOSS

    def handle_events(self):
        """Process keyboard, mouse, and system events."""
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.VIDEORESIZE and not self.headless:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.state in [self.STATE_PLAYING, self.STATE_BOSS]:
                    self.state = self.STATE_PAUSED
                elif event.key == pygame.K_p and self.state == self.STATE_PAUSED:
                    self.state = self.STATE_PLAYING if not self.boss else self.STATE_BOSS
                elif event.key == pygame.K_ESCAPE:
                    if self.state in [self.STATE_PLAYING, self.STATE_BOSS]:
                        self.state = self.STATE_PAUSED
                    elif self.state in [self.STATE_SETTINGS, self.STATE_HIGHSCORES]:
                        self.state = self.STATE_MENU

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(mouse_pos)

    def _handle_click(self, mouse_pos):
        """Dispatches mouse click to active state buttons."""
        if self.state == self.STATE_MENU:
            if self.menu_buttons[0].rect.collidepoint(mouse_pos):
                self.reset_game()
            elif self.menu_buttons[1].rect.collidepoint(mouse_pos):
                self.state = self.STATE_SETTINGS
            elif self.menu_buttons[2].rect.collidepoint(mouse_pos):
                self.state = self.STATE_HIGHSCORES
            elif self.menu_buttons[3].rect.collidepoint(mouse_pos):
                self.running = False

        elif self.state == self.STATE_PAUSED:
            if self.pause_buttons[0].rect.collidepoint(mouse_pos):
                self.state = self.STATE_PLAYING if not self.boss else self.STATE_BOSS
            elif self.pause_buttons[1].rect.collidepoint(mouse_pos):
                self.state = self.STATE_SETTINGS
            elif self.pause_buttons[2].rect.collidepoint(mouse_pos):
                self.state = self.STATE_MENU

        elif self.state == self.STATE_GAME_OVER:
            if self.game_over_buttons[0].rect.collidepoint(mouse_pos):
                self.reset_game()
            elif self.game_over_buttons[1].rect.collidepoint(mouse_pos):
                self.state = self.STATE_MENU

        elif self.state == self.STATE_VICTORY:
            if self.victory_buttons[0].rect.collidepoint(mouse_pos):
                self.reset_game()
            elif self.victory_buttons[1].rect.collidepoint(mouse_pos):
                self.state = self.STATE_MENU

        elif self.state == self.STATE_SETTINGS:
            # Toggle Music
            if self.settings_buttons[0].rect.collidepoint(mouse_pos):
                self.settings["music_on"] = not self.settings.get("music_on", True)
                save_settings(self.settings)
            # Toggle SFX
            elif self.settings_buttons[1].rect.collidepoint(mouse_pos):
                self.settings["sfx_on"] = not self.settings.get("sfx_on", True)
                save_settings(self.settings)
            # Toggle Screen Shake
            elif self.settings_buttons[2].rect.collidepoint(mouse_pos):
                self.settings["screen_shake"] = not self.settings.get("screen_shake", True)
                save_settings(self.settings)
            # Toggle Difficulty
            elif self.settings_buttons[3].rect.collidepoint(mouse_pos):
                curr = self.settings.get("difficulty", "NORMAL")
                cycle = {"EASY": "NORMAL", "NORMAL": "HARD", "HARD": "EASY"}
                self.settings["difficulty"] = cycle.get(curr, "NORMAL")
                save_settings(self.settings)
            # Back
            elif self.settings_buttons[4].rect.collidepoint(mouse_pos):
                self.state = self.STATE_MENU

        elif self.state == self.STATE_HIGHSCORES:
            if self.highscore_buttons[0].rect.collidepoint(mouse_pos):
                self.state = self.STATE_MENU

    def update(self, dt_sec):
        """Update game world, entities, physics, and collisions."""
        current_time = pygame.time.get_ticks()

        # Update Starfield & Particles (always active for background ambiance)
        star_spd = 2.0 if self.state in [self.STATE_PLAYING, self.STATE_BOSS] else 1.0
        self.starfield.update(dt_sec, speed_mult=star_spd)
        self.particle_system.update()
        self.ui.update(dt_sec)

        # Screen shake decay
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - 35 * dt_sec)

        # Gameplay Updates
        if self.state in [self.STATE_PLAYING, self.STATE_BOSS]:
            # Level transition banner timer
            if self.level_transition_timer > 0:
                self.level_transition_timer -= 1

            # Player Input & Shooting
            keys = pygame.key.get_pressed()
            if self.player and self.player.alive:
                self.player.handle_input(keys)
                self.player.update(dt_sec, self.particle_system)

                # Shooting
                if keys[pygame.K_SPACE]:
                    new_bullets = self.player.shoot(current_time)
                    if new_bullets:
                        self.player_bullets.extend(new_bullets)
                        self.sound_manager.play("shoot")

            # Update Projectiles
            for b in self.player_bullets:
                b.update()
            self.player_bullets = [b for b in self.player_bullets if b.alive]

            for eb in self.enemy_bullets:
                eb.update()
            self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

            # Update Asteroids
            for a in self.asteroids:
                a.update()
            self.asteroids = [a for a in self.asteroids if a.alive]

            # Update Enemies
            for enemy in self.enemies:
                enemy.update(self.player, current_time, self.particle_system)
                # Enemy shooting
                new_ebs = enemy.shoot(current_time, self.player)
                if new_ebs:
                    self.enemy_bullets.extend(new_ebs)
            self.enemies = [e for e in self.enemies if e.alive]

            # Update Boss
            if self.boss and self.boss.alive:
                self.boss.update(self.player, current_time, self.particle_system)
                boss_bullets = self.boss.attack(self.player, current_time)
                if boss_bullets:
                    self.enemy_bullets.extend(boss_bullets)

            # Update Power-ups
            for pu in self.powerups:
                pu.update(dt_sec)
            self.powerups = [pu for pu in self.powerups if pu.alive]

            # Wave Spawner
            if self.state == self.STATE_PLAYING:
                self.wave_timer += 1
                if self.wave_timer >= self.spawn_interval:
                    self.wave_timer = 0
                    self.spawn_wave()

                # Check level progression
                if self.score >= self.level * 1800 and not self.boss:
                    self.level += 1
                    self.level_transition_timer = 120
                    self.sound_manager.play("powerup")
                    if self.level == 5 or self.level == 10:
                        self.spawn_wave()  # Spawns boss

            # Collision Resolution
            self.collision_manager.update()

    def draw(self):
        """Render frame to screen with screen shake offset."""
        # Create rendering target surface
        render_surf = pygame.Surface((WIDTH, HEIGHT))
        render_surf.fill(BG_COLOR)

        # 1. Background Starfield & Nebulae
        self.starfield.draw(render_surf)

        # 2. Gameplay Entities
        if self.state in [self.STATE_PLAYING, self.STATE_BOSS, self.STATE_PAUSED]:
            # Powerups
            for pu in self.powerups:
                pu.draw(render_surf)

            # Asteroids
            for a in self.asteroids:
                a.draw(render_surf)

            # Enemies
            for enemy in self.enemies:
                enemy.draw(render_surf)

            # Boss
            if self.boss and self.boss.alive:
                self.boss.draw(render_surf)

            # Player
            if self.player:
                self.player.draw(render_surf)

            # Bullets
            for b in self.player_bullets:
                b.draw(render_surf)
            for eb in self.enemy_bullets:
                eb.draw(render_surf)

            # Particles & Shockwaves
            self.particle_system.draw(render_surf)

            # HUD
            self.ui.draw_hud(render_surf)

            # Level Transition Animated Banner
            if self.level_transition_timer > 0:
                alpha = int(255 * min(1.0, self.level_transition_timer / 40.0))
                banner_surf = self.ui.font_title.render(f"— LEVEL {self.level} —", True, CYAN)
                banner_surf.set_alpha(alpha)
                b_rect = banner_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                render_surf.blit(banner_surf, b_rect)

        # 3. Menu States
        mouse_pos = pygame.mouse.get_pos()
        if self.state == self.STATE_MENU:
            self.particle_system.draw(render_surf)
            self.ui.draw_menu(render_surf, self.menu_buttons, mouse_pos)

        elif self.state == self.STATE_PAUSED:
            self.ui.draw_pause_menu(render_surf, self.pause_buttons, mouse_pos)

        elif self.state == self.STATE_GAME_OVER:
            self.particle_system.draw(render_surf)
            high = self.highscores[0]["score"] if self.highscores else self.score
            self.ui.draw_game_over(render_surf, self.game_over_buttons, mouse_pos, self.score, self.level, high)

        elif self.state == self.STATE_VICTORY:
            self.particle_system.draw(render_surf)
            self.ui.draw_victory(render_surf, self.victory_buttons, mouse_pos, self.score)

        elif self.state == self.STATE_SETTINGS:
            self.ui.draw_settings(render_surf, self.settings_buttons, mouse_pos, self.settings)

        elif self.state == self.STATE_HIGHSCORES:
            self.ui.draw_high_scores(render_surf, self.highscore_buttons, mouse_pos, self.highscores)

        # 4. Blit to Screen with Screen Shake
        shake_x = 0
        shake_y = 0
        if self.screen_shake > 0:
            shake_x = int(random.uniform(-self.screen_shake, self.screen_shake))
            shake_y = int(random.uniform(-self.screen_shake, self.screen_shake))

        # Scale appropriately to window size
        curr_w, curr_h = self.screen.get_size()
        if curr_w == WIDTH and curr_h == HEIGHT:
            self.screen.blit(render_surf, (shake_x, shake_y))
        else:
            scaled_surf = pygame.transform.smoothscale(render_surf, (curr_w, curr_h))
            self.screen.blit(scaled_surf, (shake_x, shake_y))

        if not self.headless:
            pygame.display.flip()

    def run(self):
        """Main game loop executing at 60 FPS."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def test_run(self, frames=180):
        """Automated test execution method for verification without window loop."""
        self.reset_game()
        for f in range(frames):
            self.update(1 / 60)
            self.draw()
        print(f"Test run completed successfully for {frames} frames!")
