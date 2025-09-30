from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData
from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId
from src.infrastructure.services.data_extraction_service_impl import (
    DataExtractionServiceImpl,
)


class TestDataExtractionServiceImplSimple:
    @pytest.fixture
    def mock_cache_service(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_cache_service):
        return DataExtractionServiceImpl(mock_cache_service)

    @pytest.fixture
    def sample_conversation(self):
        conversation_id = ConversationId.generate()
        message_id = MessageId.generate()

        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            content="I have an issue with my order #12345",
            sender="user",
            timestamp=datetime.now(UTC),
            metadata={"test": True},
        )

        return Conversation(
            id=conversation_id,
            user_id="test_user",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            status="active",
            metadata={"test": True},
            messages=[message],
        )

    @pytest.mark.asyncio
    async def test_given_conversation_when_extracting_then_data_is_extracted(
        self, service, sample_conversation, mock_cache_service
    ):
        # Given: Conversation and mocked cache service (no cache hit)
        mock_cache_service.get_cached_extraction_data.return_value = None

        # When: Extracting data from conversation
        result = await service.extract_data(sample_conversation)

        # Then: Should return extracted data
        assert result is not None
        assert isinstance(result, ExtractedData)
        assert result.conversation_id == sample_conversation.id

    @pytest.mark.asyncio
    async def test_given_cached_data_when_extracting_then_cached_data_is_returned(
        self, service, sample_conversation, mock_cache_service
    ):
        # Given: Cached data
        cached_data = {
            "extracted_data": {
                "order_number": "12345",
                "problem_category": "shipping",
                "problem_description": "Order delivery issue",
                "urgency_level": "medium",
                "confidence_score": 0.8,
            }
        }
        mock_cache_service.get_cached_extraction_data.return_value = cached_data

        # When: Extracting data from conversation
        result = await service.extract_data(sample_conversation)

        # Then: Should return cached data
        assert result is not None
        assert isinstance(result, ExtractedData)
        assert result.conversation_id == sample_conversation.id

    @pytest.mark.asyncio
    async def test_given_empty_conversation_when_extracting_then_handles_gracefully(
        self, service, mock_cache_service
    ):
        # Given: Empty conversation

        empty_conversation = Conversation(
            id=ConversationId.generate(),
            user_id="test_user",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            status="active",
            metadata={},
            messages=[],
        )
        mock_cache_service.get_cached_extraction_data.return_value = None

        # When: Extracting data from empty conversation
        result = await service.extract_data(empty_conversation)

        # Then: Should return extracted data with None values
        assert result is not None
        assert isinstance(result, ExtractedData)
        assert result.conversation_id == empty_conversation.id

    @pytest.mark.asyncio
    async def test_given_no_cache_service_when_extracting_then_data_is_extracted(
        self, sample_conversation
    ):
        # Given: Service without cache service
        service = DataExtractionServiceImpl(None)

        # When: Extracting data from conversation
        result = await service.extract_data(sample_conversation)

        # Then: Should return extracted data
        assert result is not None
        assert isinstance(result, ExtractedData)
        assert result.conversation_id == sample_conversation.id
