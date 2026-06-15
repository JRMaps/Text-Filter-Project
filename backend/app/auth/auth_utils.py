import hashlib
import logging
import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.app.user.user_model import User

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OTP config
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))

# ----------------------
# Password utils
# ----------------------
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ----------------------
# JWT utils
# ----------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token storing only the user_id"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify JWT and return payload"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ----------------------
# User fetch utils
# ----------------------
def get_user_by_email_or_phone(db: Session, credential: str) -> Optional[User]:
    """
    Fetch user by email OR phone number.
    """
    return db.query(User).filter(
        (User.email == credential) | (User.phone_number == credential)
    ).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

# ----------------------
# OTP utils
# ----------------------
def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


# ----------------------
# OTP sending utils
# ----------------------
def send_otp_via_email(to_email: str, otp: str) -> None:
    """
    Sends OTP via email.
    """

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")   
    SMTP_PASSWORD = os.getenv("SMTP_PASS")

    if not SMTP_USER or not SMTP_PASSWORD:
        print("Email service not configured")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Your Password Reset OTP"
    msg.set_content(
        f"""
Your OTP code is: {otp}

This code will expire in 10 minutes.

If you did not request this, please ignore this email.
"""
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")


def send_otp_via_phone(phone_number: str, otp: str) -> None:
    """
    Sends OTP via SMS using Twilio.
    Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env

    Note: mema lang tong sa SMS feat, may bayad to guyz, puro twilio nakikita ko sa yt haha
    """

    try:
        from twilio.rest import Client
        
        TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            print("Twilio SMS service not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env")
            return
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your password reset OTP code is: {otp}. This code will expire in 10 minutes. If you did not request this, please ignore this message.",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number}. SID: {message.sid}")
    except ImportError:
        # Fallback: Use a generic SMS service or print for development
        print(f"[SMS] OTP for {phone_number}: {otp}")
        print("Note: Install twilio package (pip install twilio) and configure credentials for production SMS")
    except Exception as e:
        print(f"SMS sending failed: {e}")
