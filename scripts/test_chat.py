#!/usr/bin/env python3
import asyncio
from datetime import datetime
import json
import uuid

import websockets


class ChatTester:
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.user_id = f"test_user_{datetime.now().strftime('%H%M%S')}"
        self.websocket = None

    async def connect(self):
        uri = f"ws://localhost:8000/ws/chat/{self.conversation_id}"
        print(f"🔗 Connecting to: {uri}")
        print(f"👤 User ID: {self.user_id}")
        print(f"💬 Conversation ID: {self.conversation_id}")
        print("=" * 60)

        try:
            self.websocket = await websockets.connect(uri)
            print("✅ Successfully connected!")

            # Receive initial message
            initial = await self.websocket.recv()
            initial_data = json.loads(initial)
            print(f"📥 Initial message: {initial_data.get('content', 'No content')}")
            print()

        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
        else:
            return True

    async def send_message(self, content: str):
        """Send a message."""
        if not self.websocket:
            print("❌ No WebSocket connection")
            return

        message = {
            "type": "text",
            "data": {"content": content},
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
        }

        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {content}")

            # Receive response
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30)
            response_data = json.loads(response)

            print("📥 Response:")
            print(f"   Type: {response_data.get('type', 'N/A')}")
            print(f"   Content: {response_data.get('content', 'No content')}")

            # Show extracted information if exists
            extracted_info = response_data.get("extracted_info")
            if extracted_info:
                print("   📊 Extracted data:")
                for key, value in extracted_info.items():
                    if value:
                        print(f"      {key}: {value}")

            print()

        except TimeoutError:
            print("⏰ Timeout waiting for response")
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    async def interactive_chat(self):
        """Interactive chat."""
        print("🚀 Interactive Chat - Vega AI Support System")
        print("=" * 60)
        print("Special commands:")
        print("  /quit - Exit")
        print("  /help - Show help")
        print("=" * 60)

        if not await self.connect():
            return

        while True:
            try:
                user_input = input("💬 You: ").strip()

                if user_input.lower() == "/quit":
                    print("👋 Goodbye!")
                    break
                if user_input.lower() == "/help":
                    print("📋 Available commands:")
                    print("  /quit - Exit the chat")
                    print("  Any other text - Send message")
                    continue
                if not user_input:
                    continue

                await self.send_message(user_input)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def close(self):
        """Close connection."""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Connection closed")


async def main():
    """Main function."""
    tester = ChatTester()
    try:
        await tester.interactive_chat()
    finally:
        await tester.close()


if __name__ == "__main__":
    print("🚀 Starting WebSocket chat tester...")
    asyncio.run(main())
