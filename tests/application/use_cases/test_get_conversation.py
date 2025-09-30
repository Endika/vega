from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.dtos.conversation_dto import ConversationDTO
from src.application.use_cases.get_conversation import GetConversationUseCase
from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId


class TestGetConversationUseCase:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetConversationUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_given_existing_conversation_when_executing_then_conversation_is_returned(
        self, use_case, mock_repository
    ):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            status="active",
            metadata={"key": "value"},
        )

        # Add a message to the conversation
        message = Message(
            id=MessageId.generate(),
            conversation_id=conversation.id,
            content="Hello, world!",
            sender="user",
            timestamp=datetime.now(UTC),
            metadata={"msg_key": "msg_value"},
        )
        conversation.add_message(message)

        mock_repository.get_by_id.return_value = conversation

        # When
        result = await use_case.execute(conversation_id)

        # Then
        assert isinstance(result, ConversationDTO)
        assert result.user_id == "user123"
        assert result.status == "active"
        assert result.metadata == {"key": "value"}
        assert len(result.messages) == 1

        message_dto = result.messages[0]
        assert message_dto.content == "Hello, world!"
        assert message_dto.sender == "user"
        assert message_dto.metadata == {"msg_key": "msg_value"}

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_when_executing_then_none_is_returned(
        self, use_case, mock_repository
    ):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_repository.get_by_id.return_value = None

        # When
        result = await use_case.execute(conversation_id)

        # Then
        assert result is None
