from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    backup_email: Optional[EmailStr] = None
    backup_phone_number: Optional[str] = None
    active_status: Optional[bool] = True

    @model_validator(mode="after")
    def validate_contact_info(self) -> "UserBase":
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone_number must be provided.")
        return self

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def validate_login_info(self) -> "UserLogin":
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone_number must be provided.")
        return self

class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    backup_email: Optional[EmailStr] = None
    backup_phone_number: Optional[str] = None