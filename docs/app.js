/**
 * FakePaste — Interactive Biometric Simulator & Demo Suite
 * Ported directly from core/typer.py and core/presets.py
 */

// ═══════════════════════════════════════════════════════════════════
// 1. PROCEDURAL MECHANICAL KEYBOARD AUDIO SYNTHESIZER (WEB AUDIO API)
// ═══════════════════════════════════════════════════════════════════

class MechanicalAudio {
  constructor() {
    this.ctx = null;
    this.enabled = false;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggle() {
    this.init();
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playKeyClick(isBackspace = false) {
    if (!this.enabled || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      // White noise buffer for crisp mechanical bottom-out click
      const bufferSize = this.ctx.sampleRate * 0.04;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }

      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = this.ctx.createBiquadFilter();
      filter.type = isBackspace ? 'lowpass' : 'bandpass';
      filter.frequency.setValueAtTime(isBackspace ? 800 : 2200 + (Math.random() * 600 - 300), t);
      filter.Q.setValueAtTime(3, t);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.08, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.035);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      noise.start(t);
      noise.stop(t + 0.035);
    } catch (e) {
      // Audio fallback silent
    }
  }
}

const audioSynth = new MechanicalAudio();

// ═══════════════════════════════════════════════════════════════════
// 2. QWERTY ADJACENCY MATRIX (MATCHING core/typer.py)
// ═══════════════════════════════════════════════════════════════════

const ADJACENT_KEYS = {
  'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx',
  'e': 'wsdfr', 'f': 'dertgcv', 'g': 'frtyhvb', 'h': 'gyujbn',
  'i': 'ujklo', 'j': 'huiknm', 'k': 'jiolm', 'l': 'kop',
  'm': 'njk', 'n': 'bhjm', 'o': 'iklp', 'p': 'ol',
  'q': 'wa', 'r': 'edfgt', 's': 'awedxz', 't': 'rfghy',
  'u': 'yhjki', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
  'y': 'tghju', 'z': 'asx',
  '1': '2q', '2': '13qw', '3': '24we', '4': '35er', '5': '46rt',
  '6': '57ty', '7': '68yu', '8': '79ui', '9': '80io', '0': '9op',
  ',': 'm.', '.': ',/', '/': '.'
};

// Built-in presets matching core/presets.py
const PRESETS = {
  slow: { wpm: 25, variation: 0.35, accuracy: 0.93 },
  normal: { wpm: 55, variation: 0.25, accuracy: 0.97 },
  fast: { wpm: 90, variation: 0.20, accuracy: 0.98 },
  blazing: { wpm: 130, variation: 0.15, accuracy: 0.99 }
};

// ═══════════════════════════════════════════════════════════════════
// 3. FAKEPASTE SIMULATION ENGINE (JS PORT)
// ═══════════════════════════════════════════════════════════════════

class FakePasteSimulator {
  constructor() {
    this.state = 'idle'; // idle | countdown | typing | paused | stopped | completed
    this.textToType = '';
    this.typedChars = [];
    this.charIndex = 0;
    this.timerId = null;

    // Config defaults
    this.wpm = 55;
    this.variation = 0.25;
    this.accuracy = 0.97;
    this.multiplier = 1.0;
    this.countdownSeconds = 3;

    // Stats
    this.totalKeystrokes = 0;
    this.typosMade = 0;
    this.correctionsMade = 0;
    this.startTime = 0;
    this.elapsedSeconds = 0;
    this.statsTimer = null;

    // DOM Elements
    this.dom = {
      textarea: document.getElementById('fpTextarea'),
      btnStart: document.getElementById('btnStart'),
      btnStop: document.getElementById('btnStop'),
      progressFill: document.getElementById('progressFill'),
      editorText: document.getElementById('editorText'),
      countdownOverlay: document.getElementById('countdownOverlay'),
      countdownNum: document.getElementById('countdownNum'),
      focusTag: document.getElementById('focusTag'),
      wpmRange: document.getElementById('wpmRange'),
      wpmVal: document.getElementById('wpmVal'),
      accRange: document.getElementById('accRange'),
      accVal: document.getElementById('accVal'),
      statWpm: document.getElementById('statWpm'),
      statAcc: document.getElementById('statAcc'),
      statChars: document.getElementById('statChars'),
      statTypos: document.getElementById('statTypos'),
      statElapsed: document.getElementById('statElapsed'),
      presetChips: document.querySelectorAll('.preset-chip'),
      modeTabs: document.querySelectorAll('.mode-tab'),
      recordingTimeline: document.getElementById('recordingTimeline'),
      timelineFill: document.getElementById('timelineFill'),
      btnPlayStep: document.getElementById('btnPlayStep'),
      dualGrid: document.getElementById('dualGrid'),
      videoContainer: document.getElementById('videoContainer')
    };

    this.isRecordingMode = false;
    this.recordingStep = 0;
    this.sampleText = "def synthesize_typing(cadence, variance):\n    # Simulate realistic human neuromuscular delay\n    latency = calculate_gaussian_jitter(cadence)\n    return apply_keystroke_physics(latency)";

    this.initEvents();
    this.setPreset('normal');
  }

  initEvents() {
    if (!this.dom.btnStart) return;

    this.dom.btnStart.addEventListener('click', () => {
      audioSynth.init();
      if (this.state === 'typing') {
        this.pause();
      } else if (this.state === 'paused') {
        this.resume();
      } else {
        this.start();
      }
    });

    this.dom.btnStop.addEventListener('click', () => this.emergencyStop());

    // Emergency stop via physical ESC key
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && (this.state === 'typing' || this.state === 'countdown')) {
        this.emergencyStop();
      }
    });

    // Preset chips
    this.dom.presetChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const presetKey = chip.dataset.preset;
        this.setPreset(presetKey);
      });
    });

    // Sliders
    this.dom.wpmRange.addEventListener('input', (e) => {
      this.wpm = parseInt(e.target.value, 10);
      this.dom.wpmVal.textContent = `${this.wpm} WPM`;
      this.clearActivePreset();
      if (window.renderCadenceWaveform) window.renderCadenceWaveform(this.wpm, this.variation);
    });

    this.dom.accRange.addEventListener('input', (e) => {
      this.accuracy = parseInt(e.target.value, 10) / 100;
      this.dom.accVal.textContent = `${Math.round(this.accuracy * 100)}%`;
      this.clearActivePreset();
    });

    // Studio Mode Switch (Sandbox vs Demo Recording)
    this.dom.modeTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        this.dom.modeTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const mode = tab.dataset.mode;
        this.switchMode(mode);
      });
    });

    if (this.dom.btnPlayStep) {
      this.dom.btnPlayStep.addEventListener('click', () => {
        this.playRecordingDemo();
      });
    }
  }

  setPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    this.wpm = p.wpm;
    this.variation = p.variation;
    this.accuracy = p.accuracy;

    this.dom.wpmRange.value = p.wpm;
    this.dom.wpmVal.textContent = `${p.wpm} WPM`;
    this.dom.accRange.value = Math.round(p.accuracy * 100);
    this.dom.accVal.textContent = `${Math.round(p.accuracy * 100)}%`;

    this.dom.presetChips.forEach(c => {
      c.classList.toggle('active', c.dataset.preset === key);
    });

    if (window.renderCadenceWaveform) window.renderCadenceWaveform(this.wpm, this.variation);
  }

  clearActivePreset() {
    this.dom.presetChips.forEach(c => c.classList.remove('active'));
  }

  switchMode(mode) {
    this.emergencyStop();
    if (mode === 'recording') {
      this.isRecordingMode = true;
      if (this.dom.recordingTimeline) this.dom.recordingTimeline.style.display = 'flex';
      if (this.dom.dualGrid) this.dom.dualGrid.style.display = 'grid';
      if (this.dom.videoContainer) this.dom.videoContainer.style.display = 'none';
      this.dom.textarea.value = this.sampleText;
      this.setPreset('normal');
      this.playRecordingDemo();
    } else if (mode === 'video') {
      this.isRecordingMode = false;
      if (this.dom.recordingTimeline) this.dom.recordingTimeline.style.display = 'none';
      if (this.dom.dualGrid) this.dom.dualGrid.style.display = 'none';
      if (this.dom.videoContainer) this.dom.videoContainer.style.display = 'flex';
    } else {
      this.isRecordingMode = false;
      if (this.dom.recordingTimeline) this.dom.recordingTimeline.style.display = 'none';
      if (this.dom.dualGrid) this.dom.dualGrid.style.display = 'grid';
      if (this.dom.videoContainer) this.dom.videoContainer.style.display = 'none';
      this.dom.textarea.value = "Realistic typing that passes velocity filters with ease.\nNo robotic clock-ticks. Just human rhythm.";
      this.resetEditor();
    }
  }

  resetEditor() {
    this.charIndex = 0;
    this.typedChars = [];
    this.dom.editorText.innerHTML = '<span class="typing-cursor"></span>';
    this.dom.progressFill.style.width = '0%';
    this.updateTelemetry();
  }

  start() {
    this.textToType = this.dom.textarea.value;
    if (!this.textToType || this.textToType.trim() === '') {
      this.dom.textarea.focus();
      return;
    }

    this.state = 'countdown';
    this.resetEditor();
    this.totalKeystrokes = 0;
    this.typosMade = 0;
    this.correctionsMade = 0;
    this.startTime = Date.now();
    this.startStatsTimer();

    this.dom.btnStart.textContent = '⏸ Pause';
    this.dom.countdownOverlay.classList.add('active');

    let count = this.countdownSeconds;
    this.dom.countdownNum.textContent = count;

    const countInterval = setInterval(() => {
      count--;
      if (count > 0) {
        this.dom.countdownNum.textContent = count;
        audioSynth.playKeyClick(true);
      } else {
        clearInterval(countInterval);
        this.dom.countdownOverlay.classList.remove('active');
        this.dom.focusTag.classList.add('focused');
        this.dom.focusTag.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Focused
        `;
        this.state = 'typing';
        this.stepTyping();
      }
    }, 1000);
  }

  pause() {
    this.state = 'paused';
    clearTimeout(this.timerId);
    this.dom.btnStart.textContent = '▶ Resume';
  }

  resume() {
    this.state = 'typing';
    this.dom.btnStart.textContent = '⏸ Pause';
    this.stepTyping();
  }

  emergencyStop() {
    this.state = 'stopped';
    clearTimeout(this.timerId);
    clearInterval(this.statsTimer);
    this.dom.countdownOverlay.classList.remove('active');
    this.dom.btnStart.textContent = '▶ Start Typing';
    this.dom.focusTag.classList.remove('focused');
    this.dom.focusTag.textContent = 'Target Idle';
  }

  stepTyping() {
    if (this.state !== 'typing') return;

    if (this.charIndex >= this.textToType.length) {
      this.state = 'completed';
      this.dom.btnStart.textContent = '▶ Type Again';
      this.dom.progressFill.style.width = '100%';
      this.updateTelemetry();
      return;
    }

    const targetChar = this.textToType[this.charIndex];

    // Check if we should inject a human typo
    const isLetter = /[a-zA-Z0-9]/.test(targetChar);
    const shouldMakeTypo = isLetter && (Math.random() > this.accuracy);

    if (shouldMakeTypo) {
      this.handleTypoSequence(targetChar);
    } else {
      this.typeCorrectChar(targetChar);
    }
  }

  typeCorrectChar(char) {
    this.typedChars.push({ char, isTypo: false });
    this.charIndex++;
    this.totalKeystrokes++;
    audioSynth.playKeyClick(false);
    this.renderEditor();

    const delay = this.calculateKeystrokeDelay(char);
    this.timerId = setTimeout(() => this.stepTyping(), delay);
  }

  handleTypoSequence(correctChar) {
    // Pick adjacent physical key
    const lower = correctChar.toLowerCase();
    const neighbors = ADJACENT_KEYS[lower] || 'efst';
    const typoChar = neighbors[Math.floor(Math.random() * neighbors.length)];

    this.typosMade++;
    this.totalKeystrokes++;
    this.typedChars.push({ char: typoChar, isTypo: true });
    audioSynth.playKeyClick(false);
    this.renderEditor();

    // Human cognitive lag before noticing error (180ms - 320ms)
    const reactionDelay = 180 + Math.random() * 140;

    this.timerId = setTimeout(() => {
      if (this.state !== 'typing') return;
      // Backspace step
      this.typedChars.pop();
      this.correctionsMade++;
      this.totalKeystrokes++;
      audioSynth.playKeyClick(true);
      this.renderEditor();

      // Typing correct character after backspace
      const recoveryDelay = 120 + Math.random() * 100;
      this.timerId = setTimeout(() => {
        if (this.state !== 'typing') return;
        this.typeCorrectChar(correctChar);
      }, recoveryDelay);
    }, reactionDelay);
  }

  renderEditor() {
    let html = '';
    for (const item of this.typedChars) {
      if (item.isTypo) {
        html += `<span class="char-typo">${this.escapeHtml(item.char)}</span>`;
      } else {
        html += this.escapeHtml(item.char);
      }
    }
    html += '<span class="typing-cursor"></span>';
    this.dom.editorText.innerHTML = html;

    const progress = Math.min(100, Math.round((this.charIndex / this.textToType.length) * 100));
    this.dom.progressFill.style.width = `${progress}%`;
    this.updateTelemetry();
  }

  calculateKeystrokeDelay(char) {
    const cpm = this.wpm * 5.0;
    const baseDelaySec = 60.0 / cpm;

    // Normal distribution variance
    const u1 = Math.random();
    const u2 = Math.random();
    const z = Math.sqrt(-2.0 * Math.log(u1 || 0.0001)) * Math.cos(2.0 * Math.PI * u2);
    const varianceFactor = 1.0 + z * (this.variation * 0.5);
    let delay = baseDelaySec * Math.max(0.3, Math.min(2.5, varianceFactor)) * 1000;

    // Punctuation pauses (. , ? ! : ;)
    if (/[\.\,\?\!\:\;]/.test(char)) {
      delay += 150 + Math.random() * 300;
    }

    // Word breaks (space)
    if (char === ' ') {
      delay += 30 + Math.random() * 70;
    }

    // Paragraph break
    if (char === '\n') {
      delay += 400 + Math.random() * 500;
    }

    return delay * this.multiplier;
  }

  startStatsTimer() {
    clearInterval(this.statsTimer);
    this.statsTimer = setInterval(() => {
      if (this.state === 'typing') {
        this.elapsedSeconds = (Date.now() - this.startTime) / 1000;
        this.updateTelemetry();
      }
    }, 200);
  }

  updateTelemetry() {
    const elapsedMinutes = Math.max(0.01, this.elapsedSeconds / 60);
    const currentWpm = Math.round((this.charIndex / 5.0) / elapsedMinutes) || this.wpm;
    const effectiveAccuracy = this.totalKeystrokes === 0 
      ? 100 
      : Math.max(0, Math.round((1 - (this.typosMade / Math.max(1, this.totalKeystrokes))) * 100));

    this.dom.statWpm.textContent = `${currentWpm}`;
    this.dom.statAcc.textContent = `${effectiveAccuracy}%`;
    this.dom.statChars.textContent = `${this.charIndex}/${this.textToType.length || 0}`;
    this.dom.statTypos.textContent = `${this.typosMade}`;
    this.dom.statElapsed.textContent = `${this.elapsedSeconds.toFixed(1)}s`;
  }

  playRecordingDemo() {
    this.emergencyStop();
    this.textToType = "Human-like typing simulator for Windows.\nAdjustable WPM with self-correcting typos.";
    this.dom.textarea.value = this.textToType;
    this.dom.timelineFill.style.width = '20%';

    setTimeout(() => {
      this.dom.timelineFill.style.width = '40%';
      this.start();
    }, 400);
  }

  escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// ═══════════════════════════════════════════════════════════════════
// 4. CADENCE WAVEFORM INSPECTOR (CANVAS RENDERER)
// ═══════════════════════════════════════════════════════════════════

function initCadenceWaveform() {
  const canvas = document.getElementById('cadenceWaveform');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function render(wpm = 55, variation = 0.25) {
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let y = 20; y < height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Calculate baseline ms
    const baseMs = (60 / (wpm * 5)) * 1000;
    const points = 40;
    const stepX = width / (points - 1);

    // Generate simulated delay points with gaussian variance
    const dataPoints = [];
    for (let i = 0; i < points; i++) {
      const u1 = Math.random();
      const u2 = Math.random();
      const z = Math.sqrt(-2.0 * Math.log(u1 || 0.001)) * Math.cos(2.0 * Math.PI * u2);
      const ms = baseMs * (1 + z * variation * 0.5);
      dataPoints.push(Math.max(20, Math.min(400, ms)));
    }

    // Fill gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(56, 189, 248, 0.35)');
    gradient.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

    ctx.beginPath();
    ctx.moveTo(0, height);
    for (let i = 0; i < points; i++) {
      const x = i * stepX;
      // Map ms to y (inverted)
      const y = height - (dataPoints[i] / 400) * (height - 30) - 10;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Waveform stroke line
    ctx.beginPath();
    for (let i = 0; i < points; i++) {
      const x = i * stepX;
      const y = height - (dataPoints[i] / 400) * (height - 30) - 10;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Key points
    for (let i = 0; i < points; i += 4) {
      const x = i * stepX;
      const y = height - (dataPoints[i] / 400) * (height - 30) - 10;
      ctx.beginPath();
      ctx.arc(x, y, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = '#10b981';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }

  window.renderCadenceWaveform = render;
  render(55, 0.25);
  window.addEventListener('resize', () => render(55, 0.25));
}

// ═══════════════════════════════════════════════════════════════════
// 5. FAQ ACCORDION INTERACTIVITY
// ═══════════════════════════════════════════════════════════════════

function initFaq() {
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;
    questionBtn.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      faqItems.forEach(i => i.classList.remove('open'));
      if (!isOpen) {
        item.classList.add('open');
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════════════
// 6. AMBIENT GLOW MOUSE TRACKING & COPY BUTTON
// ═══════════════════════════════════════════════════════════════════

function initAmbientGlow() {
  const glow = document.querySelector('.ambient-glow');
  if (!glow) return;
  window.addEventListener('mousemove', (e) => {
    const x = e.clientX - 250;
    const y = e.clientY - 250;
    glow.style.transform = `translate(${x}px, ${y}px)`;
  });
}

function initTerminalCopy() {
  const btn = document.querySelector('.terminal-copy-btn');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const code = "git clone https://github.com/SamSunny4/FakePaste.git\ncd FakePaste\npip install -r requirements.txt\npython main.py";
    navigator.clipboard.writeText(code).then(() => {
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
    });
  });
}

function initSoundToggle() {
  const soundBtn = document.getElementById('soundToggle');
  if (!soundBtn) return;
  soundBtn.addEventListener('click', () => {
    const active = audioSynth.toggle();
    soundBtn.classList.toggle('active', active);
    const label = soundBtn.querySelector('.sound-label');
    if (label) label.textContent = active ? 'Audio: ON' : 'Audio: OFF';
  });
}

// ═══════════════════════════════════════════════════════════════════
// BOOTSTRAP
// ═══════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
  window.simulator = new FakePasteSimulator();
  initCadenceWaveform();
  initFaq();
  initAmbientGlow();
  initTerminalCopy();
  initSoundToggle();
});
