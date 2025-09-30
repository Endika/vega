from uuid import UUID

from src.application.dtos.conversation_dto import ConversationDTO
from src.application.dtos.message_dto import MessageDTO
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.value_objects.conversation_id import ConversationId


class GetConversationUseCase:
    def __init__(self, conversation_repository: ConversationRepository) -> None:
        self.conversation_repository = conversation_repository

    async def execute(self, conversation_id: str) -> ConversationDTO | None:
        conversation_id_obj = ConversationId(UUID(conversation_id))
        conversation = await self.conversation_repository.get_by_id(conversation_id_obj)

        if not conversation:
            return None

        # Convert messages to DTOs
        message_dtos = [
            MessageDTO(
                id=str(msg.id),
                conversation_id=str(msg.conversation_id),
                content=msg.content,
                sender=msg.sender,
                timestamp=msg.timestamp,
                metadata=msg.metadata,
            )
            for msg in conversation.messages
        ]

        return ConversationDTO(
            id=str(conversation.id),
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=message_dtos,
            status=conversation.status,
            metadata=conversation.metadata,
        )
