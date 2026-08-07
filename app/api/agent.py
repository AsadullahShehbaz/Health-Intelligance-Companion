# app/api/agent.py
from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_service import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest):
    try:
        return await run_agent(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))