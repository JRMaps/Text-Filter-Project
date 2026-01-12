from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.user.user_controller import (
    search_user,
    view_user_profile,
    edit_user_profile,
)
from backend.app.user.user_schema import UserRead, UserUpdate
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user
from backend.app.database.database import get_db

router = APIRouter()


@router.get("/profile", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get the current authenticated user's information."""
    return UserRead.model_validate(current_user)


@router.get("/search", response_model=List[UserRead])
async def get_search_user(
    query: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for users by username or email."""
    return search_user(query, db)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View a user's profile by user ID."""
    return view_user_profile(user_id, db)


@router.put("/profile/edit", response_model=UserRead)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit the current authenticated user's profile."""
    return edit_user_profile(current_user.id, user_update, db)
