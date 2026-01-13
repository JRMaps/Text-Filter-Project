from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    phone_number = Column(String, nullable=True, unique=True)
    backup_email = Column(String, nullable=True, unique=True)
    backup_phone_number = Column(String, nullable=True, unique=True)
    active_status = Column(Boolean, default=True)
    password_hash = Column(String, nullable=False)
    
    # For password reset via OTP
    otp_hash = Column(String, nullable=True) 
    password_reset_expires = Column(DateTime, nullable=True)
    otp_verified = Column(Boolean, default=False)
    
    sent_messages = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender"
    )

    message_receipts = relationship(
        "MessageReceipt",
        back_populates="user"
    )
