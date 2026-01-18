from fastapi import WebSocket
from backend.app.message.message_service import mark_message_delivered, mark_message_read
from backend.app.websocket.connection_manager import manager
from datetime import datetime


async def handle_mark_delivered(websocket: WebSocket, payload: dict, current_user_id: int):
    """Handle message:mark_delivered event."""
    message_id = payload.get("message_id")
    
    if not message_id:
        await manager.send_error(
            user_id=current_user_id,
            error_message="message_id is required",
            error_code="MISSING_MESSAGE_ID"
        )
        return
    
    try:
        result = mark_message_delivered(message_id, current_user_id)
        
        if result is None:
            # Already delivered, no broadcast needed
            return
        
        # Broadcast delivery status to all participants
        await manager.broadcast_receipt_status(
            participant_ids=result["participant_ids"],
            message_id=result["message_id"],
            user_id=result["user_id"],
            delivery_status=result["delivery_status"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        await manager.send_error(
            user_id=current_user_id,
            error_message=str(e),
            error_code="DELIVERY_UPDATE_FAILED"
        )


async def handle_mark_read(websocket: WebSocket, payload: dict, current_user_id: int):
    """Handle message:mark_read event."""
    message_id = payload.get("message_id")
    
    if not message_id:
        await manager.send_error(
            user_id=current_user_id,
            error_message="message_id is required",
            error_code="MISSING_MESSAGE_ID"
        )
        return
    
    try:
        result = mark_message_read(message_id, current_user_id)
        
        if result is None:
            # Already read, no broadcast needed
            return
        
        # Broadcast read status to all participants
        await manager.broadcast_receipt_status(
            participant_ids=result["participant_ids"],
            message_id=result["message_id"],
            user_id=result["user_id"],
            delivery_status=result["delivery_status"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        await manager.send_error(
            user_id=current_user_id,
            error_message=str(e),
            error_code="READ_UPDATE_FAILED"
        )

async def handle_ping(websocket: WebSocket):
    """Handle user:ping event by responding with a pong."""
    await websocket.send_json({
        "type": "user:pong",
        "payload": {
            "timestamp": datetime.utcnow().isoformat()
        }
    })