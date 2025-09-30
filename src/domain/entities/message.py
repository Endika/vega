from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId


@dataclass
class Message:
    id: MessageId
    conversation_id: ConversationId
    content: str
    sender: str  # "user" or "assistant"
    timestamp: datetime
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Message content cannot be empty")

        if self.sender not in ["user", "assistant"]:
            raise ValueError("Sender must be 'user' or 'assistant'")

    def is_from_user(self) -> bool:
        return self.sender == "user"

    def is_from_assistant(self) -> bool:
        return self.sender == "assistant"

    def add_metadata(self, key: str, value: Any) -> None:
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any | None = None) -> Any | None:
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
