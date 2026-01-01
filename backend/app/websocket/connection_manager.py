from typing import Dict, Set, List
from fastapi import WebSocket
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Map user_id -> Set of WebSocket connections
        self.active_users: Dict[int, Set[WebSocket]] = {}
        # Track which users are online (have at least one active connection)
        self.online_users: Set[int] = set()

    async def connect(self, user_id: int, websocket: WebSocket):
        """Connect a user and mark them as online."""
        await websocket.accept()
        was_offline = user_id not in self.online_users
        self.active_users.setdefault(user_id, set()).add(websocket)
        self.online_users.add(user_id)
        
        # If user just came online, broadcast to their contacts
        if was_offline:
            return True  # Return True to indicate status change
        return False

    def disconnect(self, user_id: int, websocket: WebSocket):
        """Disconnect a user and mark offline if no more connections."""
        if user_id in self.active_users:
            self.active_users[user_id].discard(websocket)
            if not self.active_users[user_id]:
                del self.active_users[user_id]
                self.online_users.discard(user_id)
                return True  # Return True to indicate status change
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

    async def send_to_conversation(self, participant_ids: List[int], payload: dict, exclude_user_id: int = None):
        """Send a message to all participants in a conversation."""
        for uid in participant_ids:
            if exclude_user_id is None or uid != exclude_user_id:
                await self.send_to_user(uid, payload)

    async def broadcast_online_status(self, user_id: int, is_online: bool, contact_ids: List[int]):
        """Broadcast a user's online/offline status to their contacts."""
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

    def is_user_online(self, user_id: int) -> bool:
        """Check if a user is currently online."""
        return user_id in self.online_users

    def get_online_users(self) -> Set[int]:
        """Get set of all online user IDs."""
        return self.online_users.copy()


# Global instance shared across the application
manager = ConnectionManager()
