from dataclasses import dataclass
from datetime import datetime

from src.application.dtos.message_dto import MessageDTO


@dataclass
class ConversationDTO:
    id: str
    user_id: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageDTO]
    status: str
    metadata: dict | None = None


@dataclass
class CreateConversationRequest:
    user_id: str | None = None
    metadata: dict | None = None


@dataclass
class ConversationSummaryDTO:
    conversation_id: str
    summary: str
    key_points: list[str]
    extracted_data: dict
    created_at: datetime
    updated_at: datetime
