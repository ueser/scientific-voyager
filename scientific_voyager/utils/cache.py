"""
Caching utilities for Scientific Voyager.

This module provides caching mechanisms to avoid redundant API calls and
improve performance when fetching scientific literature.
"""

import os
import json
import hashlib
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable, TypeVar, Generic, Union
from pathlib import Path
import pickle
from functools import wraps
from datetime import datetime, timedelta

from scientific_voyager.config.config_manager import get_config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheItem(Generic[T]):
    """
    A cache item with expiration.
    
    Attributes:
        value: The cached value
        expiry: The expiration time as a timestamp
    """
    
    def __init__(self, value: T, ttl: int = 3600):
        """
        Initialize a cache item.
        
        Args:
            value: The value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.value = value
        self.expiry = time.time() + ttl
    
    def is_expired(self) -> bool:
        """
        Check if the cache item is expired.
        
        Returns:
            True if the cache item is expired, False otherwise
        """
        return time.time() > self.expiry


class MemoryCache:
    """
    In-memory cache implementation.
    
    This class provides a simple in-memory cache with expiration.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the memory cache.
        
        Args:
            default_ttl: Default time to live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        logger.info("Initialized memory cache with default TTL of %d seconds", default_ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if the key is not found or expired
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if item.is_expired():
                del self.cache[key]
                return None
            
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (default: use default_ttl)
        """
        with self.lock:
            self.cache[key] = CacheItem(value, ttl or self.default_ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted, False otherwise
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
    
    def cleanup(self) -> int:
        """
        Remove expired items from the cache.
        
        Returns:
            The number of items removed
        """
        with self.lock:
            expired_keys = [
                key for key, item in self.cache.items() if item.is_expired()
            ]
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary with cache statistics
        """
        with self.lock:
            total_items = len(self.cache)
            expired_items = sum(1 for item in self.cache.values() if item.is_expired())
            valid_items = total_items - expired_items
            
            return {
                'total_items': total_items,
                'valid_items': valid_items,
                'expired_items': expired_items
            }


class DiskCache:
    """
    Disk-based cache implementation.
    
    This class provides a disk-based cache with expiration, suitable for
    caching larger objects or for persistence across application restarts.
    """
    
    def __init__(self, 
                 cache_dir: Optional[str] = None, 
                 default_ttl: int = 86400):
        """
        Initialize the disk cache.
        
        Args:
            cache_dir: The directory to store cache files (default: ~/.scientific_voyager/cache)
            default_ttl: Default time to live in seconds (default: 1 day)
        """
        self.default_ttl = default_ttl
        
        if cache_dir is None:
            home_dir = os.path.expanduser("~")
            cache_dir = os.path.join(home_dir, ".scientific_voyager", "cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.lock = threading.RLock()
        logger.info("Initialized disk cache at %s with default TTL of %d seconds", 
                   self.cache_dir, default_ttl)
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get the cache file path for a key.
        
        Args:
            key: The cache key
            
        Returns:
            The cache file path
        """
        # Use a hash of the key as the filename to avoid invalid characters
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if the key is not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with self.lock:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                
                expiry = cache_data.get('expiry')
                if expiry and time.time() > expiry:
                    # Cache item is expired, delete it
                    cache_path.unlink(missing_ok=True)
                    return None
                
                return cache_data.get('value')
        except (pickle.PickleError, IOError, EOFError) as e:
            logger.warning("Error reading cache file %s: %s", cache_path, str(e))
            # Delete corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (default: use default_ttl)
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with self.lock:
                cache_data = {
                    'key': key,
                    'value': value,
                    'created': time.time(),
                    'expiry': time.time() + (ttl or self.default_ttl)
                }
                
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
        except (pickle.PickleError, IOError) as e:
            logger.warning("Error writing cache file %s: %s", cache_path, str(e))
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted, False otherwise
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return False
        
        try:
            with self.lock:
                cache_path.unlink()
                return True
        except IOError as e:
            logger.warning("Error deleting cache file %s: %s", cache_path, str(e))
            return False
    
    def clear(self) -> None:
        """Clear the cache."""
        try:
            with self.lock:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink(missing_ok=True)
        except IOError as e:
            logger.warning("Error clearing cache directory %s: %s", self.cache_dir, str(e))
    
    def cleanup(self) -> int:
        """
        Remove expired items from the cache.
        
        Returns:
            The number of items removed
        """
        removed = 0
        
        try:
            with self.lock:
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        expiry = cache_data.get('expiry')
                        if expiry and time.time() > expiry:
                            cache_file.unlink()
                            removed += 1
                    except (pickle.PickleError, IOError, EOFError):
                        # Delete corrupted cache file
                        cache_file.unlink(missing_ok=True)
                        removed += 1
        except IOError as e:
            logger.warning("Error cleaning up cache directory %s: %s", self.cache_dir, str(e))
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary with cache statistics
        """
        total_items = 0
        expired_items = 0
        total_size = 0
        
        try:
            with self.lock:
                for cache_file in self.cache_dir.glob("*.cache"):
                    total_items += 1
                    total_size += cache_file.stat().st_size
                    
                    try:
                        with open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        expiry = cache_data.get('expiry')
                        if expiry and time.time() > expiry:
                            expired_items += 1
                    except (pickle.PickleError, IOError, EOFError):
                        expired_items += 1
        except IOError as e:
            logger.warning("Error getting cache statistics: %s", str(e))
        
        return {
            'total_items': total_items,
            'valid_items': total_items - expired_items,
            'expired_items': expired_items,
            'total_size_bytes': total_size
        }


class CacheManager:
    """
    Cache manager that provides a unified interface to different cache implementations.
    
    This class manages different cache implementations and provides a unified interface
    for caching operations.
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        config = get_config()
        cache_config = config.get('cache', {})
        
        # Create memory cache
        memory_ttl = cache_config.get('memory_ttl', 3600)
        self.memory_cache = MemoryCache(default_ttl=memory_ttl)
        
        # Create disk cache
        disk_ttl = cache_config.get('disk_ttl', 86400)
        disk_cache_dir = cache_config.get('disk_cache_dir')
        self.disk_cache = DiskCache(cache_dir=disk_cache_dir, default_ttl=disk_ttl)
        
        # Set up cleanup interval
        self.cleanup_interval = cache_config.get('cleanup_interval', 3600)
        self._last_cleanup = time.time()
        
        logger.info("Initialized cache manager")
    
    def get(self, key: str, use_disk: bool = False) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            use_disk: Whether to use the disk cache (default: False)
            
        Returns:
            The cached value, or None if the key is not found or expired
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # If not found in memory and disk cache is requested, try disk cache
        if use_disk:
            value = self.disk_cache.get(key)
            if value is not None:
                # Store in memory cache for faster access next time
                self.memory_cache.set(key, value)
                return value
        
        return None
    
    def set(self, 
            key: str, 
            value: Any, 
            memory_ttl: Optional[int] = None,
            disk_ttl: Optional[int] = None,
            use_disk: bool = False) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            memory_ttl: Time to live in memory in seconds (default: use default_ttl)
            disk_ttl: Time to live on disk in seconds (default: use default_ttl)
            use_disk: Whether to use the disk cache (default: False)
        """
        # Set in memory cache
        self.memory_cache.set(key, value, ttl=memory_ttl)
        
        # If disk cache is requested, set in disk cache
        if use_disk:
            self.disk_cache.set(key, value, ttl=disk_ttl)
    
    def delete(self, key: str, use_disk: bool = False) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            use_disk: Whether to use the disk cache (default: False)
            
        Returns:
            True if the key was deleted from any cache, False otherwise
        """
        memory_deleted = self.memory_cache.delete(key)
        disk_deleted = False
        
        if use_disk:
            disk_deleted = self.disk_cache.delete(key)
        
        return memory_deleted or disk_deleted
    
    def clear(self, use_disk: bool = False) -> None:
        """
        Clear the cache.
        
        Args:
            use_disk: Whether to clear the disk cache (default: False)
        """
        self.memory_cache.clear()
        
        if use_disk:
            self.disk_cache.clear()
    
    def _maybe_cleanup(self) -> None:
        """Perform cleanup if needed."""
        current_time = time.time()
        if current_time - self._last_cleanup > self.cleanup_interval:
            self.cleanup()
            self._last_cleanup = current_time
    
    def cleanup(self) -> Dict[str, int]:
        """
        Remove expired items from the cache.
        
        Returns:
            A dictionary with the number of items removed from each cache
        """
        memory_removed = self.memory_cache.cleanup()
        disk_removed = self.disk_cache.cleanup()
        
        logger.info("Cache cleanup: removed %d memory items, %d disk items", 
                   memory_removed, disk_removed)
        
        return {
            'memory_removed': memory_removed,
            'disk_removed': disk_removed
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary with cache statistics
        """
        memory_stats = self.memory_cache.get_stats()
        disk_stats = self.disk_cache.get_stats()
        
        return {
            'memory': memory_stats,
            'disk': disk_stats,
            'last_cleanup': self._last_cleanup
        }


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        The global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(
    ttl: int = 3600,
    use_disk: bool = False,
    key_prefix: str = "",
    key_func: Optional[Callable[..., str]] = None
) -> Callable:
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
        use_disk: Whether to use the disk cache (default: False)
        key_prefix: Prefix for cache keys (default: "")
        key_func: Function to generate cache keys (default: None)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get cache manager
            cache_manager = get_cache_manager()
            
            # Generate cache key
            if key_func is not None:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation: function name + args + kwargs
                arg_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{key_prefix}{func.__name__}:{hashlib.md5(arg_str.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key, use_disk=use_disk)
            if cached_value is not None:
                logger.debug("Cache hit for %s", cache_key)
                return cached_value
            
            # Cache miss, call the function
            logger.debug("Cache miss for %s", cache_key)
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, memory_ttl=ttl, disk_ttl=ttl, use_disk=use_disk)
            
            return result
        
        return wrapper
    
    return decorator
