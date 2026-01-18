from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table, String, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from backend.app.database.database import Base 

class ConversationType(PyEnum):
    PRIVATE = "private"
    GROUP = "group"

conversation_participants = Table(
    "conversation_participants",
    Base.metadata,
    Column(
        "conversation_id",
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, nullable=True)
    last_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    type = Column(Enum(ConversationType), nullable=False, default=ConversationType.PRIVATE)

    participants = relationship(
        "User",
        secondary=conversation_participants,
        backref="conversations"
    )

    
    messages = relationship(
        "Message",
        foreign_keys="Message.conversation_id",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    
    last_message = relationship(
        "Message",
        foreign_keys=[last_message_id],
        post_update=True 
    )
