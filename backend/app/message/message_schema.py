from backend.app.message.message_model import ModerationStatus
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DeliveryStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None  
    receiver_id: Optional[int] = None

    def validate(self):
        if not self.conversation_id and not self.receiver_id:
            raise ValueError("Either conversation_id or receiver_id must be provided.")
        
        if self.conversation_id and self.receiver_id:
            raise ValueError("Only one of conversation_id or receiver_id should be provided.")


class MessageReceiptRead(BaseModel):
    user_id: int
    delivery_status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageRead(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    moderation_status: ModerationStatus
    created_at: datetime
    receipts: Optional[List[MessageReceiptRead]] = None
    masked_words: Optional[List[str]] = None

    class Config:
        from_attributes = True
