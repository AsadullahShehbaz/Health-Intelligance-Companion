# app/api/agent.py
import time

import httpx
from fastapi import APIRouter, Depends, HTTPException
from openai import APIConnectionError
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.deps import get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    ConversationDetail,
    ConversationMeta,
)
from app.core.rag.ocr import extract_text_from_base64
from app.services.agent_service import run_agent
from app.services.conversation_service import get_conversation, list_conversations
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest,user: User = Depends(get_current_user)):
    if req.patient_id != str(user.id):
        raise HTTPException(403, "Cannot act on another patient's record")
    start = time.monotonic()
    logger.info(
        "▶ POST /agent/invoke | patient=%s | thread=%s | OCR=%s",
        req.patient_id,
        req.thread_id or "(default)",
        "yes" if req.image_base64 else "no",
    )
    try:
        ocr_text = ""
        if req.image_base64:
            ocr_text = extract_text_from_base64(req.image_base64)
            logger.info("OCR extraction completed | chars=%d", len(ocr_text))
        result = await run_agent(req, ocr_text)
        logger.info(
            "✓ POST /agent/invoke completed in %.2fs | patient=%s",
            time.monotonic() - start,
            req.patient_id,
        )
        return result
    except (APIConnectionError, httpx.ConnectError, httpx.HTTPError) as e:
        logger.exception(
            "✗ POST /agent/invoke failed because the LLM backend is unavailable after %.2fs | patient=%s",
            time.monotonic() - start,
            req.patient_id,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "LLM backend unavailable. Start the local model server or fix "
                f"LLM_BASE_URL={settings.LLM_BASE_URL}."
            ),
        ) from e
    except Exception as e:
        logger.exception(
            "✗ POST /agent/invoke failed after %.2fs | patient=%s",
            time.monotonic() - start,
            req.patient_id,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads", response_model=list[ConversationMeta])
async def list_threads(user: User = Depends(get_current_user)):
    """Sidebar rows: every conversation the current patient has started,
    newest first. Reads turn-end checkpoints — no separate storage layer."""
    start = time.monotonic()
    logger.info("▶ GET /agent/threads | user=%s", str(user.id))
    conversations = await run_in_threadpool(list_conversations, str(user.id))
    logger.info(
        "✓ GET /agent/threads returned %d conversations in %.2fs | user=%s",
        len(conversations),
        time.monotonic() - start,
        str(user.id),
    )
    return conversations


@router.get("/threads/{thread_id}", response_model=ConversationDetail)
async def load_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Full transcript of one conversation, restored from its checkpoints.
    Ownership is enforced by the patient_id stored inside the state."""
    start = time.monotonic()
    logger.info(
        "▶ GET /agent/threads/%s | user=%s",
        thread_id,
        str(user.id),
    )
    conversation = await run_in_threadpool(get_conversation, thread_id, str(user.id))
    if conversation is None:
        logger.warning(
            "Conversation not found or access denied | thread=%s | user=%s",
            thread_id,
            str(user.id),
        )
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(
        "✓ GET /agent/threads/%s loaded %d messages in %.2fs",
        thread_id,
        len(conversation.get("messages", [])),
        time.monotonic() - start,
    )
    return conversation