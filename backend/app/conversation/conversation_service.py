from datetime import datetime
from fastapi import HTTPException, status
from typing import List
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from backend.app.message.message_model import Message, ModerationStatus, DeliveryStatus as ModelDeliveryStatus
from backend.app.conversation.conversation_model import Conversation, conversation_participants
from backend.app.conversation.conversation_schema import ConversationDashboardItem, ConversationWithMessages
from backend.app.message.message_schema import MessageRead, MessageStatus, DeliveryStatus
from backend.app.user.user_schema import UserRead
from backend.app.conversation.conversation_schema import ConversationType


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# DASHBOARD: Get All Conversations
# Returns a list of conversations with the last message and other user info
# This does NOT load messages, it only builds the chat list
def get_all_conversations(current_user_id: int) -> List[ConversationDashboardItem]:
    """
    Get all conversations for the current user with last message preview.
    
    Args:
        current_user_id: ID of the current user
        
    Returns:
        List of conversation summaries with other user info and last message
    """
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all conversations where user is a participant
        conversations = db.query(Conversation).join(
            conversation_participants,
            Conversation.id == conversation_participants.c.conversation_id
        ).filter(
            conversation_participants.c.user_id == current_user_id
        ).all()
        
        dashboard = []
        
        for convo in conversations:
            if convo.type == ConversationType.PRIVATE:
                # Process private conversation
                # Get the other user (not the current user)
                other_user = next(
                    (p for p in convo.participants if p.id != current_user_id),
                    None
                )
                
                if not other_user:
                    continue  # Skip if no other user found (shouldn't happen)
                
                # Get last message if exists
                last_message_content = None
                if convo.last_message_id:
                    last_message = db.query(Message).filter(
                        Message.id == convo.last_message_id
                    ).first()
                    if last_message:
                        last_message_content = last_message.raw_content
                
                dashboard.append(ConversationDashboardItem(
                    id=convo.id,
                    type=ConversationType.PRIVATE,
                    updated_at=convo.updated_at,
                    last_message=last_message_content
                ))
            elif convo.type == ConversationType.GROUP:
                # Process group conversation
                # Get last message if exists
                last_message_content = None
                if convo.last_message_id:
                    last_message = db.query(Message).filter(
                        Message.id == convo.last_message_id
                    ).first()
                    if last_message:
                        last_message_content = last_message.raw_content
                
                dashboard.append(ConversationDashboardItem(
                    id=convo.id,
                    type=ConversationType.GROUP,
                    updated_at=convo.updated_at,
                    last_message=last_message_content
                ))
        
        # Sort by updated_at, newest first
        dashboard.sort(key=lambda x: x.updated_at if x.updated_at else datetime.min, reverse=True)
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )
    finally:
        db.close()


# OPEN CHAT: Get Messages by Conversation ID (Called only when user clicks a conversation)
def get_conversation_by_id(conversation_id: int, current_user_id: int) -> ConversationWithMessages:
    """
    Get a conversation with all its messages by conversation ID.
    
    Args:
        conversation_id: ID of the conversation
        current_user_id: ID of the current user (for access control)
        
    Returns:
        ConversationWithMessages: The conversation with all messages
    """
    db = SessionLocal()
    try:
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Check if current user is a participant
        user_ids = [p.id for p in conversation.participants]
        if current_user_id not in user_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get all messages for this conversation, sorted by timestamp
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        # Map moderation_status enum to MessageStatus schema enum
        moderation_status_map = {
            ModerationStatus.ALLOWED: MessageStatus.allowed,
            ModerationStatus.MASKED: MessageStatus.masked,
            ModerationStatus.BLOCKED: MessageStatus.blocked,
            ModerationStatus.FLAGGED: MessageStatus.flagged,
        }
        
        # Map delivery_status enum to DeliveryStatus schema enum
        delivery_status_map = {
            ModelDeliveryStatus.SENT: DeliveryStatus.sent,
            ModelDeliveryStatus.DELIVERED: DeliveryStatus.delivered,
            ModelDeliveryStatus.READ: DeliveryStatus.read,
        }
        
        # Convert messages to MessageRead schema
        message_reads = [
            MessageRead(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_id=msg.sender_id,
                receiver_id=msg.receiver_id,
                content=msg.raw_content,  # Map raw_content to content
                status=moderation_status_map.get(msg.moderation_status, MessageStatus.allowed),
                delivery_status=delivery_status_map.get(msg.delivery_status, DeliveryStatus.sent),
                created_at=msg.timestamp  # Map timestamp to created_at
            )
            for msg in messages
        ]
        
        # Build response
        return ConversationWithMessages(
            id=conversation.id,
            participants=[p.id for p in conversation.participants],
            last_message_id=conversation.last_message_id,
            updated_at=conversation.updated_at,
            messages=message_reads
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation: {str(e)}"
        )
    finally:
        db.close()
