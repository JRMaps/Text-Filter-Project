from fastapi import APIRouter, HTTPException
from backend.app.auth.controllers.auth_controller import register_user, login_user
from backend.app.user.schemas.user_schema import UserCreate, UserLogin
from backend.app.auth.schemas.auth_schema import Token

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
