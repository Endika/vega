from abc import ABC, abstractmethod

from src.domain.entities.customer_support_ticket import CustomerSupportTicket
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.order_number import OrderNumber


class CustomerSupportTicketRepository(ABC):
    @abstractmethod
    async def save(self, ticket: CustomerSupportTicket) -> None:
        """Save a customer support ticket."""

    @abstractmethod
    async def get_by_conversation_id(
        self, conversation_id: ConversationId
    ) -> CustomerSupportTicket | None:
        """Get ticket by conversation ID."""

    @abstractmethod
    async def get_by_order_number(
        self, order_number: OrderNumber
    ) -> list[CustomerSupportTicket]:
        """Get tickets by order number."""

    @abstractmethod
    async def get_by_status(self, status: str) -> list[CustomerSupportTicket]:
        """Get tickets by status."""

    @abstractmethod
    async def get_by_urgency_level(
        self, urgency_level: str
    ) -> list[CustomerSupportTicket]:
        """Get tickets by urgency level."""

    @abstractmethod
    async def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[CustomerSupportTicket]:
        """Get all tickets with pagination."""

    @abstractmethod
    async def delete(self, conversation_id: ConversationId) -> None:
        """Delete a ticket."""

    @abstractmethod
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if ticket exists."""
