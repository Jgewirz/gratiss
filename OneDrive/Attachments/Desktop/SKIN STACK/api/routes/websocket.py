"""
WebSocket endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import uuid
import asyncio
import logging

from lib.websocket_manager import manager
from lib.db import db

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time updates.

    Client can optionally provide a client_id, otherwise one will be generated.

    Message Types:
    - connection: Initial connection confirmation
    - history: Recent event history
    - click: Real-time click events
    - conversion: Real-time conversion events
    - webhook: Webhook processing events
    - metric: System metric updates
    - error: Error/warning notifications
    """

    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())[:8]

    # Connect the client
    await manager.connect(websocket, client_id)

    try:
        # Start sending periodic heartbeat to keep connection alive
        async def send_heartbeat():
            while True:
                try:
                    await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                    await manager.send_personal_message({
                        "type": "heartbeat",
                        "timestamp": asyncio.get_event_loop().time()
                    }, client_id)
                except:
                    break

        # Start heartbeat task
        heartbeat_task = asyncio.create_task(send_heartbeat())

        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            # Handle different message types from client
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, client_id)

            elif message_type == "subscribe":
                # Client wants to subscribe to specific events
                events = data.get("events", [])
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "events": events
                }, client_id)

            elif message_type == "get_stats":
                # Client requests current statistics
                stats = await get_current_stats()
                await manager.send_personal_message({
                    "type": "stats",
                    "data": stats
                }, client_id)

            else:
                # Echo unknown messages back
                await manager.send_personal_message({
                    "type": "echo",
                    "original": data
                }, client_id)

    except WebSocketDisconnect:
        # Clean disconnect
        manager.disconnect(client_id)
        heartbeat_task.cancel()
        logger.info(f"WebSocket client {client_id} disconnected")

    except Exception as e:
        # Unexpected error
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
        if 'heartbeat_task' in locals():
            heartbeat_task.cancel()


@router.websocket("/ws/admin")
async def admin_websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Admin WebSocket endpoint with additional capabilities.
    Requires authentication token (to be implemented).
    """

    # TODO: Verify admin token
    # if not verify_admin_token(token):
    #     await websocket.close(code=1008, reason="Unauthorized")
    #     return

    client_id = f"admin_{str(uuid.uuid4())[:8]}"
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")

            if command == "get_connections":
                # Get all active connections
                stats = manager.get_stats()
                await manager.send_personal_message({
                    "type": "connections",
                    "data": stats
                }, client_id)

            elif command == "broadcast":
                # Admin can broadcast custom messages
                message = data.get("message")
                if message:
                    await manager.broadcast(message)
                    await manager.send_personal_message({
                        "type": "broadcast_sent",
                        "success": True
                    }, client_id)

            elif command == "kick_client":
                # Disconnect a specific client
                target_client = data.get("client_id")
                if target_client in manager.active_connections:
                    manager.disconnect(target_client)
                    await manager.send_personal_message({
                        "type": "client_kicked",
                        "client_id": target_client
                    }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Admin WebSocket error: {e}")
        manager.disconnect(client_id)


async def get_current_stats() -> dict:
    """Get current system statistics"""

    async with db.pool.acquire() as conn:
        # Get today's stats
        today_stats = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT c.id) as clicks_today,
                COUNT(DISTINCT conv.id) as conversions_today,
                COALESCE(SUM(conv.order_amount), 0) as revenue_today
            FROM clicks c
            LEFT JOIN conversions conv ON conv.tracking_link_id = c.tracking_link_id
            WHERE DATE(c.clicked_at) = CURRENT_DATE
        """)

        # Get active influencers (based on recent clicks)
        active_influencers = await conn.fetchval("""
            SELECT COUNT(DISTINCT tl.influencer_id)
            FROM tracking_links tl
            JOIN clicks c ON c.tracking_link_id = tl.id
            WHERE c.clicked_at >= CURRENT_DATE - INTERVAL '30 days'
        """)

        return {
            "clicks_today": today_stats["clicks_today"],
            "conversions_today": today_stats["conversions_today"],
            "revenue_today": float(today_stats["revenue_today"]),
            "active_influencers": active_influencers,
            "websocket_connections": len(manager.active_connections)
        }