from pydantic import BaseModel, Field
from typing import Optional

# For JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# For forgot password func: OTP requests and verification
class ForgotPasswordOTPRequest(BaseModel):
    identifier: str 

class VerifyOTPRequest(BaseModel):
    identifier: str
    otp: str

class ResetPasswordRequest(BaseModel):
    identifier: str
    new_password: str