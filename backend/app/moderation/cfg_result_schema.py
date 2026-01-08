from pydantic import BaseModel
from backend.app.message.message_model import ModerationStatus

# CFG moderation result
class CFGResult(BaseModel):
    severity_score: int
    moderation_status: ModerationStatus