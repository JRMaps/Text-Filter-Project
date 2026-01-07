from pydantic import BaseModel
from backend.app.message.message_schema import MessageStatus

# CFG moderation result
class CFGResult(BaseModel):
    severity_score: int
    moderation_status: MessageStatus