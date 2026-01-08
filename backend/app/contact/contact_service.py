from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from typing import List, Optional
from backend.app.database.database import SessionLocal
from backend.app.user.user_model import User
from backend.app.contact.contact_model import Contact, ContactStatus
from backend.app.contact.contact_shema import (
    ContactRead, 
    ContactWithUser, 
    ContactStatus as SchemaContactStatus
)
from backend.app.user.user_schema import UserRead


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def send_contact_request(user_id: int, contact_id: int) -> ContactRead:
    """
    Send a contact request to another user.
    
    Args:
        user_id: ID of the user sending the request
        contact_id: ID of the user to contact
        
    Returns:
        ContactRead: The created contact request
    """
    if user_id == contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send contact request to yourself"
        )
    
    db = SessionLocal()
    try:
        # Verify both users exist
        user = db.query(User).filter(User.id == user_id).first()
        contact_user = db.query(User).filter(User.id == contact_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not contact_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact user not found"
            )
        
        # Check if contact relationship already exists
        existing_contact = db.query(Contact).filter(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_id == contact_id),
                and_(Contact.user_id == contact_id, Contact.contact_id == user_id)
            )
        ).first()
        
        if existing_contact:
            if existing_contact.status == ContactStatus.BLOCKED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot send request. Contact is blocked."
                )
            elif existing_contact.status == ContactStatus.ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contact already exists"
                )
            elif existing_contact.user_id == user_id and existing_contact.status == ContactStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contact request already sent"
                )
            elif existing_contact.user_id == contact_id and existing_contact.status == ContactStatus.PENDING:
                # If the other user sent a request, accept it
                existing_contact.status = ContactStatus.ACCEPTED
                existing_contact.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing_contact)
                
                return ContactRead(
                    id=existing_contact.id,
                    user_id=existing_contact.user_id,
                    contact_id=existing_contact.contact_id,
                    status=SchemaContactStatus.accepted,
                    created_at=existing_contact.created_at,
                    updated_at=existing_contact.updated_at
                )
        
        # Create new contact request
        new_contact = Contact(
            user_id=user_id,
            contact_id=contact_id,
            status=ContactStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        return ContactRead(
            id=new_contact.id,
            user_id=new_contact.user_id,
            contact_id=new_contact.contact_id,
            status=SchemaContactStatus.pending,
            created_at=new_contact.created_at,
            updated_at=new_contact.updated_at
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending contact request: {str(e)}"
        )
    finally:
        db.close()


def accept_contact_request(user_id: int, contact_id: int) -> ContactRead:
    """
    Accept a pending contact request.
    
    Args:
        user_id: ID of the user accepting the request
        contact_id: ID of the user who sent the request
        
    Returns:
        ContactRead: The updated contact
    """
    db = SessionLocal()
    try:
        # Find the pending request (contact_id sent to user_id)
        contact = db.query(Contact).filter(
            Contact.user_id == contact_id,
            Contact.contact_id == user_id,
            Contact.status == ContactStatus.PENDING
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact request not found"
            )
        
        contact.status = ContactStatus.ACCEPTED
        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)
        
        return ContactRead(
            id=contact.id,
            user_id=contact.user_id,
            contact_id=contact.contact_id,
            status=SchemaContactStatus.accepted,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accepting contact request: {str(e)}"
        )
    finally:
        db.close()


def reject_contact_request(user_id: int, contact_id: int) -> dict:
    """
    Reject a pending contact request (delete it).
    
    Args:
        user_id: ID of the user rejecting the request
        contact_id: ID of the user who sent the request
        
    Returns:
        dict: Success message
    """
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(
            Contact.user_id == contact_id,
            Contact.contact_id == user_id,
            Contact.status == ContactStatus.PENDING
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact request not found"
            )
        
        db.delete(contact)
        db.commit()
        
        return {"message": "Contact request rejected"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting contact request: {str(e)}"
        )
    finally:
        db.close()


def remove_contact(user_id: int, contact_id: int) -> dict:
    """
    Remove an accepted contact.
    
    Args:
        user_id: ID of the user removing the contact
        contact_id: ID of the contact to remove
        
    Returns:
        dict: Success message
    """
    db = SessionLocal()
    try:
        # Find contact relationship (bidirectional)
        contact = db.query(Contact).filter(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_id == contact_id),
                and_(Contact.user_id == contact_id, Contact.contact_id == user_id)
            ),
            Contact.status == ContactStatus.ACCEPTED
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        db.delete(contact)
        db.commit()
        
        return {"message": "Contact removed"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing contact: {str(e)}"
        )
    finally:
        db.close()


def block_contact(user_id: int, contact_id: int) -> ContactRead:
    """
    Block a contact.
    
    Args:
        user_id: ID of the user blocking
        contact_id: ID of the user to block
        
    Returns:
        ContactRead: The updated contact
    """
    if user_id == contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself"
        )
    
    db = SessionLocal()
    try:
        # Check if contact relationship exists
        contact = db.query(Contact).filter(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_id == contact_id),
                and_(Contact.user_id == contact_id, Contact.contact_id == user_id)
            )
        ).first()
        
        if contact:
            # Update existing contact to blocked
            # Always set user_id as the blocker
            if contact.user_id != user_id:
                # Swap the relationship
                contact.user_id, contact.contact_id = contact.contact_id, contact.user_id
            
            contact.status = ContactStatus.BLOCKED
            contact.updated_at = datetime.utcnow()
        else:
            # Create new blocked contact
            contact = Contact(
                user_id=user_id,
                contact_id=contact_id,
                status=ContactStatus.BLOCKED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(contact)
        
        db.commit()
        db.refresh(contact)
        
        return ContactRead(
            id=contact.id,
            user_id=contact.user_id,
            contact_id=contact.contact_id,
            status=SchemaContactStatus.blocked,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error blocking contact: {str(e)}"
        )
    finally:
        db.close()


def unblock_contact(user_id: int, contact_id: int) -> dict:
    """
    Unblock a contact (remove the blocked contact).
    
    Args:
        user_id: ID of the user unblocking
        contact_id: ID of the user to unblock
        
    Returns:
        dict: Success message
    """
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(
            Contact.user_id == user_id,
            Contact.contact_id == contact_id,
            Contact.status == ContactStatus.BLOCKED
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blocked contact not found"
            )
        
        db.delete(contact)
        db.commit()
        
        return {"message": "Contact unblocked"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unblocking contact: {str(e)}"
        )
    finally:
        db.close()


def get_contacts(user_id: int, status_filter: Optional[ContactStatus] = None) -> List[ContactWithUser]:
    """
    Get all contacts for a user.
    
    Args:
        user_id: ID of the user
        status_filter: Optional status filter (ACCEPTED, PENDING, BLOCKED)
        
    Returns:
        List of contacts with user information
    """
    db = SessionLocal()
    try:
        query = db.query(Contact).filter(
            Contact.user_id == user_id
        )
        
        if status_filter:
            query = query.filter(Contact.status == status_filter)
        
        contacts = query.all()
        
        result = []
        for contact in contacts:
            contact_user = db.query(User).filter(User.id == contact.contact_id).first()
            if contact_user:
                result.append(ContactWithUser(
                    id=contact.id,
                    contact_id=contact.contact_id,
                    contact=UserRead(
                        id=contact_user.id,
                        username=contact_user.username,
                        email=contact_user.email
                    ),
                    status=SchemaContactStatus(contact.status.value),
                    created_at=contact.created_at,
                    updated_at=contact.updated_at
                ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching contacts: {str(e)}"
        )
    finally:
        db.close()


def get_pending_requests(user_id: int) -> List[ContactWithUser]:
    """
    Get all pending contact requests received by a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of pending contact requests
    """
    db = SessionLocal()
    try:
        # Get requests where user_id is the contact (requests sent TO this user)
        contacts = db.query(Contact).filter(
            Contact.contact_id == user_id,
            Contact.status == ContactStatus.PENDING
        ).all()
        
        result = []
        for contact in contacts:
            contact_user = db.query(User).filter(User.id == contact.user_id).first()
            if contact_user:
                result.append(ContactWithUser(
                    id=contact.id,
                    contact_id=contact.user_id,  # The requester
                    contact=UserRead(
                        id=contact_user.id,
                        username=contact_user.username,
                        email=contact_user.email
                    ),
                    status=SchemaContactStatus.pending,
                    created_at=contact.created_at,
                    updated_at=contact.updated_at
                ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pending requests: {str(e)}"
        )
    finally:
        db.close()


def get_contact_status(user_id: int, contact_id: int) -> Optional[ContactRead]:
    """
    Get the status of a contact relationship.
    
    Args:
        user_id: ID of the user
        contact_id: ID of the contact
        
    Returns:
        ContactRead or None if no relationship exists
    """
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_id == contact_id),
                and_(Contact.user_id == contact_id, Contact.contact_id == user_id)
            )
        ).first()
        
        if not contact:
            return None
        
        return ContactRead(
            id=contact.id,
            user_id=contact.user_id,
            contact_id=contact.contact_id,
            status=SchemaContactStatus(contact.status.value),
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    finally:
        db.close()

