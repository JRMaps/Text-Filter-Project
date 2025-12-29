from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from backend.app.database.database import Base

class DeliveryStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"

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
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    raw_content = Column(Text, nullable=False)
    normalized_content = Column(Text)

    # Moderation filtering status
    moderation_status = Column(
        SQLEnum(ModerationStatus),
        default=ModerationStatus.ALLOWED
    ) 

    # Delivery tracking status
    delivery_status = Column(
        SQLEnum(DeliveryStatus), 
        default=DeliveryStatus.SENT
    )

    severity_score = Column(Integer)
    matched_layers = Column(JSON)
    matched_rules = Column(JSON)

    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages"
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )
