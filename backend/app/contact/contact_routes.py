from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from backend.app.contact.contact_service import (
    send_contact_request,
    accept_contact_request,
    reject_contact_request,
    remove_contact,
    block_contact,
    unblock_contact,
    get_contacts,
    get_pending_requests,
    get_contact_status
)
from backend.app.contact.contact_shema import (
    ContactCreate,
    ContactRead,
    ContactWithUser,
    ContactRequestResponse,
    ContactListResponse,
    ContactStatus as SchemaContactStatus
)
from backend.app.contact.contact_model import ContactStatus
from backend.app.user.user_model import User
from backend.app.core.dependencies import get_current_user
from backend.app.websocket.connection_manager import manager
from datetime import datetime

router = APIRouter()


@router.post("/send_request", response_model=ContactRead)
async def api_send_contact_request(
    request: ContactCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Send a contact request to another user.
    Triggers WebSocket event for real-time notification.
    """
    contact = send_contact_request(
        user_id=current_user.id,
        contact_id=request.contact_id
    )
    
    # Broadcast WebSocket event to the contact
    await manager.send_to_user(
        request.contact_id,
        {
            "type": "contact:request_received",
            "payload": {
                "id": contact.id,
                "user_id": current_user.id,
                "username": current_user.username,
                "contact_id": contact.contact_id,
                "status": contact.status.value,
                "created_at": contact.created_at.isoformat()
            }
        }
    )
    
    return contact


@router.post("/accept/{contact_id}", response_model=ContactRead)
async def api_accept_contact_request(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Accept a pending contact request.
    Triggers WebSocket event for real-time notification.
    """
    contact = accept_contact_request(
        user_id=current_user.id,
        contact_id=contact_id
    )
    
    # Broadcast WebSocket event to both users
    await manager.send_to_user(
        contact_id,
        {
            "type": "contact:request_accepted",
            "payload": {
                "id": contact.id,
                "user_id": contact.user_id,
                "contact_id": contact.contact_id,
                "status": contact.status.value,
                "updated_at": contact.updated_at.isoformat()
            }
        }
    )
    
    await manager.send_to_user(
        current_user.id,
        {
            "type": "contact:request_accepted",
            "payload": {
                "id": contact.id,
                "user_id": contact.user_id,
                "contact_id": contact.contact_id,
                "status": contact.status.value,
                "updated_at": contact.updated_at.isoformat()
            }
        }
    )
    
    return contact


@router.post("/reject/{contact_id}")
async def api_reject_contact_request(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Reject a pending contact request.
    """
    result = reject_contact_request(
        user_id=current_user.id,
        contact_id=contact_id
    )
    
    # Notify the requester
    await manager.send_to_user(
        contact_id,
        {
            "type": "contact:request_rejected",
            "payload": {
                "contact_id": current_user.id,
                "username": current_user.username
            }
        }
    )
    
    return result


@router.delete("/remove/{contact_id}")
async def api_remove_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Remove an accepted contact.
    """
    result = remove_contact(
        user_id=current_user.id,
        contact_id=contact_id
    )
    
    # Notify the removed contact
    await manager.send_to_user(
        contact_id,
        {
            "type": "contact:removed",
            "payload": {
                "user_id": current_user.id,
                "username": current_user.username
            }
        }
    )
    
    return result


@router.post("/block/{contact_id}", response_model=ContactRead)
async def api_block_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Block a contact.
    """
    contact = block_contact(
        user_id=current_user.id,
        contact_id=contact_id
    )
    
    # Notify the blocked contact
    await manager.send_to_user(
        contact_id,
        {
            "type": "contact:blocked",
            "payload": {
                "user_id": current_user.id,
                "username": current_user.username
            }
        }
    )
    
    return contact


@router.post("/unblock/{contact_id}")
async def api_unblock_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Unblock a contact.
    """
    result = unblock_contact(
        user_id=current_user.id,
        contact_id=contact_id
    )
    
    return result


@router.get("/list", response_model=List[ContactWithUser])
async def api_get_contacts(
    status: Optional[str] = Query(None, description="Filter by status: accepted, pending, blocked"),
    current_user: User = Depends(get_current_user)
):
    """
    Get all contacts for the current user.
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
        status_filter=status_filter
    )
    
    return contacts


@router.get("/pending", response_model=List[ContactWithUser])
async def api_get_pending_requests(
    current_user: User = Depends(get_current_user)
):
    """
    Get all pending contact requests received by the current user.
    """
    requests = get_pending_requests(user_id=current_user.id)
    return requests


@router.get("/status/{contact_id}", response_model=Optional[ContactRead])
async def api_get_contact_status(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a contact relationship.
    Returns None if no relationship exists.
    """
    status = get_contact_status(
        user_id=current_user.id,
        contact_id=contact_id
    )
    return status

