from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ConversationId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError("Conversation ID must be a valid UUID")

    @classmethod
    def generate(cls) -> "ConversationId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConversationId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
