"""Chat and config API routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import get_settings
from src.agent.react_agent import create_agent, normalize_clarification, run_agent
from src.conversation.state import conversation_store

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
    session_id: Optional[str] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    needs_clarification: bool = False
    session_title: Optional[str] = None


def _save_and_reply(state, reply: str, session_id: str, needs_clarification: bool = False, session_title: Optional[str] = None) -> ChatResponse:
    conversation_store.save(state)
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        needs_clarification=needs_clarification,
        session_title=session_title,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Send a message to the ReACT agent and get a reply."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    state = conversation_store.get(req.session_id)
    is_new = len(state.messages) == 0
    agent = _get_agent(api_url=req.api_url, api_key=req.api_key, model_name=req.model_name)
    user_message = req.message.strip()

    if state.pending_clarification:
        state.append("user", user_message)
        reply = run_agent(agent, state.to_langchain_messages())
        is_clarification, cleaned_reply = normalize_clarification(reply)
        if is_clarification:
            state.append("assistant", cleaned_reply)
            state.pending_clarification = cleaned_reply
            return _save_and_reply(state, cleaned_reply, state.session_id, needs_clarification=True)
        state.append("assistant", cleaned_reply)
        state.pending_clarification = None
        state.pending_user_message = None
        return _save_and_reply(state, cleaned_reply, state.session_id)

    state.append("user", user_message)
    reply = run_agent(agent, state.to_langchain_messages())
    is_clarification, cleaned_reply = normalize_clarification(reply)
    if is_clarification:
        state.append("assistant", cleaned_reply)
        state.pending_clarification = cleaned_reply
        state.pending_user_message = user_message
        return _save_and_reply(
            state, cleaned_reply, state.session_id, needs_clarification=True,
            session_title=state.title if is_new else None,
        )

    state.append("assistant", cleaned_reply)
    state.pending_clarification = None
    state.pending_user_message = None
    return _save_and_reply(
        state, cleaned_reply, state.session_id,
        session_title=state.title if is_new else None,
    )


class ModelsResponse(BaseModel):
    models: list[str]
    default: str


class SessionItem(BaseModel):
    id: str
    title: str
    updated_at: float


class SessionDetail(BaseModel):
    id: str
    title: Optional[str]
    messages: list[dict[str, str]]
    updated_at: float


@router.get("/sessions", response_model=list[SessionItem])
def list_sessions() -> list[SessionItem]:
    """List saved chat sessions for the sidebar (id, title, updated_at)."""
    raw = conversation_store.list_sessions()
    return [SessionItem(id=e["id"], title=e.get("title", "New chat"), updated_at=e["updated_at"]) for e in raw]


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: str) -> SessionDetail:
    """Load one session's messages for continuing a chat."""
    state = conversation_store.get(session_id)
    return SessionDetail(
        id=state.session_id,
        title=state.title,
        messages=state.messages,
        updated_at=state.updated_at,
    )


@router.get("/models", response_model=ModelsResponse)
def list_models() -> ModelsResponse:
    """Return model list and default from .env (MODEL_LIST, MODEL_NAME)."""
    settings = get_settings()
    models = settings.model_list_parsed or [settings.model_name]
    default = settings.model_name if settings.model_name in models else (models[0] if models else "")
    return ModelsResponse(models=models, default=default)


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
