// Simple Player - M3U Matrix Pro
// Clean, responsive video player with playlist support

// Playlist data is injected in player.html by the generator
// Access it via window.PLAYLIST_DATA

let playlist = [];
let currentIndex = 0;
let played = new Set();
let retryTimer = null;
let playbackMode = 'sequential';
let isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
let hlsInstance = null;

// DOM Elements
const video = document.getElementById('video');
const titleEl = document.getElementById('title');
const loading = document.getElementById('loading');
const fakeBtn = document.getElementById('fake-click');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const playlistBtn = document.getElementById('playlist-btn');
const playlistModal = document.getElementById('playlist-modal');
const playlistContent = document.getElementById('playlist-content');
const playlistClose = document.getElementById('playlist-close');
const playlistInfo = document.getElementById('playlist-info');
const touchOverlay = document.getElementById('touch-overlay');
const sequentialBtn = document.getElementById('sequential-btn');
const shuffleBtn = document.getElementById('shuffle-btn');

// Initialize on load
document.addEventListener('DOMContentLoaded', init);

function init() {
  parsePlaylistData();
  setupEventListeners();
  initPlaylistModal();
  
  if (playlist.length > 0) {
    loadVideo(playbackMode === 'shuffle' ? getRandomIndex() : 0);
  } else {
    showError('No channels found in playlist');
  }
}

function parsePlaylistData() {
  try {
    const data = window.PLAYLIST_DATA;
    if (data && typeof data === 'object') {
      playlist = data.channels || data || [];
    } else {
      console.warn('No playlist data found');
      playlist = [];
    }
  } catch (e) {
    console.error('Error parsing playlist data:', e);
    playlist = [];
  }
}

function setupEventListeners() {
  video.addEventListener('ended', onVideoEnded);
  video.addEventListener('error', onVideoError);
  prevBtn.addEventListener('click', prevVideo);
  nextBtn.addEventListener('click', nextVideo);
  playlistBtn.addEventListener('click', () => playlistModal.classList.add('active'));
  playlistClose.addEventListener('click', () => playlistModal.classList.remove('active'));
  
  sequentialBtn.addEventListener('click', () => setPlaybackMode('sequential'));
  shuffleBtn.addEventListener('click', () => setPlaybackMode('shuffle'));
  
  if (isMobile) {
    touchOverlay.classList.add('active');
    touchOverlay.addEventListener('click', togglePlayPause);
  }
}

function setPlaybackMode(mode) {
  playbackMode = mode;
  sequentialBtn.classList.toggle('active', mode === 'sequential');
  shuffleBtn.classList.toggle('active', mode === 'shuffle');
}

function togglePlayPause() {
  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
}

function initPlaylistModal() {
  const groups = {};
  
  playlist.forEach((item, index) => {
    const group = item.group || 'Uncategorized';
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push({...item, index});
  });
  
  let html = '';
  for (const group in groups) {
    html += `<div class="playlist-group">
              <h3 class="playlist-group-title">
                ${group}
                <span class="group-count">${groups[group].length}</span>
              </h3>
              <div class="playlist-items">`;
    
    groups[group].forEach(item => {
      const isActive = item.index === currentIndex;
      html += `<div class="playlist-item ${isActive ? 'active' : ''}" 
                    data-index="${item.index}">
                ${item.name || item.title || `Channel ${item.index + 1}`}
              </div>`;
    });
    
    html += `</div></div>`;
  }
  
  playlistContent.innerHTML = html;
  
  document.querySelectorAll('.playlist-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = parseInt(this.getAttribute('data-index'));
      loadVideo(index);
      playlistModal.classList.remove('active');
    });
  });
}

function getRandomIndex() {
  if (played.size >= playlist.length) {
    played.clear();
  }
  
  let next;
  do {
    next = Math.floor(Math.random() * playlist.length);
  } while (played.has(next) && played.size < playlist.length);
  
  played.add(next);
  return next;
}

function getNextIndex() {
  if (playbackMode === 'shuffle') {
    return getRandomIndex();
  } else {
    return (currentIndex + 1) % playlist.length;
  }
}

function getPrevIndex() {
  if (playbackMode === 'shuffle') {
    return getRandomIndex();
  } else {
    return currentIndex === 0 ? playlist.length - 1 : currentIndex - 1;
  }
}

function loadVideo(index) {
  if (index < 0 || index >= playlist.length) return;
  
  const item = playlist[index];
  currentIndex = index;
  
  titleEl.textContent = item.name || item.title || `Channel ${index + 1}`;
  playlistInfo.textContent = `${index + 1}/${playlist.length}`;
  
  updatePlaylistUI();
  
  loading.innerHTML = 'Loading...<span class="loading-spinner"></span>';
  loading.classList.add('show');
  
  cleanupPlayers();
  
  if (retryTimer) clearTimeout(retryTimer);
  
  const url = item.url || item.src;
  
  if (url.includes('.m3u8')) {
    loadHLS(url);
  } else {
    video.src = url;
    video.load();
  }
  
  retryTimer = setTimeout(() => {
    if (video.readyState < 2) {
      console.warn('Video stalled, skipping...');
      nextVideo();
    }
  }, 5000);
  
  video.oncanplay = video.onloadeddata = () => {
    loading.classList.remove('show');
    if (retryTimer) clearTimeout(retryTimer);
    triggerPlay();
  };
}

function loadHLS(url) {
  if (typeof Hls !== 'undefined' && Hls.isSupported()) {
    hlsInstance = new Hls({
      enableWorker: true,
      lowLatencyMode: true,
      backBufferLength: 90
    });
    hlsInstance.loadSource(url);
    hlsInstance.attachMedia(video);
    hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
      loading.classList.remove('show');
      if (retryTimer) clearTimeout(retryTimer);
      triggerPlay();
    });
    hlsInstance.on(Hls.Events.ERROR, (event, data) => {
      if (data.fatal) {
        console.error('HLS fatal error:', data);
        nextVideo();
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = url;
    video.load();
  } else {
    showError('HLS not supported');
  }
}

function cleanupPlayers() {
  if (hlsInstance) {
    hlsInstance.destroy();
    hlsInstance = null;
  }
  video.removeAttribute('src');
  video.load();
}

function updatePlaylistUI() {
  document.querySelectorAll('.playlist-item').forEach(el => {
    const index = parseInt(el.getAttribute('data-index'));
    el.classList.toggle('active', index === currentIndex);
  });
}

function triggerPlay() {
  video.muted = false;
  video.play().catch(err => {
    console.warn('Autoplay failed:', err);
    video.muted = true;
    video.play().catch(() => {
      fakeBtn.focus();
      fakeBtn.click();
      setTimeout(() => video.muted = false, 1000);
    });
  });
}

function prevVideo() {
  loadVideo(getPrevIndex());
}

function nextVideo() {
  loadVideo(getNextIndex());
}

function onVideoEnded() {
  nextVideo();
}

function onVideoError() {
  console.error('Video error, skipping...');
  showError('Failed to load video');
  setTimeout(nextVideo, 2000);
}

function showError(message) {
  loading.innerHTML = `⚠️ ${message}`;
  loading.classList.add('show');
  setTimeout(() => loading.classList.remove('show'), 3000);
}
