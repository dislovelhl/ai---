from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time collaboration.
    Brokers Yjs binary update messages between clients in the same room.
    """
    def __init__(self):
        # Room ID -> List of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        logger.info(f"Client connected to room: {room_id}. Total clients: {len(self.active_connections[room_id])}")

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
            logger.info(f"Client disconnected from room: {room_id}")

    async def broadcast(self, room_id: str, message: bytes, sender: WebSocket):
        """
        Broadcasts a binary message to all other clients in the room.
        """
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    try:
                        await connection.send_bytes(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client in room {room_id}: {e}")

manager = ConnectionManager()

@router.websocket("/collaboration/{room_id}")
async def collaboration_websocket(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            # Yjs updates are binary
            data = await websocket.receive_bytes()
            await manager.broadcast(room_id, data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error in room {room_id}: {e}")
        manager.disconnect(room_id, websocket)
