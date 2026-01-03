from fastapi import WebSocket, WebSocketDisconnect
from backend.app.websocket.connection_manager import manager
from backend.app.websocket.ws_auth import get_user_from_websocket
from backend.app.websocket.ws_helpers import get_user_contact_ids
from backend.app.database.database import SessionLocal
from backend.app.message.message_service import send_message
from backend.app.message.message_model import Message, DeliveryStatus as ModelDeliveryStatus
from backend.app.conversation.conversation_model import Conversation
from datetime import datetime

async def ws_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat features.
    
    Events handled:
    - send a new message
    - update the conversation dashboard
    - message status updates (sent/delivered/read)
    - active status updates (online/offline)
    - user:ping - Keep connection alive (optional)
    """
    # Authenticate user
    try:
        current_user = await get_user_from_websocket(websocket)
    except Exception:
        return 
    
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
                
                try:
                    message = send_message(
                        sender_id=current_user.id,
                        receiver_id=receiver_id,
                        content=content
                    )

                    # Get conversation details for dashboard update
                    db = SessionLocal()
                    try:
                        conversation = db.query(Conversation).filter(
                            Conversation.id == message.conversation_id
                        ).first()
                        
                        # Build dashboard update payload
                        dashboard_update = {
                            "type": "conversation:dashboard:update",
                            "payload": {
                                "conversation_id": message.conversation_id,
                                "last_message": message.content,
                                "updated_at": conversation.updated_at.isoformat() if conversation else datetime.utcnow().isoformat()
                            }
                        }
                    finally:
                        db.close()

                    # Broadcast to conversation participants
                    participant_ids = [current_user.id, receiver_id]
                    
                    # Send new message event
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
                    
                    # Send dashboard update event to all participants
                    await manager.send_to_conversation(
                        participant_ids=participant_ids,
                        payload=dashboard_update
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
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Disconnect user and broadcast offline status
        status_changed = manager.disconnect(current_user.id, websocket)
        if status_changed:
            await manager.broadcast_online_status(
                user_id=current_user.id,
                is_online=False,
                contact_ids=list(contact_ids)
            )
