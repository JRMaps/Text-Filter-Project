from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from backend.app.message.message_model import Message
from backend.app.conversation.conversation_model import Conversation, conversation_participants
from backend.app.message.message_schema import MessageRead, MessageStatus


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def find_or_create_conversation(db: Session, sender_id: int, receiver_id: int) -> Conversation:
    """
    Find an existing conversation between two users, or create a new one.
    
    Args:
        db: Database session
        sender_id: ID of the sender
        receiver_id: ID of the receiver
        
    Returns:
        Conversation: The existing or newly created conversation
    """
    # Find existing conversation where both users are participants
    # Query conversations that have both sender and receiver as participants
    conversations = db.query(Conversation).join(
        conversation_participants,
        Conversation.id == conversation_participants.c.conversation_id
    ).filter(
        conversation_participants.c.user_id.in_([sender_id, receiver_id])
    ).all()
    
    # Filter to find conversation with exactly both users
    for conv in conversations:
        participant_ids = [p.id for p in conv.participants]
        if sender_id in participant_ids and receiver_id in participant_ids and len(participant_ids) == 2:
            return conv
    
    # No existing conversation found, create new one
    
    # Create new conversation
    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()
    
    if not sender or not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender or receiver not found"
        )
    
    new_conversation = Conversation()
    db.add(new_conversation)
    db.flush()  # Get the ID
    
    # Add participants
    new_conversation.participants.append(sender)
    new_conversation.participants.append(receiver)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation


# SEND MESSAGE: Send a message and update/create conversation summary
def send_message(sender_id: int, receiver_id: int, content: str):
    """
    Send a message between two users. Creates a conversation if it doesn't exist.
    
    Args:
        sender_id: ID of the user sending the message
        receiver_id: ID of the user receiving the message
        content: Message content
        
    Returns:
        MessageRead: The created message
    """
    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    # ------------------------------------------------------- #
    # CFG implementation logic here: (filter before sending)
    # 1. Normalization
    # 2. Tokenization
    # 3. CFG Parsing
    # 4. Severity Scoring
    # 5. Decision (allow / mask / block / flag)
    # ------------------------------------------------------- #
    
    db = SessionLocal()
    try:
        # Verify sender and receiver exist
        sender = db.query(User).filter(User.id == sender_id).first()
        receiver = db.query(User).filter(User.id == receiver_id).first()
        
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found"
            )
        
        if sender_id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to yourself"
            )
        
        # Find or create conversation
        conversation = find_or_create_conversation(db, sender_id, receiver_id)
        
        # Create message
        new_message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            raw_content=content,
            normalized_content=content,  # Will be set by CFG implementation
            status=MessageStatus.allowed.value,  # Default status
            severity_score=None,  # Will be set by CFG implementation
            matched_layers=None,  # Will be set by CFG implementation
            matched_rules=None,  # Will be set by CFG implementation
            timestamp=datetime.utcnow()
        )
        
        db.add(new_message)
        db.flush()  # Get the message ID
        
        # Update conversation metadata
        conversation.last_message_id = new_message.id
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(new_message)
        
        # Convert to MessageRead schema
        return MessageRead(
            id=new_message.id,
            conversation_id=new_message.conversation_id,
            sender_id=new_message.sender_id,
            receiver_id=new_message.receiver_id,
            content=new_message.raw_content,  # Map raw_content to content
            status=MessageStatus(new_message.status),
            created_at=new_message.timestamp  # Map timestamp to created_at
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )
    finally:
        db.close()
