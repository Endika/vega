from dataclasses import dataclass
from datetime import datetime


@dataclass
class MessageDTO:
    id: str
    conversation_id: str
    content: str
    sender: str
    timestamp: datetime
    metadata: dict | None = None


@dataclass
class CreateMessageRequest:
    content: str
    sender: str
    conversation_id: str
    metadata: dict | None = None
