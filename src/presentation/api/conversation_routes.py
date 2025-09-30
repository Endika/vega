from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.conversation_dto import (
    ConversationDTO,
    ConversationSummaryDTO,
    CreateConversationRequest,
)
from src.application.use_cases.create_conversation import CreateConversationUseCase
from src.application.use_cases.generate_conversation_summary import (
    GenerateConversationSummaryUseCase,
)
from src.application.use_cases.get_conversation import GetConversationUseCase
from src.infrastructure.database.config import get_async_session
from src.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from src.infrastructure.services.data_extraction_service_impl import (
    DataExtractionServiceImpl,
)
from src.infrastructure.services.rag_service_impl import RAGServiceImpl

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationDTO)
async def create_conversation(
    request: CreateConversationRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ConversationDTO:
    conversation_repository = ConversationRepositoryImpl(session)
    use_case = CreateConversationUseCase(conversation_repository)

    return await use_case.execute(request)


@router.get("/{conversation_id}", response_model=ConversationDTO)
async def get_conversation(
    conversation_id: str, session: AsyncSession = Depends(get_async_session)
) -> ConversationDTO:
    conversation_repository = ConversationRepositoryImpl(session)
    use_case = GetConversationUseCase(conversation_repository)

    conversation = await use_case.execute(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.get("/", response_model=list[ConversationDTO])
async def list_conversations(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
) -> list[ConversationDTO]:
    conversation_repository = ConversationRepositoryImpl(session)
    conversations = await conversation_repository.get_all(limit=limit, offset=offset)

    # Convert to DTOs
    return [
        ConversationDTO(
            id=str(conv.id),
            user_id=conv.user_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[],  # Simplified for list view
            status=conv.status,
            metadata=conv.metadata,
        )
        for conv in conversations
    ]


@router.post("/{conversation_id}/summary", response_model=ConversationSummaryDTO)
async def generate_conversation_summary(
    conversation_id: str, session: AsyncSession = Depends(get_async_session)
) -> ConversationSummaryDTO:
    conversation_repository = ConversationRepositoryImpl(session)
    rag_service = RAGServiceImpl()
    data_extraction_service = DataExtractionServiceImpl()

    use_case = GenerateConversationSummaryUseCase(
        conversation_repository=conversation_repository,
        rag_service=rag_service,
        data_extraction_service=data_extraction_service,
    )

    summary = await use_case.execute(conversation_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return summary
