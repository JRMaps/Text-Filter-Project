from fastapi import WebSocket, WebSocketDisconnect
from backend.app.websocket.connection_manager import manager
from backend.app.websocket.ws_auth import get_user_from_websocket
from backend.app.websocket.ws_helpers import get_user_contact_ids
from backend.app.database.database import SessionLocal
from backend.app.message.message_service import send_message
from backend.app.message.message_schema import MessageRead, DeliveryStatus
from backend.app.conversation.conversation_service import get_all_conversations
from backend.app.conversation.conversation_schema import ConversationDashboardItem
from backend.app.message.message_model import Message, DeliveryStatus as ModelDeliveryStatus
from backend.app.contact.contact_service import (
    send_contact_request,
    accept_contact_request,
    reject_contact_request,
    remove_contact,
    block_contact
)
from datetime import datetime

async def ws_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat features.
    
    Events handled:
    - message:new - Send a new message
    - message:mark_delivered - Mark message as delivered
    - message:mark_read - Mark message as read
    - contact:send_request - Send a contact request
    - contact:accept - Accept a contact request
    - contact:reject - Reject a contact request
    - contact:remove - Remove a contact
    - contact:block - Block a contact
    - user:ping - Keep connection alive (optional)
    """
    # Authenticate user
    try:
        current_user = await get_user_from_websocket(websocket)
    except Exception as e:
        return  # Connection already closed by auth function
    
    # Connect user and check if status changed
    status_changed = await manager.connect(current_user.id, websocket)
    
    # Get user's contacts for broadcasting status
    contact_ids = get_user_contact_ids(current_user.id)
    
    # Broadcast online status to contacts if user just came online
    if status_changed:
        await manager.broadcast_online_status(
            user_id=current_user.id,
            is_online=True,
            contact_ids=list(contact_ids)
        )

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("type")
            payload = data.get("payload", {})

            if event == "message:new":
                # Send a new message
                receiver_id = payload.get("receiver_id")
                content = payload.get("content")
                
                if not receiver_id or not content:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "receiver_id and content are required"}
                    })
                    continue
                
                # Send message using service
                try:
                    message = send_message(
                    sender_id=current_user.id,
                        receiver_id=receiver_id,
                        content=content
                )

                    # Broadcast to conversation participants
                    participant_ids = [current_user.id, receiver_id]
                await manager.send_to_conversation(
                        participant_ids=participant_ids,
                        payload={
                        "type": "message:new",
                        "payload": {
                            "id": message.id,
                            "conversation_id": message.conversation_id,
                                "sender_id": message.sender_id,
                                "receiver_id": message.receiver_id,
                                "content": message.content,
                                "status": message.status.value,
                                "delivery_status": message.delivery_status.value,
                                "created_at": message.created_at.isoformat()
                            }
                        }
                    )
                    
                    # Broadcast dashboard update to both participants
                    await manager.send_to_conversation(
                        participant_ids=participant_ids,
                        payload={
                            "type": "conversation:dashboard_update",
                            "payload": {
                                "conversation_id": message.conversation_id,
                                "last_message_id": message.id,
                                "updated_at": message.created_at.isoformat()
                            }
                        }
                    )
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "message:mark_delivered":
                # Mark message as delivered
                message_id = payload.get("message_id")
                if not message_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "message_id is required"}
                    })
                    continue
                
                db = SessionLocal()
                try:
                    message = db.query(Message).filter(Message.id == message_id).first()
                    if not message:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Message not found"}
                        })
                        continue
                    
                    # Only receiver can mark as delivered
                    if message.receiver_id != current_user.id:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Unauthorized"}
                        })
                        continue
                    
                    # Update delivery status
                    if message.delivery_status != ModelDeliveryStatus.DELIVERED:
                        message.delivery_status = ModelDeliveryStatus.DELIVERED
                        db.commit()
                        
                        # Notify sender
                        await manager.send_to_user(
                            message.sender_id,
                            {
                                "type": "message:delivery_status",
                                "payload": {
                                    "message_id": message.id,
                                    "delivery_status": "delivered",
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                finally:
                    db.close()
            
            elif event == "message:mark_read":
                # Mark message as read
                message_id = payload.get("message_id")
                if not message_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "message_id is required"}
                    })
                    continue
                
                db = SessionLocal()
                try:
                    message = db.query(Message).filter(Message.id == message_id).first()
                    if not message:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Message not found"}
                        })
                        continue
                    
                    # Only receiver can mark as read
                    if message.receiver_id != current_user.id:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Unauthorized"}
                        })
                        continue
                    
                    # Update delivery status
                    if message.delivery_status != ModelDeliveryStatus.READ:
                        message.delivery_status = ModelDeliveryStatus.READ
                        db.commit()
                        
                        # Notify sender
                        await manager.send_to_user(
                            message.sender_id,
                            {
                                "type": "message:delivery_status",
                                "payload": {
                                    "message_id": message.id,
                                    "delivery_status": "read",
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                        )
                finally:
                    db.close()
            
            elif event == "contact:send_request":
                # Send a contact request
                contact_id = payload.get("contact_id")
                if not contact_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "contact_id is required"}
                    })
                    continue
                
                try:
                    contact = send_contact_request(
                        user_id=current_user.id,
                        contact_id=contact_id
                    )
                    
                    # Notify the contact
                    await manager.send_to_user(
                        contact_id,
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
                    
                    # Confirm to sender
                    await websocket.send_json({
                        "type": "contact:request_sent",
                        "payload": {
                            "id": contact.id,
                            "contact_id": contact.contact_id,
                            "status": contact.status.value,
                            "created_at": contact.created_at.isoformat()
                        }
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "contact:accept":
                # Accept a contact request
                contact_id = payload.get("contact_id")
                if not contact_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "contact_id is required"}
                    })
                    continue
                
                try:
                    contact = accept_contact_request(
                        user_id=current_user.id,
                        contact_id=contact_id
                    )
                    
                    # Notify both users
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
                    
                    await websocket.send_json({
                        "type": "contact:request_accepted",
                        "payload": {
                            "id": contact.id,
                            "contact_id": contact_id,
                            "status": contact.status.value,
                            "updated_at": contact.updated_at.isoformat()
                        }
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "contact:reject":
                # Reject a contact request
                contact_id = payload.get("contact_id")
                if not contact_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "contact_id is required"}
                    })
                    continue
                
                try:
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
                    
                    await websocket.send_json({
                        "type": "contact:request_rejected",
                        "payload": result
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "contact:remove":
                # Remove a contact
                contact_id = payload.get("contact_id")
                if not contact_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "contact_id is required"}
                    })
                    continue
                
                try:
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
                    
                    await websocket.send_json({
                        "type": "contact:removed",
                        "payload": result
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "contact:block":
                # Block a contact
                contact_id = payload.get("contact_id")
                if not contact_id:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "contact_id is required"}
                    })
                    continue
                
                try:
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
                    
                    await websocket.send_json({
                        "type": "contact:blocked",
                        "payload": {
                            "id": contact.id,
                            "contact_id": contact.contact_id,
                            "status": contact.status.value,
                            "updated_at": contact.updated_at.isoformat()
                        }
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": str(e)}
                    })
            
            elif event == "user:ping":
                # Keep-alive ping
                await websocket.send_json({
                    "type": "user:pong",
                    "payload": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "payload": {"message": f"Unknown event type: {event}"}
                })
    
    except WebSocketDisconnect:
        # User disconnected
        pass
    except Exception as e:
        # Handle other errors
        print(f"WebSocket error: {e}")
    finally:
        # Disconnect user and broadcast offline status if needed
        status_changed = manager.disconnect(current_user.id, websocket)
        if status_changed:
            await manager.broadcast_online_status(
                user_id=current_user.id,
                is_online=False,
                contact_ids=list(contact_ids)
            )
