from uuid import UUID

import pytest

from src.domain.value_objects.conversation_id import ConversationId


class TestConversationId:
    def test_given_valid_uuid_object_when_creating_conversation_id_then_id_is_created(
        self,
    ):
        # Given
        uuid_obj = UUID("123e4567-e89b-12d3-a456-426614174000")

        # When
        conversation_id = ConversationId(uuid_obj)

        # Then
        assert conversation_id.value == uuid_obj

    def test_given_invalid_string_when_creating_conversation_id_then_raises_type_error(
        self,
    ):
        # Given
        invalid_string = "not-a-uuid"

        # When & Then
        with pytest.raises(TypeError, match="Conversation ID must be a valid UUID"):
            ConversationId(invalid_string)  # type: ignore[arg-type]

    def test_given_conversation_id_when_generating_new_then_new_id_is_created(self):
        # When
        conversation_id = ConversationId.generate()

        # Then
        assert isinstance(conversation_id, ConversationId)
        assert conversation_id.value is not None
        assert str(conversation_id.value) is not None
