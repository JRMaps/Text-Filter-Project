import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from email.message import EmailMessage
import os
import smtplib
import hashlib
import secrets
from collections import defaultdict
from threading import Lock

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email from the database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by ID from the database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username from the database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    finally:
        db.close()

# For OTP generation and hashing purposes
def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

# For OTP notification purposes
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


# Rate limiting storage (in-memory, can be upgraded to Redis for production)
_rate_limit_store: Dict[str, list] = defaultdict(list)
_rate_limit_lock = Lock()

# OTP Configuration
OTP_EXPIRY_MINUTES = 10
OTP_MAX_RETRY_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60 
RATE_LIMIT_MAX_REQUESTS = 5  
RATE_LIMIT_WINDOW_MINUTES = 15 


def check_rate_limit(identifier: str) -> Tuple[bool, Optional[int]]:
    """
    Check if identifier has exceeded rate limit.
    Returns (is_allowed, seconds_until_reset)
    """
    with _rate_limit_lock:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
        
        # Clean old entries
        _rate_limit_store[identifier] = [
            timestamp for timestamp in _rate_limit_store[identifier]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(_rate_limit_store[identifier]) >= RATE_LIMIT_MAX_REQUESTS:
            # Calculate seconds until oldest request expires
            oldest_request = min(_rate_limit_store[identifier])
            reset_time = oldest_request + timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
            seconds_until_reset = int((reset_time - now).total_seconds())
            return False, max(0, seconds_until_reset)
        
        return True, None


def record_rate_limit_request(identifier: str) -> None:
    """Record a rate limit request for the identifier."""
    with _rate_limit_lock:
        _rate_limit_store[identifier].append(datetime.utcnow())
