from datetime import UTC, datetime

from src.application.dtos.conversation_dto import ConversationDTO


class TestConversationDTO:
    def test_given_valid_data_when_creating_dto_then_dto_is_created(self):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        user_id = "user123"
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)
        status = "active"
        metadata = {"key": "value"}

        # When
        dto = ConversationDTO(
            id=conversation_id,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
            messages=[],
            status=status,
            metadata=metadata,
        )

        # Then
        assert dto.id == conversation_id
        assert dto.user_id == user_id
        assert dto.status == status
        assert dto.metadata == metadata
        assert dto.created_at == created_at
        assert dto.updated_at == updated_at
        assert dto.messages == []

    def test_given_none_values_when_creating_dto_then_none_values_are_handled(self):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        # When
        dto = ConversationDTO(
            id=conversation_id,
            user_id=None,
            created_at=created_at,
            updated_at=updated_at,
            messages=[],
            status="active",
            metadata=None,
        )

        # Then
        assert dto.id == conversation_id
        assert dto.user_id is None
        assert dto.metadata is None
        assert dto.status == "active"
