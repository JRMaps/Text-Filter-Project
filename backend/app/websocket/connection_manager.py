from typing import Dict, Set, List, Optional
from fastapi import WebSocket
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Map user_id -> Set of WebSocket connections
        self.active_users: Dict[int, Set[WebSocket]] = {}
        # Track which users are online (have at least one active connection)
        self.online_users: Set[int] = set()

    async def connect(self, user_id: int, websocket: WebSocket) -> bool:
        """
        Connect a user and mark them as online.
        
        Returns:
            bool: True if user just came online, False if already online
        """
        await websocket.accept()
        was_offline = user_id not in self.online_users
        self.active_users.setdefault(user_id, set()).add(websocket)
        self.online_users.add(user_id)
        
        return was_offline

    def disconnect(self, user_id: int, websocket: WebSocket) -> bool:
        """
        Disconnect a user and mark offline if no more connections.
        
        Returns:
            bool: True if user went offline, False if still has other connections
        """
        if user_id in self.active_users:
            self.active_users[user_id].discard(websocket)
            if not self.active_users[user_id]:
                del self.active_users[user_id]
                self.online_users.discard(user_id)
                return True
        return False

    async def send_to_user(self, user_id: int, payload: dict):
        """Send a message to all WebSocket connections of a user."""
        if user_id in self.active_users:
            disconnected = []
            for ws in self.active_users[user_id]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    # Connection is dead, mark for removal
                    disconnected.append(ws)
            
            # Remove dead connections
            for ws in disconnected:
                self.active_users[user_id].discard(ws)
            
            # If no more connections, mark offline
            if user_id in self.active_users and not self.active_users[user_id]:
                del self.active_users[user_id]
                self.online_users.discard(user_id)

    async def send_to_conversation(
        self, 
        participant_ids: List[int], 
        payload: dict, 
        exclude_user_id: Optional[int] = None
    ):
        """
        Send a message to all participants in a conversation.
        
        Args:
            participant_ids: List of user IDs in the conversation
            payload: Data to send
            exclude_user_id: Optional user ID to exclude from broadcast
        """
        for uid in participant_ids:
            if exclude_user_id is None or uid != exclude_user_id:
                await self.send_to_user(uid, payload)

    # ========================================================================
    # SPECIALIZED BROADCAST METHODS
    # ========================================================================

    async def broadcast_new_message(
        self,
        participant_ids: List[int],
        message_data: dict
    ):
        """
        Broadcast a new message to all conversation participants.
        
        Args:
            participant_ids: List of user IDs in the conversation
            message_data: Message data including:
                - id: Message ID
                - conversation_id: Conversation ID
                - sender_id: Sender user ID
                - content: Message content
                - status: Moderation status
                - created_at: Timestamp
                - receipts: List of receipt data
        """
        payload = {
            "type": "message:new",
            "payload": message_data
        }
        await self.send_to_conversation(participant_ids, payload)

    async def broadcast_dashboard_update(
        self,
        participant_ids: List[int],
        conversation_id: int,
        last_message: str,
        updated_at: str
    ):
        """
        Broadcast conversation dashboard update to all participants.
        This updates the conversation list preview.
        
        Args:
            participant_ids: List of user IDs in the conversation
            conversation_id: ID of the conversation
            last_message: Preview of the last message
            updated_at: Timestamp of last update
        """
        payload = {
            "type": "conversation:dashboard:update",
            "payload": {
                "conversation_id": conversation_id,
                "last_message": last_message,
                "updated_at": updated_at
            }
        }
        await self.send_to_conversation(participant_ids, payload)

    async def broadcast_receipt_status(
        self,
        participant_ids: List[int],
        message_id: int,
        user_id: int,
        delivery_status: str,
        timestamp: str
    ):
        """
        Broadcast message receipt status update (delivered/read).
        
        Args:
            participant_ids: List of user IDs in the conversation
            message_id: ID of the message
            user_id: User who updated the status
            delivery_status: "sent", "delivered", or "read"
            timestamp: When the status was updated
        """
        payload = {
            "type": "message:delivery_status",
            "payload": {
                "message_id": message_id,
                "user_id": user_id,
                "delivery_status": delivery_status,
                "timestamp": timestamp
            }
        }
        await self.send_to_conversation(participant_ids, payload)

    async def broadcast_online_status(
        self,
        user_id: int,
        is_online: bool,
        contact_ids: List[int]
    ):
        """
        Broadcast a user's online/offline status to their contacts.
        
        Args:
            user_id: User whose status changed
            is_online: True if online, False if offline
            contact_ids: List of contact user IDs to notify
        """
        payload = {
            "type": "user:status",
            "payload": {
                "user_id": user_id,
                "is_online": is_online,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        for contact_id in contact_ids:
            await self.send_to_user(contact_id, payload)

    async def send_error(self, user_id: int, error_message: str, error_code: Optional[str] = None):
        """
        Send error message to a specific user.
        
        Args:
            user_id: User to send error to
            error_message: Error message
            error_code: Optional error code for client handling
        """
        payload = {
            "type": "error",
            "payload": {
                "message": error_message,
                "code": error_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.send_to_user(user_id, payload)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def is_user_online(self, user_id: int) -> bool:
        """Check if a user is currently online."""
        return user_id in self.online_users

    def get_online_users(self) -> Set[int]:
        """Get set of all online user IDs."""
        return self.online_users.copy()

    def get_online_status_for_users(self, user_ids: List[int]) -> Dict[int, bool]:
        """
        Get online status for multiple users.
        
        Args:
            user_ids: List of user IDs to check
            
        Returns:
            Dict mapping user_id to online status (True/False)
        """
        return {
            user_id: user_id in self.online_users 
            for user_id in user_ids
        }

    def get_active_connection_count(self, user_id: int) -> int:
        """
        Get number of active connections for a user.
        Useful for checking if user has multiple devices connected.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Number of active WebSocket connections
        """
        if user_id in self.active_users:
            return len(self.active_users[user_id])
        return 0


# Global instance shared across the application
manager = ConnectionManager()