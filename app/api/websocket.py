from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.manager import manager

router = APIRouter()

@router.websocket("/ws/{room_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str):
    await manager.connect(websocket, room_id, player_id)
    try:
        await manager.broadcast_to_room(room_id, {"event": "player_online", "player_id": player_id})
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(room_id, player_id)
        await manager.broadcast_to_room(room_id, {"event": "player_offline", "player_id": player_id})