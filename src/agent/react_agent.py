"""ReACT agent for memristor crossbar design: uses LLM with web + local paper tools."""

from typing import Optional

import warnings

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

warnings.filterwarnings("ignore", module="langgraph")
from langgraph.prebuilt import create_react_agent

from config import get_settings
from src.agent.prompts import REACT_SYSTEM_PROMPT
from src.agent.skills_loader import load_skills_prompt
from src.agent.tools import get_tools


def _make_llm(api_url: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        base_url=api_url or settings.api_url,
        api_key=api_key or settings.api_key,
        model=model_name or settings.model_name,
        temperature=0.2,
    )


def _react_prompt() -> str:
    """System prompt for the LangGraph ReACT agent (base + skills)."""
    base = (
        REACT_SYSTEM_PROMPT
        + "\n\nIf you need more details from the user, respond with exactly one short question."
    )
    skills_text = load_skills_prompt()
    if skills_text:
        base = base + "\n\n" + skills_text
    return base


def create_agent(
    tools: Optional[list[BaseTool]] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    papers_path: Optional[str] = None,
):
    """Build a LangGraph ReACT agent with optional overrides for API and papers path."""
    from pathlib import Path
    llm = _make_llm(api_url=api_url, api_key=api_key, model_name=model_name)
    tool_list = tools or get_tools(papers_path=Path(papers_path) if papers_path else None)
    prompt = _react_prompt()
    return create_react_agent(llm, tool_list, prompt=prompt, version="v2")


def run_agent(agent, messages: list[BaseMessage]) -> str:
    """Run the agent and return the final assistant message."""
    result = agent.invoke({"messages": messages})
    output_messages = result.get("messages", []) if isinstance(result, dict) else []
    for msg in reversed(output_messages):
        if isinstance(msg, AIMessage):
            return msg.content or "No response generated."
    return "No response generated."


def normalize_clarification(reply: str) -> tuple[bool, str]:
    """Detect clarification-style replies from the agent."""
    cleaned = reply.strip()
    upper = cleaned.upper()
    if upper.startswith("FINAL ANSWER:"):
        cleaned = cleaned.split(":", 1)[1].strip() if ":" in cleaned else cleaned
        upper = cleaned.upper()
    if upper.startswith("CLARIFY:"):
        return True, cleaned[len("CLARIFY:") :].strip()
    if "CLARIFY:" in upper:
        idx = upper.find("CLARIFY:")
        return True, cleaned[idx + len("CLARIFY:") :].strip()
    return False, cleaned
