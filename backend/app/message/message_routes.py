from fastapi import APIRouter, Depends
from backend.app.message.message_controller import send_message
from backend.app.message.message_schema import MessageCreate, MessageRead
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/messages", response_model=MessageRead)
async def api_send_message(
    request: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    API to send a message to another user.
    Creates a conversation if it doesn't exist.
    """
    response = send_message(
        sender_id=current_user.id,
        receiver_id=request.receiver_id,
        content=request.content
    )
    return response
