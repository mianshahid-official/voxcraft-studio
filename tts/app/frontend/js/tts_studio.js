/**
 * VoxCraft Studio - TTS Studio Controller
 * Handles Single & Batch Text Synthesis, Voice Selection, Voice Blending, and Pitch/Speed DSP.
 */

class TTSStudio {
  constructor() {
    this.voices = [];
    this.selectedVoice = 'af_bella';
    this.selectedEngine = 'kokoro';
    this.isBlendingActive = false;
    this.isGenerating = false;

    this.initElements();
    this.initEvents();
    this.loadVoices();
  }

  initElements() {
    this.textInput = document.getElementById('tts-text-input');
    this.charCount = document.getElementById('char-count');
    this.wordCount = document.getElementById('word-count');
    this.estDuration = document.getElementById('est-duration');

    this.engineSelect = document.getElementById('tts-engine-select');
    this.voiceSelect = document.getElementById('tts-voice-select');
    this.voiceAvatar = document.getElementById('selected-voice-avatar');
    this.voiceName = document.getElementById('selected-voice-name');
    this.voiceStyle = document.getElementById('selected-voice-style');

    this.speedSlider = document.getElementById('tts-speed-slider');
    this.speedVal = document.getElementById('tts-speed-val');
    this.pitchSlider = document.getElementById('tts-pitch-slider');
    this.pitchVal = document.getElementById('tts-pitch-val');
    this.volumeSlider = document.getElementById('tts-volume-slider');
    this.volumeVal = document.getElementById('tts-volume-val');

    // Voice Blending elements
    this.blendToggle = document.getElementById('blend-toggle');
    this.blendContainer = document.getElementById('blend-controls-container');
    this.blendVoiceA = document.getElementById('blend-voice-a');
    this.blendVoiceB = document.getElementById('blend-voice-b');
    this.blendSlider = document.getElementById('blend-ratio-slider');
    this.blendVal = document.getElementById('blend-ratio-val');

    this.generateBtn = document.getElementById('btn-generate-tts');
  }

  initEvents() {
    // Text input statistics
    if (this.textInput) {
      this.textInput.addEventListener('input', () => this.updateTextStats());
    }

    // Engine change
    if (this.engineSelect) {
      this.engineSelect.addEventListener('change', (e) => {
        this.selectedEngine = e.target.value;
        this.filterVoiceDropdown();
      });
    }

    // Voice change
    if (this.voiceSelect) {
      this.voiceSelect.addEventListener('change', (e) => {
        this.selectedVoice = e.target.value;
        this.updateVoiceDisplay();
      });
    }

    // Sliders
    if (this.speedSlider) {
      this.speedSlider.addEventListener('input', (e) => {
        if (this.speedVal) this.speedVal.textContent = `${parseFloat(e.target.value).toFixed(2)}x`;
        this.updateTextStats();
      });
    }

    if (this.pitchSlider) {
      this.pitchSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        if (this.pitchVal) this.pitchVal.textContent = `${val > 0 ? '+' : ''}${val.toFixed(1)} st`;
      });
    }

    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        if (this.volumeVal) this.volumeVal.textContent = `${Math.round(e.target.value * 100)}%`;
      });
    }

    // Voice Blending Toggle
    if (this.blendToggle) {
      this.blendToggle.addEventListener('change', (e) => {
        this.isBlendingActive = e.target.checked;
        if (this.blendContainer) {
          this.blendContainer.style.display = this.isBlendingActive ? 'flex' : 'none';
        }
      });
    }

    if (this.blendSlider) {
      this.blendSlider.addEventListener('input', (e) => {
        const ratioA = Math.round(e.target.value * 100);
        const ratioB = 100 - ratioA;
        if (this.blendVal) this.blendVal.textContent = `${ratioA}% A / ${ratioB}% B`;
      });
    }

    // Generate Button
    if (this.generateBtn) {
      this.generateBtn.addEventListener('click', () => this.generateSpeech());
    }

    // Quick Sample Prompts
    document.querySelectorAll('.quick-sample-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        const sampleText = e.target.getAttribute('data-sample');
        if (sampleText && this.textInput) {
          this.textInput.value = sampleText;
          this.updateTextStats();
        }
      });
    });
  }

  async loadVoices() {
    try {
      this.voices = await window.studioAPI.getVoices();
      this.filterVoiceDropdown();
    } catch (err) {
      console.error('Failed to load voice catalog:', err);
    }
  }

  filterVoiceDropdown() {
    if (!this.voiceSelect) return;
    this.voiceSelect.innerHTML = '';

    const filtered = this.voices.filter(v => {
      if (this.selectedEngine === 'all') return true;
      return v.engine === this.selectedEngine;
    });

    filtered.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v.id;
      opt.textContent = `${v.name} (${v.language} - ${v.gender})`;
      this.voiceSelect.appendChild(opt);
    });

    if (filtered.length > 0) {
      this.selectedVoice = filtered[0].id;
      this.voiceSelect.value = this.selectedVoice;
      this.updateVoiceDisplay();
    }

    // Populate Blend selects if present
    if (this.blendVoiceA && this.blendVoiceB) {
      this.blendVoiceA.innerHTML = '';
      this.blendVoiceB.innerHTML = '';
      const kokoroVoices = this.voices.filter(v => v.engine === 'kokoro');
      kokoroVoices.forEach(v => {
        this.blendVoiceA.appendChild(new Option(v.name, v.id));
        this.blendVoiceB.appendChild(new Option(v.name, v.id));
      });
      if (kokoroVoices.length > 1) {
        this.blendVoiceA.selectedIndex = 0;
        this.blendVoiceB.selectedIndex = 1;
      }
    }
  }

  updateVoiceDisplay() {
    const current = this.voices.find(v => v.id === this.selectedVoice);
    if (!current) return;

    if (this.voiceAvatar) this.voiceAvatar.textContent = current.avatar || '🎙️';
    if (this.voiceName) this.voiceName.textContent = current.name;
    if (this.voiceStyle) this.voiceStyle.textContent = `${current.language} • ${current.style}`;
  }

  updateTextStats() {
    if (!this.textInput) return;
    const text = this.textInput.value || '';
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const speed = this.speedSlider ? parseFloat(this.speedSlider.value) : 1.0;
    
    // Average 150 words per minute at 1.0x speed
    const estSec = words > 0 ? (words / (150 / 60)) / speed : 0;

    if (this.charCount) this.charCount.textContent = `${chars} chars`;
    if (this.wordCount) this.wordCount.textContent = `${words} words`;
    if (this.estDuration) this.estDuration.textContent = `~${estSec.toFixed(1)}s`;
  }

  async generateSpeech() {
    if (this.isGenerating) return;
    const text = this.textInput ? this.textInput.value.trim() : '';

    if (!text) {
      window.studioApp.showToast('Please enter text to synthesize.', 'warning');
      return;
    }

    this.isGenerating = true;
    this.updateGenerateButtonState(true);

    const payload = {
      text: text,
      voice: this.selectedVoice,
      engine: this.selectedEngine,
      speed: this.speedSlider ? parseFloat(this.speedSlider.value) : 1.0,
      pitch: this.pitchSlider ? parseFloat(this.pitchSlider.value) : 0.0,
      volume: this.volumeSlider ? parseFloat(this.volumeSlider.value) : 1.0
    };

    if (this.isBlendingActive && this.blendVoiceA && this.blendVoiceB && this.blendSlider) {
      payload.voice_blend = {
        voice_a: this.blendVoiceA.value,
        voice_b: this.blendVoiceB.value,
        weight_a: parseFloat(this.blendSlider.value)
      };
    }

    try {
      const res = await window.studioAPI.synthesize(payload);
      if (res.success && res.audio_data_uri) {
        const vMeta = this.voices.find(v => v.id === this.selectedVoice) || { name: 'Voice' };
        window.studioPlayer.loadAudio(
          res.audio_data_uri,
          vMeta.name,
          `${res.duration_sec}s • Generated with ${res.engine_used.toUpperCase()}`,
          res.duration_sec
        );
        window.studioApp.showToast(`Synthesized in ${res.generation_time_sec}s!`, 'success');
      } else {
        window.studioApp.showToast(`Synthesis failed: ${res.error || 'Unknown error'}`, 'error');
      }
    } catch (err) {
      window.studioApp.showToast(`Error: ${err.message}`, 'error');
    } finally {
      this.isGenerating = false;
      this.updateGenerateButtonState(false);
    }
  }

  updateGenerateButtonState(isLoading) {
    if (!this.generateBtn) return;
    if (isLoading) {
      this.generateBtn.disabled = true;
      this.generateBtn.innerHTML = `
        <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
        </svg>
        <span>Synthesizing...</span>
      `;
    } else {
      this.generateBtn.disabled = false;
      this.generateBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"></polygon>
        </svg>
        <span>Generate Speech</span>
      `;
    }
  }
}

window.ttsStudio = new TTSStudio();
