from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.infrastructure.cache.conversation_cache import ConversationCacheService
from src.infrastructure.cache.redis_service import RedisService
from src.infrastructure.database.config import create_tables_async
from src.infrastructure.websockets.websocket_handler import WebSocketHandler
from src.presentation.api.conversation_routes import router as conversation_router
from src.presentation.websockets.websocket_routes import router as websocket_router
from src.shared.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
redis_service = RedisService()
cache_service = ConversationCacheService(redis_service)
websocket_handler = WebSocketHandler()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting Vega Customer Support System...")

    # Test Redis connection
    try:
        redis_connected = await redis_service.ping()
        if redis_connected:
            logger.info("Redis connection established successfully")
        else:
            logger.warning("Redis connection failed - continuing without cache")
    except Exception as e:
        logger.warning("Redis connection error: %s - continuing without cache", e)

    # Create database tables (optional for now)
    try:
        await create_tables_async()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning("Database not available: %s - continuing without database", e)

    yield

    # Shutdown
    logger.info("Shutting down Vega Customer Support System...")

    # Close Redis connection
    try:
        await redis_service.disconnect()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning("Error closing Redis connection: %s", e)


# Create FastAPI app
app = FastAPI(
    title="Vega Customer Support System",
    description="Intelligent customer support system with RAG and WebSocket communication",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversation_router)
app.include_router(websocket_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Vega Customer Support System",
        "version": "1.0.0",
        "status": "running",
        "websocket_endpoint": "/ws/chat/{conversation_id}",
        "api_docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "active_connections": str(
            websocket_handler.get_connection_stats()["active_connections"]
        ),
    }


@app.get("/stats")
async def get_stats() -> dict[str, Any]:
    # Get WebSocket stats
    ws_stats = websocket_handler.get_connection_stats()

    # Get cache stats
    try:
        cache_stats = await cache_service.get_cache_stats()
    except Exception as e:
        logger.warning("Error getting cache stats: %s", e)
        cache_stats = {"redis_connected": False}

    return {
        "websocket": ws_stats,
        "cache": cache_stats,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/cache/stats")
async def get_cache_stats() -> dict[str, Any]:
    try:
        stats = await cache_service.get_cache_stats()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@app.post("/cache/clear")
async def clear_cache() -> dict[str, str]:
    try:
        await redis_service.flushdb()
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    # Get configuration from settings
    host = settings.host
    port = settings.port
    debug = settings.debug

    logger.info("Starting server on %s:%s", host, port)
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug",
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30,
    )
