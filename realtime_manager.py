"""
Real-time WebSocket manager for multi-user collaboration.
Allows multiple users to see board updates in real-time.
"""

import asyncio
import json
from typing import Set
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connected_users: dict = {}  # {websocket: user_info}
    
    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """Register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connected_users[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.now().isoformat()
        }
        print(f"✓ User {user_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        self.active_connections.discard(websocket)
        if websocket in self.connected_users:
            user_info = self.connected_users.pop(websocket)
            print(f"✗ User {user_info['user_id']} disconnected")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        message["timestamp"] = datetime.now().isoformat()
        message_json = json.dumps(message)
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                disconnected.append(connection)
                print(f"✗ Broadcast failed: {e}")
        
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_board_update(self, item_id: str, action: str, data: dict):
        """Broadcast board/item updates to all clients."""
        update = {
            "type": "board_update",
            "action": action,  # 'add', 'update', 'delete', 'move'
            "item_id": item_id,
            "data": data,
            "active_users": len(self.active_connections)
        }
        await self.broadcast(update)
    
    async def broadcast_agent_progress(self, item_id: str, status: str, progress: float):
        """Broadcast agent processing progress."""
        update = {
            "type": "agent_progress",
            "item_id": item_id,
            "status": status,  # 'classifying', 'interpreting', 'planning', 'complete'
            "progress": progress  # 0.0 to 1.0
        }
        await self.broadcast(update)
    
    def get_connected_count(self) -> int:
        """Get number of connected users."""
        return len(self.active_connections)
    
    def get_user_list(self) -> list:
        """Get list of connected users."""
        return [info["user_id"] for info in self.connected_users.values()]


# Global connection manager
connection_manager = ConnectionManager()
