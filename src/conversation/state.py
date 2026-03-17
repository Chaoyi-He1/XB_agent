"""Conversation state per session with optional disk persistence.

Keeps chat history and clarification handoffs together. Can persist sessions
to disk so users can see and reopen past chats in the sidebar.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock
from time import time
from typing import Optional
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


@dataclass
class ConversationState:
    session_id: str
    messages: list[dict[str, str]] = field(default_factory=list)
    title: Optional[str] = None
    pending_clarification: Optional[str] = None
    pending_user_message: Optional[str] = None
    updated_at: float = field(default_factory=time)

    def append(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.updated_at = time()
        if self.title is None and role == "user":
            self.title = (content.strip() or "New chat")[:80]

    def render_history(self, limit: int = 12) -> str:
        recent = self.messages[-limit:]
        if not recent:
            return "No prior conversation."
        return "\n".join(f"{item['role'].title()}: {item['content']}" for item in recent)

    def to_langchain_messages(self) -> list[BaseMessage]:
        """Convert stored chat turns into LangChain message objects."""
        out: list[BaseMessage] = []
        for item in self.messages:
            role = item["role"]
            content = item["content"]
            if role == "user":
                out.append(HumanMessage(content=content))
            elif role == "assistant":
                out.append(AIMessage(content=content))
        return out


def _sessions_dir() -> Path:
    from config import get_settings
    d = get_settings().data_dir / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _index_path() -> Path:
    from config import get_settings
    return get_settings().data_dir / "sessions_index.json"


def _session_path(session_id: str) -> Path:
    return _sessions_dir() / f"{session_id}.json"


def _state_to_dict(state: ConversationState) -> dict:
    return {
        "session_id": state.session_id,
        "title": state.title,
        "messages": state.messages,
        "pending_clarification": state.pending_clarification,
        "pending_user_message": state.pending_user_message,
        "updated_at": state.updated_at,
    }


def _state_from_dict(d: dict) -> ConversationState:
    return ConversationState(
        session_id=d["session_id"],
        title=d.get("title"),
        messages=d.get("messages", []),
        pending_clarification=d.get("pending_clarification"),
        pending_user_message=d.get("pending_user_message"),
        updated_at=float(d.get("updated_at", time())),
    )


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}
        self._lock = Lock()

    def get(self, session_id: Optional[str] = None) -> ConversationState:
        with self._lock:
            key = session_id or str(uuid4())
            state = self._sessions.get(key)
            if state is not None:
                return state
            path = _session_path(key)
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    state = _state_from_dict(data)
                    self._sessions[key] = state
                    return state
                except Exception:
                    pass
            state = ConversationState(session_id=key)
            self._sessions[key] = state
            return state

    def save(self, state: ConversationState) -> None:
        with self._lock:
            path = _session_path(state.session_id)
            path.write_text(json.dumps(_state_to_dict(state), ensure_ascii=False, indent=0), encoding="utf-8")
            index_path = _index_path()
            index_path.parent.mkdir(parents=True, exist_ok=True)
            entries = []
            if index_path.exists():
                try:
                    entries = json.loads(index_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            by_id = {e["id"]: e for e in entries}
            by_id[state.session_id] = {
                "id": state.session_id,
                "title": state.title or "New chat",
                "updated_at": state.updated_at,
            }
            entries = sorted(by_id.values(), key=lambda e: -e["updated_at"])
            index_path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")

    def list_sessions(self) -> list[dict]:
        index_path = _index_path()
        if not index_path.exists():
            return []
        try:
            return json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def upsert(self, state: ConversationState) -> None:
        with self._lock:
            self._sessions[state.session_id] = state

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            path = _session_path(session_id)
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass


conversation_store = ConversationStore()

