from datetime import UTC, datetime

from src.application.dtos.extracted_data_dto import ExtractedDataDto


class TestExtractedDataDTO:
    def test_given_valid_data_when_creating_dto_then_dto_is_created(self):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        order_number = "12345"
        problem_category = "shipping"
        problem_description = "Order issue"
        urgency_level = "medium"
        confidence_score = 0.8
        extracted_at = datetime.now(UTC)

        # When
        dto = ExtractedDataDto(
            conversation_id=conversation_id,
            order_number=order_number,
            problem_category=problem_category,
            problem_description=problem_description,
            urgency_level=urgency_level,
            extracted_at=extracted_at,
            confidence_score=confidence_score,
            metadata={"key": "value"},
        )

        # Then
        assert dto.conversation_id == conversation_id
        assert dto.order_number == order_number
        assert dto.problem_category == problem_category
        assert dto.problem_description == problem_description
        assert dto.urgency_level == urgency_level
        assert dto.confidence_score == confidence_score
        assert dto.extracted_at == extracted_at
        assert dto.metadata == {"key": "value"}

    def test_given_none_values_when_creating_dto_then_none_values_are_handled(self):
        # Given
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"
        extracted_at = datetime.now(UTC)

        # When
        dto = ExtractedDataDto(
            conversation_id=conversation_id,
            order_number=None,
            problem_category=None,
            problem_description=None,
            urgency_level=None,
            extracted_at=extracted_at,
            confidence_score=0.0,
        )

        # Then
        assert dto.conversation_id == conversation_id
        assert dto.order_number is None
        assert dto.problem_category is None
        assert dto.problem_description is None
        assert dto.urgency_level is None
        assert dto.confidence_score == 0.0
        assert dto.extracted_at == extracted_at
