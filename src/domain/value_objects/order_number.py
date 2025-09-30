from dataclasses import dataclass
import re


@dataclass(frozen=True)
class OrderNumber:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Order number cannot be empty")

        # Basic validation for order number format
        if not re.match(r"^[A-Z0-9-]{3,20}$", self.value.upper()):
            raise ValueError(
                "Order number must be 3-20 characters, alphanumeric and hyphens only"
            )

    def __str__(self) -> str:
        return self.value.upper()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderNumber):
            return False
        return self.value.upper() == other.value.upper()

    def __hash__(self) -> int:
        return hash(self.value.upper())
