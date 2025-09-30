from dataclasses import dataclass
from enum import Enum


class ProblemCategoryType(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    SHIPPING = "shipping"
    PRODUCT = "product"
    ACCOUNT = "account"
    GENERAL = "general"


@dataclass(frozen=True)
class ProblemCategory:
    value: ProblemCategoryType

    def __post_init__(self) -> None:
        if not isinstance(self.value, ProblemCategoryType):
            raise TypeError("Problem category must be a valid ProblemCategoryType")

    @classmethod
    def from_string(cls, category_str: str) -> "ProblemCategory":
        try:
            return cls(value=ProblemCategoryType(category_str.lower()))
        except ValueError as e:
            raise ValueError(f"Invalid problem category: {category_str}") from e

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProblemCategory):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
