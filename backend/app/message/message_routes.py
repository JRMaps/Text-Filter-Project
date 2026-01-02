from fastapi import APIRouter, Depends
from backend.app.message.message_service import send_message
from backend.app.message.message_schema import MessageCreate, MessageRead
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user
from backend.app.websocket.connection_manager import manager
from datetime import datetime

router = APIRouter()


@router.post("/send_message", response_model=MessageRead)
async def api_send_message(
    request: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    API to send a message to another user.
    Creates a conversation if it doesn't exist.
    Triggers WebSocket events for real-time updates.
    """
    response = send_message(
        sender_id=current_user.id,
        receiver_id=request.receiver_id,
        content=request.content
    )
    
    # Broadcast WebSocket events for real-time updates
    participant_ids = [current_user.id, request.receiver_id]
    
    # Broadcast new message event
    await manager.send_to_conversation(
        participant_ids=participant_ids,
        payload={
            "type": "message:new",
            "payload": {
                "id": response.id,
                "conversation_id": response.conversation_id,
                "sender_id": response.sender_id,
                "receiver_id": response.receiver_id,
                "content": response.content,
                "status": response.status.value,
                "delivery_status": response.delivery_status.value,
                "created_at": response.created_at.isoformat()
            }
        }
    )
    
    # Broadcast dashboard update
    await manager.send_to_conversation(
        participant_ids=participant_ids,
        payload={
            "type": "conversation:dashboard_update",
            "payload": {
                "conversation_id": response.conversation_id,
                "last_message_id": response.id,
                "updated_at": response.created_at.isoformat()
            }
        }
    )
    
    return response
