from fastapi import APIRouter, HTTPException
from backend.app.api.controllers.message_controller import get_all_conversations, get_conversation_by_id, send_message
from pydantic import BaseModel, Field

router = APIRouter()

class MessageRequest(BaseModel):
    conversation_id: int = Field(..., gt=0, description="ID of the conversation (must be a positive integer)")
    content: str

# To add on every route: authentication dependency to get current user ID
@router.get("/conversations")
def api_get_all_conversations():
    """API to get all conversations for the current user."""
    return get_all_conversations(current_user_id=1)  # Replace with actual user ID

@router.get("/conversations/{conversation_id}")
def api_get_conversation_by_id(conversation_id: int):
    """API to get all messages in a conversation by conversation ID."""
    return get_conversation_by_id(conversation_id, current_user_id=1)  # Replace with actual user ID

@router.post("/messages")
def api_send_message(request: MessageRequest):
    """API to send a message in a specific conversation."""
    return send_message(request.conversation_id, sender_id=1, content=request.content)  # Replace with actual user ID

# Example commands for calling the APIs:
# 1. Get all conversations:
#    curl -X GET http://127.0.0.1:8000/conversations
#
# 2. Get messages with a specific user (e.g., user_id=2):
#    curl -X GET http://127.0.0.1:8000/conversations/2
#
# 3. Send a message to a specific user:
#    curl -X POST http://127.0.0.1:8000/messages -H "Content-Type: application/json" -d '{"receiver_id": 2, "content": "Hey Bob, are you free?"}'
