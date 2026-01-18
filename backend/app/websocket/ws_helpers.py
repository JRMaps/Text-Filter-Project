from typing import List, Set
from backend.app.database.database import SessionLocal
from backend.app.contact.contact_model import Contact, ContactStatus

def get_user_contact_ids(user_id: int) -> Set[int]:
    """
    Get all user IDs that the given user has accepted contacts with.
    This is used to broadcast online/offline status to relevant users.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Set of user IDs that are accepted contacts with this user
    """
    db = SessionLocal()
    try:
        contact_ids: Set[int] = set()
        
        # Get all accepted contacts where user is the requester
        contacts_as_user = db.query(Contact).filter(
            Contact.user_id == user_id,
            Contact.status == ContactStatus.ACCEPTED
        ).all()
        for contact in contacts_as_user:
            contact_ids.add(contact.contact_id)
        
        # Get all accepted contacts where user is the contact
        contacts_as_contact = db.query(Contact).filter(
            Contact.contact_id == user_id,
            Contact.status == ContactStatus.ACCEPTED
        ).all()
        for contact in contacts_as_contact:
            contact_ids.add(contact.user_id)
        
        return contact_ids
    finally:
        db.close()

