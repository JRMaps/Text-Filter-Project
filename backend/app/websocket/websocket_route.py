from fastapi import WebSocket, WebSocketDisconnect
from backend.app.websocket.connection_manager import manager
from backend.app.websocket.ws_auth import get_user_from_websocket
from backend.app.websocket.ws_helpers import get_user_contact_ids
from backend.app.database.database import SessionLocal
from backend.app.message.message_service import send_message
from backend.app.message.message_model import Message
from backend.app.message.message_receipt_model import MessageReceipt, DeliveryStatus as ReceiptDeliveryStatus
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
                conversation_id = payload.get("conversation_id")
                content = payload.get("content")
                
                if not conversation_id or not content:
                    await websocket.send_json({
                        "type": "error",
                        "payload": {"message": "conversation_id and content are required"}
                    })
                    continue
                
                try:
                    message = send_message(
                        sender_id=current_user.id,
                        conversation_id=conversation_id,
                        content=content
                    )

                    # Get conversation details for dashboard update
                    db = SessionLocal()
                    try:
                        conversation = db.query(Conversation).filter(
                            Conversation.id == message.conversation_id
                        ).first()
                        
                        if not conversation:
                            await websocket.send_json({
                                "type": "error",
                                "payload": {"message": "Conversation not found"}
                            })
                            continue
                        
                        # Get participant IDs
                        participant_ids = [p.id for p in conversation.participants]
                        
                        # Get receipts for the message
                        receipts = db.query(MessageReceipt).filter(
                            MessageReceipt.message_id == message.id
                        ).all()
                        
                        receipt_data = [
                            {
                                "user_id": receipt.user_id,
                                "delivery_status": receipt.delivery_status.value,
                                "delivered_at": receipt.delivered_at.isoformat() if receipt.delivered_at else None,
                                "read_at": receipt.read_at.isoformat() if receipt.read_at else None
                            }
                            for receipt in receipts
                        ]
                        
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

                    # Send new message event to all participants
                    await manager.send_to_conversation(
                        participant_ids=participant_ids,
                        payload={
                            "type": "message:new",
                            "payload": {
                                "id": message.id,
                                "conversation_id": message.conversation_id,
                                "sender_id": message.sender_id,
                                "content": message.content,
                                "status": message.status.value,
                                "receipts": receipt_data,
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
                    
                    # Get receipt for current user
                    receipt = db.query(MessageReceipt).filter(
                        MessageReceipt.message_id == message_id,
                        MessageReceipt.user_id == current_user.id
                    ).first()
                    
                    if not receipt:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Receipt not found or unauthorized"}
                        })
                        continue
                    
                    # Update delivery status
                    if receipt.delivery_status != ReceiptDeliveryStatus.DELIVERED:
                        receipt.delivery_status = ReceiptDeliveryStatus.DELIVERED
                        receipt.delivered_at = datetime.utcnow()
                        db.commit()
                        
                        # Get conversation participants
                        conversation = db.query(Conversation).filter(
                            Conversation.id == message.conversation_id
                        ).first()
                        
                        if conversation:
                            participant_ids = [p.id for p in conversation.participants]
                            
                            # Notify all participants about delivery status update
                            await manager.send_to_conversation(
                                participant_ids=participant_ids,
                                payload={
                                    "type": "message:delivery_status",
                                    "payload": {
                                        "message_id": message.id,
                                        "user_id": current_user.id,
                                        "delivery_status": "delivered",
                                        "timestamp": receipt.delivered_at.isoformat()
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
                    
                    # Get receipt for current user
                    receipt = db.query(MessageReceipt).filter(
                        MessageReceipt.message_id == message_id,
                        MessageReceipt.user_id == current_user.id
                    ).first()
                    
                    if not receipt:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Receipt not found or unauthorized"}
                        })
                        continue
                    
                    # Update delivery status
                    if receipt.delivery_status != ReceiptDeliveryStatus.READ:
                        receipt.delivery_status = ReceiptDeliveryStatus.READ
                        receipt.read_at = datetime.utcnow()
                        # Also update delivered_at if not already set
                        if not receipt.delivered_at:
                            receipt.delivered_at = receipt.read_at
                        db.commit()
                        
                        # Get conversation participants
                        conversation = db.query(Conversation).filter(
                            Conversation.id == message.conversation_id
                        ).first()
                        
                        if conversation:
                            participant_ids = [p.id for p in conversation.participants]
                            
                            # Notify all participants about read status update
                            await manager.send_to_conversation(
                                participant_ids=participant_ids,
                                payload={
                                    "type": "message:delivery_status",
                                    "payload": {
                                        "message_id": message.id,
                                        "user_id": current_user.id,
                                        "delivery_status": "read",
                                        "timestamp": receipt.read_at.isoformat()
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
