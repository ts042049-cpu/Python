"""
NEBULA STRIKE - Global Settings & Configuration
Contains display constants, color palettes, difficulty presets, and persistence helpers.
"""

import os
import json

# Display Configuration
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "NEBULA STRIKE"
SUBTITLE = "DEFEND THE GALAXY"

# File System Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Ensure necessary directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Sci-Fi Neon Color Palette
BG_COLOR = (7, 11, 25)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 240, 255)
CYAN_GLOW = (0, 240, 255, 70)
MAGENTA = (255, 0, 128)
MAGENTA_GLOW = (255, 0, 128, 70)
GREEN = (0, 255, 136)
GREEN_GLOW = (0, 255, 136, 70)
YELLOW = (255, 215, 0)
YELLOW_GLOW = (255, 215, 0, 70)
ORANGE = (255, 102, 0)
PURPLE = (153, 0, 255)
RED = (255, 42, 75)
RED_GLOW = (255, 42, 75, 80)
GRAY = (140, 150, 175)
DARK_GRAY = (35, 42, 65)
PANEL_BG = (12, 18, 40)
PANEL_BORDER = (0, 240, 255, 180)

# Player Configuration
PLAYER_SPEED = 6.5
PLAYER_MAX_HP = 100
PLAYER_MAX_SHIELD = 100
PLAYER_INITIAL_LIVES = 3
PLAYER_SHOOT_COOLDOWN = 200  # Milliseconds
PLAYER_RAPID_COOLDOWN = 95   # Milliseconds
PLAYER_INVINCIBILITY_TIME = 2000  # Milliseconds

# Projectile Speeds
PLAYER_BULLET_SPEED = 14
ENEMY_BULLET_NORMAL_SPEED = 5
ENEMY_BULLET_FAST_SPEED = 8
ENEMY_BULLET_TRACKING_SPEED = 4

# Power-up Configuration
POWERUP_DURATION_SHIELD = 10.0
POWERUP_DURATION_RAPID = 10.0
POWERUP_DURATION_DOUBLE = 12.0
POWERUP_DURATION_LASER = 8.0
POWERUP_HEAL_AMOUNT = 35
POWERUP_DROP_CHANCE = 0.22  # Base chance from enemies & asteroids

# Scoring System
SCORE_ASTEROID_SMALL = 10
SCORE_ASTEROID_MED = 25
SCORE_ASTEROID_LARGE = 50
SCORE_SCOUT = 50
SCORE_FIGHTER = 100
SCORE_TANK = 200
SCORE_HUNTER = 300
SCORE_BOSS = 5000
SCORE_FINAL_BOSS = 15000

# Difficulty Presets
DIFFICULTY_PRESETS = {
    "EASY": {
        "hp_mult": 0.75,
        "speed_mult": 0.8,
        "bullet_speed_mult": 0.85,
        "spawn_rate_mult": 0.8,
        "damage_mult": 0.75
    },
    "NORMAL": {
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "bullet_speed_mult": 1.0,
        "spawn_rate_mult": 1.0,
        "damage_mult": 1.0
    },
    "HARD": {
        "hp_mult": 1.35,
        "speed_mult": 1.25,
        "bullet_speed_mult": 1.25,
        "spawn_rate_mult": 1.35,
        "damage_mult": 1.3
    }
}

# Settings Management
DEFAULT_SETTINGS = {
    "music_on": True,
    "sfx_on": True,
    "screen_shake": True,
    "difficulty": "NORMAL"
}


def load_settings():
    """Load settings from JSON, returning defaults if missing or invalid."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all default keys exist
            for key, val in DEFAULT_SETTINGS.items():
                if key not in data:
                    data[key] = val
            return data
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings_data):
    """Save settings to JSON securely."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save settings: {e}")


def load_highscores():
    """Load top high scores from JSON, returning fallback list if missing."""
    if not os.path.exists(HIGHSCORE_FILE):
        default_scores = [
            {"score": 15000, "level": 8, "date": "2026-09-20"},
            {"score": 12500, "level": 6, "date": "2026-09-18"},
            {"score": 9800, "level": 5, "date": "2026-09-15"},
            {"score": 7500, "level": 4, "date": "2026-09-12"},
            {"score": 5200, "level": 3, "date": "2026-09-10"}
        ]
        save_highscores(default_scores)
        return default_scores
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            scores = json.load(f)
            if isinstance(scores, list):
                return sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:10]
            return []
    except Exception:
        return []


def save_highscores(scores_list):
    """Save top 10 high scores to JSON."""
    try:
        sorted_scores = sorted(scores_list, key=lambda x: x.get("score", 0), reverse=True)[:10]
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_scores, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save highscores: {e}")
