from fastapi import FastAPI
from backend.app.message import message_routes
from backend.app.auth import auth_routes
from backend.app.conversation import conversation_routes
from backend.app.database.database import create_tables
from backend.app.user import user_routes
from backend.app.contact import contact_routes
from backend.app.websocket import websocket_route

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(message_routes.router, prefix="/api/messages", tags=["messages"])
app.include_router(conversation_routes.router, prefix="/api", tags=["conversations"])
app.include_router(user_routes.router, prefix="/api/users", tags=["users"])
app.include_router(contact_routes.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(websocket_route.router, prefix="", tags=["websocket"])