from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities.extracted_data import ExtractedData
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.order_number import OrderNumber
from src.domain.value_objects.problem_category import ProblemCategory
from src.domain.value_objects.urgency_level import UrgencyLevel
from src.infrastructure.database.repositories.extracted_data_repository_impl import (
    ExtractedDataRepositoryImpl,
)


class TestExtractedDataRepositoryImplSimple:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        # Configure session.get to return None by default
        session.get.return_value = None
        # Configure session.add to do nothing
        session.add.return_value = None
        # Configure session.commit to do nothing
        session.commit.return_value = None

        # Configure session.execute for exists method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        return session

    @pytest.fixture
    def repository(self, mock_session):
        return ExtractedDataRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_extracted_data(self):
        conversation_id = ConversationId.generate()
        return ExtractedData(
            conversation_id=conversation_id,
            order_number=OrderNumber("12345"),
            problem_category=ProblemCategory.from_string("shipping"),
            problem_description="Order delivery issue",
            urgency_level=UrgencyLevel.from_string("medium"),
            extracted_at=datetime.now(UTC),
            confidence_score=0.8,
            metadata={"source": "chat"},
        )

    @pytest.mark.asyncio
    async def test_given_new_extracted_data_when_saving_then_data_is_created(
        self, repository, sample_extracted_data, mock_session
    ):
        # Given: New extracted data
        extracted_data = sample_extracted_data

        # When: Saving the extracted data
        await repository.save(extracted_data)

        # Then: session.add should be called
        assert mock_session.add.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_existing_extracted_data_when_saving_then_data_is_updated(
        self, repository, sample_extracted_data, mock_session
    ):
        # Given: Existing extracted data
        extracted_data = sample_extracted_data

        # Mock existing data
        existing_data = MagicMock()
        existing_data.conversation_id = extracted_data.conversation_id.value
        existing_data.order_number = "old_order"
        existing_data.problem_description = "old_description"
        existing_data.confidence_score = 0.5

        mock_session.get.return_value = existing_data

        # When: Saving the extracted data
        await repository.save(extracted_data)

        # Then: session.commit should be called
        assert mock_session.commit.called
        # Verify the existing data was updated
        assert existing_data.order_number == extracted_data.order_number.value
        assert existing_data.problem_description == extracted_data.problem_description
        assert existing_data.confidence_score == extracted_data.confidence_score

    @pytest.mark.asyncio
    async def test_given_existing_conversation_id_when_deleting_then_data_is_deleted(
        self, repository, sample_extracted_data, mock_session
    ):
        # Given: Existing conversation ID
        conversation_id = sample_extracted_data.conversation_id
        mock_data = MagicMock()
        mock_session.get.return_value = mock_data

        # When: Deleting the extracted data
        await repository.delete(conversation_id)

        # Then: session.delete should be called
        assert mock_session.delete.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_id_when_deleting_then_nothing_happens(
        self, repository, mock_session
    ):
        # Given: Non-existent conversation ID
        conversation_id = ConversationId.generate()
        mock_session.get.return_value = None

        # When: Deleting the extracted data
        await repository.delete(conversation_id)

        # Then: session.delete should not be called
        assert not mock_session.delete.called
        assert not mock_session.commit.called

    @pytest.mark.asyncio
    async def test_given_existing_conversation_id_when_checking_exists_then_returns_true(
        self, repository, sample_extracted_data, mock_session
    ):
        # Given: Existing conversation ID
        conversation_id = sample_extracted_data.conversation_id

        # Configure mock to return a value (indicating existence)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = conversation_id.value
        mock_session.execute.return_value = mock_result

        # When: Checking if extracted data exists
        result = await repository.exists(conversation_id)

        # Then: Should return True
        assert result is True

    @pytest.mark.asyncio
    async def test_given_nonexistent_conversation_id_when_checking_exists_then_returns_false(
        self, repository, mock_session
    ):
        # Given: Non-existent conversation ID
        conversation_id = ConversationId.generate()
        mock_session.get.return_value = None

        # When: Checking if extracted data exists
        result = await repository.exists(conversation_id)

        # Then: Should return False
        assert result is False
