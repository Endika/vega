from datetime import UTC, datetime
from typing import Any

from src.infrastructure.cache.redis_service import RedisService


class RateLimiter:
    def __init__(self, redis_service: RedisService) -> None:
        self.redis = redis_service

    def _get_rate_limit_key(self, identifier: str, window_type: str) -> str:
        return f"rate_limit:{window_type}:{identifier}"

    def _get_window_key(
        self, identifier: str, window_type: str, window_start: int
    ) -> str:
        return f"rate_limit:{window_type}:{identifier}:{window_start}"

    async def is_allowed(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_type: str = "default",
    ) -> dict[str, Any]:
        """
        Check if request is allowed.

        Args:
            identifier: Unique identifier (user_id, ip, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            window_type: Type of rate limit (messages, api_calls, etc.)

        Returns:
            Dict with allowed status and remaining info
        """
        current_time = datetime.now(UTC)
        window_start = int(current_time.timestamp() // window_seconds) * window_seconds

        # Get current window key
        window_key = self._get_window_key(identifier, window_type, window_start)

        # Get current count
        current_count = await self.redis.get_counter(window_key)

        if current_count >= limit:
            return {
                "allowed": False,
                "current_count": current_count,
                "limit": limit,
                "reset_time": window_start + window_seconds,
                "remaining": 0,
            }

        # Increment counter
        new_count = await self.redis.incr(window_key)

        # Set expiration for the window
        await self.redis.expire(window_key, window_seconds)

        return {
            "allowed": True,
            "current_count": new_count,
            "limit": limit,
            "reset_time": window_start + window_seconds,
            "remaining": limit - new_count,
        }

    async def get_remaining_requests(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_type: str = "default",
    ) -> int:
        current_time = datetime.now(UTC)
        window_start = int(current_time.timestamp() // window_seconds) * window_seconds
        window_key = self._get_window_key(identifier, window_type, window_start)

        current_count = await self.redis.get_counter(window_key)
        return max(0, limit - current_count)

    async def reset_rate_limit(
        self, identifier: str, window_type: str = "default"
    ) -> None:
        # Get all keys for this identifier and window type
        pattern = f"rate_limit:{window_type}:{identifier}:*"
        keys = await self.redis.keys(pattern)

        if keys:
            await self.redis.delete(*keys)

    async def get_rate_limit_info(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_type: str = "default",
    ) -> dict[str, Any]:
        current_time = datetime.now(UTC)
        window_start = int(current_time.timestamp() // window_seconds) * window_seconds
        window_key = self._get_window_key(identifier, window_type, window_start)

        current_count = await self.redis.get_counter(window_key)
        ttl = await self.redis.ttl(window_key)

        return {
            "identifier": identifier,
            "window_type": window_type,
            "current_count": current_count,
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "window_seconds": window_seconds,
            "window_start": window_start,
            "window_end": window_start + window_seconds,
            "ttl": ttl,
            "reset_time": window_start + window_seconds if ttl > 0 else None,
        }


class MessageRateLimiter:
    def __init__(self, redis_service: RedisService) -> None:
        self.rate_limiter = RateLimiter(redis_service)

        # Default limits
        self.default_limits = {
            "messages_per_minute": 30,
            "messages_per_hour": 500,
            "messages_per_day": 2000,
            "conversations_per_hour": 10,
            "api_calls_per_minute": 60,
        }

    async def check_message_rate_limit(self, user_id: str) -> dict[str, Any]:
        # Check per-minute limit
        minute_result = await self.rate_limiter.is_allowed(
            user_id,
            self.default_limits["messages_per_minute"],
            60,
            "messages_per_minute",
        )

        if not minute_result["allowed"]:
            return minute_result

        # Check per-hour limit
        hour_result = await self.rate_limiter.is_allowed(
            user_id, self.default_limits["messages_per_hour"], 3600, "messages_per_hour"
        )

        if not hour_result["allowed"]:
            return hour_result

        # Check per-day limit
        return await self.rate_limiter.is_allowed(
            user_id, self.default_limits["messages_per_day"], 86400, "messages_per_day"
        )

    async def check_conversation_rate_limit(self, user_id: str) -> dict[str, Any]:
        return await self.rate_limiter.is_allowed(
            user_id,
            self.default_limits["conversations_per_hour"],
            3600,
            "conversations_per_hour",
        )

    async def check_api_rate_limit(self, user_id: str) -> dict[str, Any]:
        return await self.rate_limiter.is_allowed(
            user_id,
            self.default_limits["api_calls_per_minute"],
            60,
            "api_calls_per_minute",
        )

    async def get_user_rate_limits(self, user_id: str) -> dict[str, Any]:
        return {
            "messages_per_minute": await self.rate_limiter.get_rate_limit_info(
                user_id,
                self.default_limits["messages_per_minute"],
                60,
                "messages_per_minute",
            ),
            "messages_per_hour": await self.rate_limiter.get_rate_limit_info(
                user_id,
                self.default_limits["messages_per_hour"],
                3600,
                "messages_per_hour",
            ),
            "messages_per_day": await self.rate_limiter.get_rate_limit_info(
                user_id,
                self.default_limits["messages_per_day"],
                86400,
                "messages_per_day",
            ),
            "conversations_per_hour": await self.rate_limiter.get_rate_limit_info(
                user_id,
                self.default_limits["conversations_per_hour"],
                3600,
                "conversations_per_hour",
            ),
            "api_calls_per_minute": await self.rate_limiter.get_rate_limit_info(
                user_id,
                self.default_limits["api_calls_per_minute"],
                60,
                "api_calls_per_minute",
            ),
        }

    async def reset_user_rate_limits(self, user_id: str) -> None:
        window_types = [
            "messages_per_minute",
            "messages_per_hour",
            "messages_per_day",
            "conversations_per_hour",
            "api_calls_per_minute",
        ]

        for window_type in window_types:
            await self.rate_limiter.reset_rate_limit(user_id, window_type)
