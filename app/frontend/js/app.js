/**
 * VoxCraft Studio - Core Application Shell Controller
 * Navigation Router, Toast Notification Engine, Export Manager, and Global Hotkeys.
 */

class VoxCraftApp {
  constructor() {
    this.currentView = 'studio';
    this.initNavigation();
    this.initHotkeys();
    this.initExportModal();
    this.initHistoryView();
  }

  initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const viewName = item.getAttribute('data-view');
        if (viewName) {
          this.switchView(viewName);
        }
      });
    });
  }

  switchView(viewName) {
    this.currentView = viewName;

    // Update Nav Items
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-view') === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update Views
    document.querySelectorAll('.view-container').forEach(view => {
      if (view.id === `view-${viewName}`) {
        view.classList.add('active');
      } else {
        view.classList.remove('active');
      }
    });

    // Update Top Header Title
    const headerTitle = document.getElementById('current-view-title');
    const titles = {
      'studio': '🎙️ Studio TTS Generator',
      'podcast': '📻 Podcast & Multi-Speaker Dialogue',
      'voices': '🎭 Voice Explorer & Library',
      'cloning': '🧬 F5-TTS Voice Cloning Lab',
      'effects': '🎚️ Master DSP & Audio Effects',
      'models': '⚙️ Offline Model Hub & Diagnostics',
      'history': '📜 Generation History & Drafts'
    };
    if (headerTitle && titles[viewName]) {
      headerTitle.textContent = titles[viewName];
    }

    if (viewName === 'models' && window.modelHub) {
      window.modelHub.refreshStatus();
    } else if (viewName === 'history') {
      this.loadHistory();
    }
  }

  initHotkeys() {
    window.addEventListener('keydown', (e) => {
      // Ctrl + Enter: Generate Speech
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (this.currentView === 'studio' && window.ttsStudio) {
          window.ttsStudio.generateSpeech();
        } else if (this.currentView === 'podcast' && window.podcastStudio) {
          window.podcastStudio.generateEpisode();
        }
      }

      // Spacebar: Toggle Audio Playback (when not focused on input/textarea)
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        if (window.studioPlayer) {
          window.studioPlayer.togglePlay();
        }
      }
    });
  }

  initExportModal() {
    const exportBtn = document.getElementById('player-export-btn');
    const modal = document.getElementById('export-modal');
    const cancelBtn = document.getElementById('btn-export-cancel');
    const confirmBtn = document.getElementById('btn-export-confirm');
    const filenameInput = document.getElementById('export-filename-input');
    const formatSelect = document.getElementById('export-format-select');

    if (exportBtn && modal) {
      exportBtn.addEventListener('click', () => {
        if (!window.studioPlayer.currentDataUri) {
          this.showToast('No synthesized audio to export.', 'warning');
          return;
        }
        modal.classList.add('active');
      });
    }

    if (cancelBtn && modal) {
      cancelBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    if (confirmBtn && modal) {
      confirmBtn.addEventListener('click', async () => {
        const filename = filenameInput ? filenameInput.value.trim() : 'voxcraft_speech';
        const format = formatSelect ? formatSelect.value : 'wav';

        this.showToast(`Exporting audio as ${format.toUpperCase()}...`, 'info');
        try {
          const res = await window.studioAPI.exportAudio({
            audio_data_uri: window.studioPlayer.currentDataUri,
            filename: filename,
            format: format
          });

          if (res.success) {
            this.showToast(`Audio saved to exports/${res.filename}`, 'success');
            modal.classList.remove('active');
          } else {
            this.showToast(`Export failed: ${res.error}`, 'error');
          }
        } catch (err) {
          this.showToast(`Export error: ${err.message}`, 'error');
        }
      });
    }
  }

  async initHistoryView() {
    const clearBtn = document.getElementById('btn-clear-history');
    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        await window.studioAPI.clearHistory();
        this.loadHistory();
        this.showToast('History cleared.', 'info');
      });
    }
  }

  async loadHistory() {
    const list = document.getElementById('history-items-list');
    if (!list) return;
    list.innerHTML = '<div style="padding: 24px; color: #94a3b8;">Loading history...</div>';

    try {
      const items = await window.studioAPI.getHistory();
      if (!items || items.length === 0) {
        list.innerHTML = `
          <div style="padding: 48px; text-align: center; color: var(--text-muted);">
            <div style="font-size: 2.2rem; margin-bottom: 8px;">📜</div>
            <div style="font-weight: 600; color: #fff;">No generation history yet</div>
            <div style="font-size: 0.85rem; margin-top: 4px;">Synthesized audio clips will automatically appear here.</div>
          </div>
        `;
        return;
      }

      list.innerHTML = '';
      items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'turn-block glass-panel';
        row.style.marginBottom = '12px';

        const dateStr = new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        row.innerHTML = `
          <div>
            <span class="badge badge-engine-${item.engine || 'kokoro'}">${(item.engine || 'kokoro').toUpperCase()}</span>
          </div>
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 0.95rem; color: #f8fafc; line-height: 1.4;">${item.text}</div>
            <div style="font-size: 0.78rem; color: #94a3b8; font-family: var(--font-mono); margin-top: 6px;">
              Voice: ${item.voice} • Speed: ${item.speed}x • ${item.duration_sec}s • ${dateStr}
            </div>
          </div>
          <div style="display: flex; gap: 8px;">
            ${item.audio_data_uri ? `
              <button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.82rem;" onclick="window.studioPlayer.loadAudio('${item.audio_data_uri}', '${item.voice}', '${item.duration_sec}s', ${item.duration_sec})">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span>Play</span>
              </button>
            ` : ''}
          </div>
        `;
        list.appendChild(row);
      });
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
      'success': `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      'info': `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
      'warning': `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
      'error': `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`
    };

    toast.innerHTML = `
      <div>${icons[type] || icons.info}</div>
      <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(60px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.studioApp = new VoxCraftApp();
});
