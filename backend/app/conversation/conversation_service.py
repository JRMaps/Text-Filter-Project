from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.user.user_model import User
from backend.app.message.message_model import Message
from backend.app.message.message_receipt_model import MessageReceipt
from backend.app.conversation.conversation_model import Conversation, conversation_participants, ConversationType
from backend.app.conversation.conversation_schema import ConversationDashboardItem, ConversationWithMessages, PrivateConversationDashboardItem, GroupConversationDashboardItem, ConversationParticipantRead, GroupConversationCreateResponse
from backend.app.message.message_schema import MessageRead, MessageReceiptRead, DeliveryStatus, ModerationStatus
from backend.app.user.user_schema import UserRead


def get_all_conversations(current_user_id: int, db: Session) -> List[ConversationDashboardItem]:
    """
    Get all conversations for the current user with last message preview.

    Args:
        current_user_id: ID of the current user
        
    Returns:
        List of conversation summaries with other user info and last message
    """
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        conversations = (
            db.query(Conversation)
            .join(conversation_participants)
            .filter(conversation_participants.c.user_id == current_user_id)
            .all()
        )

        dashboard = []

        # Build dashboard items
        for convo in conversations:
            last_message = db.query(Message).filter(
                Message.id == convo.last_message_id,
            ).first()

            last_message_content = last_message.content if last_message else None
            last_message_moderation_status = last_message.moderation_status if last_message else None
            last_message_masked_words = last_message.masked_words if last_message else None  # Include masked words

            convo_type = convo.type.value.lower()

            if convo_type == ConversationType.PRIVATE.value:
                other_user = next(
                    (p for p in convo.participants if p.id != current_user_id),
                    None
                )
                if not other_user:
                    continue

                dashboard.append(
                    PrivateConversationDashboardItem(
                        id=convo.id,
                        type=convo_type,
                        updated_at=convo.updated_at,
                        last_message={
                            "content": last_message_content,
                            "moderation_status": last_message_moderation_status,
                            "masked_words": last_message_masked_words  # Add masked words here
                        },
                        other_user=ConversationParticipantRead(
                            id=other_user.id,
                            username=other_user.username
                        )
                    )
                )
            elif convo_type == ConversationType.GROUP.value:
                dashboard.append(
                    GroupConversationDashboardItem(
                        id=convo.id,
                        type=convo_type,
                        updated_at=convo.updated_at,
                        last_message={
                            "content": last_message_content,
                            "moderation_status": last_message_moderation_status,
                            "masked_words": last_message_masked_words  # Add masked words here
                        },
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
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        if not any(participant.id == current_user_id for participant in conversation.participants):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not a participant in this conversation"
            )

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        # Convert messages to MessageRead schema with receipts
        message_reads = [
            MessageRead(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_id=msg.sender_id,
                content=msg.content, 
                moderation_status=ModerationStatus[msg.moderation_status.name],
                created_at=msg.timestamp,
                receipts=[
                    MessageReceiptRead(
                        user_id=receipt.user_id,
                        delivery_status=DeliveryStatus[receipt.delivery_status.name],
                        delivered_at=receipt.delivered_at,
                        read_at=receipt.read_at
                    )
                    for receipt in msg.receipts
                ]
            )
            for msg in messages
        ]
        

        return ConversationWithMessages(
            id=conversation.id,
            participants=[
                ConversationParticipantRead(
                    id=participant.id,
                    username=participant.username
                )
                for participant in conversation.participants
            ],
            group_name=conversation.group_name,
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


def create_group_chat(
    db: Session,
    creator_id: int,
    participant_ids: List[int],
    group_name: Optional[str] = None
) -> GroupConversationCreateResponse:
    """
    Create a new group chat conversation.

    Args:
        db: Database session
        creator_id: ID of the user creating the group chat
        participant_ids: List of user IDs to add to the group chat
        group_name: Name of the group chat (optional)

    Returns:
        GroupConversationCreateResponse: The created group chat conversation with details
    """
    try:
        participant_ids = list(set(participant_ids))
        if creator_id not in participant_ids:
            participant_ids.append(creator_id)

        if len(participant_ids) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A group chat must have at least 3 participants (including the creator)."
            )

        participants = db.query(User).filter(User.id.in_(participant_ids)).all()

        if len(participants) != len(participant_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more participant IDs are invalid"
            )

        new_conversation = Conversation(
            type=ConversationType.GROUP,
            group_name=group_name,
            updated_at=datetime.utcnow()
        )
        db.add(new_conversation)
        db.flush()

        new_conversation.participants.extend(participants)
        db.commit()
        db.refresh(new_conversation)


        return GroupConversationCreateResponse(
            id=new_conversation.id,
            group_name=new_conversation.group_name,
            created_by=creator_id,
            type=new_conversation.type,
            created_at=new_conversation.updated_at,
            participants=[
                ConversationParticipantRead(
                    id=participant.id,
                    username=participant.username
                )
                for participant in new_conversation.participants
            ]
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating group chat: {str(e)}"
        )