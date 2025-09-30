from unittest.mock import AsyncMock

import pytest

from src.application.dtos.conversation_dto import (
    ConversationDTO,
    CreateConversationRequest,
)
from src.application.use_cases.create_conversation import CreateConversationUseCase
from src.domain.entities.conversation import Conversation


class TestCreateConversationUseCase:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return CreateConversationUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_given_valid_request_when_executing_then_conversation_is_created(
        self, use_case, mock_repository
    ):
        # Given
        request = CreateConversationRequest(
            user_id="user123", metadata={"key": "value"}
        )

        # When
        result = await use_case.execute(request)

        # Then
        assert isinstance(result, ConversationDTO)
        assert result.user_id == "user123"
        assert result.metadata == {"key": "value"}
        assert result.status == "active"
        assert result.messages == []
        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is not None

        # Verify repository was called
        mock_repository.save.assert_called_once()
        saved_conversation = mock_repository.save.call_args[0][0]
        assert isinstance(saved_conversation, Conversation)
        assert saved_conversation.user_id == "user123"

    @pytest.mark.asyncio
    async def test_given_none_values_when_executing_then_conversation_is_created_with_none(
        self, use_case
    ):
        # Given
        request = CreateConversationRequest(user_id=None, metadata=None)

        # When
        result = await use_case.execute(request)

        # Then
        assert isinstance(result, ConversationDTO)
        assert result.user_id is None
        assert result.metadata is None
        assert result.status == "active"
        assert result.messages == []
