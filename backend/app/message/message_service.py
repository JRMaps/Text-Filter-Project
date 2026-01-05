from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from backend.app.message.message_model import Message, ModerationStatus
from backend.app.message.message_receipt_model import MessageReceipt, DeliveryStatus as ReceiptDeliveryStatus
from backend.app.conversation.conversation_model import Conversation, conversation_participants
from backend.app.message.message_schema import MessageRead, MessageStatus, MessageReceiptRead, DeliveryStatus
from backend.app.moderation import cfg_result_schema, normalizationV1, tokenizer, parser

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


def send_message(sender_id: int, conversation_id: int, content: str):
    """
    Send a message to a conversation (private or group). Creates a conversation if it doesn't exist.
    
    Args:
        sender_id: ID of the user sending the message
        conversation_id: ID of the conversation
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
        # Verify sender exists
        sender = db.query(User).filter(User.id == sender_id).first()
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        # Verify conversation exists
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Create message
        new_message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            raw_content=content,
            normalized_content=content,  # Will be set by CFG implementation
            moderation_status=ModerationStatus.ALLOWED,  # Default status
            delivery_status=ReceiptDeliveryStatus.SENT,  # Initial delivery status
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
        
        # Create message receipts for all participants except the sender
        for participant in conversation.participants:
            if participant.id != sender_id:
                receipt = MessageReceipt(
                    message_id=new_message.id,
                    user_id=participant.id,
                    delivery_status=ReceiptDeliveryStatus.SENT
                )
                db.add(receipt)
        
        db.commit()
        db.refresh(new_message)
        
        # Map moderation_status enum to MessageStatus schema enum
        moderation_status_map = {
            ModerationStatus.ALLOWED: MessageStatus.allowed,
            ModerationStatus.MASKED: MessageStatus.masked,
            ModerationStatus.BLOCKED: MessageStatus.blocked,
            ModerationStatus.FLAGGED: MessageStatus.flagged,
        }
        
        # Map receipt delivery_status enum to DeliveryStatus schema enum
        delivery_status_map = {
            ReceiptDeliveryStatus.SENT: DeliveryStatus.sent,
            ReceiptDeliveryStatus.DELIVERED: DeliveryStatus.delivered,
            ReceiptDeliveryStatus.READ: DeliveryStatus.read,
        }
        
        # Get receipts for the message
        receipts = db.query(MessageReceipt).filter(
            MessageReceipt.message_id == new_message.id
        ).all()
        
        receipt_reads = [
            MessageReceiptRead(
                user_id=receipt.user_id,
                delivery_status=delivery_status_map.get(receipt.delivery_status, DeliveryStatus.sent),
                delivered_at=receipt.delivered_at,
                read_at=receipt.read_at
            )
            for receipt in receipts
        ]
        
        return MessageRead(
            id=new_message.id,
            conversation_id=new_message.conversation_id,
            sender_id=new_message.sender_id,
            content=new_message.raw_content,
            status=moderation_status_map.get(new_message.moderation_status, MessageStatus.allowed),
            created_at=new_message.timestamp,
            receipts=receipt_reads
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
