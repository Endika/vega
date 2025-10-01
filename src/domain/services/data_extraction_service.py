from abc import ABC, abstractmethod

from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData


class DataExtractionService(ABC):
    @abstractmethod
    async def extract_data(self, conversation: Conversation) -> ExtractedData:
        """Extract structured data from conversation."""

    @abstractmethod
    async def validate_extracted_data(self, extracted_data: ExtractedData) -> bool:
        """Validate extracted data."""

    @abstractmethod
    async def get_extraction_confidence(self, extracted_data: ExtractedData) -> float:
        """Get confidence score for extracted data."""
