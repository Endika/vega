from uuid import UUID

from src.application.dtos.conversation_dto import ConversationSummaryDTO
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.services.data_extraction_service import DataExtractionService
from src.domain.services.rag_service import RAGService
from src.domain.value_objects.conversation_id import ConversationId


class GenerateConversationSummaryUseCase:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        rag_service: RAGService,
        data_extraction_service: DataExtractionService,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.rag_service = rag_service
        self.data_extraction_service = data_extraction_service

    async def execute(self, conversation_id: str) -> ConversationSummaryDTO | None:
        conversation_id_obj = ConversationId(UUID(conversation_id))
        conversation = await self.conversation_repository.get_by_id(conversation_id_obj)

        if not conversation:
            return None

        # Generate summary using RAG service
        summary_data = await self.rag_service.generate_summary(conversation)
        key_points = await self.rag_service.extract_key_points(conversation)

        # Extract structured data
        extracted_data = await self.data_extraction_service.extract_data(conversation)

        # Convert extracted data to dictionary
        extracted_data_dict = {
            "order_number": str(extracted_data.order_number)
            if extracted_data.order_number
            else None,
            "problem_category": str(extracted_data.problem_category)
            if extracted_data.problem_category
            else None,
            "problem_description": extracted_data.problem_description,
            "urgency_level": str(extracted_data.urgency_level)
            if extracted_data.urgency_level
            else None,
            "confidence_score": extracted_data.confidence_score,
            "completion_percentage": extracted_data.get_completion_percentage(),
        }

        return ConversationSummaryDTO(
            conversation_id=str(conversation.id),
            summary=summary_data.get("summary", ""),
            key_points=key_points,
            extracted_data=extracted_data_dict,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
