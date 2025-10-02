# Vega Customer Support System

An intelligent customer support system built with Domain-Driven Design (DDD), Hexagonal Architecture, WebSockets, PostgreSQL, and RAG (Retrieval-Augmented Generation) capabilities using LangGraph and OpenAI.

## 🚀 Features

- **🤖 Intelligent Conversational Agent**: Natural language processing with context awareness
- **🔌 Real-time WebSocket Communication**: Live chat functionality for customer support
- **🧠 RAG Implementation**: Knowledge base integration using LangGraph for intelligent responses
- **📊 Structured Data Extraction**: Automatic extraction of order numbers, problem categories, descriptions, and urgency levels
- **📝 Conversation Summarization**: Generate summaries and extract key points from conversations
- **🏗️ Clean Architecture**: DDD, Hexagonal Architecture, and Design Patterns
- **📊 PostgreSQL Integration**: Structured data storage with migrations
- **🐳 Docker Support**: Containerized deployment with Docker Compose
- **🧪 Comprehensive Testing**: Full test suite with WebSocket testing
- **💾 Redis Caching**: High-performance caching system for improved response times
- **📚 Knowledge Base Management**: Automated setup and management of RAG knowledge base

## 🏗️ Architecture

The project follows Domain-Driven Design (DDD) and Hexagonal Architecture principles:

```
src/
├── domain/                 # Domain layer
│   ├── entities/          # Business entities
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── extracted_data.py
│   │   └── customer_support_ticket.py
│   ├── value_objects/     # Value objects
│   │   ├── conversation_id.py
│   │   ├── message_id.py
│   │   ├── order_number.py
│   │   ├── problem_category.py
│   │   └── urgency_level.py
│   ├── repositories/      # Repository interfaces (ports)
│   │   ├── conversation_repository.py
│   │   ├── extracted_data_repository.py
│   │   └── customer_support_ticket_repository.py
│   └── services/          # Domain services
│       ├── data_extraction_service.py
│       └── rag_service.py
├── application/           # Application layer
│   ├── use_cases/        # Use cases
│   │   ├── process_websocket_message.py
│   │   ├── create_conversation.py
│   │   ├── get_conversation.py
│   │   └── generate_conversation_summary.py
│   └── dtos/             # Data Transfer Objects
│       ├── websocket_message.py
│       ├── conversation_dto.py
│       ├── message_dto.py
│       └── extracted_data_dto.py
├── infrastructure/        # Infrastructure layer
│   ├── cache/           # Caching implementations
│   │   ├── conversation_cache.py
│   │   └── redis_service.py
│   ├── database/         # Database implementations
│   │   ├── models.py
│   │   ├── config.py
│   │   └── repositories/
│   ├── external_services/ # External service integrations
│   ├── websockets/       # WebSocket handling
│   │   └── websocket_handler.py
│   └── services/         # Service implementations
│       ├── rag_service_impl.py
│       └── data_extraction_service_impl.py
├── presentation/          # Presentation layer
│   ├── api/              # API endpoints
│   │   └── conversation_routes.py
│   └── websockets/       # WebSocket endpoints
│       └── websocket_routes.py
└── shared/               # Shared utilities
    ├── config/           # Configuration
    ├── logging/          # Logging setup
    └── exceptions/       # Custom exceptions

scripts/                  # Utility scripts
├── setup_knowledge_base.py
└── test_chat.py
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- OpenAI API Key

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd vega
   make setup
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Start with Docker (Recommended)**
   ```bash
   make docker-up
   ```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://vega_user:vega_password@localhost:5432/vega_ai
REDIS_URL=redis://localhost:6379

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002

# Application Configuration
APP_NAME=Vega Customer Support System
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=vega-secret-key-change-in-production

# WebSocket Configuration
WS_MAX_CONNECTIONS=100
WS_HEARTBEAT_INTERVAL=30

# RAG Configuration
KNOWLEDGE_BASE_PATH=./knowledge_base
VECTOR_STORE_TYPE=chroma

# Redis Configuration
REDIS_MAX_CONNECTIONS=100
REDIS_RETRY_ON_TIMEOUT=true

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🌐 API Endpoints

### REST API

- `GET /` - Root endpoint with system information
- `GET /health` - Health check with WebSocket connection stats
- `GET /stats` - Connection and cache statistics
- `GET /cache/stats` - Detailed cache statistics
- `POST /cache/clear` - Clear Redis cache
- `GET /conversations` - List conversations with pagination
- `GET /conversations/{id}` - Get specific conversation
- `POST /conversations` - Create new conversation
- `POST /conversations/{id}/summary` - Generate conversation summary

### WebSocket Endpoints

- `ws://localhost:8000/ws/chat/{conversation_id}` - Chat with specific conversation
- `ws://localhost:8000/ws/chat` - General chat (creates new conversation automatically)
- `ws://localhost:8000/ws/test` - WebSocket test page

## 💬 WebSocket Usage

### Message Types

**Send a text message:**
```json
{
  "type": "text",
  "data": {
    "content": "Hello, I need help with my order ORD123456"
  },
  "conversation_id": "optional-conversation-id",
  "user_id": "optional-user-id"
}
```

**Send typing indicator:**
```json
{
  "type": "typing",
  "data": {
    "is_typing": true
  }
}
```

**Request conversation summary:**
```json
{
  "type": "summary_request",
  "conversation_id": "conversation-id"
}
```

**Heartbeat:**
```json
{
  "type": "heartbeat",
  "data": {
    "timestamp": 1234567890
  }
}
```

### Response Types

**Text response:**
```json
{
  "type": "text_response",
  "content": "I'd be happy to help you with order ORD123456...",
  "extracted_info": {
    "order_number": "ORD123456",
    "problem_category": "technical",
    "problem_description": "Application not working",
    "urgency_level": "high",
    "confidence_score": 0.85,
    "completion_percentage": 100.0
  }
}
```

**Summary response:**
```json
{
  "type": "summary_response",
  "summary": "Customer reported technical issues with order ORD123456...",
  "key_points": [
    "Order number: ORD123456",
    "Technical problem with application",
    "High urgency level",
    "Customer needs immediate assistance"
  ],
  "extracted_data": {
    "order_number": "ORD123456",
    "problem_category": "technical",
    "problem_description": "Application not working",
    "urgency_level": "high",
    "confidence_score": 0.85
  }
}
```

## 📊 Data Extraction

The system automatically extracts structured data from conversations:

### Extracted Fields

- **Order Number**: Patterns like ORD123456, #123456, order-123
- **Problem Category**: technical, billing, shipping, product, account, general
- **Problem Description**: Clear description of the issue
- **Urgency Level**: low, medium, high, critical
- **Confidence Score**: 0.0 to 1.0 based on extraction quality

### Validation

- Order numbers must be 3-20 characters, alphanumeric and hyphens only
- Problem categories must be valid enum values
- Urgency levels must be valid enum values
- Confidence scores are calculated based on field completeness

## 🧠 RAG Implementation

### Knowledge Base Integration

The system uses LangGraph for intelligent response generation:

1. **Document Retrieval**: Searches knowledge base for relevant information
2. **Context Building**: Combines retrieved docs with conversation history
3. **Response Generation**: Uses OpenAI to generate contextual responses
4. **Summary Generation**: Creates conversation summaries and key points

### Knowledge Base Setup

The system includes automated knowledge base setup with sample documents covering:
- Order processing information
- Technical support guidelines
- Billing and payment procedures
- Shipping information
- Product details
- Account management
- General support policies

Use `make setup-kb` to initialize the knowledge base with these documents.

### LangGraph Workflow

```python
def _build_graph(self) -> StateGraph:
    def retrieve_documents(state):
        # Retrieve relevant documents from knowledge base
        pass

    def generate_response(state):
        # Generate response using retrieved documents
        pass

    # Build the graph
    workflow = StateGraph(dict)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("generate", generate_response)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()
```

## 🗄️ Database Schema

### Tables

- **conversations**: Store conversation metadata
- **messages**: Store individual messages
- **extracted_data**: Store structured data extracted from conversations
- **customer_support_tickets**: Store support tickets created from conversations

### Migrations

```bash
# Create new migration
make migrate-create message="Add new table"

# Run migrations
make migrate

# Setup knowledge base
make setup-kb

# Check environment variables
make check-env

# Open API documentation
make docs

# Clean database files
make clean-db
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Services

- **app**: FastAPI application
- **postgres**: PostgreSQL database
- **redis**: Redis cache (for future use)

## 🛠️ Scripts

### Knowledge Base Setup

```bash
# Setup knowledge base with sample documents
make setup-kb

# Or run directly
poetry run python scripts/setup_knowledge_base.py
```

### Chat Testing

```bash
# Test WebSocket chat
poetry run python scripts/test_chat.py
```

## 🧪 Testing

### WebSocket Testing

```bash
# Interactive test
make test-client

# Or use the test page
open http://localhost:8000/ws/test
```

### API Testing

```bash
# Run tests
make test

# Check health
make status
```

## 📈 Monitoring

### Health Checks

- **Application**: `GET /health` - System status with WebSocket connections
- **Database**: Automatic connection health checks
- **WebSocket**: Connection count monitoring
- **Cache**: Redis connection and performance monitoring via `GET /cache/stats`

### Logs

```bash
# View application logs
make logs

# View Docker logs
make docker-logs
```

## 🔧 Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Pre-commit checks
make pre-commit

# Check environment setup
make check-env
```

### Database Management

```bash
# Create migration
make migrate-create message="Description"

# Run migrations
make migrate
```

## 🚀 Production Deployment

### Environment Variables

Ensure all required environment variables are set:

```env
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=your_key
SECRET_KEY=your_secret_key
DEBUG=false
```

### Security Considerations

- Set strong `SECRET_KEY`
- Configure proper CORS origins
- Use environment-specific database URLs
- Enable HTTPS in production
- Set appropriate rate limits

## 📚 Usage Examples

### Python Client

```python
import asyncio
import websockets
import json

async def chat_example():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "text",
            "data": {"content": "I need help with order ORD123456"}
        }))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"AI: {data['content']}")
        print(f"Extracted: {data['extracted_info']}")

asyncio.run(chat_example())
```

### JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('AI:', data.content);
    console.log('Extracted:', data.extracted_info);
};

// Send message
ws.send(JSON.stringify({
    type: "text",
    data: { content: "I need help with order ORD123456" }
}));
```

## 📄 License

This project is licensed under the MIT License.

---

**Vega Customer Support System** - Intelligent customer support with DDD, WebSockets, and RAG capabilities.
