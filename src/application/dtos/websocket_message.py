from dataclasses import dataclass
from typing import Any


@dataclass
class WebSocketMessage:
    type: str
    data: dict[str, Any]
    conversation_id: str | None = None
    user_id: str | None = None


@dataclass
class TextMessage:
    content: str
    conversation_id: str | None = None
    user_id: str | None = None


@dataclass
class TypingIndicator:
    is_typing: bool
    conversation_id: str | None = None
    user_id: str | None = None


@dataclass
class HeartbeatMessage:
    timestamp: float
    conversation_id: str | None = None
    user_id: str | None = None


@dataclass
class SummaryRequest:
    conversation_id: str
    user_id: str | None = None


@dataclass
class WebSocketResponse:
    type: str
    content: str | None = None
    extracted_info: dict[str, Any] | None = None
    summary: str | None = None
    key_points: list[str] | None = None
    extracted_data: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None
