from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId
from src.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)


class TestConversationRepositoryImplSimple:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        # Configure session.get to return None by default
        session.get.return_value = None
        # Configure session.add to do nothing
        session.add.return_value = None
        # Configure session.commit to do nothing
        session.commit.return_value = None
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return ConversationRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_conversation(self):
        conversation_id = ConversationId.generate()
        message_id = MessageId.generate()

        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            content="Hello, world!",
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
    async def test_given_new_conversation_when_saving_then_conversation_is_created(
        self, repository, sample_conversation, mock_session
    ):
        # Given: A new conversation
        conversation = sample_conversation

        # When: Saving the conversation
        await repository.save(conversation)

        # Then: session.add should be called
        assert mock_session.add.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_existing_conversation_when_saving_then_conversation_is_updated(
        self, repository, sample_conversation, mock_session
    ):
        # Given: An existing conversation
        conversation = sample_conversation

        # Mock existing conversation
        existing_conversation = MagicMock()
        existing_conversation.id = conversation.id.value
        existing_conversation.user_id = "old_user"
        existing_conversation.status = "old_status"
        existing_conversation.data = {"old": "data"}
        existing_conversation.updated_at = datetime.now(UTC)

        mock_session.get.return_value = existing_conversation

        # When: Saving the conversation
        await repository.save(conversation)

        # Then: session.commit should be called
        assert mock_session.commit.called
        # Verify the existing conversation was updated
        assert existing_conversation.user_id == conversation.user_id
        assert existing_conversation.status == conversation.status
        assert existing_conversation.data == conversation.metadata

    @pytest.mark.asyncio
    async def test_given_conversation_with_messages_when_saving_then_messages_are_saved(
        self, repository, sample_conversation, mock_session
    ):
        # Given: A conversation with messages
        conversation = sample_conversation

        # When: Saving the conversation
        await repository.save(conversation)

        # Then: session.add should be called for each message
        # The number of add calls should be at least 1 (conversation) + 1 (message)
        assert mock_session.add.call_count >= 2
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_existing_conversation_when_deleting_then_conversation_is_deleted(
        self, repository, sample_conversation, mock_session
    ):
        # Given: An existing conversation
        conversation_id = sample_conversation.id
        mock_conversation = MagicMock()
        mock_session.get.return_value = mock_conversation

        # When: Deleting the conversation
        await repository.delete(conversation_id)

        # Then: session.delete should be called
        assert mock_session.delete.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_when_deleting_then_nothing_happens(
        self, repository, mock_session
    ):
        # Given: A non-existent conversation
        conversation_id = ConversationId.generate()
        mock_session.get.return_value = None

        # When: Deleting the conversation
        await repository.delete(conversation_id)

        # Then: session.delete should not be called
        assert not mock_session.delete.called
        assert not mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_existing_conversation_when_checking_exists_then_returns_true(
        self, repository, sample_conversation, mock_session
    ):
        # Given: An existing conversation
        conversation_id = sample_conversation.id
        mock_session.get.return_value = MagicMock()

        # When: Checking if conversation exists
        result = await repository.exists(conversation_id)

        # Then: Should return True
        assert result is True

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_when_checking_exists_then_returns_false(
        self, repository, mock_session
    ):
        # Given: A non-existent conversation
        conversation_id = ConversationId.generate()
        mock_session.get.return_value = None

        # When: Checking if conversation exists
        result = await repository.exists(conversation_id)

        # Then: Should return False
        assert result is False
