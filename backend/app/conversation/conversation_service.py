from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.user.user_model import User
from backend.app.message.message_model import Message
from backend.app.message.message_receipt_model import MessageReceipt
from backend.app.conversation.conversation_model import Conversation, conversation_participants
from backend.app.conversation.conversation_schema import ConversationDashboardItem, ConversationWithMessages, PrivateConversationDashboardItem, GroupConversationDashboardItem, ConversationParticipantRead
from backend.app.message.message_schema import MessageRead, MessageReceiptRead, DeliveryStatus, ModerationStatus
from backend.app.user.user_schema import UserRead
from backend.app.conversation.conversation_schema import ConversationType


def get_all_conversations(current_user_id: int, db: Session) -> List[ConversationDashboardItem]:
    """
    Get all conversations for the current user with last message preview.
    Note: This does NOT load messages, it only builds the chat list.

    Args:
        current_user_id: ID of the current user
        
    Returns:
        List of conversation summaries with other user info and last message
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch conversations where user is a participant
        conversations = (
            db.query(Conversation)
            .join(conversation_participants)
            .filter(conversation_participants.c.user_id == current_user_id)
            .all()
        )

        dashboard = []

        # Build dashboard items
        for convo in conversations:
            # Fetch last message content
            last_message_content = (
                db.query(Message.content)
                .filter(Message.id == convo.last_message_id)
                .scalar()
                if convo.last_message_id else None
            )

            if convo.type == ConversationType.PRIVATE:
                # Get the other user in private conversations
                other_user = next(
                    (p for p in convo.participants if p.id != current_user_id),
                    None
                )
                if not other_user:
                    continue

                dashboard.append(
                    PrivateConversationDashboardItem(
                        id=convo.id,
                        type=ConversationType.PRIVATE,
                        updated_at=convo.updated_at,
                        last_message=last_message_content,
                        other_user=other_user
                    )
                )
            else:
                # Add group conversation details
                dashboard.append(
                    GroupConversationDashboardItem(
                        id=convo.id,
                        type=ConversationType.GROUP,
                        updated_at=convo.updated_at,
                        last_message=last_message_content,
                        group_name=convo.group_name,
                        member_count=len(convo.participants),
                        participants=[
                            ConversationParticipantRead(
                                id=participant.id,
                                username=participant.username
                            )
                            for participant in convo.participants
                        ]
                    )
                )

        # Sort by latest activity
        dashboard.sort(key=lambda x: x.updated_at, reverse=True)
        return dashboard

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )


def get_conversation_by_id(conversation_id: int, current_user_id: int, db: Session) -> ConversationWithMessages:
    """
    Get a conversation with all its messages by conversation ID.
    Note: This is called when a user opens a conversation thread.
    Args:
        conversation_id: ID of the conversation
        current_user_id: ID of the current user (for access control)
        
    Returns:
        ConversationWithMessages: The conversation with all messages
    """
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
        
        # Convert messages to MessageRead schema with receipts
        message_reads = []
        for msg in messages:
            # Get receipts for this message
            receipts = db.query(MessageReceipt).filter(
                MessageReceipt.message_id == msg.id
            ).all()
            
            receipt_reads = [
                MessageReceiptRead(
                    user_id=receipt.user_id,
                    delivery_status=DeliveryStatus[receipt.delivery_status.name],  # Ensure proper enum handling
                    delivered_at=receipt.delivered_at,
                    read_at=receipt.read_at
                )
                for receipt in receipts
            ]
            
            message_reads.append(
                MessageRead(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    sender_id=msg.sender_id,
                    content=msg.content, 
                    status=ModerationStatus[msg.moderation_status.name],  # Ensure proper enum handling
                    created_at=msg.timestamp,
                    receipts=receipt_reads
                )
            )
        
        # Build response
        return ConversationWithMessages(
            id=conversation.id,
            participants=[
                ConversationParticipantRead(
                    id=participant.id,
                    username=participant.username
                )
                for participant in conversation.participants
            ],
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
