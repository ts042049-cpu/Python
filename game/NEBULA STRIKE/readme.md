# 🚀 NEBULA STRIKE — Advanced 2D Space Shooter

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5+-00F0FF?style=for-the-badge&logo=gamemaker&logoColor=black)](https://pyga.me/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-FF007F?style=for-the-badge)](LICENSE)

> **"Defend the Galaxy from the cosmic onslaught of the Void Destroyer."**

**NEBULA STRIKE** is a feature-packed, retro-futuristic 2D arcade space shooter built from scratch with Python and Pygame. Engineered with clean modular architecture, procedural glowing vector graphics, multi-layered parallax starfields, authentic synthesized audio fallbacks, and multi-phase boss battles, it delivers a commercial-quality indie arcade experience.

---

## 🎮 Gameplay Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│ SCORE: 0002500       LEVEL: 04          HP: ████████░░   SHIELD: █████ │
│                                                                        │
│                ☄ (Large Asteroid)                                      │
│                                           🛸 (Hunter Interceptor)      │
│                        💥 (Explosion)                                  │
│                                                                        │
│         🚀 (Player Starfighter)                                        │
│         ││ (Dual Lasers)                                               │
│                                                                        │
│ POWER-UP: [⚡ RAPID FIRE 08s]           LIVES: 🚀 🚀 🚀                 │
└────────────────────────────────────────────────────────────────────────┘
```

You pilot an advanced combat starfighter deep inside enemy space. Blast your way through asteroid belts and enemy squadrons, harvest high-tier tactical power-ups, defeat sector dreadnoughts, and annihilate the colossal **VOID DESTROYER**!

---

## ✨ Features

* 🚀 **Futuristic Player Starfighter**:
  * Dual input support (`WASD` + Arrow Keys).
  * Smooth acceleration physics with banking tilt animations.
  * Screen boundary enforcement, energy shields, lives counter, and temporary invincibility on damage.
  * Real-time engine thruster exhaust particles.
* 🌌 **Multi-Layered Parallax Starfield & Nebulae**:
  * 3 parallax star tiers with independent drift rates and twinkling brightness.
  * Procedurally rendered soft glowing cosmic nebula clouds drifting in deep space.
* ☄ **Procedural Asteroid Fragmentation**:
  * Random jagged geometry and surface craters with realistic tumbling rotation.
  * 3 Size Tiers: Large asteroids shatter into 2 Mediums; Mediums split into 2 Smalls; Smalls burst into rock debris.
* 🛸 **4 Unique Enemy Archetypes**:
  * **Scout**: Fast, agile swooper executing sinusoidal flight paths.
  * **Fighter**: Tactical strafer firing aimed needle lasers directly at the player.
  * **Tank**: Heavily armored dreadnought with a dedicated mini health bar, firing triple spread salvos.
  * **Hunter**: Aggressive interceptor dynamically tracking the player's position and launching homing missiles.
* 🔥 **Multi-Phase Boss Battles**:
  * **Sector Guardian (Level 5)**: Colossal battlecruiser with straight volleys, quintuple spread cannons, and spiral bullet-hell attacks. Enrages below 50% HP.
  * **VOID DESTROYER (Final Boss)**: Epic 3-phase flagship featuring void rift flares, dual-spiral storm barrages, seismic shock lasers, and screen-shaking seismic blasts.
* 🛡 **Dynamic Collectible Power-Ups**:
  * 🛡 **SHIELD**: Restores and supercharges your protective energy barrier.
  * ⚡ **RAPID FIRE**: Doubles your firing rate for 10 seconds.
  * ❤️ **HEALTH**: Nanite hull repair (+40 HP).
  * 💥 **LASER**: Unlocks a continuous piercing plasma beam for 8 seconds.
  * 🔥 **DOUBLE SHOT**: Dual wing-mounted heavy cannons for 12 seconds.
* 💥 **Modular Particle Engine**:
  * Radial spark explosions, expanding energy shockwaves, engine trails, asteroid debris, and floating combat text (`+100`, `SHIELD UP!`).
* 🔊 **Zero-Dependency Audio Synthesizer**:
  * Generates authentic 8-bit/16-bit arcade sound effects (`shoot`, `explosion`, `hit`, `powerup`, `boss_warning`, `player_damage`, `game_over`) directly using Python's standard library (`wave` + `math`).
  * Runs immediately with zero missing-asset crashes.
* 💾 **Local Data Persistence**:
  * JSON-based high-score leaderboard tracking top 10 runs (score, sector level, timestamp).
  * System settings persistence (music, sound effects, screen shake, difficulty presets: EASY / NORMAL / HARD).
* 🌐 **Browser Edition (HTML5 Canvas & Web Audio)**:
  * Includes a dedicated web version that runs natively in any browser with 60 FPS hardware acceleration and Web Audio API.

---

## 🕹 Controls

| Action | Primary Key | Alternate Key |
| :--- | :---: | :---: |
| **Move Up** | <kbd>W</kbd> | <kbd>↑</kbd> |
| **Move Down** | <kbd>S</kbd> | <kbd>↓</kbd> |
| **Move Left** | <kbd>A</kbd> | <kbd>←</kbd> |
| **Move Right** | <kbd>D</kbd> | <kbd>→</kbd> |
| **Primary Fire** | <kbd>SPACE</kbd> | — |
| **Pause Game** | <kbd>P</kbd> | — |
| **Back / Menu** | <kbd>ESC</kbd> | — |

---

## 📦 Project Structure

```text
NEBULA-STRIKE/
├── main.py                # Game entry point and window initialization
├── settings.py            # Global constants, color palettes, difficulty presets, configuration
├── game.py                # Core game loop, state machine, audio synthesizer, level progression
├── player.py              # Player spaceship, movement, health, shield, power-up timers
├── bullet.py              # Player & enemy projectiles (normal, fast, spread, tracking, laser)
├── asteroid.py            # Procedural asteroids (Large, Medium, Small) with splitting & rotation
├── enemy.py               # Enemy archetypes (Scout, Fighter, Tank, Hunter) with custom AI
├── boss.py                # Bosses (Level 5 Boss & Final Boss "VOID DESTROYER") with multi-phase AI
├── powerup.py             # Collectible power-ups (Shield, Rapid Fire, Health, Laser, Double Shot)
├── particles.py           # High-performance particle engine (sparks, shockwaves, floating text)
├── starfield.py           # Multi-layered parallax starfield with procedural nebula clouds
├── ui.py                  # HUD, Main Menu, Pause Menu, Game Over, Victory, Settings, High Scores
├── collision.py           # Centralized collision detection and damage resolution
├── index.html             # Browser edition entry point
├── style.css              # Modern sci-fi arcade UI styles
├── game.js                # HTML5 Canvas & Web Audio engine
│
├── assets/                # Asset directories (supports external drop-ins)
│   ├── images/
│   ├── sounds/
│   └── fonts/
│
├── data/
│   ├── highscore.json     # Top 10 high scores (score, level, date)
│   └── settings.json      # User settings (music, sfx, shake, difficulty)
│
├── requirements.txt       # Project dependencies
└── README.md              # Documentation
```

---

## 🛠 Technologies

* **Python 3.11+**
* **Pygame / Pygame-CE**: 2D hardware-accelerated rendering and input management.
* **HTML5 Canvas & Web Audio API**: Browser edition.
* **JSON**: Local persistence for high scores and user settings.
* **Standard Library `wave`, `struct`, `math`**: In-engine procedural sound synthesis.

---

## 🚀 Installation & How to Run

### 1. Clone or Navigate to the Project

```bash
cd "game/NEBULA STRIKE"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Or `pip install pygame-ce` / `pip install pygame`)*

### 3. Launch the Desktop Game

```bash
python main.py
```

### 4. Or Run in Browser

```bash
python -m http.server 8000
```
Then open `http://localhost:8000` in your web browser.

---

## 🎯 Scoring Guide

| Target | Points | Notes |
| :--- | :---: | :--- |
| **Small Asteroid** | `+10` | 1 Hit |
| **Medium Asteroid** | `+25` | Splits into 2 Small asteroids |
| **Large Asteroid** | `+50` | Splits into 2 Medium asteroids |
| **Scout** | `+50` | Fast sinusoidal flier |
| **Fighter** | `+100` | Aimed precision sniper |
| **Tank** | `+200` | Armored, triple spread salvos |
| **Hunter** | `+300` | Homing missile interceptor |
| **Sector Boss** | `+5,000` | Level 5 Guardian |
| **VOID DESTROYER** | `+15,000` | Final Boss |

---

## 📜 License

This project is licensed under the **MIT License**. Feel free to modify and build upon it!

---

*Engineered with precision for space combat.* 🌌
