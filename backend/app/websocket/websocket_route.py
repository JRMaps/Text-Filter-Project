from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.websocket.connection_manager import manager
from backend.app.websocket.ws_auth import get_user_from_websocket
from backend.app.websocket.ws_helpers import get_user_contact_ids
from backend.app.websocket.ws_events import (
    handle_mark_delivered,
    handle_mark_read,
    handle_ping
)

router = APIRouter()

@router.websocket("/ws")
async def ws_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat features.
    
    This endpoint handles:
    - Connection management (online/offline status)
    - Read receipts (delivered/read status updates)
    - Keep-alive pings
    
    Message sending and conversation updates is done via HTTP POST, then broadcast here.
    """
    try:
        current_user = await get_user_from_websocket(websocket)
    except Exception:
        return 
    
    # Connect user and check if status changed
    status_changed = await manager.connect(current_user.id, websocket)
    
    # Get user's contacts for broadcasting status
    contact_ids = get_user_contact_ids(current_user.id)
    
    # Broadcast online status to contacts if user just came online
    if status_changed:
        await manager.broadcast_online_status(
            user_id=current_user.id,
            is_online=True,
            contact_ids=list(contact_ids)
        )

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("type")
            payload = data.get("payload", {})

            # Route events to appropriate handlers
            if event == "message:mark_delivered":
                await handle_mark_delivered(websocket, payload, current_user.id)
            
            elif event == "message:mark_read":
                await handle_mark_read(websocket, payload, current_user.id)
            
            elif event == "user:ping":
                await handle_ping(websocket)
            
            else:
                await manager.send_error(
                    user_id=current_user.id,
                    error_message=f"Unknown event type: {event}",
                    error_code="UNKNOWN_EVENT"
                )
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Disconnect user and broadcast offline status
        status_changed = manager.disconnect(current_user.id, websocket)
        if status_changed:
            await manager.broadcast_online_status(
                user_id=current_user.id,
                is_online=False,
                contact_ids=list(contact_ids)
            )