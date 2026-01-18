from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from typing import List, Optional
from backend.app.conversation.conversation_service import get_all_conversations, get_conversation_by_id, create_group_chat
from backend.app.conversation.conversation_schema import (
    ConversationDashboardResponse,
    ConversationWithMessages,
    GroupConversationCreateResponse,
    GroupConversationCreateRequest
)
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationDashboardResponse])
async def api_get_all_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API to get all conversations for the current user.
    Returns a list of conversation summaries with other user info and last message.

    Note: This does NOT load messages, it only builds the chat list.
    """
    return get_all_conversations(current_user_id=current_user.id, db=db)


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def api_get_conversation_by_id(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API to get all messages in a conversation by conversation ID.
    """
    return get_conversation_by_id(conversation_id, current_user_id=current_user.id, db=db)


@router.post("/conversations/group-chats", response_model=GroupConversationCreateResponse)
async def api_create_group_chat(
    request: GroupConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API to create a new group chat conversation.
    """
    return create_group_chat(
        db=db,
        creator_id=current_user.id,
        participant_ids=request.participant_ids,
        group_name=request.group_name
    )

