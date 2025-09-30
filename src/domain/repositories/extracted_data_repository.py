from abc import ABC, abstractmethod

from src.domain.entities.extracted_data import ExtractedData
from src.domain.value_objects.conversation_id import ConversationId


class ExtractedDataRepository(ABC):
    @abstractmethod
    async def save(self, extracted_data: ExtractedData) -> None:
        """Save extracted data."""

    @abstractmethod
    async def get_by_conversation_id(
        self, conversation_id: ConversationId
    ) -> ExtractedData | None:
        """Get extracted data by conversation ID."""

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ExtractedData]:
        """Get all extracted data with pagination."""

    @abstractmethod
    async def delete(self, conversation_id: ConversationId) -> None:
        """Delete extracted data."""

    @abstractmethod
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if extracted data exists."""
