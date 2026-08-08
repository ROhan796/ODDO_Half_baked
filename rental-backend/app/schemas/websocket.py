# app/schemas/websocket.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class WSMessage(BaseModel):
    type: str
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None


class WSConnect(BaseModel):
    type: str = "connect"
    token: str


class WSSubscribe(BaseModel):
    type: str = "subscribe"
    room: str


class WSPing(BaseModel):
    type: str = "ping"


class WSPong(BaseModel):
    type: str = "pong"
    timestamp: datetime
