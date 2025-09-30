import uuid

from fastapi import APIRouter, WebSocket

from src.infrastructure.websockets.websocket_handler import WebSocketHandler

router = APIRouter()
websocket_handler = WebSocketHandler()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str) -> None:
    await websocket_handler.handle_websocket(websocket, conversation_id)


@router.websocket("/ws/chat")
async def websocket_chat_general(websocket: WebSocket) -> None:
    conversation_id = str(uuid.uuid4())
    await websocket_handler.handle_websocket(websocket, conversation_id)
