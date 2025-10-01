from datetime import UTC, datetime
import hashlib
from typing import Any

from src.domain.entities.conversation import Conversation
from src.domain.value_objects.conversation_id import ConversationId
from src.infrastructure.cache.redis_service import RedisService


class ConversationCacheService:
    def __init__(self, redis_service: RedisService) -> None:
        self.redis = redis_service
        self.conversation_ttl = 3600  # 1 hour
        self.active_connections_ttl = 1800  # 30 minutes

    def _get_conversation_key(self, conversation_id: ConversationId) -> str:
        return f"conversation:{conversation_id}"

    def _get_active_connections_key(self) -> str:
        return "active_connections"

    def _get_user_conversations_key(self, user_id: str) -> str:
        return f"user_conversations:{user_id}"

    def _get_rag_cache_key(self, query: str) -> str:
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return f"rag_response:{query_hash}"

    def _get_extraction_cache_key(self, conversation_text: str) -> str:
        text_hash = hashlib.sha256(conversation_text.encode()).hexdigest()
        return f"extraction:{text_hash}"

    async def cache_conversation(self, conversation: Conversation) -> None:
        key = self._get_conversation_key(conversation.id)

        # Convert conversation to cacheable format
        conversation_data = {
            "id": str(conversation.id),
            "user_id": conversation.user_id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "status": conversation.status,
            "metadata": conversation.metadata,
            "message_count": len(conversation.messages),
            "last_message": {
                "content": conversation.messages[-1].content
                if conversation.messages
                else None,
                "sender": conversation.messages[-1].sender
                if conversation.messages
                else None,
                "timestamp": conversation.messages[-1].timestamp.isoformat()
                if conversation.messages
                else None,
            }
            if conversation.messages
            else None,
        }

        await self.redis.set(key, conversation_data, self.conversation_ttl)

    async def get_cached_conversation(
        self, conversation_id: ConversationId
    ) -> dict[str, Any] | None:
        key = self._get_conversation_key(conversation_id)
        return await self.redis.get(key)

    async def invalidate_conversation(self, conversation_id: ConversationId) -> None:
        key = self._get_conversation_key(conversation_id)
        await self.redis.delete(key)

    async def add_active_connection(
        self, conversation_id: str, connection_id: str
    ) -> None:
        key = self._get_active_connections_key()
        await self.redis.sadd(key, f"{conversation_id}:{connection_id}")
        await self.redis.expire(key, self.active_connections_ttl)

    async def remove_active_connection(
        self, conversation_id: str, connection_id: str
    ) -> None:
        key = self._get_active_connections_key()
        await self.redis.srem(key, f"{conversation_id}:{connection_id}")

    async def get_active_connections(self) -> list[str]:
        key = self._get_active_connections_key()
        connections = await self.redis.smembers(key)
        return list(connections)

    async def get_connection_count(self) -> int:
        key = self._get_active_connections_key()
        return await self.redis.scard(key)

    async def cache_rag_response(
        self, query: str, response: str, extracted_info: dict[str, Any]
    ) -> None:
        key = self._get_rag_cache_key(query)
        cache_data = {
            "response": response,
            "extracted_info": extracted_info,
            "cached_at": datetime.now(UTC).isoformat(),
            "query_hash": hashlib.sha256(query.encode()).hexdigest(),
        }
        # Cache for 1 hour
        await self.redis.set(key, cache_data, 3600)

    async def get_cached_rag_response(self, query: str) -> dict[str, Any] | None:
        key = self._get_rag_cache_key(query)
        return await self.redis.get(key)

    async def cache_extraction_data(
        self, conversation_text: str, extracted_data: dict[str, Any]
    ) -> None:
        key = self._get_extraction_cache_key(conversation_text)
        cache_data = {
            "extracted_data": extracted_data,
            "cached_at": datetime.now(UTC).isoformat(),
            "text_hash": hashlib.sha256(conversation_text.encode()).hexdigest(),
        }
        # Cache for 2 hours
        await self.redis.set(key, cache_data, 7200)

    async def get_cached_extraction_data(
        self, conversation_text: str
    ) -> dict[str, Any] | None:
        key = self._get_extraction_cache_key(conversation_text)
        return await self.redis.get(key)

    async def add_user_conversation(self, user_id: str, conversation_id: str) -> None:
        key = self._get_user_conversations_key(user_id)
        await self.redis.lpush(key, conversation_id)
        # Keep only last 50 conversations per user
        await self.redis.ltrim(key, 0, 49)
        await self.redis.expire(key, 86400)  # 24 hours

    async def get_user_conversations(self, user_id: str) -> list[str]:
        key = self._get_user_conversations_key(user_id)
        length = await self.redis.llen(key)
        if length > 0:
            conversations = []
            for _ in range(min(length, 20)):  # Get last 20 conversations
                conv_id = await self.redis.rpop(key)
                if conv_id:
                    conversations.append(conv_id)
                    # Put it back at the end
                    await self.redis.lpush(key, conv_id)
            return conversations
        return []

    async def clear_user_conversations(self, user_id: str) -> None:
        key = self._get_user_conversations_key(user_id)
        await self.redis.delete(key)

    async def get_cache_stats(self) -> dict[str, Any]:
        active_connections = await self.get_connection_count()

        # Get RAG cache stats
        rag_keys = await self.redis.keys("rag_response:*")
        extraction_keys = await self.redis.keys("extraction:*")
        conversation_keys = await self.redis.keys("conversation:*")

        return {
            "active_connections": active_connections,
            "cached_rag_responses": len(rag_keys),
            "cached_extractions": len(extraction_keys),
            "cached_conversations": len(conversation_keys),
            "redis_connected": await self.redis.ping(),
        }
