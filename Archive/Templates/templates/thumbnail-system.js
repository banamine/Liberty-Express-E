/**
 * M3U MATRIX - IndexedDB Thumbnail System
 * Auto-captures 2 screenshots per video and stores them in browser storage
 */

class ThumbnailManager {
    constructor(dbName = 'M3U_MATRIX_THUMBNAILS', version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
        this.captureQueue = new Set();
        this.capturedThumbnails = new Map();
        this.isCapturing = false;
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                console.log('✅ Thumbnail DB initialized');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object store for thumbnails
                if (!db.objectStoreNames.contains('thumbnails')) {
                    const store = db.createObjectStore('thumbnails', { keyPath: 'id' });
                    store.createIndex('videoUrl', 'videoUrl', { unique: false });
                    store.createIndex('channelName', 'channelName', { unique: false });
                    console.log('📦 Created thumbnails object store');
                }
            };
        });
    }

    /**
     * Generate unique ID for thumbnail
     */
    generateThumbnailId(videoUrl, captureNumber) {
        const hash = this.hashCode(videoUrl);
        return `thumb_${hash}_${captureNumber}`;
    }

    /**
     * Simple hash function for URLs
     */
    hashCode(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(36);
    }

    /**
     * Capture screenshot from video element
     */
    captureScreenshot(videoElement, videoUrl, channelName, captureNumber) {
        return new Promise((resolve, reject) => {
            try {
                // Create canvas
                const canvas = document.createElement('canvas');
                canvas.width = videoElement.videoWidth || 1280;
                canvas.height = videoElement.videoHeight || 720;
                
                // Draw video frame
                const ctx = canvas.getContext('2d');
                ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
                
                // Convert to blob
                canvas.toBlob(async (blob) => {
                    if (!blob) {
                        reject(new Error('Failed to create thumbnail blob'));
                        return;
                    }

                    const thumbnail = {
                        id: this.generateThumbnailId(videoUrl, captureNumber),
                        videoUrl: videoUrl,
                        channelName: channelName,
                        captureNumber: captureNumber,
                        blob: blob,
                        timestamp: Date.now(),
                        width: canvas.width,
                        height: canvas.height
                    };

                    // Save to IndexedDB
                    await this.saveThumbnail(thumbnail);
                    resolve(thumbnail);
                }, 'image/jpeg', 0.85);

            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Save thumbnail to IndexedDB
     */
    async saveThumbnail(thumbnail) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['thumbnails'], 'readwrite');
            const store = transaction.objectStore('thumbnails');
            const request = store.put(thumbnail);

            request.onsuccess = () => {
                console.log(`💾 Saved thumbnail: ${thumbnail.id}`);
                this.capturedThumbnails.set(thumbnail.id, thumbnail);
                resolve(thumbnail);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get thumbnail from IndexedDB
     */
    async getThumbnail(videoUrl, captureNumber) {
        const id = this.generateThumbnailId(videoUrl, captureNumber);
        
        // Check memory cache first
        if (this.capturedThumbnails.has(id)) {
            return this.capturedThumbnails.get(id);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['thumbnails'], 'readonly');
            const store = transaction.objectStore('thumbnails');
            const request = store.get(id);

            request.onsuccess = () => {
                const result = request.result;
                if (result) {
                    this.capturedThumbnails.set(id, result);
                }
                resolve(result);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all thumbnails for a video
     */
    async getVideoThumbnails(videoUrl) {
        const thumbnails = [];
        for (let i = 1; i <= 2; i++) {
            const thumb = await this.getThumbnail(videoUrl, i);
            if (thumb) thumbnails.push(thumb);
        }
        return thumbnails;
    }

    /**
     * Check if video has all thumbnails
     */
    async hasAllThumbnails(videoUrl) {
        const thumb1 = await this.getThumbnail(videoUrl, 1);
        const thumb2 = await this.getThumbnail(videoUrl, 2);
        return thumb1 && thumb2;
    }

    /**
     * Convert thumbnail blob to data URL for display
     */
    thumbnailToDataURL(thumbnail) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(thumbnail.blob);
        });
    }

    /**
     * Auto-capture system: captures 2 screenshots per video
     * Captures at 25% and 75% of video duration
     */
    setupAutoCapture(videoElement, videoUrl, channelName) {
        if (!videoElement || !videoUrl) return;

        const capturePoints = [0.25, 0.75]; // 25% and 75% of duration
        let capturedCount = 0;
        let captureNumber = 1;

        const handleTimeUpdate = async () => {
            if (capturedCount >= 2) return;

            const currentTime = videoElement.currentTime;
            const duration = videoElement.duration;

            if (!duration || duration === Infinity) return;

            const progress = currentTime / duration;

            // Check if we've reached a capture point
            for (let i = 0; i < capturePoints.length; i++) {
                const capturePoint = capturePoints[i];
                
                // Capture within 0.5 seconds of target point
                if (Math.abs(progress - capturePoint) < 0.02 && captureNumber === i + 1) {
                    // Check if already exists
                    const existing = await this.getThumbnail(videoUrl, captureNumber);
                    if (!existing) {
                        try {
                            await this.captureScreenshot(videoElement, videoUrl, channelName, captureNumber);
                            console.log(`📸 Captured thumbnail ${captureNumber}/2 for: ${channelName}`);
                        } catch (error) {
                            console.error('Capture failed:', error);
                        }
                    }
                    capturedCount++;
                    captureNumber++;
                    break;
                }
            }

            // Remove listener when done
            if (capturedCount >= 2) {
                videoElement.removeEventListener('timeupdate', handleTimeUpdate);
            }
        };

        // Check if thumbnails already exist
        this.hasAllThumbnails(videoUrl).then(hasAll => {
            if (!hasAll) {
                videoElement.addEventListener('timeupdate', handleTimeUpdate);
            }
        });
    }

    /**
     * Get statistics about thumbnail coverage
     */
    async getStats(playlist) {
        let totalVideos = playlist.length;
        let videosWithThumbnails = 0;
        let totalThumbnails = 0;

        for (const video of playlist) {
            const thumbnails = await this.getVideoThumbnails(video.url);
            if (thumbnails.length > 0) {
                videosWithThumbnails++;
                totalThumbnails += thumbnails.length;
            }
        }

        return {
            totalVideos,
            videosWithThumbnails,
            totalThumbnails,
            coverage: totalVideos > 0 ? (videosWithThumbnails / totalVideos * 100).toFixed(1) : 0,
            complete: videosWithThumbnails === totalVideos
        };
    }

    /**
     * Get placeholder image data URL
     */
    getPlaceholderImage() {
        // Simple SVG placeholder
        const svg = `
            <svg width="320" height="180" xmlns="http://www.w3.org/2000/svg">
                <rect width="320" height="180" fill="#1a1a2e"/>
                <circle cx="160" cy="90" r="30" fill="#00f3ff" opacity="0.3"/>
                <text x="160" y="100" text-anchor="middle" fill="#00f3ff" font-size="16" font-family="Arial">
                    No Thumbnail
                </text>
            </svg>
        `;
        return `data:image/svg+xml;base64,${btoa(svg)}`;
    }

    /**
     * Clear all thumbnails (for debugging)
     */
    async clearAll() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['thumbnails'], 'readwrite');
            const store = transaction.objectStore('thumbnails');
            const request = store.clear();

            request.onsuccess = () => {
                this.capturedThumbnails.clear();
                console.log('🗑️ Cleared all thumbnails');
                resolve();
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Export thumbnails as JSON (for backup)
     */
    async exportThumbnails() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['thumbnails'], 'readonly');
            const store = transaction.objectStore('thumbnails');
            const request = store.getAll();

            request.onsuccess = async () => {
                const thumbnails = request.result;
                const exported = [];

                for (const thumb of thumbnails) {
                    const dataURL = await this.thumbnailToDataURL(thumb);
                    exported.push({
                        id: thumb.id,
                        videoUrl: thumb.videoUrl,
                        channelName: thumb.channelName,
                        captureNumber: thumb.captureNumber,
                        dataURL: dataURL,
                        timestamp: thumb.timestamp
                    });
                }

                resolve(exported);
            };
            request.onerror = () => reject(request.error);
        });
    }
}

// Make available globally
window.ThumbnailManager = ThumbnailManager;
