from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.websocket_message import WebSocketResponse
from src.application.use_cases.process_websocket_message import (
    ProcessWebSocketMessageUseCase,
)
from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData
from src.domain.value_objects.conversation_id import ConversationId


class TestProcessWebSocketMessageUseCase:
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
        return ProcessWebSocketMessageUseCase(
            mock_repository, mock_rag_service, mock_data_extraction_service
        )

    @pytest.mark.asyncio
    async def test_given_text_message_when_executing_then_text_is_processed(
        self, use_case, mock_repository, mock_rag_service, mock_data_extraction_service
    ):
        # Given
        message_data = {
            "type": "text",
            "conversation_id": str(uuid4()),
            "data": {"content": "Hello, how can I help you?"},
            "user_id": "user123",
        }

        # Mock repository to return None (new conversation)
        mock_repository.get_by_id.return_value = None

        # Mock the RAG service response
        mock_rag_service.generate_response.return_value = "I can help you with that!"

        # Mock the data extraction service
        mock_extracted_data = ExtractedData(
            conversation_id=ConversationId.generate(),
            order_number=None,
            problem_category=None,
            problem_description="Hello, how can I help you?",
            urgency_level=None,
            extracted_at=datetime.now(UTC),
            confidence_score=0.8,
        )
        mock_data_extraction_service.extract_data.return_value = mock_extracted_data

        # When
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "text_response"
        assert result.content == "I can help you with that!"
        assert result.extracted_info is not None

    @pytest.mark.asyncio
    async def test_given_typing_message_when_executing_then_typing_is_processed(
        self, use_case
    ):
        # Given
        message_data = {
            "type": "typing",
            "conversation_id": str(uuid4()),
            "is_typing": True,
        }

        # When
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "typing_response"

    @pytest.mark.asyncio
    async def test_given_heartbeat_message_when_executing_then_heartbeat_is_processed(
        self, use_case
    ):
        # Given
        message_data = {"type": "heartbeat", "timestamp": datetime.now(UTC).isoformat()}

        # When
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "heartbeat_response"

    @pytest.mark.asyncio
    async def test_given_summary_request_when_executing_then_summary_is_generated(
        self, use_case, mock_repository, mock_rag_service, mock_data_extraction_service
    ):
        # Given
        conversation_id = str(uuid4())
        message_data = {"type": "summary_request", "conversation_id": conversation_id}

        # Mock conversation
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            status="active",
        )
        mock_repository.get_by_id.return_value = conversation

        mock_rag_service.generate_summary.return_value = {
            "summary": "This is a summary of the conversation."
        }
        mock_rag_service.extract_key_points.return_value = ["Point 1", "Point 2"]

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
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "summary_response"
        assert result.summary == "This is a summary of the conversation."

    @pytest.mark.asyncio
    async def test_given_unknown_message_type_when_executing_then_error_is_returned(
        self, use_case
    ):
        # Given
        message_data = {"type": "unknown_type", "content": "Some content"}

        # When
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "error"
        assert result.error is not None
        assert "Unknown message type" in result.error

    @pytest.mark.asyncio
    async def test_given_exception_when_executing_then_error_is_returned(
        self, use_case, mock_repository, mock_rag_service
    ):
        # Given
        message_data = {
            "type": "text",
            "conversation_id": str(uuid4()),
            "data": {"content": "Hello"},
            "user_id": "user123",
        }

        # Mock repository to return None (new conversation)
        mock_repository.get_by_id.return_value = None

        # Make the RAG service raise an exception
        mock_rag_service.generate_response.side_effect = Exception("RAG service error")

        # When
        result = await use_case.execute(message_data)

        # Then
        assert isinstance(result, WebSocketResponse)
        assert result.type == "error"
        assert result.error is not None
        assert "Error processing message" in result.error
