#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Management for GLM-5.1 API Requests
"""

import os
import hashlib
import time
from typing import Any, Optional, Dict
from pathlib import Path
from dataclasses import dataclass

try:
    import diskcache
except ImportError:
    diskcache = None


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class CacheManager:
    """
    File-based cache manager for API responses

    Features:
    - Persistent disk cache
    - TTL support
    - Automatic cleanup
    - Statistics tracking
    """

    DEFAULT_CACHE_DIR = Path.home() / ".glm_toolkit" / "cache"
    DEFAULT_TTL = 3600 * 24  # 24 hours

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl: int = DEFAULT_TTL,
        max_size: int = 100 * 1024 * 1024  # 100MB
    ):
        """
        Initialize cache manager

        Args:
            cache_dir: Cache directory path
            ttl: Time-to-live for cache entries in seconds
            max_size: Maximum cache size in bytes
        """
        if diskcache is None:
            raise ImportError("diskcache is required for CacheManager. Install with: pip install diskcache")

        self.cache_dir = Path(cache_dir or self.DEFAULT_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.max_size = max_size

        self.cache = diskcache.Cache(
            str(self.cache_dir),
            size_limit=max_size,
            eviction_policy="least-recently-used"
        )

        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data"""
        import json
        try:
            content = json.dumps(data, sort_keys=True)
        except:
            content = str(data)
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.cache.get(key)
            if value is not None:
                self.stats["hits"] += 1
                return value
            self.stats["misses"] += 1
            return None
        except Exception:
            self.stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL
        """
        try:
            expire_time = time.time() + (ttl or self.ttl)
            self.cache.set(
                key,
                value,
                expire_time=expire_time
            )
            self.stats["sets"] += 1
        except Exception as e:
            pass

    def delete(self, key: str):
        """
        Delete value from cache

        Args:
            key: Cache key
        """
        try:
            self.cache.delete(key)
            self.stats["deletes"] += 1
        except Exception:
            pass

    def clear(self):
        """Clear all cache entries"""
        try:
            self.cache.clear()
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%",
            "cache_size": self.cache.volume(),
            "cache_dir": str(self.cache_dir)
        }

    def cleanup(self):
        """Clean up expired cache entries"""
        try:
            self.cache.expire()
        except Exception:
            pass

    def close(self):
        """Close cache connection"""
        try:
            self.cache.close()
        except Exception:
            pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
