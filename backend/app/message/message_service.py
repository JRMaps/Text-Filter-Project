from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.user.user_model import User
from backend.app.message.message_model import Message, ModerationStatus
from backend.app.message.message_receipt_model import MessageReceipt, DeliveryStatus as ReceiptDeliveryStatus
from backend.app.conversation.conversation_model import Conversation, ConversationType, ProfanityWordTracking, ConversationUserMute
from backend.app.message.message_schema import MessageRead, MessageReceiptRead
from typing import Optional
from backend.app.moderation.normalizationV1 import normalization
from backend.app.moderation.tokenizer import tokenize
from backend.app.moderation.rank import Ranker
from backend.app.websocket.connection_manager import manager


#--------------------#
#   HELPER METHODS   #
#--------------------#
def create_new_conversation(db: Session, sender_id: int, receiver_id: int) -> Conversation:
    """
    Create a new conversation between two users.

    Args:
        db: Database session
        sender_id: ID of the sender
        receiver_id: ID of the receiver

    Returns:
        Conversation: The newly created conversation
    """
    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender or receiver not found"
        )

    new_conversation = Conversation()
    db.add(new_conversation)
    db.flush()

    new_conversation.participants.append(sender)
    new_conversation.participants.append(receiver)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation


def reset_expired_mutes(db: Session, conversation_id: int, user_id: int):
    """
    Reset profanity counts and conversation mutes after the mute duration has expired.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        user_id: ID of the user
    """
    # Reset expired word-level mutes
    expired_word_mutes = db.query(ProfanityWordTracking).filter(
        ProfanityWordTracking.conversation_id == conversation_id,
        ProfanityWordTracking.user_id == user_id,
        ProfanityWordTracking.muted_until < datetime.utcnow()
    ).all()

    for record in expired_word_mutes:
        record.count = 0
        record.muted_until = None

    # Reset expired conversation-level mutes
    expired_conversation_mutes = db.query(ConversationUserMute).filter(
        ConversationUserMute.conversation_id == conversation_id,
        ConversationUserMute.user_id == user_id,
        ConversationUserMute.muted_until < datetime.utcnow()
    ).all()

    for record in expired_conversation_mutes:
        record.profanity_count = 0
        record.muted_until = None

    db.commit()


#--------------------#
#   API METHODS      #
#--------------------#
def send_message(
    db: Session,
    sender_id: int,
    content: str,
    conversation_id: Optional[int] = None, 
    receiver_id: Optional[int] = None
):
    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    if not conversation_id and not receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either conversation_id or receiver_id must be provided"
        )

    if conversation_id and receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one of conversation_id or receiver_id"
        )

    if receiver_id and sender_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a message to yourself."
        )

    try:
        sender = db.query(User).filter(User.id == sender_id).first()
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )

        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

            if sender not in conversation.participants:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not a conversation participant"
                )

        else:
            # First message (private chat)
            receiver = db.query(User).filter(User.id == receiver_id).first()
            if not receiver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Receiver not found"
                )
            
            # Handle cases where the frontend mistakenly sends a receiver_id instead of a conversation_id.
            existing_conversation = db.query(Conversation).filter(
                Conversation.participants.any(id=sender_id),
                Conversation.participants.any(id=receiver_id),
                Conversation.type == ConversationType.PRIVATE
            ).first()
            if existing_conversation:
                conversation = existing_conversation
            else:
                conversation = create_new_conversation(db, sender_id, receiver_id)

        reset_expired_mutes(db, conversation.id, sender_id)

        user_mute = db.query(ConversationUserMute).filter(
            ConversationUserMute.conversation_id == conversation.id,
            ConversationUserMute.user_id == sender_id,
            ConversationUserMute.muted_until > datetime.utcnow()
        ).first()
        if user_mute:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are temporarily muted in this conversation."
            )

        # Message Moderation Pipeline (filter before sending)
        normalized_content = normalization(content)
        tokens = tokenize(normalized_content)
        ranker = Ranker(tokens, muted_words=conversation.muted_words)
        severity_score = ranker.calculate_severity()
        offensive_spans = ranker.offensive_spans

        for span in offensive_spans:
            offensive_word = span[3]
            profanity_record = db.query(ProfanityWordTracking).filter(
                ProfanityWordTracking.conversation_id == conversation.id,
                ProfanityWordTracking.user_id == sender_id,
                ProfanityWordTracking.word == offensive_word,
                ProfanityWordTracking.muted_until > datetime.utcnow()
            ).first()

            if profanity_record:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"The word '{offensive_word}' is temporarily muted in this conversation."
                )

        # Set moderation status based on severity score
        action = ranker.get_action(severity_score)
        moderation_status = ModerationStatus[action.upper()]

        # Case 1: Reject the message if the moderation status is blocked (based from the system design).
        # Justification: The system should not allow messages that have high severity levels in the first place.
        # Note: The other cases that are only "masked" / "flagged" are monitored and muted once it reaches a specific count of detection
        # because the user just might say a profanity word out of frustrations or expression. However, it still need to have a limit
        if moderation_status == ModerationStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Message blocked due to policy violations."
            )

        # Case 2: Mute a specific profanity word after detecting it 5 times
        masked_words = []
        profanity_count = 0
        for span in offensive_spans:
            offensive_word = span[3]
            if offensive_word not in masked_words:
                masked_words.append(offensive_word)

            profanity_record = db.query(ProfanityWordTracking).filter(
                ProfanityWordTracking.conversation_id == conversation.id,
                ProfanityWordTracking.user_id == sender_id,
                ProfanityWordTracking.word == offensive_word
            ).first()

            if profanity_record:
                profanity_record.count += 1
                if profanity_record.count >= 5:
                    profanity_record.muted_until = datetime.utcnow() + timedelta(minutes=5)
            else:
                db.add(ProfanityWordTracking(
                    conversation_id=conversation.id,
                    user_id=sender_id,
                    word=offensive_word,
                    count=1
                ))

        if (masked_words):
            profanity_count += 1

        # Case 3: Check if the user has an existing muted word and a new profanity is detected
        existing_mute = db.query(ProfanityWordTracking).filter(
            ProfanityWordTracking.conversation_id == conversation.id,
            ProfanityWordTracking.user_id == sender_id,
            ProfanityWordTracking.muted_until > datetime.utcnow()
        ).first()

        if existing_mute and profanity_count > 0:
            db.add(ConversationUserMute(
                conversation_id=conversation.id,
                user_id=sender_id,
                muted_until=datetime.utcnow() + timedelta(minutes=5),
                profanity_count=0
            ))
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are temporarily muted in this conversation due to repeated offensive language."
            )

        # Case 4: Mute a user in the conversation after sending high volume of profanities
        if profanity_count > 0:
            user_mute_record = db.query(ConversationUserMute).filter(
                ConversationUserMute.conversation_id == conversation.id,
                ConversationUserMute.user_id == sender_id
            ).first()

            if user_mute_record:
                user_mute_record.profanity_count += profanity_count
                if user_mute_record.profanity_count >= 7:
                    user_mute_record.muted_until = datetime.utcnow() + timedelta(minutes=5)
                    db.commit()
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Error sending message: You are temporarily muted in this conversation due to sending a high volume of profanities."
                    )
            else:
                db.add(ConversationUserMute(
                    conversation_id=conversation.id,
                    user_id=sender_id,
                    profanity_count=profanity_count,
                    muted_until=None
                ))

        # Create message
        new_message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            content=content,
            moderation_status=moderation_status,
            severity_score=severity_score,
            masked_words=masked_words,
            timestamp=datetime.utcnow()
        )

        db.add(new_message)
        db.flush()

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

        # Get receipts for the message
        receipts = db.query(MessageReceipt).filter(
            MessageReceipt.message_id == new_message.id
        ).all()

        receipt_reads = [
            MessageReceiptRead(
                user_id=receipt.user_id,
                delivery_status=ReceiptDeliveryStatus[receipt.delivery_status.name], 
                delivered_at=receipt.delivered_at,
                read_at=receipt.read_at
            )
            for receipt in receipts
        ]

        # Broadcast new message to conversation participants
        participant_ids = [user.id for user in conversation.participants]
        manager.broadcast_new_message(
            participant_ids=participant_ids,
            message_data={
                "id": new_message.id,
                "conversation_id": new_message.conversation_id,
                "sender_id": new_message.sender_id,
                "content": new_message.content,
                "status": new_message.moderation_status.name,
                "created_at": new_message.timestamp.isoformat(),
                "receipts": receipt_reads,
                "masked_words": masked_words
            }
        )

        # Broadcast dashboard update to all participants
        manager.broadcast_dashboard_update(
            participant_ids=participant_ids,
            conversation_id=conversation.id,
            last_message=conversation.last_message_id,
            updated_at=new_message.timestamp.isoformat()
        )

        return MessageRead(
            id=new_message.id,
            conversation_id=new_message.conversation_id,
            sender_id=new_message.sender_id,
            content=new_message.content,  
            moderation_status=new_message.moderation_status,
            masked_words=masked_words,
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


def mark_message_delivered(db: Session, message_id: int, user_id: int) -> Optional[dict]:
    """
    Mark a message as delivered for a specific user.

    Args:
        message_id: ID of the message to mark as delivered.
        user_id: ID of the user for whom the message is delivered.

    Returns:
        dict: Details of the updated message receipt for broadcasting, or None if no update was made.
    """
    receipt = db.query(MessageReceipt).filter(
        MessageReceipt.message_id == message_id,
        MessageReceipt.user_id == user_id,
        MessageReceipt.delivery_status == ReceiptDeliveryStatus.SENT
    ).first()

    if not receipt:
        return None

    receipt.delivery_status = ReceiptDeliveryStatus.DELIVERED
    receipt.delivered_at = datetime.utcnow()
    db.commit()
    db.refresh(receipt)

    return {
        "participant_ids": [r.user_id for r in db.query(MessageReceipt)
            .filter(MessageReceipt.message_id == message_id).all()],
        "message_id": message_id,
        "user_id": user_id,
        "delivery_status": "delivered",
        "timestamp": receipt.delivered_at.isoformat()
    }


def mark_message_read(db: Session, message_id: int, user_id: int) -> Optional[dict]:
    """
    Mark a message as read for a specific user.

    Args:
        message_id: ID of the message to mark as read.
        user_id: ID of the user for whom the message is read.

    Returns:
        dict: Details of the updated message receipt for broadcasting, or None if no update was made.
    """
    receipt = db.query(MessageReceipt).filter(
        MessageReceipt.message_id == message_id,
        MessageReceipt.user_id == user_id,
        MessageReceipt.delivery_status == ReceiptDeliveryStatus.DELIVERED
    ).first()

    if not receipt:
        return None  # Already read or invalid receipt

    receipt.delivery_status = ReceiptDeliveryStatus.READ
    receipt.read_at = datetime.utcnow()
    db.commit()
    db.refresh(receipt)

    return {
        "participant_ids": [r.user_id for r in db.query(MessageReceipt).filter(
            MessageReceipt.message_id == message_id
        ).all()],
        "message_id": message_id,
        "user_id": user_id,
        "delivery_status": "read",
        "timestamp": receipt.read_at.isoformat()
    }
