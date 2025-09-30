from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MessageId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError("Message ID must be a valid UUID")

    @classmethod
    def generate(cls) -> "MessageId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MessageId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
