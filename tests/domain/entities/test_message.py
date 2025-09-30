from datetime import UTC, datetime

import pytest

from src.domain.entities.message import Message
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId


class TestMessage:
    def test_given_valid_data_when_creating_message_then_message_is_created(self):
        # Given
        message_id = MessageId.generate()
        conversation_id = ConversationId.generate()
        content = "Hello, world!"
        sender = "user"
        timestamp = datetime.now(UTC)

        # When
        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            content=content,
            sender=sender,
            timestamp=timestamp,
        )

        # Then
        assert message.id == message_id
        assert message.conversation_id == conversation_id
        assert message.content == content
        assert message.sender == sender
        assert message.timestamp == timestamp

    def test_given_empty_content_when_creating_message_then_raises_value_error(self):
        # Given
        message_id = MessageId.generate()
        conversation_id = ConversationId.generate()
        content = ""
        sender = "user"
        timestamp = datetime.now(UTC)

        # When & Then
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(
                id=message_id,
                conversation_id=conversation_id,
                content=content,
                sender=sender,
                timestamp=timestamp,
            )

    def test_given_invalid_sender_when_creating_message_then_raises_value_error(self):
        # Given
        message_id = MessageId.generate()
        conversation_id = ConversationId.generate()
        content = "Hello, world!"
        sender = "invalid_sender"
        timestamp = datetime.now(UTC)

        # When & Then
        with pytest.raises(ValueError, match="Sender must be 'user' or 'assistant'"):
            Message(
                id=message_id,
                conversation_id=conversation_id,
                content=content,
                sender=sender,
                timestamp=timestamp,
            )

    def test_given_user_sender_when_checking_is_from_user_then_returns_true(self):
        # Given
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # When
        result = message.is_from_user()

        # Then
        assert result is True

    def test_given_assistant_sender_when_checking_is_from_assistant_then_returns_true(
        self,
    ):
        # Given
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),
            content="Hello",
            sender="assistant",
            timestamp=datetime.now(UTC),
        )

        # When
        result = message.is_from_assistant()

        # Then
        assert result is True

    def test_given_message_when_adding_metadata_then_metadata_is_stored(self):
        # Given
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # When
        message.add_metadata("key1", "value1")
        message.add_metadata("key2", "value2")

        # Then
        assert message.metadata == {"key1": "value1", "key2": "value2"}

    def test_given_message_with_metadata_when_getting_metadata_then_returns_value(self):
        # Given
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
            metadata={"key1": "value1"},
        )

        # When
        result = message.get_metadata("key1")

        # Then
        assert result == "value1"

    def test_given_message_without_metadata_when_getting_metadata_then_returns_default(
        self,
    ):
        # Given
        message = Message(
            id=MessageId.generate(),
            conversation_id=ConversationId.generate(),
            content="Hello",
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # When
        result = message.get_metadata("nonexistent", "default_value")

        # Then
        assert result == "default_value"
