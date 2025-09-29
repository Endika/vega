#!/usr/bin/env python3
import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import app

if __name__ == "__main__":
    # Load environment variables
    
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting Vega Customer Support System on {host}:{port}")
    print("WebSocket endpoint: ws://localhost:8000/ws/chat/{conversation_id}")
    print("API documentation: http://localhost:8000/docs")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
