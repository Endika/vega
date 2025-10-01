from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId
from src.infrastructure.database.models import ConversationModel, MessageModel


class ConversationRepositoryImpl(ConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, conversation: Conversation) -> None:
        # Check if conversation exists
        existing_conversation = await self.session.get(
            ConversationModel, conversation.id.value
        )

        if existing_conversation:
            # Update existing conversation
            existing_conversation.user_id = conversation.user_id  # type: ignore[assignment]
            existing_conversation.updated_at = conversation.updated_at  # type: ignore[assignment]
            existing_conversation.status = conversation.status  # type: ignore[assignment]
            existing_conversation.data = conversation.metadata  # type: ignore[assignment]
        else:
            # Create new conversation
            conversation_model = ConversationModel(
                id=conversation.id.value,
                user_id=conversation.user_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                status=conversation.status,
                data=conversation.metadata,
            )
            self.session.add(conversation_model)

        # Save messages
        for message in conversation.messages:
            # Check if message already exists
            existing_message = await self.session.get(MessageModel, message.id.value)

            if not existing_message:
                # Create new message
                message_model = MessageModel(
                    id=message.id.value,
                    conversation_id=message.conversation_id.value,
                    content=message.content,
                    sender=message.sender,
                    timestamp=message.timestamp,
                    data=message.metadata,
                )
                self.session.add(message_model)

        await self.session.commit()

    async def get_by_id(self, conversation_id: ConversationId) -> Conversation | None:
        # Use selectinload to eagerly load messages
        query = (
            select(ConversationModel)
            .options(selectinload(ConversationModel.messages))
            .where(ConversationModel.id == conversation_id.value)
        )

        result = await self.session.execute(query)
        conversation_model = result.scalar_one_or_none()

        if not conversation_model:
            return None

        # Convert MessageModel objects to Message entities
        messages = []
        for msg_model in conversation_model.messages:
            message = Message(
                id=MessageId(msg_model.id),
                conversation_id=ConversationId(msg_model.conversation_id),
                content=msg_model.content,
                sender=msg_model.sender,
                timestamp=msg_model.timestamp,
                metadata=msg_model.data,
            )
            messages.append(message)

        return Conversation(
            id=ConversationId(conversation_model.id),  # type: ignore[arg-type]
            user_id=conversation_model.user_id,  # type: ignore[arg-type]
            created_at=conversation_model.created_at,  # type: ignore[arg-type]
            updated_at=conversation_model.updated_at,  # type: ignore[arg-type]
            status=conversation_model.status,  # type: ignore[arg-type]
            metadata=conversation_model.data or {},  # type: ignore[arg-type]
            messages=messages,
        )

    async def get_by_user_id(self, user_id: str) -> list[Conversation]:
        query = select(ConversationModel).where(ConversationModel.user_id == user_id)
        result = await self.session.execute(query)
        conversation_models = result.scalars().all()

        conversations = []
        for model in conversation_models:
            conversation = Conversation(
                id=ConversationId(model.id),  # type: ignore[arg-type]
                user_id=model.user_id,  # type: ignore[arg-type]
                created_at=model.created_at,  # type: ignore[arg-type]
                updated_at=model.updated_at,  # type: ignore[arg-type]
                status=model.status,  # type: ignore[arg-type]
                metadata=model.data or {},  # type: ignore[arg-type]
            )
            conversations.append(conversation)

        return conversations

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Conversation]:
        query = select(ConversationModel).limit(limit).offset(offset)
        result = await self.session.execute(query)
        conversation_models = result.scalars().all()

        conversations = []
        for model in conversation_models:
            conversation = Conversation(
                id=ConversationId(model.id),  # type: ignore[arg-type]
                user_id=model.user_id,  # type: ignore[arg-type]
                created_at=model.created_at,  # type: ignore[arg-type]
                updated_at=model.updated_at,  # type: ignore[arg-type]
                status=model.status,  # type: ignore[arg-type]
                metadata=model.data or {},  # type: ignore[arg-type]
            )
            conversations.append(conversation)

        return conversations

    async def delete(self, conversation_id: ConversationId) -> None:
        conversation_model = await self.session.get(
            ConversationModel, conversation_id.value
        )
        if conversation_model:
            await self.session.delete(conversation_model)
            await self.session.commit()

    async def exists(self, conversation_id: ConversationId) -> bool:
        conversation_model = await self.session.get(
            ConversationModel, conversation_id.value
        )
        return conversation_model is not None
