from fastapi import HTTPException, status
from backend.app.user.user_model import User
from backend.app.user.user_schema import UserCreate, UserLogin
from backend.app.auth.auth_schema import Token
from backend.app.auth.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_otp,
    hash_otp,
    send_otp_via_email,
    send_otp_via_phone
)
from datetime import timedelta, datetime
from sqlalchemy.orm import Session


def register_user(db: Session, user_data: UserCreate) -> dict:
    try:
        existing_user = db.query(User).filter(
            (User.email == user_data.email) |
            (User.username == user_data.username) |
            (User.phone_number == user_data.phone_number)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, phone number, or username already registered"
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            phone_number=user_data.phone_number,
            backup_email=user_data.backup_email,
            backup_phone_number=user_data.backup_phone_number,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        user_credential = (
            {"email": new_user.email} if new_user.email else {"phone_number": new_user.phone_number}
        )

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                **user_credential
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


def login_user(db: Session, login_data: UserLogin) -> Token:
    user = db.query(User).filter(
        (User.email == login_data.email) |
        (User.phone_number == login_data.phone_number)
    ).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=30)
    )

    return Token(access_token=access_token, token_type="bearer")


def request_password_reset_otp(db: Session, identifier: str) -> dict:
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

        otp = generate_otp()
        user.otp_hash = hash_otp(otp)
        user.password_reset_expires = now + timedelta(minutes=10)
        user.otp_attempts = 0
        user.otp_verified = False

        db.commit()

        if identifier in [user.email, user.backup_email]:
            send_otp_via_email(identifier, otp)
        else:
            send_otp_via_phone(identifier, otp)

        return {"message": "If the account exists, an OTP has been sent."}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error requesting OTP: {str(e)}"
        )


def verify_password_reset_otp(db: Session, identifier: str, otp: str) -> dict:
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

        if now > user.password_reset_expires:
            user.otp_hash = None
            db.commit()
            raise HTTPException(status_code=400, detail="OTP expired")

        if user.otp_hash != hash_otp(otp):
            user.otp_attempts += 1
            db.commit()
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # OTP is valid
        user.otp_verified = True
        db.commit()

        return {"message": "OTP verified successfully"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying OTP: {str(e)}"
        )


def reset_password_with_otp(db: Session, identifier: str, new_password: str) -> dict:
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

        # Cleanup
        user.otp_hash = None
        user.otp_verified = False
        user.password_reset_expires = None
        user.otp_attempts = 0

        db.commit()

        return {"message": "Password reset successfully"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

