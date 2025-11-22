/**
 * Universal Lazy Loading Module for Web Players
 * Handles pagination, caching, and efficient memory usage
 */

class UniversalLazyLoader {
    constructor(config = {}) {
        this.chunkSize = config.chunkSize || 2;
        this.cacheSize = config.cacheSize || 10;
        this.cache = new Map();
        this.currentIndex = 0;
        this.totalItems = config.totalItems || 0;
        this.items = config.items || [];
        this.isLoading = false;
        this.searchCache = new Map();
        this.preloadQueue = [];
    }

    /**
     * Load a chunk of items (only 2 by default)
     */
    async getChunk(startIndex = 0) {
        if (this.isLoading) {
            return this.getFromCache(startIndex);
        }

        this.isLoading = true;

        try {
            const cacheKey = `chunk_${startIndex}`;

            // Check cache first
            if (this.cache.has(cacheKey)) {
                this.isLoading = false;
                return this.cache.get(cacheKey);
            }

            // Load chunk
            const endIndex = Math.min(startIndex + this.chunkSize, this.items.length);
            const items = this.items.slice(startIndex, endIndex);

            const chunk = {
                items: items,
                startIndex: startIndex,
                endIndex: endIndex,
                totalItems: this.items.length,
                hasNext: endIndex < this.items.length,
                hasPrevious: startIndex > 0,
                chunkIndex: Math.floor(startIndex / this.chunkSize)
            };

            // Cache the chunk
            this.cacheChunk(cacheKey, chunk);

            // Pre-load next chunk in background
            setTimeout(() => this.preloadNext(startIndex), 100);

            this.isLoading = false;
            return chunk;

        } catch (error) {
            console.error('Failed to load chunk:', error);
            this.isLoading = false;
            return null;
        }
    }

    /**
     * Cache a chunk
     */
    cacheChunk(key, chunk) {
        this.cache.set(key, chunk);

        // Enforce cache size limit
        if (this.cache.size > this.cacheSize) {
            const firstKey = Array.from(this.cache.keys())[0];
            this.cache.delete(firstKey);
        }
    }

    /**
     * Get chunk from cache without loading
     */
    getFromCache(startIndex) {
        const cacheKey = `chunk_${startIndex}`;
        return this.cache.get(cacheKey) || null;
    }

    /**
     * Preload next chunk (non-blocking)
     */
    preloadNext(currentIndex) {
        const nextIndex = currentIndex + this.chunkSize;
        if (nextIndex < this.items.length) {
            const cacheKey = `chunk_${nextIndex}`;
            if (!this.cache.has(cacheKey)) {
                // Add to preload queue
                this.preloadQueue.push(nextIndex);
                
                // Process queue if not already loading
                if (!this.isPreloading) {
                    this.processPreloadQueue();
                }
            }
        }
    }

    /**
     * Process preload queue
     */
    async processPreloadQueue() {
        if (this.preloadQueue.length === 0) return;

        this.isPreloading = true;
        const nextIndex = this.preloadQueue.shift();

        try {
            const endIndex = Math.min(nextIndex + this.chunkSize, this.items.length);
            const items = this.items.slice(nextIndex, endIndex);

            const chunk = {
                items: items,
                startIndex: nextIndex,
                endIndex: endIndex,
                totalItems: this.items.length,
                hasNext: endIndex < this.items.length,
                hasPrevious: nextIndex > 0,
                preloaded: true
            };

            const cacheKey = `chunk_${nextIndex}`;
            this.cacheChunk(cacheKey, chunk);

            // Continue with next in queue
            if (this.preloadQueue.length > 0) {
                setTimeout(() => this.processPreloadQueue(), 50);
            } else {
                this.isPreloading = false;
            }

        } catch (error) {
            console.error('Preload error:', error);
            this.isPreloading = false;
        }
    }

    /**
     * Get single item by index
     */
    getItem(index) {
        if (index >= 0 && index < this.items.length) {
            return this.items[index];
        }
        return null;
    }

    /**
     * Search items (returns immediately with cached results)
     */
    search(query) {
        if (query.length === 0) {
            return [];
        }

        // Check search cache first
        if (this.searchCache.has(query)) {
            return this.searchCache.get(query);
        }

        const queryLower = query.toLowerCase();
        const results = [];

        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i];
            const searchStr = JSON.stringify(item).toLowerCase();

            if (searchStr.includes(queryLower)) {
                results.push({
                    ...item,
                    originalIndex: i
                });
            }
        }

        // Cache results
        this.searchCache.set(query, results);

        // Clear old search cache if too large
        if (this.searchCache.size > 20) {
            const firstKey = Array.from(this.searchCache.keys())[0];
            this.searchCache.delete(firstKey);
        }

        return results;
    }

    /**
     * Navigate to index
     */
    async goToIndex(index) {
        const chunkStart = Math.floor(index / this.chunkSize) * this.chunkSize;
        return await this.getChunk(chunkStart);
    }

    /**
     * Navigate to next chunk
     */
    async nextChunk() {
        const nextIndex = this.currentIndex + this.chunkSize;
        if (nextIndex < this.items.length) {
            this.currentIndex = nextIndex;
            return await this.getChunk(nextIndex);
        }
        return null;
    }

    /**
     * Navigate to previous chunk
     */
    async previousChunk() {
        const prevIndex = Math.max(0, this.currentIndex - this.chunkSize);
        this.currentIndex = prevIndex;
        return await this.getChunk(prevIndex);
    }

    /**
     * Get memory statistics
     */
    getStatistics() {
        return {
            totalItems: this.items.length,
            cachedChunks: this.cache.size,
            cacheSize: this.cacheSize,
            chunkSize: this.chunkSize,
            preloadQueueLength: this.preloadQueue.length,
            estimatedMemory: {
                items: `${(this.items.length * 0.5).toFixed(2)} KB`, // Rough estimate
                cache: `${(this.cache.size * 2).toFixed(2)} KB`,
                total: `${((this.cache.size * 2) + (this.items.length * 0.5)).toFixed(2)} KB`
            },
            currentChunk: Math.floor(this.currentIndex / this.chunkSize),
            searchCacheSize: this.searchCache.size
        };
    }

    /**
     * Clear all caches
     */
    clearCache() {
        this.cache.clear();
        this.searchCache.clear();
        this.preloadQueue = [];
    }

    /**
     * Reset to beginning
     */
    reset() {
        this.currentIndex = 0;
        this.clearCache();
    }
}

/**
 * Virtual Scrolling Helper
 * Handles UI updates for virtual lists
 */
class VirtualScrollHelper {
    constructor(loader, containerSelector, itemTemplate) {
        this.loader = loader;
        this.container = document.querySelector(containerSelector);
        this.itemTemplate = itemTemplate;
        this.currentChunk = null;
        this.scrollPosition = 0;
    }

    /**
     * Render a chunk of items
     */
    async renderChunk(chunk) {
        if (!chunk) return;

        this.currentChunk = chunk;
        this.container.innerHTML = '';

        // Render items in chunk
        chunk.items.forEach((item, index) => {
            const element = this.createItemElement(item, chunk.startIndex + index);
            this.container.appendChild(element);
        });

        // Add pagination info
        this.updatePaginationInfo(chunk);
    }

    /**
     * Create DOM element for item
     */
    createItemElement(item, index) {
        const element = document.createElement('div');
        element.className = 'lazy-item';
        element.dataset.index = index;
        element.innerHTML = typeof this.itemTemplate === 'function' 
            ? this.itemTemplate(item, index)
            : this.itemTemplate;
        return element;
    }

    /**
     * Update pagination info
     */
    updatePaginationInfo(chunk) {
        const info = document.createElement('div');
        info.className = 'pagination-info';
        info.innerHTML = `
            <span class="item-count">Items ${chunk.startIndex + 1}-${chunk.endIndex} of ${chunk.totalItems}</span>
            <button class="prev-btn" ${!chunk.hasPrevious ? 'disabled' : ''}>← Previous</button>
            <button class="next-btn" ${!chunk.hasNext ? 'disabled' : ''}>Next →</button>
        `;

        if (chunk.hasPrevious) {
            info.querySelector('.prev-btn').onclick = () => this.previousPage();
        }
        if (chunk.hasNext) {
            info.querySelector('.next-btn').onclick = () => this.nextPage();
        }

        const existing = this.container.parentElement.querySelector('.pagination-info');
        if (existing) existing.remove();
        this.container.parentElement.appendChild(info);
    }

    /**
     * Navigate to next page
     */
    async nextPage() {
        const chunk = await this.loader.nextChunk();
        if (chunk) {
            this.renderChunk(chunk);
            this.scrollToTop();
        }
    }

    /**
     * Navigate to previous page
     */
    async previousPage() {
        const chunk = await this.loader.previousChunk();
        if (chunk) {
            this.renderChunk(chunk);
            this.scrollToTop();
        }
    }

    /**
     * Scroll to top of container
     */
    scrollToTop() {
        this.container.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Display memory statistics
     */
    showStatistics() {
        const stats = this.loader.getStatistics();
        console.log('Lazy Loader Statistics:', stats);
        return stats;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UniversalLazyLoader, VirtualScrollHelper };
}