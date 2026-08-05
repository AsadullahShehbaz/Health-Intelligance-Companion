from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.chat_service import stream_chat

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/stream")
async def stream(req: ChatRequest):

    messages = [
        message.model_dump()
        for message in req.messages
    ]

    return StreamingResponse(
        stream_chat(
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ),
        media_type="text/plain",
    )