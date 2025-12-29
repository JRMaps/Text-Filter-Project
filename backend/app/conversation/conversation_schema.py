from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.app.message.message_schema import MessageRead
from backend.app.user.user_schema import UserRead  # Corrected import

class ConversationBase(BaseModel):
    participants: List[int]

# Conversation Read (used when loading dashboard)
class ConversationRead(ConversationBase):
    id: int
    last_message_id: Optional[int]
    updated_at: datetime  # Fixed incorrect usage of datetime.datetime

    class Config:
        from_attributes = True

# This is used when user opens a chat.
class ConversationWithMessages(ConversationRead):
    messages: List[MessageRead]


# Dashboard response schema (includes extra fields for UI)
class ConversationDashboardItem(BaseModel):
    id: int
    participants: List[int]
    last_message_id: Optional[int]
    updated_at: Optional[datetime]  # Fixed incorrect usage of datetime.datetime
    other_user: UserRead
    last_message: Optional[str]
