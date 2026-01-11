"""
WebSocket support for real-time execution updates.

Provides real-time step-by-step execution progress via WebSocket connections.
Clients connect to /v1/executions/{execution_id}/ws to receive updates.

Usage Example (from workflow executor):
    from .websocket import manager

    # Send step update during execution
    await manager.send_step_update(
        execution_id=str(execution.id),
        node_id="node_123",
        status="running",
        started_at=datetime.now(timezone.utc).isoformat()
    )

    # Send completion
    await manager.send_step_update(
        execution_id=str(execution.id),
        node_id="node_123",
        status="completed",
        output_data={"result": "success"},
        token_usage={"input": 10, "output": 20, "total": 30},
        completed_at=datetime.now(timezone.utc).isoformat()
    )

    # Send execution status
    await manager.send_execution_status(
        execution_id=str(execution.id),
        status="completed"
    )
"""
from fastapi import WebSocket, WebSocketDisconnect, status
from typing import Dict, List, Any
from uuid import UUID
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for execution updates.

    Supports multiple clients connected to the same execution,
    handles connection lifecycle, and broadcasts updates.
    """

    def __init__(self):
        # Maps execution_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, execution_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        async with self._lock:
            if execution_id not in self.active_connections:
                self.active_connections[execution_id] = []
            self.active_connections[execution_id].append(websocket)

        logger.info(f"WebSocket connected for execution {execution_id}. "
                   f"Total connections: {len(self.active_connections[execution_id])}")

    async def disconnect(self, websocket: WebSocket, execution_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if execution_id in self.active_connections:
                if websocket in self.active_connections[execution_id]:
                    self.active_connections[execution_id].remove(websocket)

                # Clean up empty connection lists
                if not self.active_connections[execution_id]:
                    del self.active_connections[execution_id]

        logger.info(f"WebSocket disconnected from execution {execution_id}")

    async def broadcast_to_execution(self, execution_id: str, message: Dict[str, Any]):
        """
        Send a message to all clients connected to a specific execution.

        Args:
            execution_id: The execution ID
            message: Dictionary to send as JSON
        """
        if execution_id not in self.active_connections:
            logger.debug(f"No active connections for execution {execution_id}")
            return

        # Create a copy of the connection list to avoid modification during iteration
        connections = self.active_connections[execution_id].copy()
        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    if execution_id in self.active_connections:
                        if ws in self.active_connections[execution_id]:
                            self.active_connections[execution_id].remove(ws)

                # Clean up empty lists
                if execution_id in self.active_connections and not self.active_connections[execution_id]:
                    del self.active_connections[execution_id]

    async def send_step_update(
        self,
        execution_id: str,
        node_id: str,
        status: str,
        input_data: Any = None,
        output_data: Any = None,
        error_message: str = None,
        token_usage: Dict[str, int] = None,
        started_at: str = None,
        completed_at: str = None,
    ):
        """
        Send a step update message to all connected clients.

        Args:
            execution_id: The execution ID
            node_id: The node/step ID
            status: Step status (pending, running, completed, failed)
            input_data: Step input data
            output_data: Step output data
            error_message: Error message if failed
            token_usage: Token usage stats {input, output, total}
            started_at: ISO timestamp when step started
            completed_at: ISO timestamp when step completed
        """
        message = {
            "type": "step_update",
            "execution_id": execution_id,
            "step": {
                "node_id": node_id,
                "status": status,
                "input_data": input_data,
                "output_data": output_data,
                "error_message": error_message,
                "token_usage": token_usage,
                "started_at": started_at,
                "completed_at": completed_at,
            }
        }

        await self.broadcast_to_execution(execution_id, message)

    async def send_execution_status(
        self,
        execution_id: str,
        status: str,
        error_message: str = None,
    ):
        """
        Send overall execution status update.

        Args:
            execution_id: The execution ID
            status: Execution status (running, completed, failed, cancelled)
            error_message: Error message if failed
        """
        message = {
            "type": "execution_status",
            "execution_id": execution_id,
            "status": status,
            "error_message": error_message,
        }

        await self.broadcast_to_execution(execution_id, message)

    def get_connection_count(self, execution_id: str) -> int:
        """Get the number of active connections for an execution."""
        return len(self.active_connections.get(execution_id, []))


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, execution_id: UUID):
    """
    WebSocket endpoint for real-time execution updates.

    Clients connect to this endpoint to receive step-by-step updates
    as the workflow executes. The connection remains open until the
    execution completes or the client disconnects.

    Message types sent to clients:
    - step_update: Individual step progress
    - execution_status: Overall execution status changes
    - heartbeat: Keepalive ping

    Args:
        websocket: FastAPI WebSocket connection
        execution_id: UUID of the execution to monitor
    """
    execution_id_str = str(execution_id)

    try:
        await manager.connect(websocket, execution_id_str)

        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "execution_id": execution_id_str,
            "message": "Connected to execution updates"
        })

        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for messages from client (e.g., ping, disconnect request)
                # Use a timeout to periodically check connection health
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )

                # Handle client messages (currently just echo for heartbeat)
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from client: {data}")

            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except:
                    # Connection likely closed
                    break

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from execution {execution_id_str}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id_str}: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
    finally:
        await manager.disconnect(websocket, execution_id_str)
