// ScheduleFlow - Universal App Base
// Shared utilities for all templates following the design requirements

class ScheduleFlowApp {
  constructor() {
    this.clock = document.getElementById('app-clock') || null;
    this.cacheDB = null;
    this.offlineMode = false;
    this.init();
  }

  async init() {
    this.setupClock();
    this.registerServiceWorker();
    this.setupIndexedDB();
    this.setupKeyboardShortcuts();
    this.setupFullscreenListeners();
  }

  setupClock() {
    if (!this.clock) return;
    setInterval(() => {
      const now = new Date();
      const hh = String(now.getHours()).padStart(2, '0');
      const mm = String(now.getMinutes()).padStart(2, '0');
      const ss = String(now.getSeconds()).padStart(2, '0');
      this.clock.textContent = `${hh}:${mm}:${ss}`;
    }, 1000);
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        await navigator.serviceWorker.register('/static/sw.js', { scope: '/' });
        console.log('✓ Service Worker registered - offline caching enabled');
      } catch (e) {
        console.warn('⚠️ Service Worker registration failed:', e);
      }
    }
  }

  async setupIndexedDB() {
    return new Promise((resolve) => {
      const request = indexedDB.open('ScheduleFlowCache', 1);

      request.onerror = () => {
        console.warn('⚠️ IndexedDB not available - using localStorage fallback');
        resolve(null);
      };

      request.onsuccess = (event) => {
        this.cacheDB = event.target.result;
        console.log('✓ IndexedDB initialized - offline data available');
        resolve(this.cacheDB);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('playlists')) {
          db.createObjectStore('playlists', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache', { keyPath: 'url' });
        }
      };
    });
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 's':
            e.preventDefault();
            this.saveToLocalStorage();
            console.log('✓ Data saved');
            break;
          case 'k':
            e.preventDefault();
            this.toggleMenu();
            break;
          case 'l':
            e.preventDefault();
            this.toggleFullscreen();
            break;
        }
      }
      if (e.key === 'Escape') {
        this.closeAllModals();
      }
    });
  }

  setupFullscreenListeners() {
    const fsBtn = document.getElementById('fs-btn');
    if (fsBtn) {
      fsBtn.addEventListener('click', () => this.toggleFullscreen());
    }
    document.addEventListener('fullscreenchange', () => {
      const bottomBar = document.querySelector('.bottom-bar');
      if (bottomBar) {
        bottomBar.style.display = document.fullscreenElement ? 'none' : 'flex';
      }
    });
  }

  toggleMenu() {
    const menu = document.querySelector('.top-menu');
    if (menu) menu.classList.toggle('open');
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {
        console.log('Fullscreen request failed');
      });
    } else {
      document.exitFullscreen();
    }
  }

  closeAllModals() {
    document.querySelectorAll('.modal.active').forEach(m => {
      m.classList.remove('active');
    });
  }

  saveToLocalStorage() {
    const state = {
      timestamp: Date.now(),
      data: window.appState || {}
    };
    localStorage.setItem('scheduleflow-state', JSON.stringify(state));
  }

  async cacheData(key, value) {
    if (!this.cacheDB) return localStorage.setItem(key, JSON.stringify(value));
    const tx = this.cacheDB.transaction('cache', 'readwrite');
    tx.objectStore('cache').put({ url: key, data: value, timestamp: Date.now() });
  }

  async getCachedData(key) {
    if (!this.cacheDB) return JSON.parse(localStorage.getItem(key) || 'null');
    return new Promise((resolve) => {
      const tx = this.cacheDB.transaction('cache', 'readonly');
      const request = tx.objectStore('cache').get(key);
      request.onsuccess = () => resolve(request.result?.data || null);
    });
  }
}

// Virtual Scrolling - Efficient rendering of large lists
class VirtualScroller {
  constructor(container, items, renderFn, itemHeight = 50) {
    this.container = container;
    this.items = items;
    this.renderFn = renderFn;
    this.itemHeight = itemHeight;
    this.visibleRange = { start: 0, end: 20 };
    this.init();
  }

  init() {
    this.container.style.overflow = 'auto';
    this.container.addEventListener('scroll', () => this.onScroll());
    this.render();
  }

  onScroll() {
    const scrollTop = this.container.scrollTop;
    const start = Math.floor(scrollTop / this.itemHeight);
    const visibleCount = Math.ceil(this.container.clientHeight / this.itemHeight);
    this.visibleRange = { start, end: start + visibleCount + 5 };
    this.render();
  }

  render() {
    const html = this.items
      .slice(this.visibleRange.start, this.visibleRange.end)
      .map((item, idx) => this.renderFn(item, this.visibleRange.start + idx))
      .join('');
    this.container.innerHTML = html;
  }
}

// Drag-Drop utility
class DragDropManager {
  constructor() {
    this.dragging = null;
  }

  enable(container, onDrop) {
    container.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      container.classList.add('drag-over');
    });

    container.addEventListener('dragleave', () => {
      container.classList.remove('drag-over');
    });

    container.addEventListener('drop', (e) => {
      e.preventDefault();
      container.classList.remove('drag-over');
      const data = e.dataTransfer.getData('text/plain');
      onDrop(data);
    });
  }
}

// Timer utility
class CountdownTimer {
  constructor(targetTime) {
    this.targetTime = new Date(targetTime);
    this.interval = null;
  }

  start(onTick, onEnd) {
    this.interval = setInterval(() => {
      const now = new Date();
      const diff = this.targetTime - now;

      if (diff <= 0) {
        clearInterval(this.interval);
        onEnd();
      } else {
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        onTick({ hours, minutes, seconds, total: diff });
      }
    }, 1000);
  }

  stop() {
    if (this.interval) clearInterval(this.interval);
  }
}

// Initialize global app
window.app = new ScheduleFlowApp();
