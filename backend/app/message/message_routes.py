from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.message.message_service import send_message
from backend.app.message.message_schema import MessageCreate, MessageRead
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/send_message", response_model=MessageRead)
async def api_send_message(
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to a conversation (private or group). Creates a conversation if it doesn't exist.
    Note: It will be broadcasted via WebSocket after creation.

    Args:
        sender_id: ID of the user sending the message
        content: Message content
        conversation_id: ID of the conversation (optional)
        receiver_id: ID of the receiver (optional)

        Note: Either conversation_id or receiver_id must be provided, but not both.
        Different purpose: conversation_id is for existing conversations, receiver_id is for starting new private chats.

    Returns:
        MessageRead: The created message
    """
    response = send_message(
        db=db,
        sender_id=current_user.id,
        conversation_id=request.conversation_id,
        receiver_id=request.receiver_id,
        content=request.content
    )
    return response
