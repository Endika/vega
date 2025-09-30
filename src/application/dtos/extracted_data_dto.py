from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExtractedDataDto:
    conversation_id: str
    order_number: str | None
    problem_category: str | None
    problem_description: str | None
    urgency_level: str | None
    extracted_at: datetime
    confidence_score: float
    metadata: dict | None = None


@dataclass
class ExtractedDataSummary:
    conversation_id: str
    is_complete: bool
    completion_percentage: float
    extracted_fields: dict
    confidence_score: float
    extracted_at: datetime
