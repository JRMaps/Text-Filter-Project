from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register(username: str, password: str):
    return {"message": f"User {username} registered"}

@router.post("/login")
async def login(username: str, password: str):
    return {"message": f"User {username} logged in"}


