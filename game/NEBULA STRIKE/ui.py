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
        """Render the in-game HUD: health, shield, outs, score, level, powerups, boss."""
        player = self.game.player
        if not player:
            return

        theme = self.game.theme
        primary = theme.get("primary", CYAN)
        shield_col = theme.get("shield_color", CYAN)
        border_col = theme.get("panel_border", CYAN)

        # Top Bar Background Panel
        bar_surf = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        bg = theme.get("panel_bg", (8, 12, 28))
        bar_surf.fill((bg[0], bg[1], bg[2], 195))
        surface.blit(bar_surf, (0, 0))
        pygame.draw.line(surface, border_col, (0, 70), (WIDTH, 70), 1)

        # 1. SCORE & LEVEL
        score_str = f"SCORE: {self.displayed_score:07d}"
        score_txt = self.font_hud.render(score_str, True, WHITE)
        surface.blit(score_txt, (24, 14))

        level_str = f"LEVEL: {self.game.level:02d}"
        level_txt = self.font_hud.render(level_str, True, primary)
        surface.blit(level_txt, (24, 40))

        # 2. HEALTH & SHIELD BARS (Center-Left)
        hp_x = 220
        bar_w = 150
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
            pygame.draw.rect(surface, shield_col, (hp_x, 40, int(bar_w * shield_ratio), bar_h), border_radius=3)
        pygame.draw.rect(surface, WHITE, (hp_x, 40, bar_w, bar_h), 1, border_radius=3)
        shield_label = self.font_hud_small.render(f"SHIELD {int(player.shield)}/{player.max_shield}", True, shield_col)
        surface.blit(shield_label, (hp_x + bar_w + 10, 38))

        # 3. ARCADE OUT SYSTEM TRACKER
        outs_x = 510
        outs_label = self.font_hud_small.render("OUTS:", True, GRAY)
        surface.blit(outs_label, (outs_x, 26))
        for i in range(3):
            ox = outs_x + 56 + (i * 28)
            oy = 24
            box_rect = pygame.Rect(ox, oy, 20, 20)
            if i < player.outs:
                # Struck out slot (Red X)
                pygame.draw.rect(surface, (50, 10, 15), box_rect, border_radius=3)
                pygame.draw.rect(surface, RED, box_rect, 1, border_radius=3)
                pygame.draw.line(surface, RED, (ox + 4, oy + 4), (ox + 16, oy + 16), 2)
                pygame.draw.line(surface, RED, (ox + 16, oy + 4), (ox + 4, oy + 16), 2)
            else:
                # Active life available (Glowing mini starfighter)
                pygame.draw.rect(surface, (12, 24, 42), box_rect, border_radius=3)
                pygame.draw.rect(surface, primary, box_rect, 1, border_radius=3)
                pts = [(ox + 10, oy + 3), (ox + 16, oy + 16), (ox + 10, oy + 13), (ox + 4, oy + 16)]
                pygame.draw.polygon(surface, primary, pts)

        # 4. ACTIVE POWER-UPS (Right side)
        pu_x = 720
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
            pygame.draw.rect(surface, (50, 10, 20), (bx, by, b_w, b_h), border_radius=4)
            b_col = RED if not boss.enraged else MAGENTA
            if ratio > 0:
                pygame.draw.rect(surface, b_col, (bx, by, int(b_w * ratio), b_h), border_radius=4)
            pygame.draw.rect(surface, WHITE, (bx, by, b_w, b_h), 2, border_radius=4)

            boss_info = f"{boss.name} [PHASE {boss.phase}]"
            boss_txt = self.font_hud_small.render(boss_info, True, YELLOW)
            surface.blit(boss_txt, (bx, by - 22))

        # 6. CRITICAL HULL WARNING ALARM
        if player.alive and (player.hp / player.max_hp) <= 0.30:
            alarm_pulse = int(160 + 95 * math.sin(self.time_counter * 10))
            warn_surf = self.font_hud_small.render("⚠️ CRITICAL HULL — EVASIVE ACTION ⚠️", True, RED)
            w_rect = warn_surf.get_rect(center=(WIDTH // 2, 94))
            bg_w = w_rect.width + 24
            bg_surf = pygame.Surface((bg_w, 24), pygame.SRCALPHA)
            bg_surf.fill((60, 10, 15, min(255, alarm_pulse)))
            surface.blit(bg_surf, (w_rect.centerx - bg_w // 2, w_rect.y - 2))
            surface.blit(warn_surf, w_rect)

    def draw_damage_vignette(self, surface):
        """Draws flashing and pulsing red danger vignettes on screen edges when taking damage."""
        player = self.game.player
        v_alpha = int(min(220.0, self.game.damage_vignette))
        if player and player.alive and (player.hp / player.max_hp) <= 0.30:
            pulse_v = int(70 + 45 * math.sin(self.time_counter * 8))
            v_alpha = max(v_alpha, pulse_v)

        if v_alpha > 0:
            thick = 36
            # Top
            top_surf = pygame.Surface((WIDTH, thick), pygame.SRCALPHA)
            top_surf.fill((220, 20, 40, v_alpha))
            surface.blit(top_surf, (0, 0), special_flags=pygame.BLEND_ADD)
            # Bottom
            bot_surf = pygame.Surface((WIDTH, thick), pygame.SRCALPHA)
            bot_surf.fill((220, 20, 40, v_alpha))
            surface.blit(bot_surf, (0, HEIGHT - thick), special_flags=pygame.BLEND_ADD)
            # Left
            left_surf = pygame.Surface((thick, HEIGHT), pygame.SRCALPHA)
            left_surf.fill((220, 20, 40, v_alpha))
            surface.blit(left_surf, (0, 0), special_flags=pygame.BLEND_ADD)
            # Right
            right_surf = pygame.Surface((thick, HEIGHT), pygame.SRCALPHA)
            right_surf.fill((220, 20, 40, v_alpha))
            surface.blit(right_surf, (WIDTH - thick, 0), special_flags=pygame.BLEND_ADD)

    def draw_out_banner(self, surface):
        """Renders cinematic arcade OUT banner across center during player elimination/respawn."""
        if self.game.out_banner_timer <= 0:
            return

        banner_h = 140
        banner_surf = pygame.Surface((WIDTH, banner_h), pygame.SRCALPHA)
        banner_surf.fill((16, 6, 10, 230))
        surface.blit(banner_surf, (0, (HEIGHT - banner_h) // 2))
        pygame.draw.line(surface, RED, (0, (HEIGHT - banner_h) // 2), (WIDTH, (HEIGHT - banner_h) // 2), 3)
        pygame.draw.line(surface, RED, (0, (HEIGHT + banner_h) // 2), (WIDTH, (HEIGHT + banner_h) // 2), 3)

        if self.game.player and self.game.player.lives > 0:
            out_str = f"💥 OUT {self.game.player.outs} OF 3 💥"
            title = self.font_title.render(out_str, True, (255, 70, 70))
            sub_str = f"WARPING REINFORCEMENTS IN {max(1, int(self.game.respawn_timer))}s..."
            sub = self.font_subtitle.render(sub_str, True, YELLOW)
        else:
            title = self.font_title.render("💀 STRIKE 3 — ALL OUT! 💀", True, RED)
            sub = self.font_subtitle.render("MISSION COMPROMISED — INITIATING DEBRIEFING...", True, WHITE)

        surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 28)))

    def draw_theme_toast(self, surface):
        """Renders floating notification toast when the theme is switched."""
        if self.game.theme_toast_timer <= 0:
            return
        alpha = int(255 * min(1.0, self.game.theme_toast_timer / 25.0))
        pill_w, pill_h = 380, 46
        pill_x = (WIDTH - pill_w) // 2
        pill_y = 78
        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        theme = self.game.theme
        bg = theme.get("panel_bg", (12, 18, 40))
        pill_surf.fill((bg[0], bg[1], bg[2], min(230, alpha)))
        pygame.draw.rect(pill_surf, theme["primary"], (0, 0, pill_w, pill_h), 2, border_radius=8)
        txt = self.font_hud.render(f"🎨 THEME: {theme['name']}", True, theme["primary"])
        pill_surf.blit(txt, txt.get_rect(center=(pill_w // 2, pill_h // 2)))
        surface.blit(pill_surf, (pill_x, pill_y))

    def draw_menu(self, surface, buttons, mouse_pos):
        """Render Title, Subtitle, Theme tag, and Menu Buttons."""
        theme = self.game.theme
        primary = theme.get("primary", CYAN)
        secondary = theme.get("secondary", MAGENTA)

        # Animated pulsing Title
        pulse = 0.85 + 0.15 * math.sin(self.time_counter * 3)
        title_surf = self.font_title.render("NEBULA STRIKE", True, primary)
        t_rect = title_surf.get_rect(center=(WIDTH // 2, 160))

        # Title Glow
        glow_surf = self.font_title.render("NEBULA STRIKE", True, primary)
        glow_surf.set_alpha(int(100 * pulse))
        surface.blit(glow_surf, (t_rect.x - 2, t_rect.y - 2), special_flags=pygame.BLEND_ADD)
        surface.blit(title_surf, t_rect)

        # Subtitle
        sub_surf = self.font_subtitle.render(f"— DEFEND THE GALAXY [{theme['name']}] —", True, secondary)
        s_rect = sub_surf.get_rect(center=(WIDTH // 2, 220))
        surface.blit(sub_surf, s_rect)

        # Theme switch hint
        hint = self.font_hud_small.render("PRESS [T] ANYTIME TO CYCLE THEMES", True, GRAY)
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 255)))

        # Draw buttons
        for btn in buttons:
            btn.color = primary
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_pause_menu(self, surface, buttons, mouse_pos):
        """Render Pause overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 200))
        surface.blit(overlay, (0, 0))

        theme = self.game.theme
        primary = theme.get("primary", CYAN)

        title = self.font_large.render("GAME PAUSED", True, primary)
        t_rect = title.get_rect(center=(WIDTH // 2, 200))
        surface.blit(title, t_rect)

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_game_over(self, surface, buttons, mouse_pos, final_score, level_reached, high_score):
        """Render Game Over Mission Debriefing screen with full damage and elimination stats."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((16, 5, 8, 230))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render("MISSION FAILED — ALL OUT", True, RED)
        t_rect = title.get_rect(center=(WIDTH // 2, 110))
        surface.blit(title, t_rect)

        # Debriefing Panel
        panel_w, panel_h = 580, 260
        panel_x = (WIDTH - panel_w) // 2
        panel_y = 165
        p_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        p_surf.fill((25, 8, 12, 190))
        pygame.draw.rect(p_surf, (255, 60, 60), (0, 0, panel_w, panel_h), 2, border_radius=8)
        surface.blit(p_surf, (panel_x, panel_y))

        # Stats Lines
        stats = [
            ("OUTS SUSTAINED:", "3 / 3 (ALL OUT)", RED),
            ("SECTOR REACHED:", f"LEVEL {level_reached}", CYAN),
            ("FINAL COMBAT SCORE:", f"{final_score:07d}", WHITE),
            ("TOTAL DAMAGE DEALT:", f"{self.game.total_damage_dealt:,} HP", YELLOW),
            ("DAMAGE RECEIVED:", f"{self.game.total_damage_taken:,} HP", (255, 120, 120)),
            ("ENEMIES ELIMINATED:", f"{self.game.enemies_killed} SHIPS", GREEN),
            ("RECORD HIGH SCORE:", f"{high_score:07d}", YELLOW)
        ]

        for i, (label, val, col) in enumerate(stats):
            sy = panel_y + 20 + (i * 32)
            lbl_surf = self.font_hud_small.render(label, True, GRAY)
            val_surf = self.font_hud_small.render(val, True, col)
            surface.blit(lbl_surf, (panel_x + 30, sy))
            surface.blit(val_surf, (panel_x + panel_w - 200, sy))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_victory(self, surface, buttons, mouse_pos, final_score):
        """Render Victory screen after defeating VOID DESTROYER."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 15, 25, 215))
        surface.blit(overlay, (0, 0))

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
        """Render Settings menu with theme selector badge and options."""
        theme = self.game.theme
        primary = theme.get("primary", CYAN)

        title = self.font_large.render("SYSTEM SETTINGS", True, primary)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        # Setting labels
        items = [
            ("Music", "ON" if settings_data.get("music_on") else "OFF"),
            ("Sound Effects", "ON" if settings_data.get("sfx_on") else "OFF"),
            ("Screen Shake", "ON" if settings_data.get("screen_shake") else "OFF"),
            ("Difficulty", settings_data.get("difficulty", "NORMAL")),
            ("Active Theme", theme.get("name", "CYBER NEON"))
        ]

        for i, (label, val) in enumerate(items):
            y = 190 + (i * 55)
            lbl_surf = self.font_hud.render(f"{label}:", True, WHITE)
            val_col = primary if "THEME" in label.upper() else (YELLOW if "ON" in val or val == "NORMAL" else (GREEN if val == "EASY" else RED))
            val_surf = self.font_hud.render(val, True, val_col)
            surface.blit(lbl_surf, (WIDTH // 2 - 220, y))
            surface.blit(val_surf, (WIDTH // 2 + 60, y))

        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw(surface)

    def draw_high_scores(self, surface, buttons, mouse_pos, highscores):
        """Render High Scores leaderboard."""
        theme = self.game.theme
        primary = theme.get("primary", CYAN)

        title = self.font_large.render("🏆 TOP PILOTS LEADERBOARD", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 130)))

        # Header
        hdr = self.font_hud_small.render("RANK       SCORE        SECTOR        DATE", True, primary)
        surface.blit(hdr, (WIDTH // 2 - 200, 190))
        pygame.draw.line(surface, primary, (WIDTH // 2 - 220, 215), (WIDTH // 2 + 220, 215), 1)

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
