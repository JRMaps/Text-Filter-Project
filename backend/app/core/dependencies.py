from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.auth.auth_utils import verify_token, get_user_by_email
from backend.app.user.user_model import User

# OAuth2 scheme for token extraction
# Note: tokenUrl should be the full path to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current authenticated user.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies and decodes the token
    3. Retrieves the user from the database
    4. Returns the user object
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    
    Args:
        token: JWT token from Authorization header (automatically extracted)
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode token
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except HTTPException:
        raise credentials_exception
    
    # Get user from database
    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    
    This is an additional layer that can be used to check if the user is active.
    Currently, it just returns the user, but you can add additional checks here
    (e.g., check if user account is active, not banned, etc.).
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_active_user)):
            return {"user_id": user.id}
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        User: The active user object
    """
    # Add any additional checks here (e.g., is_active, is_verified, etc.)
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

