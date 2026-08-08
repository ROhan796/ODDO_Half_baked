# app/core/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self, websocket: WebSocket, user_id: str, rooms: List[str] = None
    ):
        """Accept WebSocket connection and register user."""
        await websocket.accept()

        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)

            if rooms:
                for room in rooms:
                    if room not in self.rooms:
                        self.rooms[room] = set()
                    self.rooms[room].add(user_id)

    async def disconnect(
        self, websocket: WebSocket, user_id: str, rooms: List[str] = None
    ):
        """Remove WebSocket connection."""
        async with self._lock:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]

            if rooms:
                for room in rooms:
                    if room in self.rooms:
                        self.rooms[room].discard(user_id)
                        if not self.rooms[room]:
                            del self.rooms[room]

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def broadcast_to_room(
        self, message: dict, room: str, exclude_user: str = None
    ):
        """Broadcast message to all users in a room."""
        if room in self.rooms:
            for user_id in self.rooms[room]:
                if user_id != exclude_user:
                    await self.send_personal_message(message, user_id)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users."""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()
