from pydantic import BaseModel, model_validator
from typing import List, Optional
from datetime import datetime
from backend.app.message.message_schema import MessageRead
from backend.app.user.user_schema import UserRead 
from enum import Enum

class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class ConversationBase(BaseModel):
    """
    INPUT schema used when:
    - Creating a new conversation
    - Sending a message that may create a new conversation

    Uses user IDs only (no user objects).
    """
    participants: List[int]
    group_name: Optional[str] = None
    type: ConversationType = ConversationType.PRIVATE

    @model_validator(mode="after")
    def validate_conversation(self):
        if len(self.participants) < 2:
            raise ValueError("Conversation must have at least 2 participants")

        if self.group_name and len(self.participants) < 3:
            raise ValueError(
                "Group name can only be set for conversations with at least 3 participants"
            )

        return self


class ConversationParticipantRead(BaseModel):
    """
    Minimal user representation used inside conversations.

    Purpose:
    - Display participant names in chat headers
    - Display members in group conversations
    - Avoid exposing sensitive user data
    """
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class ConversationRead(BaseModel):
    """
    OUTPUT schema for loading a conversation's metadata.

    Used when:
    - Opening a chat
    - Fetching conversation info (without messages)
    """
    id: int

    # Users are returned as objects (not IDs)
    participants: List[ConversationParticipantRead]

    group_name: Optional[str]
    last_message_id: Optional[int]
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationWithMessages(ConversationRead):
    """
    Used when:
    - Opening a conversation thread
    - Loading messages for a chat
    """
    messages: List[MessageRead]


class ConversationDashboardItem(BaseModel):
    """
    OUTPUT schema for the chat list / inbox dashboard.

    Used when:
    - Listing all conversations
    - Showing last message preview
    """
    id: int
    type: ConversationType
    updated_at: datetime
    last_message: Optional[str]

    model_config = {
        "from_attributes": True
    }


class PrivateConversationDashboardItem(ConversationDashboardItem):
    other_user: UserRead

class GroupConversationDashboardItem(ConversationDashboardItem):
    group_name: str
    member_count: int
    participants: List[ConversationParticipantRead]
