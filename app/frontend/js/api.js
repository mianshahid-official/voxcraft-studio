/**
 * VoxCraft Studio - Unified API Client & PyWebView Bridge
 * Seamlessly interfaces with Desktop API (window.pywebview.api) or Fallback REST Endpoints.
 */

class StudioAPI {
  constructor() {
    this.isDesktop = typeof window.pywebview !== 'undefined' && window.pywebview.api;
    // Listen for pywebviewready event
    window.addEventListener('pywebviewready', () => {
      this.isDesktop = true;
      console.log('⚡ PyWebView Desktop API Bridge initialized successfully.');
    });
  }

  async call(methodName, params = null) {
    // 1. Try PyWebView Native JS API
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api[methodName] === 'function') {
      try {
        if (params === null) {
          return await window.pywebview.api[methodName]();
        } else {
          return await window.pywebview.api[methodName](params);
        }
      } catch (err) {
        console.warn(`PyWebView bridge error for ${methodName}, attempting fallback REST API:`, err);
      }
    }

    // 2. Fallback REST API
    try {
      const endpointMap = {
        'get_system_status': { url: '/api/system/status', method: 'GET' },
        'get_voices': { url: `/api/voices?${new URLSearchParams(params || {}).toString()}`, method: 'GET' },
        'synthesize_speech': { url: '/api/tts/synthesize', method: 'POST' },
        'generate_podcast_episode': { url: '/api/podcast/generate', method: 'POST' },
        'trigger_model_download': { url: '/api/models/download', method: 'POST', body: { model_key: params } },
        'get_download_status': { url: `/api/models/progress/${params}`, method: 'GET' },
        'export_audio_file': { url: '/api/export', method: 'POST' },
        'get_history_list': { url: '/api/history', method: 'GET' },
        'clear_history_list': { url: '/api/history', method: 'POST' },
        'save_voice_preset': { url: '/api/presets', method: 'POST' },
        'get_voice_presets': { url: '/api/presets', method: 'GET' },
        'save_podcast_project': { url: '/api/podcasts', method: 'POST' },
        'get_podcast_projects': { url: '/api/podcasts', method: 'GET' }
      };

      const config = endpointMap[methodName];
      if (!config) {
        throw new Error(`Unknown API method: ${methodName}`);
      }

      const fetchOptions = {
        method: config.method,
        headers: { 'Content-Type': 'application/json' }
      };

      if (config.method === 'POST') {
        fetchOptions.body = JSON.stringify(config.body || params || {});
      }

      const res = await fetch(config.url, fetchOptions);
      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`API execution failure for ${methodName}:`, err);
      throw err;
    }
  }

  // Convenience helper wrappers
  async getSystemStatus() { return await this.call('get_system_status'); }
  async getVoices(filters = {}) { return await this.call('get_voices', filters); }
  async synthesize(data) { return await this.call('synthesize_speech', data); }
  async generatePodcast(data) { return await this.call('generate_podcast_episode', data); }
  async downloadModel(key) { return await this.call('trigger_model_download', key); }
  async getModelProgress(key) { return await this.call('get_download_status', key); }
  async exportAudio(data) { return await this.call('export_audio_file', data); }
  async getHistory() { return await this.call('get_history_list'); }
  async clearHistory() { return await this.call('clear_history_list'); }
  async getPresets() { return await this.call('get_voice_presets'); }
  async savePreset(preset) { return await this.call('save_voice_preset', preset); }
  async getPodcasts() { return await this.call('get_podcast_projects'); }
  async savePodcast(project) { return await this.call('save_podcast_project', project); }
}

window.studioAPI = new StudioAPI();
