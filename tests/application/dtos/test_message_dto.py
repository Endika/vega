"""Tests for MessageDTO."""

from datetime import UTC, datetime

from src.application.dtos.message_dto import MessageDTO


class TestMessageDTO:
    """Test MessageDTO functionality."""

    def test_given_valid_data_when_creating_dto_then_dto_is_created(self):
        """Test that a DTO is created with valid data."""
        # Given
        message_id = "123e4567-e89b-12d3-a456-426614174000"
        conversation_id = "123e4567-e89b-12d3-a456-426614174001"
        content = "Hello, world!"
        sender = "user"
        timestamp = datetime.now(UTC)
        metadata = {"key": "value"}

        # When
        dto = MessageDTO(
            id=message_id,
            conversation_id=conversation_id,
            content=content,
            sender=sender,
            timestamp=timestamp,
            metadata=metadata,
        )

        # Then
        assert dto.id == message_id
        assert dto.conversation_id == conversation_id
        assert dto.content == content
        assert dto.sender == sender
        assert dto.timestamp == timestamp
        assert dto.metadata == metadata

    def test_given_none_values_when_creating_dto_then_none_values_are_handled(self):
        """Test that None values are handled correctly in DTO."""
        # Given
        message_id = "123e4567-e89b-12d3-a456-426614174000"
        conversation_id = "123e4567-e89b-12d3-a456-426614174001"
        content = "Hello, world!"
        sender = "user"
        timestamp = datetime.now(UTC)

        # When
        dto = MessageDTO(
            id=message_id,
            conversation_id=conversation_id,
            content=content,
            sender=sender,
            timestamp=timestamp,
            metadata=None,
        )

        # Then
        assert dto.id == message_id
        assert dto.conversation_id == conversation_id
        assert dto.content == content
        assert dto.sender == sender
        assert dto.timestamp == timestamp
        assert dto.metadata is None
