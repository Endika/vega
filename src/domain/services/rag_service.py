from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.conversation import Conversation


class RAGService(ABC):
    @abstractmethod
    async def generate_response(
        self, conversation: Conversation, user_message: str
    ) -> str:
        """Generate intelligent response using RAG."""

    @abstractmethod
    async def generate_summary(self, conversation: Conversation) -> dict[str, Any]:
        """Generate conversation summary."""

    @abstractmethod
    async def extract_key_points(self, conversation: Conversation) -> list[str]:
        """Extract key points from conversation."""

    @abstractmethod
    async def search_knowledge_base(self, query: str) -> list[dict[str, Any]]:
        """Search knowledge base for relevant information."""
