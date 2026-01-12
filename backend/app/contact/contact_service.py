from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
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


def get_contacts(user_id: int, status_filter: Optional[ContactStatus], db: Session) -> List[ContactWithUser]:
    """
    Get all contacts for a user, including mutual contacts.
    """
    try:
        query = db.query(Contact).filter(
            or_(
                Contact.user_id == user_id,
                Contact.contact_id == user_id
            )
        )
        
        if status_filter:
            query = query.filter(Contact.status == status_filter)
        
        contacts = query.all()
        
        result = []
        for contact in contacts:
            # Determine the other user in the contact relationship
            other_user_id = contact.contact_id if contact.user_id == user_id else contact.user_id
            contact_user = db.query(User).filter(User.id == other_user_id).first()
            if contact_user:
                result.append(ContactWithUser(
                    id=contact.id,
                    contact_id=other_user_id,
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


def send_contact_request(user_id: int, contact_id: int, db: Session) -> ContactRead:
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


def accept_contact_request(user_id: int, contact_id: int, db: Session) -> ContactRead:
    """
    Accept a pending contact request.
    
    Args:
        user_id: ID of the user accepting the request
        contact_id: ID of the user who sent the request
        
    Returns:
        ContactRead: The updated contact
    """
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


def reject_contact_request(user_id: int, contact_id: int, db: Session) -> dict:
    """
    Reject a pending contact request (delete it).
    
    Args:
        user_id: ID of the user rejecting the request
        contact_id: ID of the user who sent the request
        
    Returns:
        dict: Success message
    """
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


def remove_contact(user_id: int, contact_id: int, db: Session) -> dict:
    """
    Remove an accepted contact.
    
    Args:
        user_id: ID of the user removing the contact
        contact_id: ID of the contact to remove
        
    Returns:
        dict: Success message
    """
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


def block_contact(user_id: int, contact_id: int, db: Session) -> ContactRead:
    """
    Block a contact and set the blocked_by_id field.
    """
    if user_id == contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself"
        )
    
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
            contact.status = ContactStatus.BLOCKED
            contact.blocked_by_id = user_id
            contact.updated_at = datetime.utcnow()
        else:
            # Create new blocked contact
            contact = Contact(
                user_id=user_id,
                contact_id=contact_id,
                status=ContactStatus.BLOCKED,
                blocked_by_id=user_id,
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


def unblock_contact(user_id: int, contact_id: int, db: Session) -> dict:
    """
    Unblock a contact (remove the blocked contact).
    
    Args:
        user_id: ID of the user unblocking
        contact_id: ID of the user to unblock
        
    Returns:
        dict: Success message
    """
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

