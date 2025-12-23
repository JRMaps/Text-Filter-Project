from fastapi import FastAPI
from app.api.routes import auth_routes, message_routes

app = FastAPI()

# test
@app.get("/")
async def get_app():
    return {"message": "Hello, World!"}

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(message_routes.router, prefix="/messages", tags=["messages"])