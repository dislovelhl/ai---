"""
Rate Limiting Service for Agent Execution Control

Implements sliding window rate limiting using Redis sorted sets for accurate,
distributed rate limiting across service instances.

Features:
- Sliding window algorithm prevents boundary abuse
- Per-user tier rate limits (free: 50/day, pro: 500/day, enterprise: unlimited)
- Real-time usage statistics
- Distributed coordination via Redis

Algorithm:
Uses Redis sorted sets where:
- Key: rate_limit:{user_id}:execution:{date}
- Score: Unix timestamp in milliseconds
- Value: Unique execution ID

The sliding window removes entries older than the time window and counts
remaining entries to determine if limit is exceeded.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from .config import settings

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration per user tier."""

    # Execution limits per 24-hour window
    LIMITS = {
        "free": 50,
        "pro": 500,
        "enterprise": 9999999  # Effectively unlimited
    }

    # Window duration in seconds (24 hours)
    WINDOW_SECONDS = 86400

    @classmethod
    def get_limit(cls, user_tier: str) -> int:
        """Get execution limit for a user tier."""
        return cls.LIMITS.get(user_tier, cls.LIMITS["free"])

    @classmethod
    def get_window_seconds(cls) -> int:
        """Get rate limit window duration in seconds."""
        return cls.WINDOW_SECONDS


class RateLimitService:
    """
    Redis-based rate limiting service using sliding window algorithm.

    Provides accurate rate limiting that prevents boundary abuse by
    tracking individual request timestamps in a sorted set.
    """

    _pool: Optional[ConnectionPool] = None

    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        """Get or create Redis connection pool."""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
                decode_responses=True
            )
        return cls._pool

    async def get_redis(self) -> redis.Redis:
        """Get Redis client from connection pool."""
        pool = await self.get_pool()
        return redis.Redis(connection_pool=pool)

    def _get_redis_key(self, user_id: str) -> str:
        """
        Generate Redis key for user's rate limit tracking.

        Format: rate_limit:{user_id}:execution:{date}
        Date suffix allows for easy cleanup of old keys.
        """
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"rate_limit:{user_id}:execution:{date_str}"

    def _get_current_timestamp_ms(self) -> float:
        """Get current Unix timestamp in milliseconds."""
        return time.time() * 1000

    def _get_window_start_ms(self) -> float:
        """Get timestamp for start of current sliding window (in milliseconds)."""
        window_seconds = RateLimitConfig.get_window_seconds()
        return (time.time() - window_seconds) * 1000

    async def check_rate_limit(
        self,
        user_id: str,
        user_tier: str = "free"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if user has exceeded their rate limit.

        Args:
            user_id: User's unique identifier
            user_tier: User's subscription tier (free, pro, enterprise)

        Returns:
            Tuple of (is_allowed, stats_dict) where:
            - is_allowed: True if request is within limit
            - stats_dict: Dictionary with limit, current usage, remaining, reset_at

        Example:
            allowed, stats = await rate_limit.check_rate_limit(user_id, "free")
            if not allowed:
                raise HTTPException(429, detail=f"Limit exceeded. Reset at {stats['reset_at']}")
        """
        limit = RateLimitConfig.get_limit(user_tier)
        redis_key = self._get_redis_key(user_id)
        window_start_ms = self._get_window_start_ms()

        try:
            redis_client = await self.get_redis()

            # Remove entries outside the sliding window
            await redis_client.zremrangebyscore(redis_key, "-inf", window_start_ms)

            # Count entries in current window
            current_count = await redis_client.zcard(redis_key)

            # Calculate reset time (24 hours from now)
            reset_at = datetime.now(timezone.utc) + timedelta(
                seconds=RateLimitConfig.get_window_seconds()
            )

            # Build stats
            stats = {
                "limit": limit,
                "used": current_count,
                "remaining": max(0, limit - current_count),
                "reset_at": reset_at.isoformat(),
                "reset_at_timestamp": int(reset_at.timestamp())
            }

            is_allowed = current_count < limit

            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for user {user_id} (tier={user_tier}): "
                    f"{current_count}/{limit}"
                )

            return is_allowed, stats

        except Exception as e:
            logger.error(f"Rate limit check failed for user {user_id}: {e}")
            # On Redis failure, allow request but log error
            # This prevents Redis outages from blocking all requests
            return True, {
                "limit": limit,
                "used": 0,
                "remaining": limit,
                "reset_at": datetime.now(timezone.utc).isoformat(),
                "reset_at_timestamp": int(time.time()),
                "error": "Rate limit check unavailable"
            }

    async def increment_usage(
        self,
        user_id: str,
        execution_id: Optional[str] = None
    ) -> bool:
        """
        Increment user's execution count in the sliding window.

        Should be called after successful execution start.

        Args:
            user_id: User's unique identifier
            execution_id: Optional execution ID (generated if not provided)

        Returns:
            True if increment was successful

        Example:
            await rate_limit.increment_usage(user_id, execution.id)
        """
        redis_key = self._get_redis_key(user_id)
        current_time_ms = self._get_current_timestamp_ms()
        exec_id = execution_id or str(uuid.uuid4())

        try:
            redis_client = await self.get_redis()

            # Add execution to sorted set with current timestamp as score
            await redis_client.zadd(redis_key, {exec_id: current_time_ms})

            # Set expiry on the key (cleanup old data)
            # Keep for 48 hours to handle edge cases
            await redis_client.expire(redis_key, RateLimitConfig.get_window_seconds() * 2)

            logger.debug(f"Incremented rate limit for user {user_id}: {exec_id}")
            return True

        except Exception as e:
            logger.error(f"Rate limit increment failed for user {user_id}: {e}")
            return False

    async def get_usage_stats(
        self,
        user_id: str,
        user_tier: str = "free"
    ) -> Dict[str, Any]:
        """
        Get current usage statistics for a user.

        Args:
            user_id: User's unique identifier
            user_tier: User's subscription tier

        Returns:
            Dictionary with:
            - limit: Maximum executions allowed in window
            - used: Number of executions used in current window
            - remaining: Remaining executions available
            - reset_at: ISO timestamp when window resets
            - reset_at_timestamp: Unix timestamp when window resets
            - tier: User's subscription tier

        Example:
            stats = await rate_limit.get_usage_stats(user_id, "pro")
            print(f"Used {stats['used']}/{stats['limit']}, {stats['remaining']} remaining")
        """
        limit = RateLimitConfig.get_limit(user_tier)
        redis_key = self._get_redis_key(user_id)
        window_start_ms = self._get_window_start_ms()

        try:
            redis_client = await self.get_redis()

            # Clean up old entries
            await redis_client.zremrangebyscore(redis_key, "-inf", window_start_ms)

            # Get current count
            current_count = await redis_client.zcard(redis_key)

            # Calculate reset time
            reset_at = datetime.now(timezone.utc) + timedelta(
                seconds=RateLimitConfig.get_window_seconds()
            )

            return {
                "limit": limit,
                "used": current_count,
                "remaining": max(0, limit - current_count),
                "reset_at": reset_at.isoformat(),
                "reset_at_timestamp": int(reset_at.timestamp()),
                "tier": user_tier,
                "window_seconds": RateLimitConfig.get_window_seconds()
            }

        except Exception as e:
            logger.error(f"Failed to get usage stats for user {user_id}: {e}")
            return {
                "limit": limit,
                "used": 0,
                "remaining": limit,
                "reset_at": datetime.now(timezone.utc).isoformat(),
                "reset_at_timestamp": int(time.time()),
                "tier": user_tier,
                "window_seconds": RateLimitConfig.get_window_seconds(),
                "error": "Stats unavailable"
            }

    async def reset_user_limit(self, user_id: str) -> bool:
        """
        Reset rate limit for a specific user (admin operation).

        Args:
            user_id: User's unique identifier

        Returns:
            True if reset was successful
        """
        redis_key = self._get_redis_key(user_id)

        try:
            redis_client = await self.get_redis()
            await redis_client.delete(redis_key)
            logger.info(f"Rate limit reset for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reset rate limit for user {user_id}: {e}")
            return False

    async def get_all_user_stats(self, user_ids: list[str], user_tier: str = "free") -> Dict[str, Dict[str, Any]]:
        """
        Get usage statistics for multiple users (bulk operation).

        Args:
            user_ids: List of user identifiers
            user_tier: Default tier if not specified per user

        Returns:
            Dictionary mapping user_id to their stats
        """
        result = {}

        for user_id in user_ids:
            stats = await self.get_usage_stats(user_id, user_tier)
            result[user_id] = stats

        return result


# Singleton instance
rate_limit_service = RateLimitService()


# Convenience functions for easy import
async def check_rate_limit(user_id: str, user_tier: str = "free") -> Tuple[bool, Dict[str, Any]]:
    """Check if user has exceeded rate limit. Returns (is_allowed, stats)."""
    return await rate_limit_service.check_rate_limit(user_id, user_tier)


async def increment_usage(user_id: str, execution_id: Optional[str] = None) -> bool:
    """Increment user's execution count. Returns True if successful."""
    return await rate_limit_service.increment_usage(user_id, execution_id)


async def get_usage_stats(user_id: str, user_tier: str = "free") -> Dict[str, Any]:
    """Get usage statistics for a user."""
    return await rate_limit_service.get_usage_stats(user_id, user_tier)
