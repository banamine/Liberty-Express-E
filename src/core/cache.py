"""
Simple Request Caching for ScheduleFlow

Caches GET responses with TTL and auto-invalidation.
"""

import hashlib
import time
from typing import Any, Dict, Optional
from datetime import datetime


class CacheEntry:
    """Single cache entry with TTL"""
    
    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return (time.time() - self.created_at) > self.ttl_seconds
    
    def get(self) -> Optional[Any]:
        """Get data if not expired"""
        if self.is_expired():
            return None
        return self.data


class ResponseCache:
    """Cache for GET responses"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
    
    @staticmethod
    def _make_key(path: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from path and params"""
        key = path
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            key += f"?{param_str}"
        
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, path: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached response"""
        key = self._make_key(path, params)
        entry = self.cache.get(key)
        
        if not entry:
            return None
        
        data = entry.get()
        if data is None:
            del self.cache[key]
        
        return data
    
    def set(self, path: str, data: Any, params: Optional[Dict] = None, ttl: Optional[int] = None):
        """Cache a response"""
        key = self._make_key(path, params)
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(data, ttl)
    
    def invalidate(self, path: Optional[str] = None):
        """Invalidate cache entries"""
        if not path:
            # Clear all
            self.cache.clear()
        else:
            # Clear matching prefix
            keys_to_delete = [k for k in self.cache.keys() if path in k]
            for key in keys_to_delete:
                del self.cache[key]
    
    def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        active = sum(1 for e in self.cache.values() if not e.is_expired())
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active,
            'expired_entries': len(self.cache) - active
        }
