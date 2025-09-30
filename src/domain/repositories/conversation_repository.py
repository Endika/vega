from abc import ABC, abstractmethod

from src.domain.entities.conversation import Conversation
from src.domain.value_objects.conversation_id import ConversationId


class ConversationRepository(ABC):
    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation."""

    @abstractmethod
    async def get_by_id(self, conversation_id: ConversationId) -> Conversation | None:
        """Get a conversation by ID."""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[Conversation]:
        """Get conversations by user ID."""

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Conversation]:
        """Get all conversations with pagination."""

    @abstractmethod
    async def delete(self, conversation_id: ConversationId) -> None:
        """Delete a conversation."""

    @abstractmethod
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if conversation exists."""
