"""Rate limiting middleware for API protection."""

import time
import redis
from typing import Dict, Optional, Tuple
from fastapi import HTTPException
from agents_core.config.settings import settings


class RateLimiter:
    """Redis-based rate limiter."""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection for rate limiting."""
        try:
            redis_url = settings.get_redis_url_for_memory()
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            print("✅ Rate limiter Redis connected")
        except Exception as e:
            print(f"⚠️ Rate limiter Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if rate limiter is available."""
        return self.redis_client is not None
    
    def check_rate_limit(self, 
                        key: str, 
                        limit: int = 60, 
                        window: int = 60) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier for rate limiting (e.g., IP, user_id)
            limit: Maximum requests allowed in window
            window: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, metadata)
        """
        if not self.is_available():
            # If Redis is down, allow request but log warning
            return True, {"rate_limiter": "unavailable", "remaining": "unknown"}
        
        try:
            current_time = int(time.time())
            redis_key = f"rate_limit:{key}:{current_time // window}"
            
            # Get current count
            current_count = self.redis_client.get(redis_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= limit:
                # Rate limit exceeded
                return False, {
                    "rate_limited": True,
                    "limit": limit,
                    "window": window,
                    "current_count": current_count,
                    "reset_time": (current_time // window + 1) * window
                }
            
            # Increment counter
            pipe = self.redis_client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, window)
            pipe.execute()
            
            remaining = limit - (current_count + 1)
            
            return True, {
                "rate_limited": False,
                "limit": limit,
                "remaining": remaining,
                "current_count": current_count + 1,
                "reset_time": (current_time // window + 1) * window
            }
            
        except Exception as e:
            print(f"Rate limiter error: {e}")
            # On error, allow request
            return True, {"rate_limiter": "error", "error": str(e)}
    
    def get_rate_limit_info(self, key: str, window: int = 60) -> Dict[str, any]:
        """Get current rate limit status for a key."""
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            current_time = int(time.time())
            redis_key = f"rate_limit:{key}:{current_time // window}"
            
            current_count = self.redis_client.get(redis_key)
            current_count = int(current_count) if current_count else 0
            
            return {
                "current_count": current_count,
                "window_start": (current_time // window) * window,
                "window_end": (current_time // window + 1) * window,
                "time_until_reset": (current_time // window + 1) * window - current_time
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}


class CacheManager:
    """Redis-based cache manager."""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection for caching."""
        try:
            redis_url = settings.get_redis_url_for_memory()
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            print("✅ Cache manager Redis connected")
        except Exception as e:
            print(f"⚠️ Cache manager Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self.redis_client is not None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.is_available():
            return None
        
        try:
            return self.redis_client.get(f"cache:{key}")
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: int = 300):
        """Set value in cache with TTL (seconds)."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.setex(f"cache:{key}", ttl, value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete value from cache."""
        if not self.is_available():
            return False
        
        try:
            self.redis_client.delete(f"cache:{key}")
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if not self.is_available():
            return False
        
        try:
            keys = self.redis_client.keys(f"cache:{pattern}")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return False


# Global instances
rate_limiter = RateLimiter()
cache_manager = CacheManager()


def apply_rate_limit(
    identifier: str,
    limit: int = 60,
    window: int = 60,
    error_message: str = "Rate limit exceeded"
) -> Dict[str, any]:
    """
    Apply rate limiting and raise HTTPException if exceeded.
    
    Args:
        identifier: Unique identifier for rate limiting
        limit: Max requests per window
        window: Time window in seconds
        error_message: Custom error message
    
    Returns:
        Rate limit metadata
    """
    is_allowed, metadata = rate_limiter.check_rate_limit(identifier, limit, window)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": error_message,
                "retry_after": metadata.get("reset_time", 0) - int(time.time()),
                "limit": limit,
                "window": window
            }
        )
    
    return metadata
