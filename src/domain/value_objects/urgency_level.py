from dataclasses import dataclass
from enum import Enum


class UrgencyLevelType(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class UrgencyLevel:
    value: UrgencyLevelType

    def __post_init__(self) -> None:
        if not isinstance(self.value, UrgencyLevelType):
            raise TypeError("Urgency level must be a valid UrgencyLevelType")

    @classmethod
    def from_string(cls, urgency_str: str) -> "UrgencyLevel":
        try:
            return cls(value=UrgencyLevelType(urgency_str.lower()))
        except ValueError as e:
            raise ValueError(f"Invalid urgency level: {urgency_str}") from e

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UrgencyLevel):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
