from datetime import UTC, datetime
import logging
import traceback
from typing import Any
from uuid import UUID

from src.application.dtos.websocket_message import WebSocketResponse
from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData
from src.domain.entities.message import Message
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.services.data_extraction_service import DataExtractionService
from src.domain.services.rag_service import RAGService
from src.domain.value_objects.conversation_id import ConversationId
from src.domain.value_objects.message_id import MessageId

logger = logging.getLogger(__name__)


class ProcessWebSocketMessageUseCase:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        rag_service: RAGService,
        data_extraction_service: DataExtractionService,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.rag_service = rag_service
        self.data_extraction_service = data_extraction_service

    async def execute(self, message_data: dict[str, Any]) -> WebSocketResponse:
        try:
            logger.info("Full message_data: %s", message_data)
            message_type = message_data.get("type")
            logger.info("Processing message type: %s", message_type)

            if message_type == "text":
                return await self._process_text_message(message_data)
            if message_type == "typing":
                return await self._process_typing_indicator(message_data)
            if message_type == "heartbeat":
                return await self._process_heartbeat(message_data)
            if message_type == "summary_request":
                return await self._process_summary_request(message_data)
            logger.warning("Unknown message type: %s", message_type)
            return WebSocketResponse(
                type="error", error=f"Unknown message type: {message_type}"
            )

        except Exception as e:
            logger.exception("Error in execute")
            return WebSocketResponse(
                type="error", error=f"Error processing message: {e!s}"
            )

    async def _process_text_message(
        self, message_data: dict[str, Any]
    ) -> WebSocketResponse:
        content = message_data.get("data", {}).get("content", "")
        conversation_id_str = message_data.get("conversation_id")
        user_id = message_data.get("user_id")

        if not content:
            return WebSocketResponse(
                type="error", error="Message content cannot be empty"
            )

        # Get or create conversation
        if conversation_id_str:
            conversation_id = ConversationId(UUID(conversation_id_str))
        else:
            conversation_id = ConversationId.generate()
        conversation = await self.conversation_repository.get_by_id(conversation_id)

        if not conversation:
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

        # Create user message
        user_message = Message(
            id=MessageId.generate(),
            conversation_id=conversation_id,
            content=content,
            sender="user",
            timestamp=datetime.now(UTC),
        )

        # Add message to conversation
        conversation.add_message(user_message)

        # Generate AI response using RAG
        ai_response_content = await self.rag_service.generate_response(
            conversation, content
        )

        # Create AI message
        ai_message = Message(
            id=MessageId.generate(),
            conversation_id=conversation_id,
            content=ai_response_content,
            sender="assistant",
            timestamp=datetime.now(UTC),
        )

        # Add AI message to conversation
        conversation.add_message(ai_message)

        # Save conversation
        await self.conversation_repository.save(conversation)

        # Extract data from conversation
        try:
            extracted_data = await self.data_extraction_service.extract_data(
                conversation
            )
        except Exception:
            logger.exception("DEBUG: Error in data_extraction_service.extract_data")
            logger.exception("DEBUG: Traceback: %s", traceback.format_exc())
            # Create a default extracted_data object
            extracted_data = ExtractedData(
                conversation_id=conversation.id,
                order_number=None,
                problem_category=None,
                problem_description=None,
                urgency_level=None,
                extracted_at=datetime.now(UTC),
                confidence_score=0.0,
            )


        # Prepare response
        extracted_info = {
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

        return WebSocketResponse(
            type="text_response",
            content=ai_response_content,
            extracted_info=extracted_info,
        )

    async def _process_typing_indicator(
        self, message_data: dict[str, Any]
    ) -> WebSocketResponse:
        is_typing = message_data.get("data", {}).get("is_typing", False)

        return WebSocketResponse(
            type="typing_response", metadata={"is_typing": is_typing}
        )

    async def _process_heartbeat(
        self, message_data: dict[str, Any]
    ) -> WebSocketResponse:
        timestamp = message_data.get("data", {}).get("timestamp", 0)

        return WebSocketResponse(
            type="heartbeat_response", metadata={"timestamp": timestamp}
        )

    async def _process_summary_request(
        self, message_data: dict[str, Any]
    ) -> WebSocketResponse:
        conversation_id_str = message_data.get("conversation_id")

        if not conversation_id_str:
            return WebSocketResponse(
                type="error", error="Conversation ID is required for summary request"
            )

        conversation_id = ConversationId(UUID(conversation_id_str))
        conversation = await self.conversation_repository.get_by_id(conversation_id)

        if not conversation:
            return WebSocketResponse(type="error", error="Conversation not found")

        # Generate summary
        summary_data = await self.rag_service.generate_summary(conversation)
        key_points = await self.rag_service.extract_key_points(conversation)

        # Extract data
        extracted_data = await self.data_extraction_service.extract_data(conversation)

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

        return WebSocketResponse(
            type="summary_response",
            summary=summary_data.get("summary", ""),
            key_points=key_points,
            extracted_data=extracted_data_dict,
        )
