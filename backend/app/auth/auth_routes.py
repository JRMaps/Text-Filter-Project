from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.auth.auth_controller import (
    register_user,
    login_user,
    request_password_reset_otp,
    verify_password_reset_otp,
    reset_password_with_otp
)
from backend.app.user.user_schema import UserCreate, UserLogin
from backend.app.auth.auth_schema import (
    Token,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest
)

router = APIRouter()

@router.post("/register", response_model=dict, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user (UserCreate): User registration data.
        - username
        - email / phone_number is required (but not both)
        - backup_email and backup_phone_number are optional.
        - password
        db (Session): Database session.

        Note: the fe should pre-validate if the credential used is email or phone number
        to match the field in the schema.

    Returns:
        dict: Success message and user details.
    """
    return register_user(db, user)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and generate an access token.

    Args:
        login_data (UserLogin): Login credentials (email/phone and password).
        db (Session): Database session.

    Returns:
        Token: JWT access token and token type.
    """
    return login_user(db, login_data)

# ---------------------------------------------------------------------- #
# Forgot password pipeline:
# 1. Request OTP
# 2. Verify OTP
# 3. Reset Password
# Note: These are in different endpoints to allow step-by-step process.
# ---------------------------------------------------------------------- #
@router.post("/forgot-password-otp")
def forgot_password_otp(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request an OTP for password reset.

    Args:
        payload (ForgotPasswordRequest): Email or phone number to send OTP.
        db (Session): Database session.

    Returns:
        dict: Message indicating OTP was sent if the account exists.
    """
    return request_password_reset_otp(db, payload.identifier)


@router.post("/verify-otp")
def verify_otp(
    payload: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify the OTP sent to the user.

    Args:
        payload (VerifyOTPRequest): Identifier and OTP to verify.
        db (Session): Database session.

    Returns:
        dict: Message indicating OTP verification status.
    """
    return verify_password_reset_otp(db, payload.identifier, payload.otp)


@router.post("/reset-password-otp")
def reset_user_password_with_otp(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset the user's password after OTP verification.

    Args:
        payload (ResetPasswordRequest): Identifier, new password, and OTP.
        db (Session): Database session.

    Returns:
        dict: Message indicating password reset status.
    """
    return reset_password_with_otp(
        db,
        payload.identifier,
        payload.new_password
    )