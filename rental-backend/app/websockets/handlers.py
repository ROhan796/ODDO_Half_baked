# app/websockets/handlers.py
import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.config import settings
from app.core.websocket import manager
from app.schemas.websocket import WSMessage, WSPong

ws_router = APIRouter()


@ws_router.websocket("/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = None
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id: str = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "detail": "Invalid JSON"}
                )
                continue

            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            elif msg_type == "subscribe":
                room = data.get("room")
                if room:
                    async with manager._lock:
                        if room not in manager.rooms:
                            manager.rooms[room] = set()
                        manager.rooms[room].add(user_id)
                    await websocket.send_json(
                        {"type": "subscribed", "room": room}
                    )
                else:
                    await websocket.send_json(
                        {"type": "error", "detail": "Missing 'room' field"}
                    )
            else:
                await websocket.send_json(
                    {"type": "error", "detail": f"Unknown message type: {msg_type}"}
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
