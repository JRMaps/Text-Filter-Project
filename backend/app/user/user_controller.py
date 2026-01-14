from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from sqlalchemy import or_
from typing import List
from backend.app.user.user_model import User
from backend.app.user.user_schema import UserRead, UserUpdate 


def search_user(query: str, db: Session) -> List[UserRead]:
    """
    Search for users by username.
    
    Args:
        query: Search query string
        db: Database session
        
    Returns:
        List of matching users
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required"
        )
    
    try:
        # Search by username (case-insensitive partial match)
        search_term = f"%{query.strip()}%"
        users = db.query(User).filter(
            User.username.ilike(search_term)
        ).limit(50).all()
        
        return [
            UserRead(
                id=user.id,
                username=user.username,
                email=user.email,
                phone_number=user.phone_number
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching users: {str(e)}"
        )


def view_user_profile(user_id: int, db: Session) -> UserRead:
    """
    View a user's profile by user ID.
    
    Args:
        user_id: ID of the user to view
        db: Database session
        
    Returns:
        UserRead: User profile information
    """
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
            email=user.email,
            phone_number=user.phone_number
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )


def edit_user_profile(user_id: int, user_update: UserUpdate, db: Session) -> UserRead:
    """ 
    Edit the current user's profile.
    
    Args:
        user_id: ID of the user to update
        user_update: Data to update the user profile with
        db: Database session
        
    Returns:
        UserRead: Updated user profile information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return UserRead.model_validate(user)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )
