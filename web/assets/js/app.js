// ScheduleFlow - Core Application JavaScript

console.log('ScheduleFlow App Loaded');

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    updateNavigation();
});

function updateNavigation() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath.includes(href) || 
            (href === 'index.html' && currentPath.endsWith('/'))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Utility functions
const Utils = {
    parseM3U(content) {
        const lines = content.split('\n').filter(l => l.trim());
        const items = [];
        let currentTitle = 'Unknown';

        for (let line of lines) {
            if (line.startsWith('#EXTINF')) {
                const match = line.match(/,(.*)$/);
                if (match) currentTitle = match[1].trim() || 'Unknown';
            } else if (line.startsWith('http')) {
                items.push({
                    title: currentTitle,
                    url: line.trim(),
                    id: Math.random().toString(36).substr(2, 9)
                });
            }
        }

        return items;
    },

    parseJSON(content) {
        try {
            return JSON.parse(content);
        } catch (e) {
            console.error('JSON Parse Error:', e);
            return [];
        }
    },

    downloadFile(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    copyToClipboard(text) {
        return navigator.clipboard.writeText(text);
    }
};

// Local Storage Manager
const Storage = {
    save(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    },

    load(key, defaultValue = []) {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        localStorage.clear();
    }
};

console.log('ScheduleFlow utilities loaded');
