from datetime import UTC, datetime

import pytest

from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId


class TestConversation:
    def test_given_valid_data_when_creating_conversation_then_conversation_is_created(
        self,
    ):
        # Given
        conversation_id = ConversationId.generate()
        user_id = "user123"
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        # When
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Then
        assert conversation.id == conversation_id
        assert conversation.user_id == user_id
        assert conversation.created_at == created_at
        assert conversation.updated_at == updated_at
        assert conversation.messages == []
        assert conversation.status == "active"

    def test_given_conversation_when_adding_message_then_message_is_added(self):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        message = Message(
            id=MessageId.generate(),
            conversation_id=conversation.id,
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # When
        conversation.add_message(message)

        # Then
        assert len(conversation.messages) == 1
        assert conversation.messages[0] == message

    def test_given_message_with_different_conversation_id_when_adding_then_raises_value_error(
        self,
    ):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),  # Different ID
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # When & Then
        with pytest.raises(
            ValueError, match="Message conversation ID must match conversation ID"
        ):
            conversation.add_message(message)

    def test_given_conversation_with_messages_when_getting_last_message_then_returns_last(
        self,
    ):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        message1 = Message(
            id=MessageId.generate(),
            conversation_id=conversation.id,
            content="First message",
            sender="user",
            timestamp=datetime.now(UTC),
        )
        message2 = Message(
            id=MessageId.generate(),
            conversation_id=conversation.id,
            content="Second message",
            sender="assistant",
            timestamp=datetime.now(UTC),
        )
        conversation.add_message(message1)
        conversation.add_message(message2)

        # When
        last_message = conversation.get_last_message()

        # Then
        assert last_message == message2

    def test_given_empty_conversation_when_getting_last_message_then_returns_none(self):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # When
        last_message = conversation.get_last_message()

        # Then
        assert last_message is None

    def test_given_conversation_when_closing_then_status_changes_to_closed(self):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # When
        conversation.close()

        # Then
        assert conversation.status == "closed"

    def test_given_conversation_when_archiving_then_status_changes_to_archived(self):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # When
        conversation.archive()

        # Then
        assert conversation.status == "archived"

    def test_given_conversation_when_adding_metadata_then_metadata_is_stored(self):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # When
        conversation.add_metadata("key1", "value1")
        conversation.add_metadata("key2", "value2")

        # Then
        assert conversation.metadata == {"key1": "value1", "key2": "value2"}

    def test_given_conversation_with_metadata_when_getting_metadata_then_returns_value(
        self,
    ):
        # Given
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id="user123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            metadata={"key1": "value1"},
        )

        # When
        result = conversation.get_metadata("key1")

        # Then
        assert result == "value1"
