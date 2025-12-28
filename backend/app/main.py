from fastapi import FastAPI
from backend.app.message.routes import message_routes
from backend.app.auth.routes import auth_routes
from backend.app.conversation.routes import conversation_routes
from backend.app.database.database import create_tables
from backend.app.user.routes import user_routes

app = FastAPI()

# Create tables on application startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# test
@app.get("/")
async def get_app():
    return {"message": "Hello, World!"}

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(message_routes.router, prefix="/api/messages", tags=["messages"])
app.include_router(conversation_routes.router, prefix="/api", tags=["conversations"])
app.include_router(user_routes.router, prefix="/api/users", tags=["users"])