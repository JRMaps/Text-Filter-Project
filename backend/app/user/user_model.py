from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

    sent_messages = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender"
    )

    received_messages = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver"
    )
