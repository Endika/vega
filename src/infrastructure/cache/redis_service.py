import builtins
import json
from typing import Any

import redis.asyncio as redis

from src.shared.config.settings import settings


class RedisService:
    def __init__(self) -> None:
        self.redis_url = settings.redis_url
        self.redis_client: redis.Redis | None = None

    async def connect(self) -> None:
        if not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Any | None:
        await self.connect()
        if not self.redis_client:
            return None
        value = await self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        if expire:
            return bool(await self.redis_client.setex(key, expire, value))
        return bool(await self.redis_client.set(key, value))

    async def delete(self, key: str) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        return bool(await self.redis_client.delete(key) > 0)

    async def exists(self, key: str) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        return bool(await self.redis_client.exists(key) > 0)

    async def expire(self, key: str, seconds: int) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        return bool(await self.redis_client.expire(key, seconds))

    async def ttl(self, key: str) -> int:
        await self.connect()
        if not self.redis_client:
            return -1
        return int(await self.redis_client.ttl(key))

    # Set operations
    async def sadd(self, key: str, *values: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.sadd(key, *values))  # type: ignore[misc]

    async def srem(self, key: str, *values: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.srem(key, *values))  # type: ignore[misc]

    async def smembers(self, key: str) -> builtins.set[str]:
        await self.connect()
        if not self.redis_client:
            return set()
        return set(await self.redis_client.smembers(key))  # type: ignore[misc]

    async def scard(self, key: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.scard(key))  # type: ignore[misc]

    # Hash operations
    async def hset(self, key: str, field: str, value: Any) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return int(await self.redis_client.hset(key, field, value))  # type: ignore[misc]

    async def hget(self, key: str, field: str) -> Any | None:
        await self.connect()
        if not self.redis_client:
            return None

        value = await self.redis_client.hget(key, field)  # type: ignore[misc]
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def hgetall(self, key: str) -> dict[str, Any]:
        await self.connect()
        if not self.redis_client:
            return {}

        data = await self.redis_client.hgetall(key)  # type: ignore[misc]
        result = {}
        for field, value in data.items():
            try:
                result[field] = json.loads(value)
            except json.JSONDecodeError:
                result[field] = value
        return result

    async def hdel(self, key: str, *fields: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.hdel(key, *fields))  # type: ignore[misc]

    # List operations
    async def lpush(self, key: str, *values: Any) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        serialized_values = []
        for value in values:
            if isinstance(value, (dict, list)):
                serialized_values.append(json.dumps(value))
            else:
                serialized_values.append(str(value))
        return int(await self.redis_client.lpush(key, *serialized_values))  # type: ignore[misc]

    async def rpop(self, key: str) -> Any | None:
        await self.connect()
        if not self.redis_client:
            return None

        value = await self.redis_client.rpop(key)  # type: ignore[misc]
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def llen(self, key: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.llen(key))  # type: ignore[misc]

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        return bool(await self.redis_client.ltrim(key, start, end))  # type: ignore[misc]

    # Counter operations
    async def incr(self, key: str, amount: int = 1) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.incrby(key, amount))

    async def decr(self, key: str, amount: int = 1) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        return int(await self.redis_client.decrby(key, amount))

    async def get_counter(self, key: str) -> int:
        await self.connect()
        if not self.redis_client:
            return 0
        value = await self.redis_client.get(key)
        return int(value) if value else 0

    # Pattern operations
    async def keys(self, pattern: str) -> list[str]:
        await self.connect()
        if not self.redis_client:
            return []
        return list(await self.redis_client.keys(pattern))

    async def flushdb(self) -> bool:
        await self.connect()
        if not self.redis_client:
            return False
        return bool(await self.redis_client.flushdb())

    # Health check
    async def ping(self) -> bool:
        try:
            await self.connect()
            if not self.redis_client:
                return False
            result = await self.redis_client.ping()
        except Exception:
            return False
        else:
            return result is True

    async def get_version(self) -> str:
        try:
            await self.connect()
            if not self.redis_client:
                return "Unknown"
            info = await self.redis_client.info("server")
            return str(info.get("redis_version", "Unknown"))
        except Exception:
            return "Unknown"
