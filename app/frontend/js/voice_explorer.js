/**
 * VoxCraft Studio - Voice Library & Explorer Controller
 * Filterable Voice Cards, Real-time Sample Audio Previews, and Custom Preset Creator.
 */

class VoiceExplorer {
  constructor() {
    this.voices = [];
    this.currentFilters = {
      engine: 'all',
      gender: 'all',
      language: 'all',
      search: ''
    };

    this.initElements();
    this.initEvents();
    this.fetchVoices();
  }

  initElements() {
    this.grid = document.getElementById('voice-cards-grid');
    this.engineFilter = document.getElementById('filter-engine');
    this.genderFilter = document.getElementById('filter-gender');
    this.langFilter = document.getElementById('filter-language');
    this.searchBox = document.getElementById('search-voices-input');
    this.voiceCountLabel = document.getElementById('voice-count-label');
  }

  initEvents() {
    if (this.engineFilter) {
      this.engineFilter.addEventListener('change', (e) => {
        this.currentFilters.engine = e.target.value;
        this.renderVoices();
      });
    }

    if (this.genderFilter) {
      this.genderFilter.addEventListener('change', (e) => {
        this.currentFilters.gender = e.target.value;
        this.renderVoices();
      });
    }

    if (this.langFilter) {
      this.langFilter.addEventListener('change', (e) => {
        this.currentFilters.language = e.target.value;
        this.renderVoices();
      });
    }

    if (this.searchBox) {
      this.searchBox.addEventListener('input', (e) => {
        this.currentFilters.search = e.target.value.toLowerCase().trim();
        this.renderVoices();
      });
    }
  }

  async fetchVoices() {
    try {
      this.voices = await window.studioAPI.getVoices();
      this.renderVoices();
    } catch (err) {
      console.error('Failed loading voice catalog:', err);
    }
  }

  renderVoices() {
    if (!this.grid) return;
    this.grid.innerHTML = '';

    const filtered = this.voices.filter(v => {
      if (this.currentFilters.engine !== 'all' && v.engine !== this.currentFilters.engine) return false;
      if (this.currentFilters.gender !== 'all' && v.gender.toLowerCase() !== this.currentFilters.gender.toLowerCase()) return false;
      if (this.currentFilters.language !== 'all' && !v.language.toLowerCase().includes(this.currentFilters.language.toLowerCase())) return false;
      if (this.currentFilters.search) {
        const q = this.currentFilters.search;
        const match = v.name.toLowerCase().includes(q) ||
          v.description.toLowerCase().includes(q) ||
          v.style.toLowerCase().includes(q) ||
          (v.tags && v.tags.some(t => t.toLowerCase().includes(q)));
        if (!match) return false;
      }
      return true;
    });

    if (this.voiceCountLabel) {
      this.voiceCountLabel.textContent = `${filtered.length} Voices Available`;
    }

    if (filtered.length === 0) {
      this.grid.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 48px; text-align: center; color: var(--text-muted);">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
          <div style="font-size: 1.1rem; font-weight: 600; color: #fff;">No matching voices found</div>
          <div style="font-size: 0.9rem; margin-top: 4px;">Try changing filters or searching another keyword.</div>
        </div>
      `;
      return;
    }

    filtered.forEach(v => {
      const card = document.createElement('div');
      card.className = 'voice-card glass-panel';

      const engineBadgeClass = v.engine === 'kokoro' ? 'badge-engine-kokoro' : (v.engine === 'piper' ? 'badge-engine-piper' : 'badge-engine-f5');

      card.innerHTML = `
        <div class="voice-card-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: ${v.color || '#8b5cf6'}22; border: 1px solid ${v.color || '#8b5cf6'}55; display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">
              ${v.avatar || '🎙️'}
            </div>
            <div>
              <div style="font-weight: 700; font-size: 1.05rem; color: #fff;">${v.name}</div>
              <div style="font-size: 0.8rem; color: #94a3b8;">${v.language} • ${v.gender}</div>
            </div>
          </div>
          <span class="badge ${engineBadgeClass}">${v.engine.toUpperCase()}</span>
        </div>

        <p style="font-size: 0.86rem; color: #cbd5e1; line-height: 1.5; margin-top: 4px; min-height: 40px;">
          ${v.description}
        </p>

        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0;">
          ${(v.tags || []).map(t => `<span class="badge" style="font-size: 0.7rem; padding: 2px 6px;">#${t}</span>`).join('')}
        </div>

        <div style="display: flex; gap: 8px; margin-top: auto; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
          <button class="btn btn-secondary" style="flex: 1; padding: 8px 12px; font-size: 0.85rem;" onclick="window.voiceExplorer.previewVoice('${v.id}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            <span>Preview Sample</span>
          </button>
          <button class="btn btn-primary" style="padding: 8px 14px; font-size: 0.85rem;" onclick="window.voiceExplorer.useVoiceInStudio('${v.id}', '${v.engine}')" title="Use in Studio">
            <span>Use</span>
          </button>
        </div>
      `;
      this.grid.appendChild(card);
    });
  }

  async previewVoice(voiceId) {
    const v = this.voices.find(item => item.id === voiceId);
    if (!v) return;

    window.studioApp.showToast(`Synthesizing preview for ${v.name}...`, 'info');

    try {
      const res = await window.studioAPI.synthesize({
        text: v.sample_text || "Welcome to offline speech synthesis with VoxCraft Studio.",
        voice: v.id,
        engine: v.engine,
        speed: 1.0,
        pitch: 0.0
      });

      if (res.success && res.audio_data_uri) {
        window.studioPlayer.loadAudio(
          res.audio_data_uri,
          v.name,
          `${v.language} • ${v.style}`,
          res.duration_sec
        );
      } else {
        window.studioApp.showToast(`Preview failed: ${res.error}`, 'error');
      }
    } catch (err) {
      window.studioApp.showToast(`Error: ${err.message}`, 'error');
    }
  }

  useVoiceInStudio(voiceId, engine) {
    if (window.ttsStudio) {
      window.ttsStudio.selectedEngine = engine;
      if (window.ttsStudio.engineSelect) window.ttsStudio.engineSelect.value = engine;
      window.ttsStudio.filterVoiceDropdown();
      window.ttsStudio.selectedVoice = voiceId;
      if (window.ttsStudio.voiceSelect) window.ttsStudio.voiceSelect.value = voiceId;
      window.ttsStudio.updateVoiceDisplay();
    }
    // Switch to studio tab
    window.studioApp.switchView('studio');
    window.studioApp.showToast(`Selected ${voiceId} for synthesis`, 'success');
  }
}

window.voiceExplorer = new VoiceExplorer();
