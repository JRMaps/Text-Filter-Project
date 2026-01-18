from fastapi import APIRouter
from app.api.controllers import message_controller

router = APIRouter()

@router.get("/")
async def get_messages():
    return message_controller.get_all_messages()

@router.post("/")
async def create_message(content: str):
    return message_controller.create_message(content)

