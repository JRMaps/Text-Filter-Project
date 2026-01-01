from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from backend.app.database.database import Base

class ContactStatus(str, Enum):
    PENDING = "pending"  # Request sent, waiting for acceptance
    ACCEPTED = "accepted"  # Contact request accepted
    BLOCKED = "blocked"  # Contact blocked

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    
    # User who initiated the contact (requester)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # User who is being contacted (contact)
    contact_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Status of the contact relationship
    status = Column(SQLEnum(ContactStatus), nullable=False, default=ContactStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref="initiated_contacts"
    )
    
    contact = relationship(
        "User",
        foreign_keys=[contact_id],
        backref="received_contacts"
    )
    
    # Ensure unique contact relationship (user_id, contact_id pair)
    __table_args__ = (
        UniqueConstraint('user_id', 'contact_id', name='unique_user_contact'),
    )

