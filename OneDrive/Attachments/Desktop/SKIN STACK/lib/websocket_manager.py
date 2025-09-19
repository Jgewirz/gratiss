"""
WebSocket Manager for real-time updates
Handles connection management and event broadcasting
"""

from typing import List, Dict, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Store active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        # Event history for new connections
        self.event_history: List[Dict] = []
        self.max_history_size = 100

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now().isoformat(),
            "ip": websocket.client.host if websocket.client else "unknown"
        }

        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }, client_id)

        # Send recent event history
        if self.event_history:
            await self.send_personal_message({
                "type": "history",
                "events": self.event_history[-20:]  # Last 20 events
            }, client_id)

        # Broadcast connection event to all other clients
        await self.broadcast({
            "type": "client_connected",
            "client_id": client_id,
            "total_connections": len(self.active_connections)
        }, exclude_client=client_id)

        logger.info(f"WebSocket connected: {client_id} from {websocket.client.host if websocket.client else 'unknown'}")

    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_metadata[client_id]

            # Broadcast disconnection to remaining clients
            asyncio.create_task(self.broadcast({
                "type": "client_disconnected",
                "client_id": client_id,
                "total_connections": len(self.active_connections)
            }))

            logger.info(f"WebSocket disconnected: {client_id}")

    async def send_personal_message(self, message: Dict[Any, Any], client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: Dict[Any, Any], exclude_client: str = None):
        """Broadcast message to all connected clients"""
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Add to history
        self._add_to_history(message)

        # Send to all connected clients
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            if exclude_client and client_id == exclude_client:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def _add_to_history(self, event: Dict):
        """Add event to history for new connections"""
        self.event_history.append(event)
        # Keep history size limited
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]

    async def broadcast_click(self, tracking_link_id: int, slug: str, ip_hash: str, device_type: str = None):
        """Broadcast click event"""
        await self.broadcast({
            "type": "click",
            "data": {
                "tracking_link_id": tracking_link_id,
                "slug": slug,
                "ip_hash": ip_hash[:8] + "...",  # Partial hash for privacy
                "device_type": device_type or "unknown"
            }
        })

    async def broadcast_conversion(self, order_id: str, amount: float, commission: float, influencer_id: int):
        """Broadcast conversion event"""
        await self.broadcast({
            "type": "conversion",
            "data": {
                "order_id": order_id,
                "amount": amount,
                "commission": commission,
                "influencer_id": influencer_id,
                "platform_fee": commission * 0.20
            }
        })

    async def broadcast_webhook(self, source: str, event_type: str, status: str, event_id: str = None):
        """Broadcast webhook processing event"""
        await self.broadcast({
            "type": "webhook",
            "data": {
                "source": source,
                "event_type": event_type,
                "status": status,
                "event_id": event_id
            }
        })

    async def broadcast_system_metric(self, metric_type: str, value: Any):
        """Broadcast system metric update"""
        await self.broadcast({
            "type": "metric",
            "data": {
                "metric_type": metric_type,
                "value": value
            }
        })

    async def broadcast_error(self, error_type: str, message: str, severity: str = "warning"):
        """Broadcast error or warning"""
        await self.broadcast({
            "type": "error",
            "data": {
                "error_type": error_type,
                "message": message,
                "severity": severity  # info, warning, error, critical
            }
        })

    def get_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "clients": list(self.active_connections.keys()),
            "metadata": self.connection_metadata,
            "history_size": len(self.event_history)
        }


# Global WebSocket manager instance
manager = ConnectionManager()