from fastapi import APIRouter, HTTPException
from backend.app.auth.auth_controller import register_user, login_user, request_password_reset_otp, verify_password_reset_otp, reset_password_with_otp
from backend.app.user.user_schema import UserCreate, UserLogin
from backend.app.auth.auth_schema import Token, ForgotPasswordOTPRequest, VerifyOTPRequest, ResetPasswordRequest

router = APIRouter()


@router.post("/register", response_model=dict, status_code=201)
async def register(user: UserCreate):
    """
    Register a new user.
    
    - **username**: Unique username for the user
    - **email**: Valid email address
    - **password**: User password (will be hashed)
    """
    try:
        return await register_user(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Authenticate a user and receive an access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns a JWT access token that can be used for authenticated requests.
    """
    try:
        return await login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot-password-otp", status_code=200)
async def forgot_password_otp(payload: ForgotPasswordOTPRequest):
    """
    Request an OTP for password reset.
    Sends OTP to user's email or phone.
    """
    return await request_password_reset_otp(payload.identifier)


@router.post("/verify-otp", status_code=200)
async def verify_otp(payload: VerifyOTPRequest):
    """
    Verify the OTP sent to user.
    Must be called before resetting password.
    """
    return await verify_password_reset_otp(payload.identifier, payload.otp)


@router.post("/reset-password-otp", status_code=200)
async def reset_user_password_with_otp(payload: ResetPasswordRequest):
    """
    Reset password after OTP verification.
    Can only be called after successful OTP verification.
    """
    return await reset_password_with_otp(
        payload.identifier,
        payload.new_password
    )