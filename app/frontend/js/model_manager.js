/**
 * VoxCraft Studio - Model & Requirements Hub Controller
 * System Diagnostics HUD, 1-Click Model Downloader, Progress Streaming, and Offline Management.
 */

class ModelManagerHub {
  constructor() {
    this.modelsData = null;
    this.pollInterval = null;

    this.initElements();
    this.initEvents();
    this.refreshStatus();
  }

  initElements() {
    this.hudDevice = document.getElementById('hud-active-device');
    this.hudCpu = document.getElementById('hud-cpu-info');
    this.hudRam = document.getElementById('hud-ram-info');
    this.hudDisk = document.getElementById('hud-disk-info');
    this.hudGpu = document.getElementById('hud-gpu-details');

    this.manifestList = document.getElementById('model-manifest-list');
    this.refreshBtn = document.getElementById('btn-refresh-models');
  }

  initEvents() {
    if (this.refreshBtn) {
      this.refreshBtn.addEventListener('click', () => this.refreshStatus());
    }
  }

  async refreshStatus() {
    try {
      const status = await window.studioAPI.getSystemStatus();
      this.renderDiagnostics(status.diagnostics);
      this.renderModels(status.models);
    } catch (err) {
      console.error('Failed refreshing system status:', err);
    }
  }

  renderDiagnostics(diag) {
    if (!diag) return;

    if (this.hudDevice) {
      this.hudDevice.textContent = diag.active_device || 'CPU';
      this.hudDevice.className = diag.gpu && diag.gpu.has_gpu ? 'badge badge-gpu' : 'badge';
    }

    if (this.hudCpu) {
      this.hudCpu.textContent = `${diag.cpu.physical_cores} Cores / ${diag.cpu.logical_threads} Threads (${diag.cpu.usage_percent}%)`;
    }

    if (this.hudRam) {
      this.hudRam.textContent = `${diag.ram.available_gb} GB Free / ${diag.ram.total_gb} GB`;
    }

    if (this.hudDisk) {
      this.hudDisk.textContent = `${diag.disk.free_gb} GB Free`;
    }

    if (this.hudGpu) {
      this.hudGpu.textContent = diag.gpu.details || 'Standard CPU';
    }

    // Update sidebar HUD as well
    const sidebarGpu = document.getElementById('sidebar-gpu-val');
    const sidebarRam = document.getElementById('sidebar-ram-val');
    if (sidebarGpu) sidebarGpu.textContent = diag.gpu.has_gpu ? 'GPU (CUDA/DML)' : 'CPU';
    if (sidebarRam) sidebarRam.textContent = `${diag.ram.available_gb}G Free`;
  }

  renderModels(modelsData) {
    if (!modelsData || !this.manifestList) return;
    this.modelsData = modelsData;
    this.manifestList.innerHTML = '';

    const manifest = modelsData.manifest || {};
    let hasActiveDownload = false;

    Object.keys(manifest).forEach(key => {
      const item = manifest[key];
      const card = document.createElement('div');
      card.className = 'model-item-card glass-panel';

      const isInstalled = item.is_installed;
      const isDownloading = item.is_downloading;
      const progress = item.download_progress || 0;

      if (isDownloading) hasActiveDownload = true;

      const engineBadge = item.engine === 'kokoro' ? 'badge-engine-kokoro' : (item.engine === 'piper' ? 'badge-engine-piper' : 'badge-engine-f5');

      card.innerHTML = `
        <div style="flex: 1; min-width: 0;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span class="badge ${engineBadge}">${item.engine.toUpperCase()}</span>
            <span style="font-weight: 700; font-size: 1.05rem; color: #fff;">${item.name}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-family: var(--font-mono);">${item.total_size_mb} MB</span>
            ${isInstalled ? `<span class="badge badge-success">✓ Installed (Offline)</span>` : (isDownloading ? `<span class="badge badge-warning">⏳ Downloading ${progress}%</span>` : `<span class="badge">Not Downloaded</span>`)}
          </div>
          <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 4px;">${item.description}</div>
          
          ${isDownloading ? `
            <div class="progress-track">
              <div class="progress-fill" style="width: ${progress}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: #cbd5e1; font-family: var(--font-mono); margin-top: 4px;">
              <span>Speed: ${item.speed_mbps || 0} MB/s</span>
              <span>ETA: ~${item.eta_seconds || 0}s</span>
            </div>
          ` : ''}
        </div>

        <div>
          ${isInstalled ? `
            <button class="btn btn-secondary" style="padding: 8px 16px; font-size: 0.85rem;" disabled>
              <span>Ready Offline</span>
            </button>
          ` : (isDownloading ? `
            <button class="btn btn-secondary" style="padding: 8px 16px; font-size: 0.85rem; color: #f43f5e;" onclick="window.modelHub.cancelDownload('${key}')">
              <span>Cancel</span>
            </button>
          ` : `
            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 0.85rem;" onclick="window.modelHub.startDownload('${key}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              <span>Download Model</span>
            </button>
          `)}
        </div>
      `;

      this.manifestList.appendChild(card);
    });

    // Start/stop polling
    if (hasActiveDownload && !this.pollInterval) {
      this.pollInterval = setInterval(() => this.refreshStatus(), 1200);
    } else if (!hasActiveDownload && this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  async startDownload(key) {
    window.studioApp.showToast(`Starting download for ${key}...`, 'info');
    try {
      await window.studioAPI.downloadModel(key);
      this.refreshStatus();
    } catch (err) {
      window.studioApp.showToast(`Failed to start download: ${err.message}`, 'error');
    }
  }

  async cancelDownload(key) {
    window.studioApp.showToast(`Cancelling download for ${key}...`, 'warning');
    // Refresh
    setTimeout(() => this.refreshStatus(), 500);
  }
}

window.modelHub = new ModelManagerHub();
