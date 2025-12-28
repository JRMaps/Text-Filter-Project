from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.database import Base

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

    status = Column(
        String,
        default="allowed"
    )  # allowed | masked | blocked | flagged

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
