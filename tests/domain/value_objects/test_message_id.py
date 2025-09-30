from uuid import UUID

import pytest

from src.domain.value_objects.message_id import MessageId


class TestMessageId:
    def test_given_valid_uuid_object_when_creating_message_id_then_id_is_created(self):
        # Given
        uuid_obj = UUID("123e4567-e89b-12d3-a456-426614174000")

        # When
        message_id = MessageId(uuid_obj)

        # Then
        assert message_id.value == uuid_obj

    def test_given_invalid_string_when_creating_message_id_then_raises_type_error(self):
        # Given
        invalid_string = "not-a-uuid"

        # When & Then
        with pytest.raises(TypeError, match="Message ID must be a valid UUID"):
            MessageId(invalid_string)  # type: ignore[arg-type]

    def test_given_message_id_when_generating_new_then_new_id_is_created(self):
        # When
        message_id = MessageId.generate()

        # Then
        assert isinstance(message_id, MessageId)
        assert message_id.value is not None
        assert str(message_id.value) is not None
