/**
 * NEBULA STRIKE 🚀 — Web Edition
 * Complete, polished 2D arcade space shooter built with HTML5 Canvas & Web Audio API.
 */

// --- GLOBAL CONSTANTS & CONFIGURATION ---
const WIDTH = 1280;
const HEIGHT = 720;
const FPS = 60;

const COLORS = {
  bg: '#070b19',
  white: '#ffffff',
  cyan: '#00f0ff',
  magenta: '#ff007f',
  green: '#00ff88',
  yellow: '#ffd700',
  orange: '#ff6600',
  purple: '#9900ff',
  red: '#ff2a4b',
  gray: '#8e9bb0',
  panelBg: 'rgba(12, 18, 40, 0.85)',
};

const THEMES = {
  CYBER_NEON: {
    name: 'CYBER NEON',
    bg: '#070b19',
    primary: '#00f0ff',
    secondary: '#ff007f',
    accent: '#00ff88',
    starTints: ['#b4dcff', '#c8f0ff', '#ffffff', '#8cb4ff'],
    nebulaColors: ['#0064c8', '#7800a0', '#00b4dc'],
    playerHull: '#19233c',
    playerAccent: '#00f0ff',
    playerGlow: '#00fff0',
    thruster: '#00f0ff',
    bullet: '#00f0ff',
    shield: '#00f0ff',
    panelBg: 'rgba(12, 18, 40, 0.85)',
    panelBorder: '#00f0ff'
  },
  SOLAR_INFERNO: {
    name: 'SOLAR INFERNO',
    bg: '#140808',
    primary: '#ff5a00',
    secondary: '#ffc800',
    accent: '#ff2828',
    starTints: ['#ffdcb4', '#ffbe8c', '#ffffe6', '#ff8250'],
    nebulaColors: ['#b42800', '#dc6400', '#8c0a14'],
    playerHull: '#321914',
    playerAccent: '#ff7800',
    playerGlow: '#ffd700',
    thruster: '#ff8c00',
    bullet: '#ffa014',
    shield: '#ffa028',
    panelBg: 'rgba(35, 15, 15, 0.85)',
    panelBorder: '#ff7800'
  },
  TOXIC_MATRIX: {
    name: 'TOXIC MATRIX',
    bg: '#05120c',
    primary: '#00ff88',
    secondary: '#00e6ff',
    accent: '#b4ff00',
    starTints: ['#b4ffc8', '#c8ffe6', '#f0fff0', '#64e696'],
    nebulaColors: ['#008c3c', '#005a64', '#28b450'],
    playerHull: '#122a1c',
    playerAccent: '#00ff88',
    playerGlow: '#8cff64',
    thruster: '#00ff88',
    bullet: '#00ffa0',
    shield: '#00ff8c',
    panelBg: 'rgba(10, 28, 20, 0.85)',
    panelBorder: '#00ff88'
  },
  RETRO_SYNTHWAVE: {
    name: 'RETRO SYNTHWAVE',
    bg: '#120620',
    primary: '#ff00a0',
    secondary: '#a000ff',
    accent: '#ffb400',
    starTints: ['#ffc8f0', '#e6b4ff', '#ffffff', '#ff8cdc'],
    nebulaColors: ['#9600b4', '#c80078', '#50008c'],
    playerHull: '#281237',
    playerAccent: '#ff00a0',
    playerGlow: '#ff78dc',
    thruster: '#ff00b4',
    bullet: '#ff32b4',
    shield: '#dc3cff',
    panelBg: 'rgba(28, 12, 45, 0.85)',
    panelBorder: '#ff00a0'
  },
  CELESTIAL_AURORA: {
    name: 'CELESTIAL AURORA',
    bg: '#0a081e',
    primary: '#aa78ff',
    secondary: '#ffd75a',
    accent: '#00e6f0',
    starTints: ['#dcd2ff', '#fff0c8', '#ffffff', '#b4a0f0'],
    nebulaColors: ['#5a28b4', '#8c5adc', '#1e78a0'],
    playerHull: '#1e193c',
    playerAccent: '#aa78ff',
    playerGlow: '#ffd75a',
    thruster: '#a078ff',
    bullet: '#be96ff',
    shield: '#a08cff',
    panelBg: 'rgba(20, 16, 45, 0.85)',
    panelBorder: '#aa78ff'
  }
};

// --- WEB AUDIO SYNTHESIZER ---
class SoundManager {
  constructor() {
    this.ctx = null;
    this.enabled = true;
    this.initContext();
  }

  initContext() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    } catch (e) {
      console.warn("Web Audio API not supported", e);
    }
  }

  ensureContext() {
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  play(name) {
    if (!this.enabled || !this.ctx) return;
    this.ensureContext();
    const t = this.ctx.currentTime;

    if (name === 'shoot') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(920, t);
      osc.frequency.exponentialRampToValueAtTime(240, t + 0.12);
      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.13);
    } else if (name === 'explosion') {
      // Noise buffer for realistic explosion
      const bufferSize = this.ctx.sampleRate * 0.4;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.1));
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(800, t);
      filter.frequency.linearRampToValueAtTime(80, t + 0.4);
      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.4);
      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      noise.start(t);
    } else if (name === 'hit') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(600, t);
      osc.frequency.exponentialRampToValueAtTime(150, t + 0.06);
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.06);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.07);
    } else if (name === 'powerup') {
      const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const noteTime = t + idx * 0.07;
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, noteTime);
        gain.gain.setValueAtTime(0.18, noteTime);
        gain.gain.exponentialRampToValueAtTime(0.01, noteTime + 0.1);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(noteTime);
        osc.stop(noteTime + 0.11);
      });
    } else if (name === 'boss_warning') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(260, t);
      osc.frequency.linearRampToValueAtTime(420, t + 0.3);
      osc.frequency.linearRampToValueAtTime(260, t + 0.6);
      gain.gain.setValueAtTime(0.22, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.65);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.65);
    } else if (name === 'player_damage') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(150, t);
      osc.frequency.exponentialRampToValueAtTime(60, t + 0.2);
      gain.gain.setValueAtTime(0.25, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.21);
    } else if (name === 'game_over') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(380, t);
      osc.frequency.linearRampToValueAtTime(120, t + 0.8);
      gain.gain.setValueAtTime(0.22, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.8);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.81);
    }
  }
}

// --- PARALLAX STARFIELD & NEBULAE ---
class Starfield {
  constructor() {
    this.stars = [];
    for (let i = 0; i < 90; i++) this.stars.push(this.createStar(0));
    for (let i = 0; i < 50; i++) this.stars.push(this.createStar(1));
    for (let i = 0; i < 25; i++) this.stars.push(this.createStar(2));

    this.nebulae = [
      { x: WIDTH * 0.25, y: HEIGHT * 0.3, radius: 260, color: 'rgba(80, 20, 140, 0.08)', speed: 0.2 },
      { x: WIDTH * 0.75, y: HEIGHT * 0.7, radius: 300, color: 'rgba(10, 80, 150, 0.08)', speed: 0.25 },
      { x: WIDTH * 0.5, y: HEIGHT * 1.1, radius: 280, color: 'rgba(120, 30, 90, 0.07)', speed: 0.22 },
    ];
    this.time = 0;
    this.theme = null;
  }

  applyTheme(theme) {
    if (!theme) return;
    this.theme = theme;
    if (theme.nebulaColors && theme.nebulaColors.length >= 3) {
      this.nebulae[0].color = theme.nebulaColors[0] + '18';
      this.nebulae[1].color = theme.nebulaColors[1] + '18';
      this.nebulae[2].color = theme.nebulaColors[2] + '14';
    }
  }

  createStar(layer) {
    const speeds = [0.6, 1.6, 3.2];
    const sizes = [1, 1.8, 2.5];
    return {
      x: Math.random() * WIDTH,
      y: Math.random() * HEIGHT,
      layer,
      speed: speeds[layer] * (0.8 + Math.random() * 0.4),
      size: sizes[layer],
      twinkle: Math.random() * Math.PI * 2,
    };
  }

  update(speedMult = 1.0) {
    this.time += 0.02;
    for (const star of this.stars) {
      star.y += star.speed * speedMult;
      if (star.y > HEIGHT) {
        star.y = 0;
        star.x = Math.random() * WIDTH;
      }
    }
    for (const neb of this.nebulae) {
      neb.y += neb.speed * speedMult;
      if (neb.y - neb.radius > HEIGHT) {
        neb.y = -neb.radius;
        neb.x = Math.random() * WIDTH;
      }
    }
  }

  draw(ctx) {
    // Draw Nebulae
    for (const neb of this.nebulae) {
      const grad = ctx.createRadialGradient(neb.x, neb.y, 0, neb.x, neb.y, neb.radius);
      grad.addColorStop(0, neb.color);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(neb.x, neb.y, neb.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw Stars
    const tints = this.theme && this.theme.starTints ? this.theme.starTints : ['#b4dcff', '#c8f0ff', '#ffffff'];
    for (let i = 0; i < this.stars.length; i++) {
      const star = this.stars[i];
      const alpha = 0.6 + 0.4 * Math.sin(this.time * 3 + star.twinkle);
      const starColor = star.layer === 2 ? '#ffffff' : tints[i % tints.length];
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = starColor;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }
}

// --- PARTICLE SYSTEM ---
class ParticleSystem {
  constructor() {
    this.particles = [];
    this.shockwaves = [];
    this.floatingTexts = [];
    this.smokeParticles = [];
  }

  createExplosion(x, y, color = COLORS.orange, count = 28, maxSpeed = 7.0) {
    this.shockwaves.push({ x, y, radius: 5, maxRadius: maxSpeed * 12, alpha: 1.0, color });
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.5 + Math.random() * maxSpeed;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color: [color, COLORS.yellow, COLORS.white][Math.floor(Math.random() * 3)],
        radius: 2 + Math.random() * 3,
        life: 25 + Math.random() * 20,
        maxLife: 45,
      });
    }
  }

  createShockwave(x, y, color = COLORS.cyan, maxRadius = 60) {
    this.shockwaves.push({ x, y, radius: 5, maxRadius, alpha: 1.0, color });
  }

  createThrusterTrail(x, y, color = COLORS.cyan) {
    this.particles.push({
      x: x + (Math.random() * 6 - 3),
      y,
      vx: (Math.random() - 0.5) * 1.5,
      vy: 2.5 + Math.random() * 2.5,
      color,
      radius: 1.5 + Math.random() * 2,
      life: 12 + Math.random() * 8,
      maxLife: 20,
    });
  }

  createDamageSmoke(x, y, isFire = false) {
    const angle = (Math.random() * 0.5 + 0.25) * Math.PI;
    const speed = 0.5 + Math.random() * 1.8;
    this.smokeParticles.push({
      x: x + (Math.random() * 8 - 4),
      y: y + (Math.random() * 8 - 4),
      vx: Math.cos(angle) * speed * (Math.random() < 0.5 ? -1 : 1),
      vy: 0.8 + Math.random() * 2.0,
      radius: isFire ? 2 + Math.random() * 2.5 : 3.5 + Math.random() * 3,
      color: isFire
        ? (Math.random() < 0.5 ? '#ff4b14' : '#ffaa00')
        : (Math.random() < 0.5 ? '#556070' : '#323845'),
      life: 22 + Math.random() * 14,
      maxLife: 36,
    });
  }

  createWarpInEffect(x, y, color = COLORS.cyan) {
    this.shockwaves.push({ x, y, radius: 5, maxRadius: 85, alpha: 1.0, color });
    this.shockwaves.push({ x, y, radius: 5, maxRadius: 50, alpha: 1.0, color: '#ffffff' });
    for (let i = 0; i < 30; i++) {
      const angle = Math.random() * Math.PI * 2;
      const dist = 40 + Math.random() * 80;
      const startX = x + Math.cos(angle) * dist;
      const startY = y + Math.sin(angle) * dist;
      this.particles.push({
        x: startX,
        y: startY,
        vx: (x - startX) / 14,
        vy: (y - startY) / 14,
        color: [color, '#ffffff', COLORS.yellow][Math.floor(Math.random() * 3)],
        radius: 2 + Math.random() * 2,
        life: 16,
        maxLife: 16,
      });
    }
  }

  createAsteroidDebris(x, y, count = 14) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.2 + Math.random() * 4.5;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color: ['#8c9ba5', '#63707c', '#abb9c4'][Math.floor(Math.random() * 3)],
        radius: 2 + Math.random() * 2.5,
        life: 20 + Math.random() * 25,
        maxLife: 45,
      });
    }
  }

  addFloatingText(x, y, text, color = COLORS.yellow, isCrit = false) {
    this.floatingTexts.push({ x, y, text, color, life: 50, maxLife: 50, isCrit });
  }

  addDamagePopup(x, y, amount, isCrit = false, isPlayer = false, isShield = false, shieldColor = COLORS.cyan) {
    const jx = x + (Math.random() * 16 - 8);
    const jy = y + (Math.random() * 10 - 5);
    let txt = `-${Math.round(amount)}`;
    let col = '#ffffff';

    if (isShield) {
      txt = `SHIELD -${Math.round(amount)}`;
      col = shieldColor;
    } else if (isPlayer) {
      txt = `-${Math.round(amount)}`;
      col = '#ff3b3b';
      isCrit = true;
    } else if (isCrit) {
      txt = `-${Math.round(amount)} CRIT!`;
      col = '#ffd700';
    } else {
      txt = `-${Math.round(amount)}`;
      col = '#ffeedd';
    }
    this.addFloatingText(jx, jy, txt, col, isCrit);
  }

  update() {
    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.96;
      p.vy *= 0.96;
      p.life--;
      if (p.life <= 0) this.particles.splice(i, 1);
    }
    // Update smoke particles
    for (let i = this.smokeParticles.length - 1; i >= 0; i--) {
      const s = this.smokeParticles[i];
      s.x += s.vx;
      s.y += s.vy;
      s.radius += 0.12;
      s.life--;
      if (s.life <= 0) this.smokeParticles.splice(i, 1);
    }
    // Update shockwaves
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const s = this.shockwaves[i];
      s.radius += (s.maxRadius - s.radius) * 0.12;
      s.alpha -= 0.035;
      if (s.alpha <= 0) this.shockwaves.splice(i, 1);
    }
    // Update floating texts
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const t = this.floatingTexts[i];
      t.y -= 1.1;
      t.life--;
      if (t.life <= 0) this.floatingTexts.splice(i, 1);
    }
  }

  draw(ctx) {
    ctx.save();
    // Draw smoke particles
    for (const sm of this.smokeParticles) {
      const progress = sm.life / sm.maxLife;
      ctx.fillStyle = sm.color;
      ctx.globalAlpha = progress * 0.65;
      ctx.beginPath();
      ctx.arc(sm.x, sm.y, sm.radius, 0, Math.PI * 2);
      ctx.fill();
    }
    // Draw shockwaves
    for (const s of this.shockwaves) {
      ctx.strokeStyle = s.color;
      ctx.globalAlpha = Math.max(0, s.alpha);
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      ctx.stroke();
    }
    // Draw particles
    for (const p of this.particles) {
      const progress = p.life / p.maxLife;
      ctx.fillStyle = p.color;
      ctx.globalAlpha = progress;
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(1, p.radius * progress), 0, Math.PI * 2);
      ctx.fill();
    }
    // Draw floating texts with pop scale and drop shadow
    ctx.textAlign = 'center';
    for (const t of this.floatingTexts) {
      const elapsed = t.maxLife - t.life;
      let scale = 1.0;
      if (elapsed < 6) scale = 1.0 + (6 - elapsed) * 0.06;
      const fontSize = Math.round((t.isCrit ? 20 : 16) * scale);
      ctx.font = `bold ${fontSize}px Orbitron, sans-serif`;
      ctx.globalAlpha = Math.min(1.0, (t.life / t.maxLife) * 1.5);

      // Drop shadow
      ctx.fillStyle = '#000000';
      ctx.fillText(t.text, t.x + 2, t.y + 2);

      // Foreground text
      ctx.fillStyle = t.color;
      ctx.fillText(t.text, t.x, t.y);
    }
    ctx.restore();
  }

  clear() {
    this.particles = [];
    this.shockwaves = [];
    this.floatingTexts = [];
    this.smokeParticles = [];
  }
}

// --- PROJECTILES ---
class Projectile {
  constructor(x, y, vx, vy, damage, color, radius) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.damage = damage;
    this.color = color;
    this.radius = radius;
    this.alive = true;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.y < -50 || this.y > HEIGHT + 50 || this.x < -50 || this.x > WIDTH + 50) {
      this.alive = false;
    }
  }

  draw(ctx) {
    ctx.save();
    ctx.shadowColor = this.color;
    ctx.shadowBlur = 10;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(1, this.radius * 0.5), 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class PlayerLaser extends Projectile {
  constructor(x, y, isDouble = false, color = null) {
    super(x, y, 0, -14, 25, color || (isDouble ? COLORS.yellow : COLORS.cyan), 4);
    this.isDouble = isDouble;
  }

  draw(ctx) {
    ctx.save();
    ctx.shadowColor = this.color;
    ctx.shadowBlur = 12;
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x - 2, this.y - 10, 4, 20);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(this.x - 1, this.y - 8, 2, 16);
    ctx.restore();
  }
}

class MegaLaserBeam extends Projectile {
  constructor(x, y) {
    super(x, y, 0, -22, 65, COLORS.green, 7);
    this.piercing = true;
  }

  draw(ctx) {
    ctx.save();
    ctx.shadowColor = COLORS.green;
    ctx.shadowBlur = 18;
    ctx.fillStyle = COLORS.green;
    ctx.fillRect(this.x - 4, this.y - 18, 8, 36);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(this.x - 2, this.y - 16, 4, 32);
    ctx.restore();
  }
}

class TrackingBullet extends Projectile {
  constructor(x, y, target) {
    super(x, y, 0, 4.2, 22, COLORS.purple, 6);
    this.target = target;
    this.angle = Math.PI / 2;
    this.turnRate = 0.045;
  }

  update() {
    if (this.target && this.target.alive) {
      const dx = this.target.x - this.x;
      const dy = this.target.y - this.y;
      const targetAngle = Math.atan2(dy, dx);
      let diff = (targetAngle - this.angle + Math.PI) % (Math.PI * 2) - Math.PI;
      if (Math.abs(diff) < this.turnRate) {
        this.angle = targetAngle;
      } else {
        this.angle += Math.sign(diff) * this.turnRate;
      }
    }
    this.vx = Math.cos(this.angle) * 4.5;
    this.vy = Math.sin(this.angle) * 4.5;
    super.update();
  }
}

// --- PLAYER STARFIGHTER ---
class Player {
  constructor() {
    this.x = WIDTH / 2;
    this.y = HEIGHT - 110;
    this.vx = 0;
    this.vy = 0;
    this.speed = 6.5;
    this.width = 46;
    this.height = 54;
    this.maxHp = 100;
    this.hp = this.maxHp;
    this.maxShield = 100;
    this.shield = this.maxShield;
    this.lives = 3;
    this.outs = 0;
    this.maxOuts = 3;
    this.alive = true;
    this.tilt = 0;
    this.lastShotTime = 0;
    this.invincibleUntil = 0;
    this.shieldCooldown = 0;

    this.powerups = {
      shield: 0,
      rapid_fire: 0,
      double_shot: 0,
      laser: 0,
    };
  }

  handleInput(keys) {
    let mx = 0, my = 0;
    if (keys['KeyW'] || keys['ArrowUp']) my -= 1;
    if (keys['KeyS'] || keys['ArrowDown']) my += 1;
    if (keys['KeyA'] || keys['ArrowLeft']) mx -= 1;
    if (keys['KeyD'] || keys['ArrowRight']) mx += 1;

    if (mx !== 0 && my !== 0) {
      mx *= 0.7071;
      my *= 0.7071;
    }

    const targetVx = mx * this.speed;
    const targetVy = my * this.speed;
    this.vx += (targetVx - this.vx) * 0.35;
    this.vy += (targetVy - this.vy) * 0.35;

    const targetTilt = mx < -0.1 ? -1 : (mx > 0.1 ? 1 : 0);
    this.tilt += (targetTilt - this.tilt) * 0.25;
  }

  update(dt, particles, theme) {
    this.x = Math.max(30, Math.min(WIDTH - 30, this.x + this.vx));
    this.y = Math.max(35, Math.min(HEIGHT - 35, this.y + this.vy));

    // Timers
    for (const key in this.powerups) {
      if (this.powerups[key] > 0) {
        this.powerups[key] = Math.max(0, this.powerups[key] - dt);
      }
    }

    // Passive shield regeneration
    const now = Date.now();
    if (this.powerups.shield > 0) {
      this.shield = this.maxShield;
    } else if (now > this.shieldCooldown && this.shield < this.maxShield) {
      this.shield = Math.min(this.maxShield, this.shield + 12 * dt);
    }

    // Thruster trail particles with theme color
    const thrusterCol = theme && theme.thruster ? theme.thruster : COLORS.cyan;
    if (particles && this.alive) {
      particles.createThrusterTrail(this.x - 12 + this.tilt * 3, this.y + 20, thrusterCol);
      particles.createThrusterTrail(this.x + 12 - this.tilt * 3, this.y + 20, thrusterCol);

      // Low health damage smoke & sparks
      if (this.hp <= this.maxHp * 0.35 && Math.random() < 0.35) {
        particles.createDamageSmoke(this.x, this.y, this.hp <= this.maxHp * 0.15);
      }
    }
  }

  shoot(now, theme) {
    const cooldown = this.powerups.rapid_fire > 0 ? 95 : 200;
    if (now - this.lastShotTime < cooldown) return [];

    this.lastShotTime = now;
    const bullets = [];
    const bulletCol = theme && theme.bullet ? theme.bullet : null;
    if (this.powerups.laser > 0) {
      bullets.push(new MegaLaserBeam(this.x, this.y - 25));
    } else if (this.powerups.double_shot > 0) {
      bullets.push(new PlayerLaser(this.x - 16, this.y - 12, true, bulletCol));
      bullets.push(new PlayerLaser(this.x + 16, this.y - 12, true, bulletCol));
    } else {
      bullets.push(new PlayerLaser(this.x, this.y - 25, false, bulletCol));
    }
    return bullets;
  }

  takeDamage(amount, now, particles, game) {
    if (now < this.invincibleUntil || !this.alive) return false;

    const theme = game ? game.theme : null;
    const shieldColor = theme && theme.shield ? theme.shield : COLORS.cyan;

    if (this.shield > 0) {
      const absorbed = Math.min(this.shield, amount);
      this.shield -= absorbed;
      amount -= absorbed;
      this.shieldCooldown = now + 4000;
      if (particles) {
        particles.createShockwave(this.x, this.y, shieldColor, 40);
        particles.addDamagePopup(this.x + 18, this.y - 12, absorbed, false, false, true, shieldColor);
      }
    }

    if (amount > 0) {
      this.hp -= amount;
      this.invincibleUntil = now + 2000;
      if (particles) {
        particles.createExplosion(this.x, this.y, COLORS.red, 16, 5);
        particles.addDamagePopup(this.x - 18, this.y - 12, amount, false, true);
      }
      if (game) {
        game.damageVignette = Math.min(220, game.damageVignette + 110);
      }

      if (this.hp <= 0) {
        this.hp = 0;
        return true;
      }
    }
    return false;
  }

  loseLife() {
    this.lives--;
    if (this.lives > 0) {
      this.respawn();
    } else {
      this.alive = false;
    }
  }

  respawn() {
    this.x = WIDTH / 2;
    this.y = HEIGHT - 110;
    this.vx = 0;
    this.vy = 0;
    this.hp = this.maxHp;
    this.shield = this.maxShield;
    this.invincibleUntil = Date.now() + 3000;
    for (const key in this.powerups) this.powerups[key] = 0;
  }

  applyPowerup(type) {
    if (type === 'shield') {
      this.powerups.shield = 10.0;
      this.shield = this.maxShield;
    } else if (type === 'rapid_fire') {
      this.powerups.rapid_fire = 10.0;
    } else if (type === 'double_shot') {
      this.powerups.double_shot = 12.0;
    } else if (type === 'laser') {
      this.powerups.laser = 8.0;
    } else if (type === 'health') {
      this.hp = Math.min(this.maxHp, this.hp + 40);
    }
  }

  draw(ctx, theme) {
    if (!this.alive) return;
    const now = Date.now();
    if (now < this.invincibleUntil && Math.floor(now / 100) % 2 === 0) return;

    const primary = theme && theme.primary ? theme.primary : COLORS.cyan;
    const hullCol = theme && theme.playerHull ? theme.playerHull : '#19233c';
    const glowCol = theme && theme.playerGlow ? theme.playerGlow : COLORS.cyan;
    const accentCol = theme && theme.playerAccent ? theme.playerAccent : COLORS.cyan;
    const shieldCol = theme && theme.shield ? theme.shield : COLORS.cyan;

    ctx.save();
    // Shield Dome
    if (this.shield > 0 || this.powerups.shield > 0) {
      ctx.strokeStyle = shieldCol;
      ctx.lineWidth = 2;
      ctx.shadowColor = shieldCol;
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.arc(this.x, this.y, 36, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Spaceship Hull
    const tiltPx = this.tilt * 6;
    ctx.fillStyle = hullCol;
    ctx.strokeStyle = accentCol;
    ctx.lineWidth = 2;
    ctx.shadowColor = glowCol;
    ctx.shadowBlur = 8;

    ctx.beginPath();
    ctx.moveTo(this.x, this.y - 26);
    ctx.lineTo(this.x + 22 + tiltPx, this.y + 18);
    ctx.lineTo(this.x + 10, this.y + 12);
    ctx.lineTo(this.x + 8, this.y + 22);
    ctx.lineTo(this.x, this.y + 16);
    ctx.lineTo(this.x - 8, this.y + 22);
    ctx.lineTo(this.x - 10, this.y + 12);
    ctx.lineTo(this.x - 22 + tiltPx, this.y + 18);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Cockpit
    ctx.fillStyle = accentCol;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y - 18);
    ctx.lineTo(this.x + 4 + tiltPx / 2, this.y - 2);
    ctx.lineTo(this.x, this.y + 5);
    ctx.lineTo(this.x - 4 + tiltPx / 2, this.y - 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
}

// --- ASTEROIDS ---
class Asteroid {
  constructor(x, y, tier = 'large', vx, vy) {
    this.tier = tier;
    if (tier === 'large') {
      this.radius = 48;
      this.hp = 4;
      this.score = 50;
      this.baseSpeed = 1.6;
    } else if (tier === 'medium') {
      this.radius = 28;
      this.hp = 2;
      this.score = 25;
      this.baseSpeed = 2.4;
    } else {
      this.radius = 16;
      this.hp = 1;
      this.score = 10;
      this.baseSpeed = 3.4;
    }

    this.x = x !== undefined ? x : Math.random() * (WIDTH - 120) + 60;
    this.y = y !== undefined ? y : -this.radius * 2;
    this.vx = vx !== undefined ? vx : (Math.random() - 0.5) * 1.5;
    this.vy = vy !== undefined ? vy : this.baseSpeed * (0.8 + Math.random() * 0.4);
    this.angle = Math.random() * Math.PI * 2;
    this.rotSpeed = (Math.random() - 0.5) * 0.05;
    this.alive = true;
    this.hitFlash = 0;

    // Jagged vertices
    this.points = [];
    const numPoints = 12;
    for (let i = 0; i < numPoints; i++) {
      const ang = (i / numPoints) * Math.PI * 2;
      const r = this.radius * (0.8 + Math.random() * 0.4);
      this.points.push({ x: Math.cos(ang) * r, y: Math.sin(ang) * r });
    }
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.angle += this.rotSpeed;
    if (this.hitFlash > 0) this.hitFlash--;
    if (this.y - this.radius > HEIGHT + 40) this.alive = false;
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hitFlash = 4;
    if (this.hp <= 0) {
      this.alive = false;
      return true;
    }
    return false;
  }

  split() {
    if (this.tier === 'large') {
      return [
        new Asteroid(this.x - 14, this.y, 'medium', this.vx - 1.2, this.vy * 1.1),
        new Asteroid(this.x + 14, this.y, 'medium', this.vx + 1.2, this.vy * 1.1),
      ];
    } else if (this.tier === 'medium') {
      return [
        new Asteroid(this.x - 10, this.y, 'small', this.vx - 1.6, this.vy * 1.2),
        new Asteroid(this.x + 10, this.y, 'small', this.vx + 1.6, this.vy * 1.2),
      ];
    }
    return [];
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);

    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#5f697d';
    ctx.strokeStyle = '#91a0b9';
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(this.points[0].x, this.points[0].y);
    for (let i = 1; i < this.points.length; i++) {
      ctx.lineTo(this.points[i].x, this.points[i].y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
}

// --- ENEMIES ---
class Enemy {
  constructor(x, y, hp, score, speed, width, height) {
    this.x = x;
    this.y = y;
    this.maxHp = hp;
    this.hp = hp;
    this.score = score;
    this.speed = speed;
    this.width = width;
    this.height = height;
    this.alive = true;
    this.hitFlash = 0;
    this.shootTimer = 40 + Math.random() * 60;
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hitFlash = 4;
    if (this.hp <= 0) {
      this.alive = false;
      return true;
    }
    return false;
  }

  drawHealthBar(ctx) {
    if (this.hp < this.maxHp) {
      const ratio = Math.max(0, this.hp / this.maxHp);
      ctx.fillStyle = 'rgba(50, 10, 10, 0.8)';
      ctx.fillRect(this.x - 20, this.y - this.height / 2 - 10, 40, 4);
      ctx.fillStyle = ratio > 0.5 ? COLORS.green : (ratio > 0.25 ? COLORS.yellow : COLORS.red);
      ctx.fillRect(this.x - 20, this.y - this.height / 2 - 10, 40 * ratio, 4);
    }
  }
}

class Scout extends Enemy {
  constructor(x, y) {
    super(x || Math.random() * (WIDTH - 120) + 60, y || -40, 22, 50, 3.6, 34, 36);
    this.sineFreq = 0.05;
    this.sineAmp = 4.5;
    this.time = Math.random() * 100;
  }

  update(player) {
    this.time++;
    this.y += this.speed;
    this.x += Math.sin(this.time * this.sineFreq) * this.sineAmp;
    if (this.hitFlash > 0) this.hitFlash--;
    if (this.y > HEIGHT + 60) this.alive = false;
  }

  shoot() {
    this.shootTimer--;
    if (this.shootTimer <= 0) {
      this.shootTimer = 110 + Math.random() * 60;
      if (this.y > 20 && this.y < HEIGHT - 120) {
        return [new Projectile(this.x, this.y + 16, 0, 5.5, 12, COLORS.orange, 4)];
      }
    }
    return [];
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#2d140a';
    ctx.strokeStyle = COLORS.orange;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 18);
    ctx.lineTo(this.x + 16, this.y - 12);
    ctx.lineTo(this.x, this.y - 6);
    ctx.lineTo(this.x - 16, this.y - 12);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
}

class Fighter extends Enemy {
  constructor(x, y) {
    super(x || Math.random() * (WIDTH - 160) + 80, y || -50, 50, 100, 2.2, 44, 42);
    this.strafeVx = (Math.random() < 0.5 ? -1 : 1) * 1.4;
  }

  update(player) {
    this.y += this.speed;
    this.x += this.strafeVx;
    if (this.x < 70 || this.x > WIDTH - 70) this.strafeVx *= -1;
    if (this.hitFlash > 0) this.hitFlash--;
    if (this.y > HEIGHT + 60) this.alive = false;
  }

  shoot(player) {
    this.shootTimer--;
    if (this.shootTimer <= 0) {
      this.shootTimer = 90 + Math.random() * 50;
      if (this.y > 30 && this.y < HEIGHT - 150) {
        if (player && player.alive) {
          const dx = player.x - this.x;
          const dy = player.y - this.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 0) {
            return [new Projectile(this.x, this.y + 18, (dx / dist) * 6, (dy / dist) * 6, 16, COLORS.red, 4)];
          }
        }
        return [new Projectile(this.x, this.y + 18, 0, 6, 16, COLORS.red, 4)];
      }
    }
    return [];
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#320c12';
    ctx.strokeStyle = COLORS.red;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 20);
    ctx.lineTo(this.x + 22, this.y - 10);
    ctx.lineTo(this.x + 10, this.y - 16);
    ctx.lineTo(this.x, this.y - 8);
    ctx.lineTo(this.x - 10, this.y - 16);
    ctx.lineTo(this.x - 22, this.y - 10);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
}

class Tank extends Enemy {
  constructor(x, y) {
    super(x || Math.random() * (WIDTH - 200) + 100, y || -80, 160, 200, 1.1, 68, 62);
  }

  update() {
    this.y += this.speed;
    if (this.hitFlash > 0) this.hitFlash--;
    if (this.y > HEIGHT + 80) this.alive = false;
  }

  shoot() {
    this.shootTimer--;
    if (this.shootTimer <= 0) {
      this.shootTimer = 110 + Math.random() * 40;
      if (this.y > 40 && this.y < HEIGHT - 180) {
        return [
          new Projectile(this.x - 18, this.y + 24, -2, 5, 20, COLORS.purple, 5),
          new Projectile(this.x, this.y + 28, 0, 5.5, 24, COLORS.purple, 5),
          new Projectile(this.x + 18, this.y + 24, 2, 5, 20, COLORS.purple, 5),
        ];
      }
    }
    return [];
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#260f37';
    ctx.strokeStyle = '#aa46f0';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 30);
    ctx.lineTo(this.x + 28, this.y + 12);
    ctx.lineTo(this.x + 34, this.y - 18);
    ctx.lineTo(this.x + 14, this.y - 28);
    ctx.lineTo(this.x - 14, this.y - 28);
    ctx.lineTo(this.x - 34, this.y - 18);
    ctx.lineTo(this.x - 28, this.y + 12);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    this.drawHealthBar(ctx);
    ctx.restore();
  }
}

class Hunter extends Enemy {
  constructor(x, y) {
    super(x || Math.random() * (WIDTH - 160) + 80, y || -60, 80, 300, 2.5, 46, 48);
    this.trackingSpeed = 3.0;
  }

  update(player) {
    this.y += this.speed * 0.75;
    if (player && player.alive) {
      const dx = player.x - this.x;
      if (Math.abs(dx) > 10) {
        this.x += Math.sign(dx) * Math.min(Math.abs(dx), this.trackingSpeed);
      }
    }
    if (this.hitFlash > 0) this.hitFlash--;
    if (this.y > HEIGHT + 60) this.alive = false;
  }

  shoot(player) {
    this.shootTimer--;
    if (this.shootTimer <= 0) {
      this.shootTimer = 80 + Math.random() * 40;
      if (this.y > 40 && this.y < HEIGHT - 150) {
        if (player && player.alive && Math.random() < 0.6) {
          return [new TrackingBullet(this.x, this.y + 20, player)];
        } else {
          return [
            new Projectile(this.x - 12, this.y + 18, -1, 6.5, 16, COLORS.cyan, 4),
            new Projectile(this.x + 12, this.y + 18, 1, 6.5, 16, COLORS.cyan, 4),
          ];
        }
      }
    }
    return [];
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#0a2332';
    ctx.strokeStyle = COLORS.cyan;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 24);
    ctx.lineTo(this.x + 12, this.y + 14);
    ctx.lineTo(this.x + 24, this.y + 22);
    ctx.lineTo(this.x + 16, this.y - 18);
    ctx.lineTo(this.x, this.y - 10);
    ctx.lineTo(this.x - 16, this.y - 18);
    ctx.lineTo(this.x - 24, this.y + 22);
    ctx.lineTo(this.x - 12, this.y + 14);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    this.drawHealthBar(ctx);
    ctx.restore();
  }
}

// --- BOSSES ---
class SectorBoss {
  constructor() {
    this.name = 'SECTOR GUARDIAN';
    this.maxHp = 1200;
    this.hp = this.maxHp;
    this.score = 5000;
    this.width = 160;
    this.height = 110;
    this.x = WIDTH / 2;
    this.y = -120;
    this.targetY = 130;
    this.vx = 2.5;
    this.alive = true;
    this.isEntering = true;
    this.phase = 1;
    this.enraged = false;
    this.hitFlash = 0;
    this.attackTimer = 0;
    this.attackMode = 0;
    this.bulletAngle = 0;
  }

  takeDamage(amount) {
    if (this.isEntering) return false;
    this.hp -= amount;
    this.hitFlash = 4;
    if (this.hp <= 0) {
      this.hp = 0;
      this.alive = false;
      return true;
    }
    return false;
  }

  update(player, particles) {
    if (this.isEntering) {
      this.y += 2.0;
      if (this.y >= this.targetY) {
        this.y = this.targetY;
        this.isEntering = false;
      }
      return;
    }

    if (!this.enraged && this.hp <= this.maxHp * 0.5) {
      this.enraged = true;
      this.phase = 2;
      this.vx = 3.8;
      if (particles) {
        particles.createShockwave(this.x, this.y, COLORS.red, 120);
        particles.addFloatingText(this.x, this.y - 40, 'PHASE 2: ENRAGED!', COLORS.red);
      }
    }

    this.x += this.vx;
    if (this.x < 110 || this.x > WIDTH - 110) this.vx *= -1;
    if (this.hitFlash > 0) this.hitFlash--;
  }

  attack(player) {
    if (this.isEntering || !this.alive) return [];
    this.attackTimer++;
    const bullets = [];

    if (this.attackTimer % 180 === 0) {
      this.attackMode = (this.attackMode + 1) % 4;
    }

    if (this.attackMode === 0) {
      if (this.attackTimer % (this.enraged ? 18 : 26) === 0) {
        bullets.push(new Projectile(this.x - 55, this.y + 40, 0, 7, 18, COLORS.red, 5));
        bullets.push(new Projectile(this.x + 55, this.y + 40, 0, 7, 18, COLORS.red, 5));
      }
    } else if (this.attackMode === 1) {
      if (this.attackTimer % (this.enraged ? 45 : 65) === 0) {
        const angles = this.enraged ? [-0.4, -0.2, 0, 0.2, 0.4] : [-0.3, 0, 0.3];
        for (const ang of angles) {
          bullets.push(new Projectile(this.x, this.y + 50, Math.sin(ang) * 5.5, Math.cos(ang) * 5.5, 16, COLORS.orange, 5));
        }
      }
    } else if (this.attackMode === 2) {
      if (this.attackTimer % (this.enraged ? 10 : 18) === 0) {
        this.bulletAngle += 0.35;
        for (let i = 0; i < 4; i++) {
          const ang = this.bulletAngle + (i * Math.PI) / 2;
          bullets.push(new Projectile(this.x, this.y + 20, Math.cos(ang) * 4.8, Math.sin(ang) * 4.8, 15, COLORS.purple, 5));
        }
      }
    } else if (this.attackMode === 3) {
      if (this.attackTimer % 50 === 0) {
        if (player && player.alive) {
          bullets.push(new TrackingBullet(this.x, this.y + 35, player));
        }
        bullets.push(new Projectile(this.x - 40, this.y + 30, -1, 7, 18, COLORS.orange, 4));
        bullets.push(new Projectile(this.x + 40, this.y + 30, 1, 7, 18, COLORS.orange, 4));
      }
    }
    return bullets;
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#230c16';
    ctx.strokeStyle = this.enraged ? '#ff3c3c' : '#c82846';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 55);
    ctx.lineTo(this.x + 45, this.y + 35);
    ctx.lineTo(this.x + 78, this.y + 15);
    ctx.lineTo(this.x + 80, this.y - 35);
    ctx.lineTo(this.x + 40, this.y - 52);
    ctx.lineTo(this.x, this.y - 35);
    ctx.lineTo(this.x - 40, this.y - 52);
    ctx.lineTo(this.x - 80, this.y - 35);
    ctx.lineTo(this.x - 78, this.y + 15);
    ctx.lineTo(this.x - 45, this.y + 35);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Core Reactor
    ctx.fillStyle = this.enraged ? COLORS.red : COLORS.yellow;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class VoidDestroyer {
  constructor() {
    this.name = 'VOID DESTROYER';
    this.maxHp = 2600;
    this.hp = this.maxHp;
    this.score = 15000;
    this.width = 220;
    this.height = 140;
    this.x = WIDTH / 2;
    this.y = -150;
    this.targetY = 145;
    this.vx = 2.0;
    this.alive = true;
    this.isEntering = true;
    this.phase = 1;
    this.hitFlash = 0;
    this.attackTimer = 0;
    this.spiralStep = 0;
  }

  takeDamage(amount) {
    if (this.isEntering) return false;
    this.hp -= amount;
    this.hitFlash = 4;
    if (this.hp <= 0) {
      this.hp = 0;
      this.alive = false;
      return true;
    }
    return false;
  }

  update(player, particles) {
    if (this.isEntering) {
      this.y += 1.8;
      if (this.y >= this.targetY) {
        this.y = this.targetY;
        this.isEntering = false;
      }
      return;
    }

    const hpRatio = this.hp / this.maxHp;
    if (hpRatio <= 0.33 && this.phase < 3) {
      this.phase = 3;
      this.vx = 4.2;
      if (particles) {
        particles.createShockwave(this.x, this.y, COLORS.magenta, 180);
        particles.addFloatingText(this.x, this.y - 50, 'FINAL PHASE: VOID COLLAPSE!', COLORS.magenta);
      }
    } else if (hpRatio <= 0.66 && this.phase < 2) {
      this.phase = 2;
      this.vx = 3.0;
      if (particles) {
        particles.createShockwave(this.x, this.y, COLORS.purple, 140);
        particles.addFloatingText(this.x, this.y - 50, 'PHASE 2: MAXIMUM FIREPOWER!', COLORS.purple);
      }
    }

    this.x += this.vx;
    if (this.x < 130 || this.x > WIDTH - 130) this.vx *= -1;
    if (this.hitFlash > 0) this.hitFlash--;
  }

  attack(player) {
    if (this.isEntering || !this.alive) return [];
    this.attackTimer++;
    const bullets = [];

    if (this.phase === 1) {
      if (this.attackTimer % 20 === 0) {
        bullets.push(new Projectile(this.x - 75, this.y + 45, -0.5, 6.5, 18, COLORS.magenta, 5));
        bullets.push(new Projectile(this.x - 30, this.y + 60, 0, 7.0, 20, COLORS.magenta, 5));
        bullets.push(new Projectile(this.x + 30, this.y + 60, 0, 7.0, 20, COLORS.magenta, 5));
        bullets.push(new Projectile(this.x + 75, this.y + 45, 0.5, 6.5, 18, COLORS.magenta, 5));
      }
    } else if (this.phase === 2) {
      if (this.attackTimer % 8 === 0) {
        this.spiralStep += 0.32;
        for (let i = 0; i < 3; i++) {
          const ang = this.spiralStep + (i * Math.PI * 2) / 3;
          bullets.push(new Projectile(this.x - 50, this.y + 35, Math.cos(ang) * 5, Math.sin(ang) * 5, 16, COLORS.purple, 5));
          bullets.push(new Projectile(this.x + 50, this.y + 35, -Math.cos(ang) * 5, Math.sin(ang) * 5, 16, COLORS.cyan, 5));
        }
      }
    } else if (this.phase === 3) {
      if (this.attackTimer % 6 === 0) {
        this.spiralStep += 0.28;
        for (let i = 0; i < 4; i++) {
          const ang = this.spiralStep + (i * Math.PI) / 2;
          bullets.push(new Projectile(this.x, this.y + 45, Math.cos(ang) * 5.5, Math.sin(ang) * 5.5, 18, COLORS.magenta, 5));
        }
      }
    }
    return bullets;
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    ctx.fillStyle = this.hitFlash > 0 ? '#ffffff' : '#14081e';
    ctx.strokeStyle = this.phase === 3 ? COLORS.magenta : COLORS.purple;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y + 70);
    ctx.lineTo(this.x + 50, this.y + 45);
    ctx.lineTo(this.x + 105, this.y + 25);
    ctx.lineTo(this.x + 110, this.y - 40);
    ctx.lineTo(this.x + 60, this.y - 70);
    ctx.lineTo(this.x, this.y - 45);
    ctx.lineTo(this.x - 60, this.y - 70);
    ctx.lineTo(this.x - 110, this.y - 40);
    ctx.lineTo(this.x - 105, this.y + 25);
    ctx.lineTo(this.x - 50, this.y + 45);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Central Void Core
    ctx.fillStyle = this.phase === 3 ? COLORS.magenta : COLORS.purple;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 22, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

// --- COLLECTIBLE POWERUPS ---
class PowerUp {
  constructor(x, y, type) {
    this.types = ['shield', 'rapid_fire', 'health', 'laser', 'double_shot'];
    this.type = type || this.types[Math.floor(Math.random() * this.types.length)];
    this.x = x;
    this.y = y;
    this.vy = 1.6;
    this.radius = 16;
    this.alive = true;

    this.colors = {
      shield: COLORS.cyan,
      rapid_fire: COLORS.yellow,
      health: COLORS.green,
      laser: COLORS.magenta,
      double_shot: COLORS.orange,
    };
    this.labels = {
      shield: 'S',
      rapid_fire: 'R',
      health: '+',
      laser: 'L',
      double_shot: 'D',
    };
  }

  update() {
    this.y += this.vy;
    if (this.y - this.radius > HEIGHT + 40) this.alive = false;
  }

  draw(ctx) {
    if (!this.alive) return;
    ctx.save();
    const col = this.colors[this.type];
    ctx.shadowColor = col;
    ctx.shadowBlur = 15;
    ctx.fillStyle = '#0f1423';
    ctx.strokeStyle = col;
    ctx.lineWidth = 2;

    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const ang = (i / 6) * Math.PI * 2;
      const hx = this.x + Math.cos(ang) * this.radius;
      const hy = this.y + Math.sin(ang) * this.radius;
      if (i === 0) ctx.moveTo(hx, hy);
      else ctx.lineTo(hx, hy);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px Orbitron, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.labels[this.type], this.x, this.y);
    ctx.restore();
  }
}

// --- MASTER GAME ENGINE ---
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.sound = new SoundManager();
    this.starfield = new Starfield();
    this.particles = new ParticleSystem();

    this.state = 'MENU'; // MENU, PLAYING, PAUSED, BOSS_FIGHT, GAME_OVER, VICTORY, SETTINGS, HIGH_SCORES
    this.score = 0;
    this.displayedScore = 0;
    this.level = 1;
    this.levelTransitionTimer = 0;
    this.screenShake = 0;

    this.player = null;
    this.playerBullets = [];
    this.enemyBullets = [];
    this.asteroids = [];
    this.enemies = [];
    this.boss = null;
    this.powerups = [];

    this.waveTimer = 0;
    this.spawnInterval = 90;
    this.keys = {};
    this.mouse = { x: 0, y: 0, clicked: false };

    this.highscores = this.loadHighScores();
    this.settings = { music: true, sfx: true, shake: true, difficulty: 'NORMAL' };

    // Theming System
    this.themeName = localStorage.getItem('nebula_theme') || 'CYBER_NEON';
    this.theme = THEMES[this.themeName] || THEMES.CYBER_NEON;
    this.themeToastTimer = 0;

    // Combat Damage & Out System
    this.damageVignette = 0;
    this.totalDamageDealt = 0;
    this.totalDamageTaken = 0;
    this.enemiesKilled = 0;
    this.asteroidsDestroyed = 0;

    this.outBannerTimer = 0;
    this.respawnTimer = 0;
    this.isRespawning = false;
    this.hitstopFrames = 0;

    this.initInputs();
    this.initButtons();
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  cycleTheme() {
    const keys = Object.keys(THEMES);
    const idx = (keys.indexOf(this.themeName) + 1) % keys.length;
    this.themeName = keys[idx];
    this.theme = THEMES[this.themeName];
    try {
      localStorage.setItem('nebula_theme', this.themeName);
    } catch (e) {}
    this.themeToastTimer = 90;
    this.sound.play('powerup');
  }

  loadHighScores() {
    try {
      const saved = localStorage.getItem('nebula_highscores');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return [
      { score: 15000, level: 8, date: '2026-09-20' },
      { score: 12500, level: 6, date: '2026-09-18' },
      { score: 9800, level: 5, date: '2026-09-15' },
      { score: 7500, level: 4, date: '2026-09-12' },
      { score: 5200, level: 3, date: '2026-09-10' },
    ];
  }

  saveHighScore() {
    const today = new Date().toISOString().split('T')[0];
    this.highscores.push({ score: this.score, level: this.level, date: today });
    this.highscores.sort((a, b) => b.score - a.score);
    this.highscores = this.highscores.slice(0, 10);
    try {
      localStorage.setItem('nebula_highscores', JSON.stringify(this.highscores));
    } catch (e) {}
  }

  initInputs() {
    window.addEventListener('keydown', (e) => {
      this.keys[e.code] = true;
      if (e.code === 'KeyT') {
        this.cycleTheme();
      } else if (e.code === 'KeyP') {
        if (this.state === 'PLAYING' || this.state === 'BOSS_FIGHT') this.state = 'PAUSED';
        else if (this.state === 'PAUSED') this.state = this.boss ? 'BOSS_FIGHT' : 'PLAYING';
      } else if (e.code === 'Escape') {
        if (this.state === 'PLAYING' || this.state === 'BOSS_FIGHT') this.state = 'PAUSED';
        else if (['SETTINGS', 'HIGH_SCORES'].includes(this.state)) this.state = 'MENU';
      }
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.code] = false;
    });

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = WIDTH / rect.width;
      const scaleY = HEIGHT / rect.height;
      this.mouse.x = (e.clientX - rect.left) * scaleX;
      this.mouse.y = (e.clientY - rect.top) * scaleY;
    });

    this.canvas.addEventListener('mousedown', (e) => {
      if (e.button === 0) {
        this.mouse.clicked = true;
        this.sound.ensureContext();
      }
    });

    // Header buttons
    document.getElementById('btn-theme-toggle')?.addEventListener('click', () => {
      this.cycleTheme();
    });

    document.getElementById('btn-audio-toggle')?.addEventListener('click', (e) => {
      this.sound.enabled = !this.sound.enabled;
      e.target.textContent = `🔊 AUDIO: ${this.sound.enabled ? 'ON' : 'OFF'}`;
      this.sound.ensureContext();
    });

    document.getElementById('btn-fullscreen')?.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  initButtons() {
    const cx = WIDTH / 2 - 120;
    this.menuBtns = [
      { x: cx, y: 310, w: 240, h: 50, text: '▶  PLAY', action: () => this.resetGame() },
      { x: cx, y: 380, w: 240, h: 50, text: '⚙  SETTINGS', action: () => (this.state = 'SETTINGS') },
      { x: cx, y: 450, w: 240, h: 50, text: '🏆  HIGH SCORES', action: () => (this.state = 'HIGH_SCORES') },
    ];

    this.pauseBtns = [
      { x: cx, y: 280, w: 240, h: 50, text: '▶  RESUME', action: () => (this.state = this.boss ? 'BOSS_FIGHT' : 'PLAYING') },
      { x: cx, y: 350, w: 240, h: 50, text: '⚙  SETTINGS', action: () => (this.state = 'SETTINGS') },
      { x: cx, y: 420, w: 240, h: 50, text: '🏠  MAIN MENU', action: () => (this.state = 'MENU') },
    ];

    this.gameOverBtns = [
      { x: cx, y: 440, w: 240, h: 50, text: '▶  PLAY AGAIN', action: () => this.resetGame() },
      { x: cx, y: 510, w: 240, h: 50, text: '🏠  MAIN MENU', action: () => (this.state = 'MENU') },
    ];

    this.settingsBtns = [
      {
        x: cx,
        y: 430,
        w: 240,
        h: 46,
        text: 'CYCLE THEME (T)',
        action: () => this.cycleTheme(),
      },
      {
        x: cx,
        y: 490,
        w: 240,
        h: 46,
        text: 'DIFFICULTY',
        action: () => {
          const diffs = ['EASY', 'NORMAL', 'HARD'];
          const idx = (diffs.indexOf(this.settings.difficulty) + 1) % diffs.length;
          this.settings.difficulty = diffs[idx];
        },
      },
      { x: cx, y: 550, w: 240, h: 46, text: '◀  BACK', action: () => (this.state = 'MENU') },
    ];

    this.highScoreBtns = [{ x: cx, y: 580, w: 240, h: 50, text: '◀  BACK', action: () => (this.state = 'MENU') }];
  }

  resetGame() {
    this.score = 0;
    this.displayedScore = 0;
    this.level = 1;
    this.player = new Player();
    this.playerBullets = [];
    this.enemyBullets = [];
    this.asteroids = [];
    this.enemies = [];
    this.boss = null;
    this.powerups = [];
    this.particles.clear();
    this.levelTransitionTimer = 120;
    this.state = 'PLAYING';

    this.damageVignette = 0;
    this.totalDamageDealt = 0;
    this.totalDamageTaken = 0;
    this.enemiesKilled = 0;
    this.asteroidsDestroyed = 0;
    this.outBannerTimer = 0;
    this.respawnTimer = 0;
    this.isRespawning = false;
    this.hitstopFrames = 0;
  }

  triggerScreenShake(intensity = 10) {
    if (this.settings.shake) {
      this.screenShake = Math.min(22, this.screenShake + intensity);
    }
  }

  spawnWave() {
    if (this.level === 1) {
      this.asteroids.push(new Asteroid());
    } else if (this.level === 2) {
      if (Math.random() < 0.5) this.asteroids.push(new Asteroid());
      else this.enemies.push(new Scout());
    } else if (this.level === 3) {
      const r = Math.random();
      if (r < 0.4) this.asteroids.push(new Asteroid());
      else if (r < 0.7) this.enemies.push(new Scout());
      else this.enemies.push(new Fighter());
    } else if (this.level === 4) {
      const r = Math.random();
      if (r < 0.25) this.asteroids.push(new Asteroid());
      else if (r < 0.5) this.enemies.push(new Fighter());
      else if (r < 0.75) this.enemies.push(new Tank());
      else this.enemies.push(new Hunter());
    } else if (this.level === 5) {
      if (!this.boss) {
        this.boss = new SectorBoss();
        this.sound.play('boss_warning');
        this.state = 'BOSS_FIGHT';
      }
    } else if (this.level >= 6 && this.level < 10) {
      const r = Math.random();
      if (r < 0.2) this.asteroids.push(new Asteroid());
      else if (r < 0.4) this.enemies.push(new Scout());
      else if (r < 0.65) this.enemies.push(new Fighter());
      else if (r < 0.85) this.enemies.push(new Hunter());
      else this.enemies.push(new Tank());
    } else if (this.level >= 10) {
      if (!this.boss) {
        this.boss = new VoidDestroyer();
        this.sound.play('boss_warning');
        this.state = 'BOSS_FIGHT';
      }
    }
  }

  updateCollisions() {
    const now = Date.now();

    // 1. Player Bullets vs Asteroids
    for (const b of this.playerBullets) {
      if (!b.alive) continue;
      for (const a of this.asteroids) {
        if (!a.alive) continue;
        const dist = Math.hypot(b.x - a.x, b.y - a.y);
        if (dist < b.radius + a.radius) {
          const destroyed = a.takeDamage(b.damage);
          this.sound.play('hit');
          this.particles.addDamagePopup(a.x, a.y - 10, b.damage, false);
          this.totalDamageDealt += b.damage;
          if (!b.piercing) b.alive = false;

          if (destroyed) {
            this.score += a.score;
            this.asteroidsDestroyed++;
            this.sound.play('explosion');
            this.particles.createAsteroidDebris(a.x, a.y, 14);
            const pieces = a.split();
            this.asteroids.push(...pieces);
            if (Math.random() < 0.22) this.powerups.push(new PowerUp(a.x, a.y));
          }
          break;
        }
      }
    }

    // 2. Player Bullets vs Enemies
    for (const b of this.playerBullets) {
      if (!b.alive) continue;
      for (const e of this.enemies) {
        if (!e.alive) continue;
        const dist = Math.hypot(b.x - e.x, b.y - e.y);
        if (dist < b.radius + e.width / 2) {
          const isCrit = b instanceof MegaLaserBeam || Math.random() < 0.2;
          const destroyed = e.takeDamage(b.damage);
          this.sound.play('hit');
          this.particles.addDamagePopup(e.x, e.y - 12, b.damage, isCrit);
          this.totalDamageDealt += b.damage;
          if (!b.piercing) b.alive = false;

          if (destroyed) {
            this.score += e.score;
            this.enemiesKilled++;
            this.sound.play('explosion');
            this.particles.createExplosion(e.x, e.y, COLORS.orange, 24);
            this.particles.addFloatingText(e.x, e.y, `+${e.score}`);
            this.triggerScreenShake(6);
            if (Math.random() < 0.22) this.powerups.push(new PowerUp(e.x, e.y));
          }
          break;
        }
      }
    }

    // 3. Player Bullets vs Boss
    if (this.boss && this.boss.alive && !this.boss.isEntering) {
      for (const b of this.playerBullets) {
        if (!b.alive) continue;
        const dist = Math.hypot(b.x - this.boss.x, b.y - this.boss.y);
        if (dist < b.radius + this.boss.width / 2) {
          const destroyed = this.boss.takeDamage(b.damage);
          this.sound.play('hit');
          this.particles.addDamagePopup(this.boss.x + (Math.random() * 50 - 25), this.boss.y + 10, b.damage, true);
          this.totalDamageDealt += b.damage;
          if (!b.piercing) b.alive = false;

          if (destroyed) {
            this.score += this.boss.score;
            this.enemiesKilled++;
            this.sound.play('explosion');
            for (let i = 0; i < 8; i++) {
              this.particles.createExplosion(
                this.boss.x + (Math.random() - 0.5) * this.boss.width,
                this.boss.y + (Math.random() - 0.5) * this.boss.height,
                COLORS.red,
                32
              );
            }
            this.triggerScreenShake(18);
            if (this.boss instanceof VoidDestroyer) {
              this.state = 'VICTORY';
              this.saveHighScore();
            } else {
              this.boss = null;
              this.level++;
              this.levelTransitionTimer = 120;
              this.state = 'PLAYING';
            }
          }
          break;
        }
      }
    }

    if (!this.player || !this.player.alive || this.isRespawning) return;

    // 4. Enemy Bullets vs Player
    for (const eb of this.enemyBullets) {
      if (!eb.alive) continue;
      const dist = Math.hypot(eb.x - this.player.x, eb.y - this.player.y);
      if (dist < eb.radius + 20) {
        eb.alive = false;
        this.totalDamageTaken += eb.damage;
        const died = this.player.takeDamage(eb.damage, now, this.particles, this);
        this.sound.play('player_damage');
        this.triggerScreenShake(8);
        if (died) this.handlePlayerOut();
        break;
      }
    }

    // 5. Asteroids & Enemies vs Player (Crash)
    for (const a of this.asteroids) {
      if (!a.alive) continue;
      const dist = Math.hypot(a.x - this.player.x, a.y - this.player.y);
      if (dist < a.radius + 22) {
        a.alive = false;
        this.particles.createAsteroidDebris(a.x, a.y, 16);
        this.totalDamageTaken += 40;
        const died = this.player.takeDamage(40, now, this.particles, this);
        this.sound.play('player_damage');
        this.triggerScreenShake(12);
        if (died) this.handlePlayerOut();
        break;
      }
    }

    // 6. Powerups vs Player
    for (const pu of this.powerups) {
      if (!pu.alive) continue;
      const dist = Math.hypot(pu.x - this.player.x, pu.y - this.player.y);
      if (dist < pu.radius + 24) {
        pu.alive = false;
        this.player.applyPowerup(pu.type);
        this.sound.play('powerup');
        this.particles.addFloatingText(this.player.x, this.player.y - 30, `${pu.type.toUpperCase()}!`, this.theme.primary);
        this.particles.createShockwave(this.player.x, this.player.y, this.theme.primary, 50);
      }
    }
  }

  handlePlayerOut() {
    this.particles.createExplosion(this.player.x, this.player.y, this.theme.primary, 36, 8.5);
    this.sound.play('explosion');
    this.triggerScreenShake(20);
    this.damageVignette = 220;
    this.hitstopFrames = 8;
    this.player.outs++;
    this.player.lives--;

    if (this.player.outs < 3) {
      this.outBannerTimer = 140;
      this.isRespawning = true;
      this.respawnTimer = 2.0;
      this.player.alive = false;
    } else {
      this.outBannerTimer = 160;
      this.player.alive = false;
      this.sound.play('game_over');
      this.saveHighScore();
      setTimeout(() => {
        if (this.state === 'PLAYING' || this.state === 'BOSS_FIGHT') {
          this.state = 'GAME_OVER';
        }
      }, 1800);
    }
  }

  update(dt) {
    // Hitstop freeze frame handling
    if (this.hitstopFrames > 0) {
      this.hitstopFrames--;
      return;
    }

    const now = Date.now();
    this.starfield.update(this.state === 'PLAYING' || this.state === 'BOSS_FIGHT' ? 2.0 : 1.0);
    this.particles.update();

    // Decay timers
    if (this.screenShake > 0) {
      this.screenShake = Math.max(0, this.screenShake - 35 * dt);
    }
    if (this.themeToastTimer > 0) this.themeToastTimer--;
    if (this.outBannerTimer > 0) this.outBannerTimer--;
    if (this.damageVignette > 0) {
      this.damageVignette = Math.max(0, this.damageVignette - 180 * dt);
    }

    // Respawn countdown handling
    if (this.isRespawning) {
      this.respawnTimer -= dt;
      if (this.respawnTimer <= 0) {
        this.isRespawning = false;
        this.player.alive = true;
        this.player.respawn();
        this.particles.createWarpInEffect(this.player.x, this.player.y, this.theme.primary);
        this.sound.play('powerup');
      }
    }

    // Roll score
    const diff = this.score - this.displayedScore;
    if (diff > 0) this.displayedScore += Math.max(1, Math.floor(diff * 0.15));

    if (this.state === 'PLAYING' || this.state === 'BOSS_FIGHT') {
      if (this.levelTransitionTimer > 0) this.levelTransitionTimer--;

      // Player input
      if (this.player && this.player.alive) {
        this.player.handleInput(this.keys);
        this.player.update(dt, this.particles, this.theme);
        if (this.keys['Space']) {
          const newBullets = this.player.shoot(now, this.theme);
          if (newBullets.length > 0) {
            this.playerBullets.push(...newBullets);
            this.sound.play('shoot');
          }
        }
      }

      // Bullets
      this.playerBullets.forEach((b) => b.update());
      this.playerBullets = this.playerBullets.filter((b) => b.alive);
      this.enemyBullets.forEach((b) => b.update());
      this.enemyBullets = this.enemyBullets.filter((b) => b.alive);

      // Asteroids & Enemies
      this.asteroids.forEach((a) => a.update());
      this.asteroids = this.asteroids.filter((a) => a.alive);
      this.enemies.forEach((e) => {
        e.update(this.player);
        const eb = e.shoot(this.player);
        if (eb.length > 0) this.enemyBullets.push(...eb);
      });
      this.enemies = this.enemies.filter((e) => e.alive);

      // Boss
      if (this.boss && this.boss.alive) {
        this.boss.update(this.player, this.particles);
        const bb = this.boss.attack(this.player);
        if (bb.length > 0) this.enemyBullets.push(...bb);
      }

      // Powerups
      this.powerups.forEach((p) => p.update());
      this.powerups = this.powerups.filter((p) => p.alive);

      // Wave Spawner
      if (this.state === 'PLAYING') {
        this.waveTimer++;
        if (this.waveTimer >= this.spawnInterval) {
          this.waveTimer = 0;
          this.spawnWave();
        }
        if (this.score >= this.level * 1800 && !this.boss) {
          this.level++;
          this.levelTransitionTimer = 120;
          this.sound.play('powerup');
          if (this.level === 5 || this.level === 10) this.spawnWave();
        }
      }

      this.updateCollisions();
    }
  }

  drawButtons(buttons) {
    for (const btn of buttons) {
      const isHover =
        this.mouse.x >= btn.x &&
        this.mouse.x <= btn.x + btn.w &&
        this.mouse.y >= btn.y &&
        this.mouse.y <= btn.y + btn.h;

      if (isHover && this.mouse.clicked) {
        btn.action();
        this.mouse.clicked = false;
      }

      const primary = this.theme && this.theme.primary ? this.theme.primary : COLORS.cyan;
      const panelBg = this.theme && this.theme.panelBg ? this.theme.panelBg : 'rgba(12, 18, 40, 0.85)';

      this.ctx.save();
      this.ctx.fillStyle = isHover ? 'rgba(255, 255, 255, 0.15)' : panelBg;
      this.ctx.strokeStyle = isHover ? '#ffffff' : primary;
      this.ctx.lineWidth = 2;
      this.ctx.fillRect(btn.x, btn.y, btn.w, btn.h);
      this.ctx.strokeRect(btn.x, btn.y, btn.w, btn.h);

      this.ctx.fillStyle = isHover ? '#ffffff' : primary;
      this.ctx.font = 'bold 18px Orbitron, sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText(btn.text, btn.x + btn.w / 2, btn.y + btn.h / 2);
      this.ctx.restore();
    }
  }

  drawDamageVignette(ctx) {
    let alpha = this.damageVignette / 255;
    if (this.player && this.player.alive && this.player.hp / this.player.maxHp <= 0.30) {
      const pulse = 0.25 + 0.15 * Math.sin(Date.now() * 0.007);
      alpha = Math.max(alpha, pulse);
    }
    if (alpha <= 0.01) return;

    ctx.save();
    const thick = 36;
    ctx.fillStyle = `rgba(220, 20, 40, ${Math.min(0.85, alpha)})`;
    ctx.fillRect(0, 0, WIDTH, thick);
    ctx.fillRect(0, HEIGHT - thick, WIDTH, thick);
    ctx.fillRect(0, 0, thick, HEIGHT);
    ctx.fillRect(WIDTH - thick, 0, thick, HEIGHT);
    ctx.restore();
  }

  drawOutBanner(ctx) {
    if (this.outBannerTimer <= 0) return;
    ctx.save();
    const bannerH = 140;
    const by = (HEIGHT - bannerH) / 2;
    ctx.fillStyle = 'rgba(16, 6, 10, 0.92)';
    ctx.fillRect(0, by, WIDTH, bannerH);
    ctx.strokeStyle = COLORS.red;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, by);
    ctx.lineTo(WIDTH, by);
    ctx.moveTo(0, by + bannerH);
    ctx.lineTo(WIDTH, by + bannerH);
    ctx.stroke();

    ctx.textAlign = 'center';
    if (this.player && this.player.outs < 3) {
      ctx.font = '900 44px Orbitron, sans-serif';
      ctx.fillStyle = '#ff4b4b';
      ctx.shadowColor = '#ff2222';
      ctx.shadowBlur = 15;
      ctx.fillText(`💥 OUT ${this.player.outs} OF 3 💥`, WIDTH / 2, HEIGHT / 2 - 14);

      ctx.font = 'bold 20px Orbitron, sans-serif';
      ctx.fillStyle = COLORS.yellow;
      ctx.shadowBlur = 0;
      ctx.fillText(`WARPING REINFORCEMENTS IN ${Math.max(1, Math.ceil(this.respawnTimer))}s...`, WIDTH / 2, HEIGHT / 2 + 28);
    } else {
      ctx.font = '900 46px Orbitron, sans-serif';
      ctx.fillStyle = COLORS.red;
      ctx.shadowColor = COLORS.red;
      ctx.shadowBlur = 20;
      ctx.fillText('💀 STRIKE 3 — ALL OUT! 💀', WIDTH / 2, HEIGHT / 2 - 14);

      ctx.font = 'bold 18px Orbitron, sans-serif';
      ctx.fillStyle = '#ffffff';
      ctx.shadowBlur = 0;
      ctx.fillText('MISSION COMPROMISED — INITIATING DEBRIEFING...', WIDTH / 2, HEIGHT / 2 + 28);
    }
    ctx.restore();
  }

  drawThemeToast(ctx) {
    if (this.themeToastTimer <= 0) return;
    const alpha = Math.min(1.0, this.themeToastTimer / 25.0);
    ctx.save();
    ctx.globalAlpha = alpha;
    const pillW = 380;
    const pillH = 46;
    const px = (WIDTH - pillW) / 2;
    const py = 76;
    ctx.fillStyle = this.theme.panelBg || 'rgba(12, 18, 40, 0.9)';
    ctx.fillRect(px, py, pillW, pillH);
    ctx.strokeStyle = this.theme.primary;
    ctx.lineWidth = 2;
    ctx.strokeRect(px, py, pillW, pillH);

    ctx.font = 'bold 16px Orbitron, sans-serif';
    ctx.fillStyle = this.theme.primary;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`🎨 THEME: ${this.theme.name}`, WIDTH / 2, py + pillH / 2);
    ctx.restore();
  }

  drawHUD() {
    this.ctx.save();
    const primary = this.theme && this.theme.primary ? this.theme.primary : COLORS.cyan;
    const shieldCol = this.theme && this.theme.shield ? this.theme.shield : COLORS.cyan;
    const borderCol = this.theme && this.theme.panelBorder ? this.theme.panelBorder : 'rgba(0, 240, 255, 0.3)';
    const bgCol = this.theme && this.theme.panelBg ? this.theme.panelBg : 'rgba(8, 12, 28, 0.75)';

    // Top Bar Background
    this.ctx.fillStyle = bgCol;
    this.ctx.fillRect(0, 0, WIDTH, 65);
    this.ctx.strokeStyle = borderCol;
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.moveTo(0, 65);
    this.ctx.lineTo(WIDTH, 65);
    this.ctx.stroke();

    // Score & Level
    this.ctx.font = 'bold 20px Orbitron, sans-serif';
    this.ctx.fillStyle = COLORS.white;
    this.ctx.textAlign = 'left';
    this.ctx.fillText(`SCORE: ${String(this.displayedScore).padStart(7, '0')}`, 25, 28);
    this.ctx.fillStyle = primary;
    this.ctx.fillText(`LEVEL: ${String(this.level).padStart(2, '0')}`, 25, 52);

    // HP & Shield Bars
    const hpX = 260;
    const barW = 140;
    const hpRatio = this.player ? Math.max(0, this.player.hp / this.player.maxHp) : 0;
    this.ctx.fillStyle = 'rgba(40, 15, 20, 0.9)';
    this.ctx.fillRect(hpX, 16, barW, 14);
    this.ctx.fillStyle = hpRatio > 0.5 ? COLORS.green : (hpRatio > 0.25 ? COLORS.yellow : COLORS.red);
    this.ctx.fillRect(hpX, 16, barW * hpRatio, 14);
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.strokeRect(hpX, 16, barW, 14);

    const shieldRatio = this.player ? Math.max(0, this.player.shield / this.player.maxShield) : 0;
    this.ctx.fillStyle = 'rgba(10, 25, 45, 0.9)';
    this.ctx.fillRect(hpX, 38, barW, 14);
    this.ctx.fillStyle = shieldCol;
    this.ctx.fillRect(hpX, 38, barW * shieldRatio, 14);
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.strokeRect(hpX, 38, barW, 14);

    this.ctx.font = 'bold 12px Orbitron, sans-serif';
    this.ctx.fillStyle = COLORS.white;
    this.ctx.fillText('HP', hpX + barW + 8, 28);
    this.ctx.fillStyle = shieldCol;
    this.ctx.fillText('SHIELD', hpX + barW + 8, 50);

    // 3-Slot Arcade Out Tracker
    const outsX = 490;
    this.ctx.fillStyle = COLORS.gray;
    this.ctx.fillText('OUTS:', outsX, 40);
    for (let i = 0; i < 3; i++) {
      const ox = outsX + 50 + i * 26;
      const oy = 26;
      if (this.player && i < this.player.outs) {
        // Red X Struck Out Box
        this.ctx.fillStyle = 'rgba(50, 10, 15, 0.85)';
        this.ctx.fillRect(ox, oy, 20, 20);
        this.ctx.strokeStyle = COLORS.red;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(ox, oy, 20, 20);
        this.ctx.strokeStyle = COLORS.red;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(ox + 4, oy + 4);
        this.ctx.lineTo(ox + 16, oy + 16);
        this.ctx.moveTo(ox + 16, oy + 4);
        this.ctx.lineTo(ox + 4, oy + 16);
        this.ctx.stroke();
      } else {
        // Active Ship Slot
        this.ctx.fillStyle = 'rgba(12, 24, 42, 0.85)';
        this.ctx.fillRect(ox, oy, 20, 20);
        this.ctx.strokeStyle = primary;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(ox, oy, 20, 20);
        this.ctx.fillStyle = primary;
        this.ctx.beginPath();
        this.ctx.moveTo(ox + 10, oy + 4);
        this.ctx.lineTo(ox + 16, oy + 16);
        this.ctx.lineTo(ox + 10, oy + 13);
        this.ctx.lineTo(ox + 4, oy + 16);
        this.ctx.closePath();
        this.ctx.fill();
      }
    }

    // Active Power-ups
    if (this.player) {
      let px = 680;
      for (const [key, val] of Object.entries(this.player.powerups)) {
        if (val > 0) {
          this.ctx.fillStyle = COLORS.yellow;
          this.ctx.fillText(`⚡ ${key.toUpperCase()}: ${Math.ceil(val)}s`, px, 40);
          px += 140;
        }
      }
    }

    // Boss Bar
    if (this.boss && this.boss.alive) {
      const bW = 480;
      const bX = (WIDTH - bW) / 2;
      const bRatio = Math.max(0, this.boss.hp / this.boss.maxHp);
      this.ctx.fillStyle = 'rgba(50, 10, 20, 0.9)';
      this.ctx.fillRect(bX, 80, bW, 16);
      this.ctx.fillStyle = this.boss.enraged || this.boss.phase === 3 ? COLORS.magenta : COLORS.red;
      this.ctx.fillRect(bX, 80, bW * bRatio, 16);
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.strokeRect(bX, 80, bW, 16);

      this.ctx.fillStyle = COLORS.yellow;
      this.ctx.textAlign = 'center';
      this.ctx.fillText(`${this.boss.name} [PHASE ${this.boss.phase}]`, WIDTH / 2, 74);
    }

    // Critical Hull Warning Alarm
    if (this.player && this.player.alive && this.player.hp / this.player.maxHp <= 0.30) {
      const pulse = 0.6 + 0.4 * Math.sin(Date.now() * 0.008);
      this.ctx.fillStyle = `rgba(220, 20, 40, ${pulse * 0.85})`;
      this.ctx.fillRect(WIDTH / 2 - 200, 75, 400, 24);
      this.ctx.strokeStyle = COLORS.red;
      this.ctx.lineWidth = 1;
      this.ctx.strokeRect(WIDTH / 2 - 200, 75, 400, 24);
      this.ctx.font = 'bold 12px Orbitron, sans-serif';
      this.ctx.fillStyle = '#ffffff';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('⚠️ CRITICAL HULL — EVASIVE ACTION ⚠️', WIDTH / 2, 91);
    }

    this.ctx.restore();
  }

  draw() {
    this.ctx.save();
    // Screen shake
    if (this.screenShake > 0) {
      const sx = (Math.random() - 0.5) * this.screenShake * 2;
      const sy = (Math.random() - 0.5) * this.screenShake * 2;
      this.ctx.translate(sx, sy);
    }

    const bgCol = this.theme && this.theme.bg ? this.theme.bg : COLORS.bg;
    this.ctx.fillStyle = bgCol;
    this.ctx.fillRect(0, 0, WIDTH, HEIGHT);

    this.starfield.draw(this.ctx);

    if (this.state === 'PLAYING' || this.state === 'BOSS_FIGHT' || this.state === 'PAUSED') {
      this.powerups.forEach((p) => p.draw(this.ctx));
      this.asteroids.forEach((a) => a.draw(this.ctx));
      this.enemies.forEach((e) => e.draw(this.ctx));
      if (this.boss) this.boss.draw(this.ctx);
      if (this.player) this.player.draw(this.ctx, this.theme);
      this.playerBullets.forEach((b) => b.draw(this.ctx));
      this.enemyBullets.forEach((b) => b.draw(this.ctx));
      this.particles.draw(this.ctx);
      this.drawHUD();
      this.drawDamageVignette(this.ctx);
      this.drawOutBanner(this.ctx);
      this.drawThemeToast(this.ctx);

      if (this.levelTransitionTimer > 0) {
        this.ctx.save();
        this.ctx.font = '900 52px Orbitron, sans-serif';
        this.ctx.fillStyle = this.theme.primary;
        this.ctx.textAlign = 'center';
        this.ctx.shadowColor = this.theme.primary;
        this.ctx.shadowBlur = 20;
        this.ctx.fillText(`— LEVEL ${this.level} —`, WIDTH / 2, HEIGHT / 2 - 20);
        this.ctx.restore();
      }
    }

    if (this.state === 'MENU') {
      this.particles.draw(this.ctx);
      this.ctx.save();
      this.ctx.font = '900 64px Orbitron, sans-serif';
      this.ctx.fillStyle = this.theme.primary;
      this.ctx.textAlign = 'center';
      this.ctx.shadowColor = this.theme.primary;
      this.ctx.shadowBlur = 25;
      this.ctx.fillText('NEBULA STRIKE', WIDTH / 2, 160);

      this.ctx.font = 'bold 22px Orbitron, sans-serif';
      this.ctx.fillStyle = this.theme.secondary;
      this.ctx.fillText(`— DEFEND THE GALAXY [${this.theme.name}] —`, WIDTH / 2, 215);

      this.ctx.font = 'bold 14px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.gray;
      this.ctx.fillText('PRESS [T] ANYTIME TO CYCLE THEMES', WIDTH / 2, 250);
      this.ctx.restore();

      this.drawThemeToast(this.ctx);
      this.drawButtons(this.menuBtns);
    } else if (this.state === 'PAUSED') {
      this.ctx.fillStyle = 'rgba(5, 8, 20, 0.8)';
      this.ctx.fillRect(0, 0, WIDTH, HEIGHT);
      this.ctx.save();
      this.ctx.font = 'bold 42px Orbitron, sans-serif';
      this.ctx.fillStyle = this.theme.primary;
      this.ctx.textAlign = 'center';
      this.ctx.fillText('GAME PAUSED', WIDTH / 2, 200);
      this.ctx.restore();
      this.drawButtons(this.pauseBtns);
    } else if (this.state === 'GAME_OVER') {
      this.ctx.fillStyle = 'rgba(16, 5, 8, 0.92)';
      this.ctx.fillRect(0, 0, WIDTH, HEIGHT);
      this.ctx.save();
      this.ctx.font = '900 48px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.red;
      this.ctx.textAlign = 'center';
      this.ctx.fillText('MISSION FAILED — ALL OUT', WIDTH / 2, 105);

      // Debriefing Panel
      const panelW = 580;
      const panelH = 265;
      const panelX = (WIDTH - panelW) / 2;
      const panelY = 140;
      this.ctx.fillStyle = 'rgba(25, 8, 12, 0.88)';
      this.ctx.fillRect(panelX, panelY, panelW, panelH);
      this.ctx.strokeStyle = 'rgba(255, 60, 60, 0.9)';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(panelX, panelY, panelW, panelH);

      const stats = [
        ['OUTS SUSTAINED:', '3 / 3 (ALL OUT)', COLORS.red],
        ['SECTOR REACHED:', `LEVEL ${this.level}`, this.theme.primary],
        ['FINAL COMBAT SCORE:', String(this.score).padStart(7, '0'), COLORS.white],
        ['TOTAL DAMAGE DEALT:', `${this.totalDamageDealt.toLocaleString()} HP`, COLORS.yellow],
        ['DAMAGE RECEIVED:', `${this.totalDamageTaken.toLocaleString()} HP`, '#ff8282'],
        ['ENEMIES ELIMINATED:', `${this.enemiesKilled} SHIPS`, COLORS.green],
        ['ASTEROIDS DEMOLISHED:', `${this.asteroidsDestroyed}`, '#abb9c4'],
      ];

      this.ctx.font = 'bold 15px Orbitron, sans-serif';
      stats.forEach(([label, val, col], i) => {
        const sy = panelY + 28 + i * 32;
        this.ctx.textAlign = 'left';
        this.ctx.fillStyle = COLORS.gray;
        this.ctx.fillText(label, panelX + 30, sy);
        this.ctx.textAlign = 'right';
        this.ctx.fillStyle = col;
        this.ctx.fillText(val, panelX + panelW - 30, sy);
      });
      this.ctx.restore();
      this.drawButtons(this.gameOverBtns);
    } else if (this.state === 'VICTORY') {
      this.ctx.fillStyle = 'rgba(5, 20, 25, 0.85)';
      this.ctx.fillRect(0, 0, WIDTH, HEIGHT);
      this.ctx.save();
      this.ctx.font = '900 52px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.green;
      this.ctx.textAlign = 'center';
      this.ctx.fillText('🌌 GALAXY SAVED 🌌', WIDTH / 2, 160);
      this.ctx.font = 'bold 24px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.yellow;
      this.ctx.fillText('VOID DESTROYER VANQUISHED!', WIDTH / 2, 230);
      this.ctx.fillStyle = COLORS.white;
      this.ctx.fillText(`VICTORY SCORE: ${String(this.score).padStart(7, '0')}`, WIDTH / 2, 290);
      this.ctx.restore();
      this.drawButtons(this.gameOverBtns);
    } else if (this.state === 'SETTINGS') {
      this.ctx.save();
      this.ctx.font = 'bold 42px Orbitron, sans-serif';
      this.ctx.fillStyle = this.theme.primary;
      this.ctx.textAlign = 'center';
      this.ctx.fillText('SETTINGS', WIDTH / 2, 140);

      this.ctx.font = 'bold 18px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.white;
      this.ctx.fillText(`ACTIVE THEME: ${this.theme.name}`, WIDTH / 2, 230);
      this.ctx.fillText(`CURRENT DIFFICULTY: ${this.settings.difficulty}`, WIDTH / 2, 280);
      this.ctx.restore();
      this.drawThemeToast(this.ctx);
      this.drawButtons(this.settingsBtns);
    } else if (this.state === 'HIGH_SCORES') {
      this.ctx.save();
      this.ctx.font = 'bold 42px Orbitron, sans-serif';
      this.ctx.fillStyle = COLORS.yellow;
      this.ctx.textAlign = 'center';
      this.ctx.fillText('🏆 TOP PILOTS LEADERBOARD', WIDTH / 2, 130);

      this.ctx.font = 'bold 16px Orbitron, sans-serif';
      this.ctx.fillStyle = this.theme.primary;
      this.ctx.fillText('RANK       SCORE        SECTOR        DATE', WIDTH / 2, 200);

      this.ctx.fillStyle = COLORS.white;
      this.highscores.slice(0, 8).forEach((item, idx) => {
        const row = `#${idx + 1}      ${String(item.score).padStart(7, '0')}      LVL ${String(item.level).padStart(2, '0')}       ${item.date}`;
        this.ctx.fillText(row, WIDTH / 2, 240 + idx * 36);
      });
      this.ctx.restore();
      this.drawButtons(this.highScoreBtns);
    }

    this.ctx.restore();
    this.mouse.clicked = false;
  }

  loop() {
    this.update(1 / 60);
    this.draw();
    requestAnimationFrame(this.loop);
  }
}

// Start Game on Page Load
window.addEventListener('DOMContentLoaded', () => {
  new Game();
});
