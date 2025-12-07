"""Widget result caching service."""

from typing import Any, Dict, Optional, Union
import json
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached widget result."""
    data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    widget_name: str
    parameters_hash: str
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class WidgetCache:
    """In-memory cache for widget calculation results.
    
    Provides caching with TTL and parameter-based key generation to avoid
    recalculating expensive widget operations.
    """
    
    def __init__(self, default_ttl_minutes: int = 15, max_entries: int = 1000):
        """Initialize widget cache.
        
        Args:
            default_ttl_minutes: Default time-to-live for cache entries
            max_entries: Maximum number of cache entries before eviction
        """
        self._cache: Dict[str, CacheEntry] = {}
        self.default_ttl_minutes = default_ttl_minutes
        self.max_entries = max_entries
        
    def _generate_cache_key(self, widget_name: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from widget name and parameters.
        
        Args:
            widget_name: Name of the widget
            parameters: Widget input parameters
            
        Returns:
            SHA-256 hash as cache key
        """
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(parameters, sort_keys=True, default=str)
        combined = f"{widget_name}:{sorted_params}"
        return hashlib.sha256(combined.encode()).hexdigest()
        
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired."""
        if entry.expires_at is None:
            return False
        return datetime.utcnow() > entry.expires_at
        
    def _evict_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = [
            key for key, entry in self._cache.items() 
            if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._cache[key]
            
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} expired cache entries")
            
    def _evict_lru(self) -> None:
        """Evict least recently used entries if cache is full."""
        if len(self._cache) < self.max_entries:
            return
            
        # Sort by last accessed time, remove oldest
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed or x[1].created_at
        )
        
        # Remove oldest 10% of entries
        num_to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:num_to_remove]:
            del self._cache[key]
            
        logger.debug(f"Evicted {num_to_remove} LRU cache entries")
        
    def get(self, widget_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result for widget with given parameters.
        
        Args:
            widget_name: Name of the widget
            parameters: Widget input parameters
            
        Returns:
            Cached result data or None if not found/expired
        """
        # Clean up expired entries first
        self._evict_expired()
        
        cache_key = self._generate_cache_key(widget_name, parameters)
        entry = self._cache.get(cache_key)
        
        if entry is None:
            logger.debug(f"Cache miss for widget: {widget_name}")
            return None
            
        if self._is_expired(entry):
            del self._cache[cache_key]
            logger.debug(f"Cache expired for widget: {widget_name}")
            return None
            
        # Update access tracking
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        
        logger.debug(f"Cache hit for widget: {widget_name}")
        return entry.data
        
    def set(self, 
           widget_name: str, 
           parameters: Dict[str, Any],
           data: Dict[str, Any],
           ttl_minutes: Optional[int] = None) -> None:
        """Cache widget result.
        
        Args:
            widget_name: Name of the widget
            parameters: Widget input parameters  
            data: Widget result data to cache
            ttl_minutes: Time-to-live in minutes (uses default if None)
        """
        # Manage cache size
        self._evict_expired()
        self._evict_lru()
        
        cache_key = self._generate_cache_key(widget_name, parameters)
        
        ttl = ttl_minutes or self.default_ttl_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=ttl) if ttl > 0 else None
        
        entry = CacheEntry(
            data=data,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            widget_name=widget_name,
            parameters_hash=cache_key,
            access_count=0
        )
        
        self._cache[cache_key] = entry
        logger.debug(f"Cached result for widget: {widget_name} (TTL: {ttl}m)")
        
    def invalidate(self, widget_name: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Invalidate cache entries.
        
        Args:
            widget_name: Widget to invalidate
            parameters: Specific parameters to invalidate (all if None)
        """
        if parameters is not None:
            # Invalidate specific entry
            cache_key = self._generate_cache_key(widget_name, parameters)
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug(f"Invalidated specific cache entry for: {widget_name}")
        else:
            # Invalidate all entries for widget
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if entry.widget_name == widget_name
            ]
            for key in keys_to_remove:
                del self._cache[key]
            logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for: {widget_name}")
            
    def clear(self) -> None:
        """Clear all cache entries."""
        entry_count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {entry_count} cache entries")
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._evict_expired()
        
        total_entries = len(self._cache)
        widget_counts = {}
        total_accesses = 0
        
        for entry in self._cache.values():
            widget_counts[entry.widget_name] = widget_counts.get(entry.widget_name, 0) + 1
            total_accesses += entry.access_count
            
        return {
            "total_entries": total_entries,
            "max_entries": self.max_entries,
            "cache_usage_percent": (total_entries / self.max_entries) * 100,
            "widget_counts": widget_counts,
            "total_accesses": total_accesses,
            "default_ttl_minutes": self.default_ttl_minutes
        }


# Global cache instance
widget_cache = WidgetCache()


def get_cached_result(widget_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convenience function to get cached widget result."""
    return widget_cache.get(widget_name, parameters)


def cache_result(widget_name: str, 
                parameters: Dict[str, Any], 
                data: Dict[str, Any],
                ttl_minutes: Optional[int] = None) -> None:
    """Convenience function to cache widget result.""" 
    widget_cache.set(widget_name, parameters, data, ttl_minutes)