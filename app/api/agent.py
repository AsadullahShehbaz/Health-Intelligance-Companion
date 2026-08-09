# app/api/agent.py
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from app.deps import get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    ConversationDetail,
    ConversationMeta,
)
from app.services.agent_service import run_agent
from app.services.conversation_service import get_conversation, list_conversations

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest):
    try:
        return await run_agent(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads", response_model=list[ConversationMeta])
async def list_threads(user: User = Depends(get_current_user)):
    """Sidebar rows: every conversation the current patient has started,
    newest first. Reads turn-end checkpoints — no separate storage layer."""
    return await run_in_threadpool(list_conversations, str(user.id))


@router.get("/threads/{thread_id}", response_model=ConversationDetail)
async def load_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Full transcript of one conversation, restored from its checkpoints.
    Ownership is enforced by the patient_id stored inside the state."""
    conversation = await run_in_threadpool(get_conversation, thread_id, str(user.id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation