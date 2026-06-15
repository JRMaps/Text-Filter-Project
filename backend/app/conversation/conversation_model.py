from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table, String, Enum, JSON
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
    muted_words = Column(JSON, default={})
    muted_users = Column(JSON, default={})

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


class ProfanityWordTracking(Base):
    __tablename__ = "profanity_word_tracking"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(255), nullable=False)
    count = Column(Integer, default=0)
    muted_until = Column(DateTime, nullable=True)

    __table_args__ = ({"sqlite_autoincrement": True},)


class ConversationUserMute(Base):
    __tablename__ = "conversation_user_mutes"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    muted_until = Column(DateTime, nullable=True)
    profanity_count = Column(Integer, default=0)  # Track total profanity count for the user in the conversation

    __table_args__ = ({"sqlite_autoincrement": True},)
