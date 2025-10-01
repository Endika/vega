import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

from src.application.dtos.websocket_message import WebSocketResponse
from src.application.use_cases.process_websocket_message import (
    ProcessWebSocketMessageUseCase,
)
from src.infrastructure.cache.conversation_cache import ConversationCacheService
from src.infrastructure.cache.rate_limiter import MessageRateLimiter
from src.infrastructure.cache.redis_service import RedisService
from src.infrastructure.database.config import get_async_session
from src.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from src.infrastructure.services.data_extraction_service_impl import (
    DataExtractionServiceImpl,
)
from src.infrastructure.services.rag_service_impl import RAGServiceImpl

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.connection_count = 0

    async def connect(self, websocket: WebSocket, conversation_id: str) -> None:
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        self.connection_count += 1
        logger.info(
            "WebSocket connected for conversation %s. Total connections: %s",
            conversation_id,
            self.connection_count,
        )

    def disconnect(self, conversation_id: str) -> None:
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            self.connection_count -= 1
            logger.info(
                "WebSocket disconnected for conversation %s. Total connections: %s",
                conversation_id,
                self.connection_count,
            )

    async def send_message(
        self, conversation_id: str, message: WebSocketResponse
    ) -> None:
        if conversation_id in self.active_connections:
            websocket = self.active_connections[conversation_id]
            try:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": message.type,
                            "content": message.content,
                            "extracted_info": message.extracted_info,
                            "summary": message.summary,
                            "key_points": message.key_points,
                            "extracted_data": message.extracted_data,
                            "error": message.error,
                            "metadata": message.metadata,
                        }
                    )
                )
            except ConnectionClosed:
                self.disconnect(conversation_id)
            except Exception:
                logger.exception("Error sending message to %s", conversation_id)
                self.disconnect(conversation_id)

    async def broadcast(self, message: WebSocketResponse) -> None:
        for conversation_id in list(self.active_connections.keys()):
            await self.send_message(conversation_id, message)

    def get_connection_count(self) -> int:
        return self.connection_count


class WebSocketHandler:
    def __init__(self) -> None:
        self.manager = WebSocketManager()
        self.redis_service = RedisService()
        self.cache_service = ConversationCacheService(self.redis_service)
        self.rate_limiter = MessageRateLimiter(self.redis_service)

    async def handle_websocket(
        self, websocket: WebSocket, conversation_id: str
    ) -> None:
        await self.manager.connect(websocket, conversation_id)

        # Add to active connections cache
        connection_id = f"{conversation_id}_{id(websocket)}"
        await self.cache_service.add_active_connection(conversation_id, connection_id)

        logger.info(
            "WebSocket handler initialized for conversation %s", conversation_id
        )

        # Send initial connection message
        try:
            initial_response = WebSocketResponse(
                type="connection",
                content="Connected to Vega AI Chat",
                metadata={"conversation_id": conversation_id, "user_id": None},
            )
            await self.manager.send_message(conversation_id, initial_response)
            logger.info("Sent initial connection message to %s", conversation_id)
        except Exception:
            logger.exception("Error sending initial message")

        try:
            logger.info(
                "Starting message processing loop for conversation %s", conversation_id
            )
            logger.info("WebSocket state: %s", websocket.client_state)

            while True:
                # Receive message
                logger.info("Waiting for message from conversation %s", conversation_id)
                data = await websocket.receive_text()
                logger.info(
                    "Received message from conversation %s: %s", conversation_id, data
                )

                try:
                    message_data = json.loads(data)
                    logger.info("Parsed message data: %s", message_data)

                    # Add conversation_id to message data
                    message_data["conversation_id"] = conversation_id
                    logger.info("Processing message data: %s", message_data)

                    # Check rate limiting
                    user_id = message_data.get("user_id", "anonymous")
                    logger.info("Checking rate limit for user %s", user_id)
                    rate_limit_result = (
                        await self.rate_limiter.check_message_rate_limit(user_id)
                    )

                    if not rate_limit_result["allowed"]:
                        response = WebSocketResponse(
                            type="error",
                            error=f"Rate limit exceeded. Try again in {rate_limit_result.get('reset_time', 60)} seconds",
                        )
                        await self.manager.send_message(conversation_id, response)
                        continue

                    # Process message using use case (this calls OpenAI)
                    logger.info(
                        "Processing message with use case for conversation %s",
                        conversation_id,
                    )
                    logger.info(
                        "About to call _process_message with data: %s", message_data
                    )
                    try:
                        response = await self._process_message(message_data)
                        logger.info("Generated response: %s", response)
                    except Exception as e:
                        logger.exception("Error in _process_message")
                        response = WebSocketResponse(
                            type="error", error=f"Error processing message: {e!s}"
                        )

                    # Send response
                    logger.info("Sending response to conversation %s", conversation_id)
                    await self.manager.send_message(conversation_id, response)

                except json.JSONDecodeError:
                    logger.exception("JSON decode error")
                    response = WebSocketResponse(
                        type="error", error="Invalid JSON format"
                    )
                    await self.manager.send_message(conversation_id, response)
                except Exception as e:
                    logger.exception("Error processing message")
                    response = WebSocketResponse(
                        type="error", error=f"Error processing message: {e!s}"
                    )
                    await self.manager.send_message(conversation_id, response)

        except WebSocketDisconnect:
            await self.cache_service.remove_active_connection(
                conversation_id, connection_id
            )
            self.manager.disconnect(conversation_id)
            logger.info("WebSocket disconnected for conversation %s", conversation_id)
        except Exception:
            await self.cache_service.remove_active_connection(
                conversation_id, connection_id
            )
            self.manager.disconnect(conversation_id)
            logger.exception("Error in WebSocket handler for %s", conversation_id)

    async def _process_message(self, message_data: dict[str, Any]) -> WebSocketResponse:
        try:
            # Get database session
            async for session in get_async_session():
                # Initialize repositories
                conversation_repository = ConversationRepositoryImpl(session)

                # Initialize services with cache
                rag_service = RAGServiceImpl(self.cache_service)
                data_extraction_service = DataExtractionServiceImpl(self.cache_service)
                logger.info("DEBUG: Services initialized successfully")
                logger.info(
                    "DEBUG: data_extraction_service type: %s",
                    type(data_extraction_service),
                )
                logger.info(
                    "DEBUG: data_extraction_service methods: %s",
                    dir(data_extraction_service),
                )

                # Initialize use case
                use_case = ProcessWebSocketMessageUseCase(
                    conversation_repository=conversation_repository,
                    rag_service=rag_service,
                    data_extraction_service=data_extraction_service,
                )
                logger.info("DEBUG: Use case initialized successfully")

                # Execute use case
                return await use_case.execute(message_data)

        except Exception as e:
            logger.exception("Error processing message")
            return WebSocketResponse(
                type="error", error=f"Internal server error: {e!s}"
            )

        # This should never be reached, but MyPy needs it
        return WebSocketResponse(type="error", error="Unexpected error")

    def get_connection_stats(self) -> dict[str, Any]:
        return {
            "active_connections": self.manager.get_connection_count(),
            "conversation_ids": list(self.manager.active_connections.keys()),
        }
