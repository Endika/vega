import contextlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.extracted_data import ExtractedData
from src.domain.repositories.extracted_data_repository import ExtractedDataRepository
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.order_number import OrderNumber
from src.domain.value_objects.problem_category import (
    ProblemCategory,
)
from src.domain.value_objects.urgency_level import UrgencyLevel
from src.infrastructure.database.models import ExtractedDataModel


class ExtractedDataRepositoryImpl(ExtractedDataRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, extracted_data: ExtractedData) -> None:
        # Check if extracted data exists
        existing_data = await self.session.get(
            ExtractedDataModel, extracted_data.conversation_id.value
        )

        if existing_data:
            # Update existing data
            existing_data.order_number = (
                str(extracted_data.order_number)  # type: ignore[assignment]
                if extracted_data.order_number
                else None
            )
            existing_data.problem_category = (
                str(extracted_data.problem_category)  # type: ignore[assignment]
                if extracted_data.problem_category
                else None
            )
            existing_data.problem_description = extracted_data.problem_description  # type: ignore[assignment]
            existing_data.urgency_level = (
                str(extracted_data.urgency_level)  # type: ignore[assignment]
                if extracted_data.urgency_level
                else None
            )
            existing_data.extracted_at = extracted_data.extracted_at  # type: ignore[assignment]
            existing_data.confidence_score = extracted_data.confidence_score  # type: ignore[assignment]
            existing_data.metadata = extracted_data.metadata  # type: ignore[misc,assignment]
        else:
            # Create new extracted data
            extracted_data_model = ExtractedDataModel(
                conversation_id=extracted_data.conversation_id.value,
                order_number=str(extracted_data.order_number)
                if extracted_data.order_number
                else None,
                problem_category=str(extracted_data.problem_category)
                if extracted_data.problem_category
                else None,
                problem_description=extracted_data.problem_description,
                urgency_level=str(extracted_data.urgency_level)
                if extracted_data.urgency_level
                else None,
                extracted_at=extracted_data.extracted_at,
                confidence_score=extracted_data.confidence_score,
                metadata=extracted_data.metadata,
            )
            self.session.add(extracted_data_model)

        await self.session.commit()

    async def get_by_conversation_id(
        self, conversation_id: ConversationId
    ) -> ExtractedData | None:
        result = await self.session.execute(
            select(ExtractedDataModel).where(
                ExtractedDataModel.conversation_id == conversation_id.value
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ExtractedData]:
        result = await self.session.execute(
            select(ExtractedDataModel)
            .order_by(ExtractedDataModel.extracted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def delete(self, conversation_id: ConversationId) -> None:
        extracted_data_model = await self.session.get(
            ExtractedDataModel, conversation_id.value
        )
        if extracted_data_model:
            await self.session.delete(extracted_data_model)
            await self.session.commit()

    async def exists(self, conversation_id: ConversationId) -> bool:
        result = await self.session.execute(
            select(ExtractedDataModel.conversation_id).where(
                ExtractedDataModel.conversation_id == conversation_id.value
            )
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: ExtractedDataModel) -> ExtractedData:
        order_number = None
        if model.order_number:
            with contextlib.suppress(ValueError):
                order_number = OrderNumber(model.order_number)  # type: ignore[arg-type]

        problem_category = None
        if model.problem_category:
            with contextlib.suppress(ValueError):
                problem_category = ProblemCategory.from_string(model.problem_category)  # type: ignore[arg-type]

        urgency_level = None
        if model.urgency_level:
            with contextlib.suppress(ValueError):
                urgency_level = UrgencyLevel.from_string(model.urgency_level)  # type: ignore[arg-type]

        return ExtractedData(
            conversation_id=ConversationId(model.conversation_id),  # type: ignore[arg-type]
            order_number=order_number,
            problem_category=problem_category,
            problem_description=model.problem_description,  # type: ignore[arg-type]
            urgency_level=urgency_level,
            extracted_at=model.extracted_at,  # type: ignore[arg-type]
            confidence_score=model.confidence_score,  # type: ignore[arg-type]
            metadata=model.metadata,  # type: ignore[arg-type]
        )
