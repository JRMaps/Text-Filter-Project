from datetime import datetime

# Mock databases
users_db = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

# INDEPDENDENT TABLE: A conversation exists because messages already exist
conversations_db = [
    {
        "id": 1,
        "participants": [1, 2],
        "last_message_id": 4, # points to the last message in messages_db
        "updated_at": "2024-01-01T10:03:00"
    }
]

# DEPENDENT TABLE: Messages belong to a conversation
messages_db = [
    {
        "id": 1,
        "conversation_id": 1,
        "content": "Hello, World!",
        "sender_id": 1,
        "receiver_id": 2,
        "timestamp": "2024-01-01T10:00:00"
    },
    {
        "id": 2,
        "conversation_id": 1,
        "content": "Hi there!",
        "sender_id": 2,
        "receiver_id": 1,
        "timestamp": "2024-01-01T10:01:00"
    },
    {
        "id": 3,
        "conversation_id": 1,
        "content": "How are you?",
        "sender_id": 1,
        "receiver_id": 2,
        "timestamp": "2024-01-01T10:02:00"
    },
    {
        "id": 4,
        "conversation_id": 1,
        "content": "I'm good, thanks!",
        "sender_id": 2,
        "receiver_id": 1,
        "timestamp": "2024-01-01T10:03:00"
    },
]

# ----------------- Helper Functions -----------------
def get_user_by_id(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


def get_message_by_id(message_id: int):
    for msg in messages_db:
        if msg["id"] == message_id:
            return msg
    return None


# ----------------- Core Functions -----------------

# DASHBOARD: Get All Conversations
# Returns a list of conversations with the last message and other user info
# This does NOT load messages, it only builds the chat list
def get_all_conversations(current_user_id: int):
    dashboard = []

    for convo in conversations_db:
        if current_user_id not in convo["participants"]:
            continue

        # find the other user
        other_user_id = next(
            uid for uid in convo["participants"] if uid != current_user_id
        )

        other_user = get_user_by_id(other_user_id)
        last_message = get_message_by_id(convo["last_message_id"])

        dashboard.append({
            "conversation_id": convo["id"],
            "other_user": {
                "id": other_user["id"],
                "name": other_user["name"]
            },
            "last_message": last_message["content"],
            "updated_at": convo["updated_at"]
        })

    # newest first
    dashboard.sort(key=lambda x: x["updated_at"], reverse=True)

    return dashboard


# OPEN CHAT: Get Messages by Conversation ID (Called only when user clicks a conversation)
def get_conversation_by_id(conversation_id: int, current_user_id: int):
    conversation = None

    for convo in conversations_db:
        if convo["id"] == conversation_id:
            conversation = convo
            break

    if not conversation:
        return {"error": "Conversation not found"}

    if current_user_id not in conversation["participants"]:
        return {"error": "Access denied"}

    messages = [
        msg for msg in messages_db
        if msg["conversation_id"] == conversation_id
    ]

    messages.sort(key=lambda x: x["timestamp"])

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }


# SEND MESSAGE: Send a message and update/create conversation summary
def send_message(conversation_id: int, sender_id: int, content: str):
    if not content.strip():
        return {"error": "Message cannot be empty"}

    conversation = None
    for convo in conversations_db:
        if convo["id"] == conversation_id:
            conversation = convo
            break

    if not conversation:
        return {"error": "Conversation not found"}

    if sender_id not in conversation["participants"]:
        return {"error": "Access denied"}

    receiver_id = next(
        uid for uid in conversation["participants"] if uid != sender_id
    )

    new_message_id = len(messages_db) + 1
    timestamp = datetime.now().isoformat()

    new_message = {
        "id": new_message_id,
        "conversation_id": conversation_id,
        "content": content,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "timestamp": timestamp
    }

    messages_db.append(new_message)

    # update conversation metadata
    conversation["last_message_id"] = new_message_id
    conversation["updated_at"] = timestamp

    return new_message


# ----------------- Example Usage -----------------
# Current authenticated user
current_user_id = 1

print("Dashboard - all conversations:")
dashboard = get_all_conversations(current_user_id)
print(dashboard)

# Assuming we want the conversation with Bob (conversation_id = 1)
conversation_id = 1

print("\nMessages in conversation with Bob:")
messages = get_conversation_by_id(conversation_id, current_user_id)
print(messages)

print("\nSend new message to Bob:")
new_msg = send_message(conversation_id, current_user_id, "Hey Bob, are you free?")
print(new_msg)

print("\nDashboard after sending new message:")
dashboard_after = get_all_conversations(current_user_id)
print(dashboard_after)

print("\nMessages in conversation with Bob after sending:")
messages_after = get_conversation_by_id(conversation_id, current_user_id)
print(messages_after)

