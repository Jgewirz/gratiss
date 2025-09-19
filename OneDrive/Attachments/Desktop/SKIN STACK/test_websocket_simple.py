"""Simple WebSocket connectivity test"""
import asyncio
import json
import websockets


async def test_basic_connection():
    """Test basic WebSocket connection"""
    uri = "ws://localhost:8000/ws"

    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected!")

            # Wait for connection message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"[OK] Received: {data['type']}")

            # Send a ping
            await websocket.send(json.dumps({
                "type": "ping",
                "timestamp": 123456
            }))
            print("[OK] Sent ping")

            # Wait for pong
            message = await websocket.recv()
            data = json.loads(message)
            print(f"[OK] Received: {data['type']}")

            print("\n[SUCCESS] WebSocket is working!")

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    asyncio.run(test_basic_connection())