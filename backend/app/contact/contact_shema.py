from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
from backend.app.user.user_schema import UserRead

class ContactStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    blocked = "blocked"

class ContactBase(BaseModel):
    contact_id: int

class ContactCreate(ContactBase):
    """Schema for creating a contact request."""
    pass

class ContactRead(BaseModel):
    """Schema for reading contact information."""
    id: int
    user_id: int
    contact_id: int
    status: ContactStatus
    blocked_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContactWithUser(BaseModel):
    """Contact information with user details."""
    id: int
    contact_id: int
    contact: UserRead  # The contact user's information
    status: ContactStatus
    blocked_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContactRequestResponse(BaseModel):
    """Response for contact request operations."""
    message: str
    contact: Optional[ContactRead] = None

class ContactListResponse(BaseModel):
    """Response for listing contacts."""
    contacts: List[ContactWithUser]
    total: int

class ContactStatusUpdate(BaseModel):
    """Schema for updating contact status."""
    status: ContactStatus

