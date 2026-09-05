/**
 * VoxCraft Studio - Podcast & Multi-Speaker Dialogue Studio Controller
 * Visual Script Editor, Cast Manager, Synchronized Multi-Speaker Playback Timeline, and Stem Exporter.
 */

class PodcastStudio {
  constructor() {
    this.speakers = [
      { id: 'speaker_1', name: 'Alex (Host)', engine: 'kokoro', voice: 'am_michael', color: '#8b5cf6', avatar: '🎙️', speed: 1.05, pitch: 0.0 },
      { id: 'speaker_2', name: 'Dr. Elena (Guest)', engine: 'kokoro', voice: 'af_sarah', color: '#06b6d4', avatar: '🔬', speed: 0.98, pitch: 0.0 },
      { id: 'speaker_3', name: 'Narrator', engine: 'kokoro', voice: 'am_adam', color: '#f59e0b', avatar: '🎬', speed: 0.95, pitch: -1.0 }
    ];

    this.dialogue = [
      { speaker_id: 'speaker_3', text: 'Episode 42: The Dawn of Local Machine Intelligence.', pause_after: 0.8 },
      { speaker_id: 'speaker_1', text: 'Welcome back everyone. Today we are speaking with Dr. Elena about neural voice synthesis running completely offline on your desktop.', pause_after: 0.5 },
      { speaker_id: 'speaker_2', text: 'Thanks for having me, Alex! The breakthrough here is delivering ultra-low latency with zero cloud dependencies.', pause_after: 0.5 },
      { speaker_id: 'speaker_1', text: 'That means complete privacy and limitless audio generation without a single API key.', pause_after: 0.8 }
    ];

    this.timelineMarkers = [];
    this.isGenerating = false;

    this.initElements();
    this.initEvents();
    this.renderCast();
    this.renderDialogue();
  }

  initElements() {
    this.castContainer = document.getElementById('podcast-cast-container');
    this.dialogueContainer = document.getElementById('podcast-dialogue-container');
    this.addTurnBtn = document.getElementById('btn-add-turn');
    this.generatePodcastBtn = document.getElementById('btn-generate-podcast');
    this.templateSelect = document.getElementById('podcast-template-select');
  }

  initEvents() {
    if (this.addTurnBtn) {
      this.addTurnBtn.addEventListener('click', () => this.addTurn());
    }

    if (this.generatePodcastBtn) {
      this.generatePodcastBtn.addEventListener('click', () => this.generateEpisode());
    }

    if (this.templateSelect) {
      this.templateSelect.addEventListener('change', (e) => this.loadTemplate(e.target.value));
    }

    // Connect timeline sync to player time update
    if (window.studioPlayer) {
      window.studioPlayer.onTimeUpdateCallback = (currentTime) => {
        this.highlightActiveTurn(currentTime);
      };
    }
  }

  renderCast() {
    if (!this.castContainer) return;
    this.castContainer.innerHTML = '';

    this.speakers.forEach(s => {
      const card = document.createElement('div');
      card.className = 'cast-card';
      card.style.borderColor = s.color;
      card.innerHTML = `
        <div style="font-size: 1.6rem; background: ${s.color}22; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
          ${s.avatar}
        </div>
        <div style="flex: 1; min-width: 0;">
          <div style="font-weight: 700; font-size: 0.92rem; color: #ffffff;">${s.name}</div>
          <div style="font-size: 0.76rem; color: #94a3b8; font-family: var(--font-mono);">${s.voice} • ${s.speed}x</div>
        </div>
      `;
      this.castContainer.appendChild(card);
    });
  }

  renderDialogue() {
    if (!this.dialogueContainer) return;
    this.dialogueContainer.innerHTML = '';

    this.dialogue.forEach((turn, idx) => {
      const speaker = this.speakers.find(s => s.id === turn.speaker_id) || this.speakers[0];
      const block = document.createElement('div');
      block.className = 'turn-block glass-panel';
      block.id = `turn-block-${idx}`;
      block.style.borderLeft = `4px solid ${speaker.color}`;

      block.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; gap: 6px;">
          <div style="font-size: 1.5rem;">${speaker.avatar}</div>
          <select class="custom-select" style="padding: 4px 8px; font-size: 0.78rem; width: 110px;" onchange="window.podcastStudio.changeTurnSpeaker(${idx}, this.value)">
            ${this.speakers.map(s => `<option value="${s.id}" ${s.id === turn.speaker_id ? 'selected' : ''}>${s.name.split(' ')[0]}</option>`).join('')}
          </select>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <textarea class="textarea-field" style="min-height: 64px; font-size: 0.95rem;" oninput="window.podcastStudio.updateTurnText(${idx}, this.value)">${turn.text}</textarea>
          <div style="display: flex; align-items: center; gap: 16px; font-size: 0.8rem; color: #94a3b8;">
            <label style="display: flex; align-items: center; gap: 6px;">
              <span>Pause After:</span>
              <input type="number" step="0.1" min="0" max="5" value="${turn.pause_after || 0.5}" style="width: 55px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 2px 6px; border-radius: 4px;" onchange="window.podcastStudio.updateTurnPause(${idx}, this.value)">
              <span>sec</span>
            </label>
          </div>
        </div>
        <div>
          <button class="btn-icon" style="color: #f43f5e;" onclick="window.podcastStudio.deleteTurn(${idx})" title="Delete Turn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      `;
      this.dialogueContainer.appendChild(block);
    });
  }

  addTurn() {
    const lastSpeaker = this.dialogue.length > 0 ? this.dialogue[this.dialogue.length - 1].speaker_id : 'speaker_1';
    const nextSpeaker = lastSpeaker === 'speaker_1' ? 'speaker_2' : 'speaker_1';
    this.dialogue.push({
      speaker_id: nextSpeaker,
      text: '',
      pause_after: 0.5
    });
    this.renderDialogue();
  }

  deleteTurn(index) {
    if (this.dialogue.length <= 1) {
      window.studioApp.showToast('Podcast must have at least one dialogue block.', 'warning');
      return;
    }
    this.dialogue.splice(index, 1);
    this.renderDialogue();
  }

  changeTurnSpeaker(index, speakerId) {
    if (this.dialogue[index]) {
      this.dialogue[index].speaker_id = speakerId;
      this.renderDialogue();
    }
  }

  updateTurnText(index, text) {
    if (this.dialogue[index]) {
      this.dialogue[index].text = text;
    }
  }

  updateTurnPause(index, pause) {
    if (this.dialogue[index]) {
      this.dialogue[index].pause_after = parseFloat(pause) || 0.5;
    }
  }

  async generateEpisode() {
    if (this.isGenerating) return;
    this.isGenerating = true;

    if (this.generatePodcastBtn) {
      this.generatePodcastBtn.disabled = true;
      this.generatePodcastBtn.innerHTML = `<span>Synthesizing Episode...</span>`;
    }

    try {
      const payload = {
        speakers: this.speakers,
        dialogue: this.dialogue,
        master_effects: { normalize: true, reverb: 0.05 }
      };

      const res = await window.studioAPI.generatePodcast(payload);
      if (res.success && res.audio_data_uri) {
        this.timelineMarkers = res.timeline || [];
        window.studioPlayer.loadAudio(
          res.audio_data_uri,
          "Podcast Episode (Multi-Speaker)",
          `${res.total_duration_sec}s • ${res.num_blocks} Speaker Turns`,
          res.total_duration_sec
        );
        window.studioApp.showToast(`Podcast master generated (${res.total_duration_sec}s)!`, 'success');
      } else {
        window.studioApp.showToast(`Failed generating podcast: ${res.error}`, 'error');
      }
    } catch (err) {
      window.studioApp.showToast(`Podcast synthesis error: ${err.message}`, 'error');
    } finally {
      this.isGenerating = false;
      if (this.generatePodcastBtn) {
        this.generatePodcastBtn.disabled = false;
        this.generatePodcastBtn.innerHTML = `<span>Generate Full Podcast</span>`;
      }
    }
  }

  highlightActiveTurn(currentTime) {
    if (!this.timelineMarkers || this.timelineMarkers.length === 0) return;

    this.timelineMarkers.forEach(marker => {
      const el = document.getElementById(`turn-block-${marker.block_index}`);
      if (el) {
        if (currentTime >= marker.start_time && currentTime <= marker.end_time) {
          el.classList.add('highlighted');
        } else {
          el.classList.remove('highlighted');
        }
      }
    });
  }

  loadTemplate(templateKey) {
    if (templateKey === 'tech_interview') {
      this.dialogue = [
        { speaker_id: 'speaker_1', text: 'Welcome to Future Stack. Today we are joined by AI researcher Dr. Elena.', pause_after: 0.5 },
        { speaker_id: 'speaker_2', text: 'Great to be here! We are pushing the limits of on-device neural voice models.', pause_after: 0.6 },
        { speaker_id: 'speaker_1', text: 'How does Kokoro-82M compare in inference speed on typical hardware?', pause_after: 0.4 },
        { speaker_id: 'speaker_2', text: 'It runs at over 50 times realtime speed with studio grade 24 kilohertz audio.', pause_after: 0.8 }
      ];
    } else if (templateKey === 'story_intro') {
      this.dialogue = [
        { speaker_id: 'speaker_3', text: 'Chapter One: The Signal in the Dark.', pause_after: 1.0 },
        { speaker_id: 'speaker_2', text: 'Captain, we are receiving an unidentified audio transmission from sector seven.', pause_after: 0.6 },
        { speaker_id: 'speaker_1', text: 'Route it through the primary filters and enhance the voice resonance.', pause_after: 0.8 }
      ];
    }
    this.renderDialogue();
  }
}

window.podcastStudio = new PodcastStudio();
