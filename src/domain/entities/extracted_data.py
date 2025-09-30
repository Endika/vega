from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.order_number import OrderNumber
from src.domain.value_objects.problem_category import ProblemCategory
from src.domain.value_objects.urgency_level import UrgencyLevel


@dataclass
class ExtractedData:
    conversation_id: ConversationId
    order_number: OrderNumber | None
    problem_category: ProblemCategory | None
    problem_description: str | None
    urgency_level: UrgencyLevel | None
    extracted_at: datetime
    confidence_score: float = 0.0
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")

    def is_complete(self) -> bool:
        return all(
            [
                self.order_number is not None,
                self.problem_category is not None,
                self.problem_description is not None,
                self.urgency_level is not None,
            ]
        )

    def get_completion_percentage(self) -> float:
        fields = [
            self.order_number,
            self.problem_category,
            self.problem_description,
            self.urgency_level,
        ]
        completed = sum(1 for field in fields if field is not None)
        return (completed / len(fields)) * 100

    def add_metadata(self, key: str, value: Any) -> None:
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any | None = None) -> Any | None:
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
