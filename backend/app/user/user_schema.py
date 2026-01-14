from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional


class ExclusiveContactMixin:
    """Mixin to ensure either email or phone_number is provided, but not both."""
    
    @model_validator(mode="after")
    def validate_exclusive_contact(self):
        email = getattr(self, 'email', None)
        phone_number = getattr(self, 'phone_number', None)
        
        if not email and not phone_number:
            raise ValueError("Either email or phone_number must be provided.")
        
        if email and phone_number:
            raise ValueError("Only one of email or phone_number should be provided.")
        
        return self


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    backup_email: Optional[EmailStr] = None
    backup_phone_number: Optional[str] = None
    active_status: Optional[bool] = True


class UserCreate(ExclusiveContactMixin, UserBase):
    password: str


class UserLogin(ExclusiveContactMixin, BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    backup_email: Optional[EmailStr] = None
    backup_phone_number: Optional[str] = None

    if not username and not backup_email and not backup_phone_number:
        raise ValueError("No field to update provided.")