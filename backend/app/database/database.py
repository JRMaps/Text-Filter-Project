import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
env_loaded = load_dotenv(dotenv_path=env_path)
if not env_loaded:
    print(f"Warning: .env file not found at {env_path} or could not be loaded.")

# Debug: Print the DATABASE_URL to verify it's being read
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Ensure it is defined in the .env file or as an environment variable.")
else:
    print(f"DATABASE_URL loaded: {DATABASE_URL}")

# Create a shared Base for all models
Base = declarative_base()

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable SQLAlchemy logging for debugging
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to ensure they're registered with Base
from backend.app.user.models.user_model import User
from backend.app.message.models.messages_model import Message
from backend.app.conversation.models.conversation_model import Conversation

# Create all tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
