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
    API to send a message to a conversation.
    """
    response = send_message(
        db=db,
        sender_id=current_user.id,
        conversation_id=request.conversation_id,
        receiver_id=request.receiver_id,
        content=request.content
    )
    return response
