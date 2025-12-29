from pydantic import BaseModel
from backend.app.message.message_schema import MessageRead

# Incoming WebSocket Messages
class WSMessageIn(BaseModel):
    receiver_id: int
    content: str

# Outgoing WebSocket Messages
class WSMessageOut(BaseModel):
    message: MessageRead