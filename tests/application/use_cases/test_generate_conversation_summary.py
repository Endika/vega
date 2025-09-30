from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.conversation_dto import ConversationSummaryDTO
from src.application.use_cases.generate_conversation_summary import (
    GenerateConversationSummaryUseCase,
)
from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData
from src.domain.value_objects.conversation_id import ConversationId


class TestGenerateConversationSummaryUseCase:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_rag_service(self):
        return AsyncMock()

    @pytest.fixture
    def mock_data_extraction_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository, mock_rag_service, mock_data_extraction_service):
        return GenerateConversationSummaryUseCase(
            mock_repository, mock_rag_service, mock_data_extraction_service
        )

    @pytest.mark.asyncio
    async def test_given_existing_conversation_when_executing_then_summary_is_generated(
        self, use_case, mock_repository, mock_rag_service, mock_data_extraction_service
    ):
        # Given
        conversation_id = str(uuid4())
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            status="active",
            metadata={"key": "value"},
        )

        mock_repository.get_by_id.return_value = conversation
        mock_rag_service.generate_summary.return_value = {
            "summary": "This is a summary of the conversation."
        }
        mock_rag_service.extract_key_points.return_value = [
            "Point 1",
            "Point 2",
            "Point 3",
        ]

        mock_extracted_data = ExtractedData(
            conversation_id=ConversationId.generate(),
            order_number=None,
            problem_category=None,
            problem_description="Customer inquiry",
            urgency_level=None,
            extracted_at=datetime.now(UTC),
            confidence_score=0.9,
        )
        mock_data_extraction_service.extract_data.return_value = mock_extracted_data

        # When
        result = await use_case.execute(conversation_id)

        # Then
        assert isinstance(result, ConversationSummaryDTO)
        assert result.summary == "This is a summary of the conversation."
        assert result.key_points == ["Point 1", "Point 2", "Point 3"]
        assert (
            result.conversation_id is not None
        )  # Don't check exact value since it's generated
        assert result.extracted_data is not None

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_when_executing_then_none_is_returned(
        self, use_case, mock_repository
    ):
        """Test that None is returned for non-existent conversation."""
        # Given
        conversation_id = str(uuid4())
        mock_repository.get_by_id.return_value = None

        # When
        result = await use_case.execute(conversation_id)

        # Then
        assert result is None
