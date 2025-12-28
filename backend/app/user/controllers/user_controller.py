from fastapi import HTTPException, status
from sqlalchemy import or_
from typing import List
from backend.app.database.database import SessionLocal
from backend.app.user.models.user_model import User
from backend.app.user.schemas.user_schema import UserRead


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user() -> UserRead:
    """
    Get the current authenticated user.
    This should be called with Depends(get_current_user) in routes.
    """
    # This function is kept for backward compatibility
    # Routes should use Depends(get_current_user) directly
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="This function should not be called directly. Use Depends(get_current_user) in routes."
    )


def search_user(query: str) -> List[UserRead]:
    """
    Search for users by username or email.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching users
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required"
        )
    
    db = SessionLocal()
    try:
        # Search by username or email (case-insensitive partial match)
        search_term = f"%{query.strip()}%"
        users = db.query(User).filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        ).limit(50).all()  # Limit results to 50
        
        return [
            UserRead(
                id=user.id,
                username=user.username,
                email=user.email
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching users: {str(e)}"
        )
    finally:
        db.close()


def view_user_profile(user_id: int) -> UserRead:
    """
    View a user's profile by user ID.
    
    Args:
        user_id: ID of the user to view
        
    Returns:
        UserRead: User profile information
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserRead(
            id=user.id,
            username=user.username,
            email=user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )
    finally:
        db.close()
