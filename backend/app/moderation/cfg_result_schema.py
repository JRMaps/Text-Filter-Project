from pydantic import BaseModel
from typing import List
from backend.app.message.message_schema import MessageStatus

# CFG moderation result
class CFGResult(BaseModel):
    normalized_text: str
    matched_rules: List[str]
    severity_score: int
    status: MessageStatus