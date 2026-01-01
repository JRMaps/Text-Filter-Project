from typing import List, Set
from backend.app.database.database import SessionLocal
from backend.app.conversation.conversation_model import Conversation, conversation_participants

def get_user_contact_ids(user_id: int) -> Set[int]:
    """
    Get all user IDs that the given user has conversations with.
    This is used to broadcast online/offline status to relevant users.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Set of user IDs that have conversations with this user
    """
    db = SessionLocal()
    try:
        # Get all conversations where user is a participant
        conversations = db.query(Conversation).join(
            conversation_participants,
            Conversation.id == conversation_participants.c.conversation_id
        ).filter(
            conversation_participants.c.user_id == user_id
        ).all()
        
        # Collect all participant IDs from these conversations
        contact_ids: Set[int] = set()
        for conv in conversations:
            for participant in conv.participants:
                if participant.id != user_id:
                    contact_ids.add(participant.id)
        
        return contact_ids
    finally:
        db.close()

