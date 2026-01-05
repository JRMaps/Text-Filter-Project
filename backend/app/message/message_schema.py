from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageStatus(str, Enum):
    allowed = "allowed"
    masked = "masked"
    blocked = "blocked"
    flagged = "flagged"

class DeliveryStatus(str, Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    conversation_id: int
    receiver_id: Optional[int] = None  # Optional if conversation_id is provided

class MessageReceiptRead(BaseModel):
    user_id: int
    delivery_status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Websocket output
class MessageRead(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    status: MessageStatus
    created_at: datetime
    receipts: Optional[List[MessageReceiptRead]] = None

    class Config:
        from_attributes = True
