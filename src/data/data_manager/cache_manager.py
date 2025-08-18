"""In-memory cache management"""

import threading
from typing import Any, Dict, Optional, List
from datetime import datetime
from collections import OrderedDict

from .models import CacheEntry


class CacheManager:
    """Thread-safe in-memory cache manager"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """Initialize cache manager
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self._stats['misses'] += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        with self._lock:
            # Remove old entry if exists
            if key in self._cache:
                del self._cache[key]
            
            # Check size limit
            if len(self._cache) >= self.max_size:
                # Remove oldest entry (LRU)
                self._cache.popitem(last=False)
                self._stats['evictions'] += 1
            
            # Add new entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl=ttl or self.default_ttl
            )
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0
            }
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total if total > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'hit_rate': hit_rate
            }
    
    def get_keys(self) -> List[str]:
        """Get all cache keys
        
        Returns:
            List of cache keys
        """
        with self._lock:
            return list(self._cache.keys())