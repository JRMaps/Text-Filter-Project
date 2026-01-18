from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from backend.app.database.database import Base

class ModerationStatus(str, Enum):
    ALLOWED = "allowed"
    MASKED = "masked"
    BLOCKED = "blocked"
    FLAGGED = "flagged"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)

    moderation_status = Column(
        SQLEnum(ModerationStatus),
        default=ModerationStatus.ALLOWED
    ) 

    severity_score = Column(Integer)

    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )

    conversation = relationship(
        "Conversation",
        foreign_keys=[conversation_id],
        back_populates="messages"
    )

    receipts = relationship(
        "MessageReceipt",
        back_populates="message",
        cascade="all, delete-orphan"
    )
