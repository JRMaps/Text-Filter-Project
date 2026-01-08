from fastapi import APIRouter, Depends
from typing import List
from backend.app.conversation.conversation_service import get_all_conversations, get_conversation_by_id
from backend.app.conversation.conversation_schema import ConversationDashboardItem, ConversationWithMessages
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()


# Get conversations (load dashboard)
@router.get("/conversations", response_model=List[ConversationDashboardItem])
async def api_get_all_conversations(
    current_user: User = Depends(get_current_user)
):
    """
    API to get all conversations for the current user.
    Returns a list of conversation summaries with other user info and last message.
    """
    return get_all_conversations(current_user_id=current_user.id)

# Get conversation by ID with messages (when a user opens a conversation)
@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def api_get_conversation_by_id(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    API to get all messages in a conversation by conversation ID.
    """
    return get_conversation_by_id(conversation_id, current_user_id=current_user.id)
