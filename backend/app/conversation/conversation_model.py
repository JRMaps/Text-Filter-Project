from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.database import Base 

# Association table for many-to-many relationship between users and conversations
conversation_participants = Table(
    "conversation_participants",
    Base.metadata,
    Column("conversation_id", Integer, ForeignKey("conversations.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    last_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship(
        "User",
        secondary=conversation_participants,
        backref="conversations"
    )

    messages = relationship("Message", back_populates="conversation")
