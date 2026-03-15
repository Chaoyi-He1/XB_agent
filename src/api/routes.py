"""Chat and config API routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.react_agent import create_agent, run_agent

router = APIRouter()

# One agent per process (stateless per request; override via request body if needed)
_agent = None


def _get_agent(api_url: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None):
    global _agent
    if api_url or api_key or model_name:
        return create_agent(api_url=api_url, api_key=api_key, model_name=model_name)
    if _agent is None:
        _agent = create_agent()
    return _agent


class ChatRequest(BaseModel):
    message: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Send a message to the ReACT agent and get a reply."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    agent = _get_agent(api_url=req.api_url, api_key=req.api_key, model_name=req.model_name)
    reply = run_agent(agent, req.message.strip())
    return ChatResponse(reply=reply)


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
