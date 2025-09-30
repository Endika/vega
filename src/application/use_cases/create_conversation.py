from datetime import UTC, datetime

from src.application.dtos.conversation_dto import (
    ConversationDTO,
    CreateConversationRequest,
)
from src.domain.entities.conversation import Conversation
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.value_objects.conversation_id import ConversationId


class CreateConversationUseCase:
    def __init__(self, conversation_repository: ConversationRepository) -> None:
        self.conversation_repository = conversation_repository

    async def execute(self, request: CreateConversationRequest) -> ConversationDTO:
        # Create conversation
        conversation = Conversation(
            id=ConversationId.generate(),
            user_id=request.user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            metadata=request.metadata,
        )

        # Save conversation
        await self.conversation_repository.save(conversation)

        # Convert to DTO
        return ConversationDTO(
            id=str(conversation.id),
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[],  # Empty messages list for new conversation
            status=conversation.status,
            metadata=conversation.metadata,
        )
