from enum import Enum
from pydantic import BaseModel
from datetime import datetime

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
    receiver_id: int

# Websocket output
class MessageRead(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    status: MessageStatus
    delivery_status: DeliveryStatus
    created_at: datetime

    class Config:
        from_attributes = True
