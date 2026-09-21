"""
NEBULA STRIKE - User Interface & HUD System
Renders the sci-fi HUD, animated score rollup, power-up indicators, boss health bars,
and interactive menus (Main Menu, Pause, Game Over, Victory, Settings, High Scores).
"""

import math
import pygame
from settings import (
    WIDTH, HEIGHT, CYAN, MAGENTA, GREEN, YELLOW, ORANGE, RED, WHITE, GRAY,
    DARK_GRAY, PANEL_BG, PANEL_BORDER
)


class Button:
    """Interactive neon sci-fi button with hover glow and click callbacks."""
    def __init__(self, x, y, width, height, text, font_size=24, color=CYAN, hover_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.is_hovered = False
        self.hover_anim = 0.0

    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Smooth hover animation interpolation
        target = 1.0 if self.is_hovered else 0.0
        self.hover_anim += (target - self.hover_anim) * 0.25
        return not was_hovered and self.is_hovered  # True if newly hovered

    def draw(self, surface):
        # Background box with dynamic hover expansion
        expand = int(self.hover_anim * 3)
        draw_rect = self.rect.inflate(expand * 2, expand * 2)

        # Base panel
        bg_alpha = int(140 + 60 * self.hover_anim)
        panel_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        panel_surf.fill((12, 18, 38, bg_alpha))
        surface.blit(panel_surf, draw_rect.topleft)

        # Glowing neon border
        border_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, border_color, draw_rect, 2, border_radius=4)

        # Corner glow accents
        if self.hover_anim > 0.1:
            glow_surf = pygame.Surface((draw_rect.width + 12, draw_rect.height + 12), pygame.SRCALPHA)
            g_col = (border_color[0], border_color[1], border_color[2], int(60 * self.hover_anim))
            pygame.draw.rect(glow_surf, g_col, (0, 0, draw_rect.width + 12, draw_rect.height + 12), border_radius=6)
            surface.blit(glow_surf, (draw_rect.x - 6, draw_rect.y - 6), special_flags=pygame.BLEND_ADD)

        # Text rendering
        txt_surf = self.font.render(self.text, True, border_color)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        surface.blit(txt_surf, txt_rect)


class UI:
    """Manages all game UI, HUD elements, overlays, and menu screens."""
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("Arial", 56, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_hud_small = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 38, bold=True)

        # Animated score rolling
        self.displayed_score = 0
        self.time_counter = 0.0

    def update(self, dt_sec):
        self.time_counter += dt_sec
        # Smoothly interpolate displayed score to real score
        diff = self.game.score - self.displayed_score
        if diff > 0:
            step = max(1, int(diff * 0.15))
            self.displayed_score += step
        elif diff < 0:
            self.displayed_score = self.game.score

    def draw_hud(self, surface):
        """Render the in-game HUD: health, shield, lives, score, level, powerups, boss."""
        player = self.game.player
        if not player:
            return

        # Top Bar Background Panel
        bar_surf = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        bar_surf.fill((8, 12, 28, 180))
        surface.blit(bar_surf, (0, 0))
        pygame.draw.line(surface, (0, 240, 255, 100), (0, 70), (WIDTH, 70), 1)

        # 1. SCORE & LEVEL
        score_str = f"SCORE: {self.displayed_score:07d}"
        score_txt = self.font_hud.render(score_str, True, WHITE)
        surface.blit(score_txt, (24, 14))

        level_str = f"LEVEL: {self.game.level:02d}"
        level_txt = self.font_hud.render(level_str, True, CYAN)
        surface.blit(level_txt, (24, 40))

        # 2. HEALTH & SHIELD BARS (Center-Left)
        hp_x = 240
        bar_w = 160
        bar_h = 14

        # HP Bar
        hp_ratio = max(0.0, player.hp / player.max_hp)
        pygame.draw.rect(surface, (40, 15, 20), (hp_x, 16, bar_w, bar_h), border_radius=3)
        hp_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        if hp_ratio > 0:
            pygame.draw.rect(surface, hp_color, (hp_x, 16, int(bar_w * hp_ratio), bar_h), border_radius=3)
        pygame.draw.rect(surface, WHITE, (hp_x, 16, bar_w, bar_h), 1, border_radius=3)
        hp_label = self.font_hud_small.render(f"HP {int(player.hp)}/{player.max_hp}", True, WHITE)
        surface.blit(hp_label, (hp_x + bar_w + 10, 14))

        # Shield Bar
        shield_ratio = max(0.0, player.shield / player.max_shield)
        pygame.draw.rect(surface, (10, 25, 45), (hp_x, 40, bar_w, bar_h), border_radius=3)
        if shield_ratio > 0:
            pygame.draw.rect(surface, CYAN, (hp_x, 40, int(bar_w * shield_ratio), bar_h), border_radius=3)
        pygame.draw.rect(surface, WHITE, (hp_x, 40, bar_w, bar_h), 1, border_radius=3)
        shield_label = self.font_hud_small.render(f"SHIELD {int(player.shield)}/{player.max_shield}", True, CYAN)
        surface.blit(shield_label, (hp_x + bar_w + 10, 38))

        # 3. LIVES (Mini spaceships)
        lives_x = 550
        lives_label = self.font_hud_small.render("LIVES:", True, GRAY)
        surface.blit(lives_label, (lives_x, 26))
        for i in range(player.lives):
            lx = lives_x + 60 + (i * 26)
            ly = 34
            # Draw mini player icon
            pts = [(lx, ly - 8), (lx + 8, ly + 8), (lx, ly + 4), (lx - 8, ly + 8)]
            pygame.draw.polygon(surface, CYAN, pts)
            pygame.draw.polygon(surface, WHITE, pts, 1)

        # 4. ACTIVE POWER-UPS (Right side)
        pu_x = 760
        active_powerups = []
        for p_type, time_left in player.powerups.items():
            if time_left > 0:
                active_powerups.append((p_type.upper().replace("_", " "), time_left))

        if active_powerups:
            for i, (name, timer) in enumerate(active_powerups):
                px = pu_x + (i * 150)
                if px + 140 < WIDTH:
                    pu_txt = self.font_hud_small.render(f"⚡ {name}: {int(timer)}s", True, YELLOW)
                    surface.blit(pu_txt, (px, 26))

        # 5. BOSS HEALTH BAR (Top center overlay)
        if self.game.boss and self.game.boss.alive:
            boss = self.game.boss
            b_w = 460
            b_h = 16
            bx = (WIDTH - b_w) // 2
            by = 82

            ratio = max(0.0, boss.hp / boss.max_hp)
            # Background
            pygame.draw.rect(surface, (50, 10, 20), (bx, by, b_w, b_h), border_radius=4)
            # Fill
            b_col = RED if not boss.enraged else MAGENTA
            if ratio > 0:
                pygame.draw.rect(surface, b_col, (bx, by, int(b_w * ratio), b_h), border_radius=4)
            pygame.draw.rect(surface, WHITE, (bx, by, b_w, b_h), 2, border_radius=4)

            # Boss Title & Phase Text
            boss_info = f"{boss.name} [PHASE {boss.phase}]"
            boss_txt = self.font_hud_small.render(boss_info, True, YELLOW)
            surface.blit(boss_txt, (bx, by - 22))

    def draw_menu(self, surface, buttons, mouse_pos):
        """Render Title, Subtitle, and Menu Buttons."""
        # Animated pulsing Title
        pulse = 0.85 + 0.15 * math.sin(self.time_counter * 3)
        title_surf = self.font_title.render("NEBULA STRIKE", True, CYAN)
        t_rect = title_surf.get_rect(center=(WIDTH // 2, 170))

        # Title Glow
        glow_surf = self.font_title.render("NEBULA STRIKE", True, (0, 240, 255))
        glow_surf.set_alpha(int(100 * pulse))
        surface.blit(glow_surf, (t_rect.x - 2, t_rect.y - 2), special_flags=pygame.BLEND_ADD)
        surface.blit(title_surf, t_rect)

        # Subtitle
        sub_surf = self.font_subtitle.render("— DEFEND THE GALAXY —", True, MAGENTA)
        s_rect = sub_surf.get_rect(center=(WIDTH // 2, 230))
        surface.blit(sub_surf, s_rect)

        # Draw buttons
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_pause_menu(self, surface, buttons, mouse_pos):
        """Render Pause overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 200))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("GAME PAUSED", True, CYAN)
        t_rect = title.get_rect(center=(WIDTH // 2, 200))
        surface.blit(title, t_rect)

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_game_over(self, surface, buttons, mouse_pos, final_score, level_reached, high_score):
        """Render Game Over screen with stats."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 5, 10, 215))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("GAME OVER", True, RED)
        t_rect = title.get_rect(center=(WIDTH // 2, 160))
        surface.blit(title, t_rect)

        score_t = self.font_hud.render(f"FINAL SCORE: {final_score:07d}", True, WHITE)
        level_t = self.font_hud.render(f"SECTOR REACHED: LEVEL {level_reached}", True, CYAN)
        high_t = self.font_hud.render(f"RECORD HIGH SCORE: {high_score:07d}", True, YELLOW)

        surface.blit(score_t, score_t.get_rect(center=(WIDTH // 2, 240)))
        surface.blit(level_t, level_t.get_rect(center=(WIDTH // 2, 275)))
        surface.blit(high_t, high_t.get_rect(center=(WIDTH // 2, 310)))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_victory(self, surface, buttons, mouse_pos, final_score):
        """Render Victory screen after defeating VOID DESTROYER."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 15, 25, 215))
        surface.blit(overlay, (0, 0))

        pulse = 0.8 + 0.2 * math.sin(self.time_counter * 4)
        title = self.font_title.render("🌌 GALAXY SAVED 🌌", True, GREEN)
        t_rect = title.get_rect(center=(WIDTH // 2, 160))
        surface.blit(title, t_rect)

        sub = self.font_large.render("VOID DESTROYER VANQUISHED!", True, YELLOW)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 230)))

        score_t = self.font_hud.render(f"FINAL VICTORY SCORE: {final_score:07d}", True, WHITE)
        surface.blit(score_t, score_t.get_rect(center=(WIDTH // 2, 290)))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_settings(self, surface, buttons, mouse_pos, settings_data):
        """Render Settings menu with current state badges."""
        title = self.font_large.render("SYSTEM SETTINGS", True, CYAN)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

        # Setting labels
        items = [
            ("Music", "ON" if settings_data.get("music_on") else "OFF"),
            ("Sound Effects", "ON" if settings_data.get("sfx_on") else "OFF"),
            ("Screen Shake", "ON" if settings_data.get("screen_shake") else "OFF"),
            ("Difficulty", settings_data.get("difficulty", "NORMAL"))
        ]

        for i, (label, val) in enumerate(items):
            y = 220 + (i * 65)
            lbl_surf = self.font_hud.render(f"{label}:", True, WHITE)
            val_surf = self.font_hud.render(val, True, YELLOW if "ON" in val or val == "NORMAL" else (GREEN if val == "EASY" else RED))
            surface.blit(lbl_surf, (WIDTH // 2 - 200, y))
            surface.blit(val_surf, (WIDTH // 2 + 100, y))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_high_scores(self, surface, buttons, mouse_pos, highscores):
        """Render High Scores leaderboard."""
        title = self.font_large.render("🏆 TOP PILOTS LEADERBOARD", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 130)))

        # Header
        hdr = self.font_hud_small.render("RANK       SCORE        SECTOR        DATE", True, CYAN)
        surface.blit(hdr, (WIDTH // 2 - 200, 190))
        pygame.draw.line(surface, CYAN, (WIDTH // 2 - 220, 215), (WIDTH // 2 + 220, 215), 1)

        for i, entry in enumerate(highscores[:10]):
            y = 230 + (i * 32)
            rank = f"#{i+1:<4}"
            score = f"{entry.get('score', 0):07d}"
            level = f"LVL {entry.get('level', 1):<4}"
            date = entry.get('date', '---')
            row_str = f"{rank}    {score}      {level}       {date}"
            row_surf = self.font_hud_small.render(row_str, True, WHITE)
            surface.blit(row_surf, (WIDTH // 2 - 200, y))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)
