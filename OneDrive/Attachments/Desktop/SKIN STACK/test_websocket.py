"""Test WebSocket functionality"""
import asyncio
import json
import websockets
import aiohttp
from datetime import datetime


async def test_websocket_connection():
    """Test basic WebSocket connection and messaging"""
    uri = "ws://localhost:8000/ws?client_id=test_client"

    print("[TEST] Connecting to WebSocket...")

    async with websockets.connect(uri) as websocket:
        # Wait for connection message
        message = await websocket.recv()
        data = json.loads(message)
        print(f"[OK] Connected: {data}")

        # Send a ping
        print("[TEST] Sending ping...")
        await websocket.send(json.dumps({
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }))

        # Wait for pong
        message = await websocket.recv()
        data = json.loads(message)
        print(f"[OK] Received pong: {data['type']}")

        # Subscribe to events
        print("[TEST] Subscribing to events...")
        await websocket.send(json.dumps({
            "type": "subscribe",
            "events": ["click", "conversion", "webhook"]
        }))

        # Wait for subscription confirmation
        message = await websocket.recv()
        data = json.loads(message)
        print(f"[OK] Subscription confirmed: {data}")

        # Request stats
        print("[TEST] Requesting stats...")
        await websocket.send(json.dumps({
            "type": "get_stats"
        }))

        # Wait for stats
        message = await websocket.recv()
        data = json.loads(message)
        print(f"[OK] Stats received: {data['type']}")

        print("[SUCCESS] WebSocket basic tests passed!")
        return True


async def test_click_broadcast():
    """Test click event broadcasting"""
    print("\n[TEST] Testing click broadcast...")

    # Connect WebSocket client
    uri = "ws://localhost:8000/ws?client_id=test_broadcast"
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()

        # Make a redirect request to trigger click
        print("[TEST] Triggering click via redirect...")
        async with aiohttp.ClientSession() as session:
            # First create a test link
            async with session.post(
                "http://localhost:8000/links/generate",
                json={
                    "destination_url": "https://example.com",
                    "influencer_id": "test_influencer",
                    "program_id": "test_program"
                }
            ) as response:
                if response.status == 200:
                    link_data = await response.json()
                    slug = link_data.get("slug", "test123")
                else:
                    slug = "test123"

            # Now trigger the redirect
            async with session.get(f"http://localhost:8000/l/{slug}") as response:
                print(f"[OK] Redirect triggered: {response.status}")

        # Wait for click broadcast
        print("[TEST] Waiting for click broadcast...")
        timeout = 5
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            data = json.loads(message)
            if data.get("type") == "click":
                print(f"[OK] Click broadcast received: {data}")
                return True
            else:
                print(f"[INFO] Received other message: {data['type']}")
        except asyncio.TimeoutError:
            print(f"[WARN] No click broadcast received within {timeout} seconds")
            return False


async def test_dashboard_endpoints():
    """Test dashboard API endpoints"""
    print("\n[TEST] Testing dashboard endpoints...")

    endpoints = [
        "/api/dashboard/overview",
        "/api/dashboard/time-series?metric=clicks&days=7",
        "/api/dashboard/top-performers?limit=5",
        "/api/dashboard/recent-activity?limit=10",
        "/api/dashboard/device-stats?period_days=30",
        "/api/dashboard/commission-summary"
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"http://localhost:8000{endpoint}"
            print(f"[TEST] Testing {endpoint}...")

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"[OK] {endpoint} returned data")
                    else:
                        print(f"[FAIL] {endpoint} returned {response.status}")
            except Exception as e:
                print(f"[ERROR] {endpoint}: {e}")

    print("[SUCCESS] Dashboard endpoints tested!")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("WebSocket and Dashboard Test Suite")
    print("=" * 50)

    try:
        # Test basic WebSocket functionality
        await test_websocket_connection()

        # Test click broadcasting
        await test_click_broadcast()

        # Test dashboard endpoints
        await test_dashboard_endpoints()

        print("\n" + "=" * 50)
        print("[ALL TESTS COMPLETED]")
        print("=" * 50)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nMake sure the API server is running:")
        print("  cd C:\\Users\\jgewi\\OneDrive\\Attachments\\Desktop\\SKIN STACK")
        print("  python -m uvicorn api.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())