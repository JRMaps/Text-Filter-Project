from pydantic import BaseModel, model_validator, ValidationError
from typing import List, Optional
from datetime import datetime
from backend.app.message.message_schema import MessageRead
from backend.app.user.user_schema import UserRead 
from enum import Enum

class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"

class ConversationBase(BaseModel):
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

class ConversationRead(BaseModel):
    id: int
    participants: List[int]
    group_name: Optional[str]
    last_message_id: Optional[int]
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ConversationWithMessages(ConversationRead):
    messages: List[MessageRead]

class ConversationDashboardItem(BaseModel):
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
