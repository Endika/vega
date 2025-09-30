from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.order_number import OrderNumber
from src.domain.value_objects.problem_category import ProblemCategory
from src.domain.value_objects.urgency_level import UrgencyLevel


@dataclass
class CustomerSupportTicket:
    conversation_id: ConversationId
    order_number: OrderNumber
    problem_category: ProblemCategory
    problem_description: str
    urgency_level: UrgencyLevel
    user_id: str | None
    created_at: datetime
    updated_at: datetime
    status: str = "open"  # open, in_progress, resolved, closed
    assigned_agent: str | None = None
    resolution_notes: str | None = None
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.problem_description.strip():
            raise ValueError("Problem description cannot be empty")

    def assign_to_agent(self, agent_id: str) -> None:
        self.assigned_agent = agent_id
        self.status = "in_progress"
        self.updated_at = datetime.now(UTC)

    def resolve(self, resolution_notes: str) -> None:
        self.status = "resolved"
        self.resolution_notes = resolution_notes
        self.updated_at = datetime.now(UTC)

    def close(self) -> None:
        self.status = "closed"
        self.updated_at = datetime.now(UTC)

    def reopen(self) -> None:
        self.status = "open"
        self.updated_at = datetime.now(UTC)

    def add_metadata(self, key: str, value: Any) -> None:
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any | None = None) -> Any | None:
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
