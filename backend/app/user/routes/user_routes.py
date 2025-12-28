from fastapi import APIRouter, Query, Depends
from typing import List
from backend.app.user.controllers.user_controller import search_user, view_user_profile
from backend.app.user.schemas.user_schema import UserRead
from backend.app.user.models.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get the current authenticated user's information."""
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )


@router.get("/search", response_model=List[UserRead])
async def get_search_user(
    query: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Search for users by username or email."""
    return search_user(query)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """View a user's profile by user ID."""
    return view_user_profile(user_id)
