from fastapi import HTTPException, status
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from backend.app.user.user_schema import UserCreate, UserLogin
from backend.app.auth.auth_schema import Token
from backend.app.auth.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    generate_otp,
    hash_otp,
    send_otp_via_email,
    send_otp_via_phone,
    OTP_EXPIRY_MINUTES,
    OTP_RESEND_COOLDOWN_SECONDS,
    OTP_MAX_RETRY_ATTEMPTS
)
from datetime import timedelta, datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def register_user(user_data: UserCreate) -> dict:
    db = SessionLocal()
    try:
        existing_email = get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )
    finally:
        db.close()


async def login_user(login_data: UserLogin) -> Token:
    user = get_user_by_email(login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


async def request_password_reset_otp(identifier: str) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.email == identifier) |
            (User.phone_number == identifier) |
            (User.backup_email == identifier) |
            (User.backup_phone_number == identifier)
        ).first()

        if not user:
            return {"message": "If the account exists, an OTP has been sent."}

        now = datetime.utcnow()
        
        # Check rate limiting
        if user.otp_locked_until and now < user.otp_locked_until:
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Please try again later."
            )
        
        # Check cooldown period
        if user.otp_sent_at:
            time_since_last_otp = (now - user.otp_sent_at).total_seconds()
            if time_since_last_otp < OTP_RESEND_COOLDOWN_SECONDS:
                raise HTTPException(
                    status_code=429,
                    detail=f"Please wait {int(OTP_RESEND_COOLDOWN_SECONDS - time_since_last_otp)} seconds before requesting another OTP."
                )

        otp = generate_otp()
        user.otp_hash = hash_otp(otp)
        user.password_reset_expires = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
        user.otp_attempts = 0
        user.otp_verified = False
        user.otp_sent_at = now 

        db.commit()

        if identifier in [user.email, user.backup_email]:
            send_otp_via_email(identifier, otp)
        else:
            send_otp_via_phone(identifier, otp)

        return {"message": "If the account exists, an OTP has been sent."}

    finally:
        db.close()


async def verify_password_reset_otp(identifier: str, otp: str) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.email == identifier) |
            (User.phone_number == identifier) |
            (User.backup_email == identifier) |
            (User.backup_phone_number == identifier)
        ).first()

        if not user or not user.otp_hash:  
            raise HTTPException(status_code=400, detail="Invalid OTP")

        now = datetime.utcnow()

        # Check if OTP is expired
        if now > user.password_reset_expires:
            user.otp_hash = None 
            db.commit()
            raise HTTPException(status_code=400, detail="OTP expired")

        # Check max attempts
        if user.otp_attempts >= OTP_MAX_RETRY_ATTEMPTS:
            user.otp_locked_until = now + timedelta(minutes=30)  # ← Added: lock account
            user.otp_hash = None 
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Account locked for 30 minutes."
            )

        # Verify OTP
        if user.otp_hash != hash_otp(otp):  
            user.otp_attempts += 1
            db.commit()
            remaining_attempts = OTP_MAX_RETRY_ATTEMPTS - user.otp_attempts
            raise HTTPException(
                status_code=400,
                detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
            )

        # OTP is valid
        user.otp_verified = True
        db.commit()

        return {"message": "OTP verified successfully"}

    finally:
        db.close()


async def reset_password_with_otp(identifier: str, new_password: str) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.email == identifier) |
            (User.phone_number == identifier) |
            (User.backup_email == identifier) |
            (User.backup_phone_number == identifier)
        ).first()

        if not user or not user.otp_verified:
            raise HTTPException(
                status_code=403,
                detail="OTP verification required"
            )

        user.password_hash = get_password_hash(new_password)

        # Cleanup - use correct field names
        user.otp_hash = None  # ← Fixed: use otp_hash
        user.otp_verified = False
        user.password_reset_expires = None
        user.otp_attempts = 0
        user.otp_sent_at = None  # ← Added: clear timestamp
        user.otp_locked_until = None  # ← Added: clear lock

        db.commit()

        return {"message": "Password reset successfully"}

    finally:
        db.close()

