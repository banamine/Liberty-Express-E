// Web IPTV Player - Main Application
// Handles M3U playlist parsing, channel management, and video playback

let channels = [];
let currentChannelIndex = -1;
let hlsInstance = null;
let dashInstance = null;

// DOM Elements
const player = document.getElementById('player');
const channelList = document.getElementById('channelList');
const historyList = document.getElementById('historyList');
const favoritesList = document.getElementById('favoritesList');
const fileInput = document.getElementById('fileInput');
const urlInput = document.getElementById('urlInput');
const loadUrlBtn = document.getElementById('loadUrl');
const searchInput = document.getElementById('searchInput');
const toggleThemeBtn = document.getElementById('toggleTheme');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const localTimeBar = document.getElementById('localTime');
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializePlayer();
    setupEventListeners();
    updateLocalTime();
    setInterval(updateLocalTime, 1000);
    
    // Load embedded channel data if available
    loadEmbeddedChannels();
    
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
});

function initializePlayer() {
    player.volume = 0.5;
}

function setupEventListeners() {
    // File upload
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // URL load
    if (loadUrlBtn) {
        loadUrlBtn.addEventListener('click', loadFromUrl);
    }
    
    // Search
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Theme toggle
    if (toggleThemeBtn) {
        toggleThemeBtn.addEventListener('click', toggleTheme);
    }
    
    // Sidebar toggle
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', toggleSidebar);
    }
    
    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Player events
    player.addEventListener('error', handlePlayerError);
    player.addEventListener('ended', playNextChannel);
}

function loadEmbeddedChannels() {
    // Check if channel data was embedded in the HTML
    const channelContainer = document.getElementById('channelList');
    if (channelContainer && channelContainer.innerHTML.includes('__CHANNEL_DATA__')) {
        // No embedded data, show default message
        channelContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">Upload a playlist or enter a stream URL to start</div>';
    } else if (channelContainer) {
        // Parse embedded channel data
        const embeddedData = channelContainer.textContent.trim();
        if (embeddedData && embeddedData !== '__CHANNEL_DATA__') {
            parseM3UContent(embeddedData);
        }
    }
}

function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target.result;
        
        if (file.name.endsWith('.m3u') || file.name.endsWith('.m3u8')) {
            parseM3UContent(content);
        } else if (file.name.endsWith('.json')) {
            parseJSONContent(content);
        } else if (file.name.endsWith('.txt')) {
            parseTXTContent(content);
        }
    };
    reader.readAsText(file);
}

function parseM3UContent(content) {
    channels = [];
    const lines = content.split('\n');
    let currentChannel = {};
    
    lines.forEach(line => {
        line = line.trim();
        
        if (line.startsWith('#EXTINF')) {
            // Extract channel info
            const nameMatch = line.match(/tvg-name="([^"]*)"/);
            const logoMatch = line.match(/tvg-logo="([^"]*)"/);
            const titleMatch = line.match(/,(.+)$/);
            
            currentChannel = {
                name: nameMatch ? nameMatch[1] : (titleMatch ? titleMatch[1] : 'Unknown'),
                logo: logoMatch ? logoMatch[1] : '',
                url: ''
            };
        } else if (line && !line.startsWith('#') && currentChannel.name) {
            currentChannel.url = line;
            channels.push({...currentChannel});
            currentChannel = {};
        }
    });
    
    renderChannels();
}

function parseJSONContent(content) {
    try {
        const data = JSON.parse(content);
        channels = data.channels || data || [];
        renderChannels();
    } catch (e) {
        alert('Invalid JSON format');
    }
}

function parseTXTContent(content) {
    const lines = content.split('\n').filter(line => line.trim());
    channels = lines.map((url, index) => ({
        name: `Channel ${index + 1}`,
        url: url.trim(),
        logo: ''
    }));
    renderChannels();
}

function renderChannels(filter = '') {
    const filteredChannels = filter 
        ? channels.filter(ch => ch.name.toLowerCase().includes(filter.toLowerCase()))
        : channels;
    
    channelList.innerHTML = '';
    
    if (filteredChannels.length === 0) {
        channelList.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No channels found</div>';
        return;
    }
    
    filteredChannels.forEach((channel, index) => {
        const item = document.createElement('div');
        item.className = 'channel-item';
        if (index === currentChannelIndex) item.classList.add('playing');
        
        item.innerHTML = `
            <div class="channel-name">${channel.name}</div>
            <div class="channel-url">${channel.url.substring(0, 50)}...</div>
        `;
        
        item.addEventListener('click', () => playChannel(channels.indexOf(channel)));
        channelList.appendChild(item);
    });
}

function playChannel(index) {
    if (index < 0 || index >= channels.length) return;
    
    currentChannelIndex = index;
    const channel = channels[index];
    
    // Clean up previous players
    cleanupPlayers();
    
    const url = channel.url;
    
    // Check URL type and use appropriate player
    if (url.includes('.m3u8')) {
        playHLS(url);
    } else if (url.includes('.mpd')) {
        playDASH(url);
    } else {
        // Direct playback
        player.src = url;
        player.play().catch(e => console.error('Playback error:', e));
    }
    
    renderChannels();
    addToHistory(channel);
    
    document.title = `${channel.name} - Web IPTV Player`;
}

function playHLS(url) {
    if (typeof Hls !== 'undefined' && Hls.isSupported()) {
        hlsInstance = new Hls();
        hlsInstance.loadSource(url);
        hlsInstance.attachMedia(player);
        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
            player.play().catch(e => console.error('HLS playback error:', e));
        });
    } else if (player.canPlayType('application/vnd.apple.mpegurl')) {
        player.src = url;
        player.play().catch(e => console.error('Native HLS playback error:', e));
    }
}

function playDASH(url) {
    if (typeof dashjs !== 'undefined') {
        dashInstance = dashjs.MediaPlayer().create();
        dashInstance.initialize(player, url, true);
    }
}

function cleanupPlayers() {
    if (hlsInstance) {
        hlsInstance.destroy();
        hlsInstance = null;
    }
    if (dashInstance) {
        dashInstance.reset();
        dashInstance = null;
    }
}

function playNextChannel() {
    if (currentChannelIndex < channels.length - 1) {
        playChannel(currentChannelIndex + 1);
    }
}

function loadFromUrl() {
    const url = urlInput.value.trim();
    if (!url) return;
    
    channels = [{
        name: 'Direct Stream',
        url: url,
        logo: ''
    }];
    
    renderChannels();
    playChannel(0);
}

function handleSearch(e) {
    renderChannels(e.target.value);
}

function switchTab(tabName) {
    tabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

function toggleTheme() {
    document.body.classList.toggle('light');
    const isDark = !document.body.classList.contains('light');
    
    const icon = toggleThemeBtn.querySelector('i');
    if (icon) {
        icon.setAttribute('data-feather', isDark ? 'moon' : 'sun');
        if (typeof feather !== 'undefined') feather.replace();
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.style.display = sidebar.style.display === 'none' ? 'flex' : 'none';
}

function updateLocalTime() {
    if (localTimeBar) {
        const now = new Date();
        localTimeBar.textContent = now.toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

function addToHistory(channel) {
    // Store in localStorage
    const history = JSON.parse(localStorage.getItem('iptvHistory') || '[]');
    history.unshift({
        ...channel,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('iptvHistory', JSON.stringify(history.slice(0, 50)));
}

function handlePlayerError(e) {
    console.error('Player error:', e);
    // Try next channel on error
    setTimeout(() => playNextChannel(), 2000);
}
