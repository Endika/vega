from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId


@dataclass
class Conversation:
    id: ConversationId
    user_id: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = field(default_factory=list)
    status: str = "active"  # active, closed, archived
    metadata: dict | None = None

    def add_message(self, message: Message) -> None:
        if message.conversation_id != self.id:
            raise ValueError("Message conversation ID must match conversation ID")

        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def get_last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None

    def get_user_messages(self) -> list[Message]:
        return [msg for msg in self.messages if msg.is_from_user()]

    def get_assistant_messages(self) -> list[Message]:
        return [msg for msg in self.messages if msg.is_from_assistant()]

    def close(self) -> None:
        self.status = "closed"
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        self.status = "archived"
        self.updated_at = datetime.now(UTC)

    def add_metadata(self, key: str, value: Any) -> None:
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any | None = None) -> Any | None:
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
