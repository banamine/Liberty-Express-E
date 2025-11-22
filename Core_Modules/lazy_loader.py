"""
Lazy Loading Module for Playlists
Implements virtual scrolling for thousands of items with minimal memory
"""

import json
from typing import List, Dict, Optional, Generator

class LazyPlaylistLoader:
    """
    Efficient playlist loader for large datasets
    - Only 2 items loaded at once
    - Caching of recent items
    - Background pre-loading
    - Generator-based streaming
    """
    
    def __init__(self, items: List[Dict], chunk_size: int = 2, cache_size: int = 10):
        """
        Initialize lazy loader
        
        Args:
            items: Full list of items (shows/channels)
            chunk_size: Items to load at once (default 2)
            cache_size: Recent items to keep cached (default 10)
        """
        self.all_items = items
        self.chunk_size = chunk_size
        self.cache_size = cache_size
        self.cache = {}  # {index: item}
        self.current_index = 0
        self.total_items = len(items)
    
    def get_chunk(self, start_index: int = 0) -> Dict:
        """
        Get a chunk of items with caching
        
        Args:
            start_index: Starting index for chunk
        
        Returns:
            {
                'items': [item1, item2],
                'start_index': 0,
                'total_items': 1000,
                'has_next': True,
                'has_previous': False,
                'cache_info': {'cached': 2, 'position': 0}
            }
        """
        # Ensure valid index
        start_index = max(0, min(start_index, self.total_items - 1))
        
        # Get items for this chunk
        end_index = min(start_index + self.chunk_size, self.total_items)
        items = self.all_items[start_index:end_index]
        
        # Update cache
        for i, item in enumerate(items):
            idx = start_index + i
            self.cache[idx] = item
        
        # Remove old cache entries if over size
        if len(self.cache) > self.cache_size:
            oldest_keys = sorted(self.cache.keys())[:-self.cache_size]
            for key in oldest_keys:
                del self.cache[key]
        
        return {
            'items': items,
            'start_index': start_index,
            'total_items': self.total_items,
            'has_next': end_index < self.total_items,
            'has_previous': start_index > 0,
            'cache_info': {
                'cached': len(self.cache),
                'position': start_index
            }
        }
    
    def get_cached_item(self, index: int) -> Optional[Dict]:
        """Get item from cache without loading"""
        return self.cache.get(index)
    
    def preload_next(self, current_index: int) -> Dict:
        """Preload next chunk in background"""
        next_index = current_index + self.chunk_size
        if next_index < self.total_items:
            # Pre-cache the next items
            next_items = self.all_items[next_index:next_index + self.chunk_size]
            for i, item in enumerate(next_items):
                self.cache[next_index + i] = item
            return {'preloaded': len(next_items), 'next_index': next_index}
        return {'preloaded': 0, 'next_index': -1}
    
    def stream_items(self) -> Generator:
        """Generator for streaming items efficiently"""
        for i in range(0, self.total_items, self.chunk_size):
            chunk = self.get_chunk(i)
            yield chunk
    
    def get_item(self, index: int) -> Optional[Dict]:
        """Get single item by index"""
        if 0 <= index < self.total_items:
            # Check cache first
            if index in self.cache:
                return self.cache[index]
            # Load and cache
            item = self.all_items[index]
            self.cache[index] = item
            return item
        return None
    
    def search_items(self, query: str, fields: List[str] = None) -> List[Dict]:
        """
        Search items with lazy loading of results
        Only returns items, doesn't cache all results
        
        Args:
            query: Search term (case-insensitive)
            fields: Fields to search in (default all)
        
        Returns:
            List of matching items
        """
        query_lower = query.lower()
        results = []
        
        for item in self.all_items:
            for field in (fields or item.keys()):
                if field in item:
                    value = str(item[field]).lower()
                    if query_lower in value:
                        results.append(item)
                        break
        
        return results
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
    
    def get_statistics(self) -> Dict:
        """Get memory usage statistics"""
        return {
            'total_items': self.total_items,
            'cached_items': len(self.cache),
            'cache_percentage': (len(self.cache) / self.total_items * 100) if self.total_items > 0 else 0,
            'chunk_size': self.chunk_size,
            'cache_size': self.cache_size
        }


class PlaylistSerializer:
    """Serialize/deserialize playlists for efficient transmission"""
    
    @staticmethod
    def serialize_chunk(chunk: Dict) -> str:
        """Serialize chunk to JSON for web transmission"""
        return json.dumps(chunk)
    
    @staticmethod
    def deserialize_chunk(json_str: str) -> Dict:
        """Deserialize chunk from JSON"""
        return json.loads(json_str)
    
    @staticmethod
    def create_manifest(items: List[Dict]) -> Dict:
        """Create a manifest describing the playlist"""
        return {
            'total_items': len(items),
            'chunk_size': 2,
            'estimated_chunks': (len(items) + 1) // 2,
            'first_item': items[0] if items else None,
            'last_item': items[-1] if items else None
        }


def create_lazy_playlist_html(playlist_data: List[Dict], chunk_size: int = 2) -> str:
    """
    Generate HTML with lazy loading for a playlist
    
    Args:
        playlist_data: List of show/channel items
        chunk_size: Items per chunk
    
    Returns:
        HTML string with lazy loader script
    """
    loader = LazyPlaylistLoader(playlist_data, chunk_size)
    manifest = PlaylistSerializer.create_manifest(playlist_data)
    
    html = f"""
    <script>
    // Lazy Playlist Loader - Minimal Memory Usage
    class LazyPlaylistLoader {{
        constructor(totalItems = {loader.total_items}, chunkSize = {chunk_size}) {{
            this.totalItems = totalItems;
            this.chunkSize = chunkSize;
            this.cache = new Map();
            this.currentIndex = 0;
            this.isLoading = false;
        }}
        
        async loadChunk(startIndex = 0) {{
            if (this.isLoading) return null;
            this.isLoading = true;
            
            try {{
                const cacheKey = `chunk_${{startIndex}}`;
                
                // Check cache first
                if (this.cache.has(cacheKey)) {{
                    this.isLoading = false;
                    return this.cache.get(cacheKey);
                }}
                
                // Load chunk from server
                const response = await fetch(`/api/playlist/chunk?start=${{startIndex}}&size=${{this.chunkSize}}`);
                const chunk = await response.json();
                
                // Cache the chunk
                this.cache.set(cacheKey, chunk);
                
                // Clear old cache if too large (keep 10 chunks)
                if (this.cache.size > 10) {{
                    const keys = Array.from(this.cache.keys());
                    this.cache.delete(keys[0]);
                }}
                
                // Pre-load next chunk in background
                this.preloadNext(startIndex);
                
                this.isLoading = false;
                return chunk;
            }} catch (error) {{
                console.error('Failed to load chunk:', error);
                this.isLoading = false;
                return null;
            }}
        }}
        
        preloadNext(currentIndex) {{
            const nextIndex = currentIndex + this.chunkSize;
            if (nextIndex < this.totalItems) {{
                // Don't await - background load
                fetch(`/api/playlist/chunk?start=${{nextIndex}}&size=${{this.chunkSize}}`);
            }}
        }}
        
        getFromCache(index) {{
            // Search cache for item at index
            for (let [key, chunk] of this.cache) {{
                if (chunk.start_index <= index && index < chunk.start_index + chunk.items.length) {{
                    const itemIndex = index - chunk.start_index;
                    return chunk.items[itemIndex];
                }}
            }}
            return null;
        }}
        
        async search(query) {{
            try {{
                const response = await fetch(`/api/playlist/search?q=${{encodeURIComponent(query)}}`);
                return await response.json();
            }} catch (error) {{
                console.error('Search failed:', error);
                return [];
            }}
        }}
        
        getStats() {{
            return {{
                totalItems: this.totalItems,
                cachedChunks: this.cache.size,
                estimatedMemory: this.cache.size * 2 // Rough estimate
            }};
        }}
    }}
    
    // Initialize loader
    window.playlistLoader = new LazyPlaylistLoader({loader.total_items}, {chunk_size});
    
    // Auto-preload first chunk
    window.playlistLoader.loadChunk(0);
    </script>
    """
    
    return html
