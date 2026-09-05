/**
 * VoxCraft Studio - High-Precision Waveform Audio Player
 * Interactive Canvas Visualizer, Web Audio API context, and synchronized scrubber.
 */

class StudioAudioPlayer {
  constructor() {
    this.audio = new Audio();
    this.canvas = document.getElementById('waveform-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    
    this.currentDataUri = null;
    this.isPlaying = false;
    this.duration = 0;
    this.currentTime = 0;
    this.wavePeaks = [];
    this.onTimeUpdateCallback = null;

    this.playBtn = document.getElementById('player-play-btn');
    this.playIcon = document.getElementById('player-play-icon');
    this.timeDisplay = document.getElementById('player-time-display');
    this.titleDisplay = document.getElementById('player-track-title');
    this.subtitleDisplay = document.getElementById('player-track-subtitle');
    this.volumeSlider = document.getElementById('player-volume-slider');
    this.rateSelector = document.getElementById('player-rate-select');

    this.initEvents();
    this.initCanvasResize();
  }

  initEvents() {
    // Audio Events
    this.audio.addEventListener('play', () => {
      this.isPlaying = true;
      this.updatePlayBtnIcon();
      this.renderWaveform();
    });

    this.audio.addEventListener('pause', () => {
      this.isPlaying = false;
      this.updatePlayBtnIcon();
      this.renderWaveform();
    });

    this.audio.addEventListener('ended', () => {
      this.isPlaying = false;
      this.audio.currentTime = 0;
      this.updatePlayBtnIcon();
      this.renderWaveform();
    });

    this.audio.addEventListener('timeupdate', () => {
      this.currentTime = this.audio.currentTime;
      this.updateTimeDisplay();
      this.renderWaveform();
      if (this.onTimeUpdateCallback) {
        this.onTimeUpdateCallback(this.currentTime);
      }
    });

    this.audio.addEventListener('loadedmetadata', () => {
      this.duration = this.audio.duration;
      this.updateTimeDisplay();
      this.renderWaveform();
    });

    // Play/Pause Button
    if (this.playBtn) {
      this.playBtn.addEventListener('click', () => this.togglePlay());
    }

    // Canvas Scrubbing
    if (this.canvas) {
      this.canvas.addEventListener('click', (e) => {
        if (!this.duration) return;
        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const pct = Math.max(0, Math.min(1, clickX / rect.width));
        this.audio.currentTime = pct * this.duration;
      });
    }

    // Volume Slider
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        this.audio.volume = parseFloat(e.target.value);
      });
    }

    // Playback Rate Selector
    if (this.rateSelector) {
      this.rateSelector.addEventListener('change', (e) => {
        this.audio.playbackRate = parseFloat(e.target.value);
      });
    }
  }

  initCanvasResize() {
    if (!this.canvas) return;
    const resize = () => {
      const rect = this.canvas.getBoundingClientRect();
      this.canvas.width = rect.width * window.devicePixelRatio || 600;
      this.canvas.height = rect.height * window.devicePixelRatio || 80;
      this.renderWaveform();
    };
    window.addEventListener('resize', resize);
    setTimeout(resize, 100);
  }

  loadAudio(dataUri, title = "Synthesized Voice", subtitle = "Ready for playback", durationSec = null) {
    this.currentDataUri = dataUri;
    this.audio.src = dataUri;
    this.audio.load();

    if (this.titleDisplay) this.titleDisplay.textContent = title;
    if (this.subtitleDisplay) this.subtitleDisplay.textContent = subtitle;
    if (durationSec) this.duration = durationSec;

    // Generate simulated waveform peaks for visualization
    this.generateWavePeaks();
    this.audio.play().catch(() => {});
  }

  generateWavePeaks(numBars = 120) {
    this.wavePeaks = [];
    for (let i = 0; i < numBars; i++) {
      // Natural speech envelope with varying amplitude bursts
      const base = Math.sin(i / 6.0) * 0.4 + 0.5;
      const noise = (Math.random() - 0.5) * 0.4;
      const peak = Math.max(0.15, Math.min(0.95, base + noise));
      this.wavePeaks.push(peak);
    }
    this.renderWaveform();
  }

  renderWaveform() {
    if (!this.canvas || !this.ctx) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const ctx = this.ctx;

    ctx.clearRect(0, 0, w, h);

    const numBars = this.wavePeaks.length || 100;
    const barSpacing = w / numBars;
    const barWidth = Math.max(2, barSpacing * 0.65);
    const progressPct = this.duration > 0 ? (this.currentTime / this.duration) : 0;

    for (let i = 0; i < numBars; i++) {
      const peak = this.wavePeaks[i] || 0.3;
      const barHeight = peak * (h * 0.75);
      const x = i * barSpacing;
      const y = (h - barHeight) / 2;

      const barPct = i / numBars;
      const isPlayed = barPct <= progressPct;

      if (isPlayed) {
        // Glowing Played Violet/Cyan Gradient
        const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
        grad.addColorStop(0, '#8b5cf6');
        grad.addColorStop(1, '#06b6d4');
        ctx.fillStyle = grad;
        ctx.shadowColor = 'rgba(139, 92, 246, 0.6)';
        ctx.shadowBlur = 6;
      } else {
        // Unplayed Dark Slate
        ctx.fillStyle = 'rgba(255, 255, 255, 0.14)';
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, 3);
      ctx.fill();
    }

    // Draw Playhead Cursor
    if (this.duration > 0) {
      const playheadX = progressPct * w;
      ctx.shadowBlur = 8;
      ctx.shadowColor = '#06b6d4';
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.roundRect(playheadX - 1.5, 0, 3, h, 2);
      ctx.fill();
    }
  }

  togglePlay() {
    if (!this.audio.src) return;
    if (this.isPlaying) {
      this.audio.pause();
    } else {
      this.audio.play().catch(e => console.log('Playback prevented:', e));
    }
  }

  updatePlayBtnIcon() {
    if (!this.playIcon) return;
    this.playIcon.innerHTML = this.isPlaying
      ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`
      : `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`;
  }

  updateTimeDisplay() {
    if (!this.timeDisplay) return;
    const cur = this.formatTime(this.currentTime);
    const dur = this.formatTime(this.duration);
    this.timeDisplay.textContent = `${cur} / ${dur}`;
  }

  formatTime(sec) {
    if (isNaN(sec) || sec < 0) return "0:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }
}

window.studioPlayer = new StudioAudioPlayer();
