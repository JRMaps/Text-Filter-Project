from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from typing import List, Optional
from backend.app.contact.contact_service import (
    send_contact_request,
    accept_contact_request,
    reject_contact_request,
    remove_contact,
    block_contact,
    unblock_contact,
    get_contacts,
)
from backend.app.contact.contact_shema import (
    ContactCreate,
    ContactRead,
    ContactWithUser,
)
from backend.app.contact.contact_model import ContactStatus
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/contact-list", response_model=List[ContactWithUser])
async def api_get_contacts(
    status: Optional[str] = Query(None, description="Filter by status: accepted, pending, blocked"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all contacts for the current user, including mutual contacts.
    Optionally filter by status.
    """
    status_filter = None
    if status:
        try:
            status_filter = ContactStatus[status.upper()]
        except KeyError:
            status_filter = None
    
    contacts = get_contacts(
        user_id=current_user.id,
        status_filter=status_filter,
        db=db
    )
    
    return contacts


@router.post("/send_request", response_model=ContactRead)
async def api_send_contact_request(
    request: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a contact request to another user.
    """
    contact = send_contact_request(
        user_id=current_user.id,
        contact_id=request.contact_id,
        db=db
    )
    return contact


@router.post("/accept/{contact_id}", response_model=ContactRead)
async def api_accept_contact_request(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a pending contact request.
    """
    contact = accept_contact_request(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )
    return contact


@router.post("/reject/{contact_id}")
async def api_reject_contact_request(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a pending contact request.
    """
    result = reject_contact_request(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )
    return result


@router.delete("/remove/{contact_id}")
async def api_remove_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an accepted contact.
    """
    result = remove_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )
    return result


@router.post("/block/{contact_id}", response_model=ContactRead)
async def api_block_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Block a contact.
    """
    contact = block_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )
    return contact


@router.post("/unblock/{contact_id}")
async def api_unblock_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unblock a contact.
    """
    result = unblock_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )
    return result
