"""ReACT agent for memristor crossbar design: uses LLM with web + local paper tools."""

from typing import Any, Optional

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import BaseTool

from config import get_settings
from src.agent.prompts import REACT_SYSTEM_PROMPT
from src.agent.tools import get_tools


def _make_llm(api_url: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        base_url=api_url or settings.api_url,
        api_key=api_key or settings.api_key,
        model=model_name or settings.model_name,
        temperature=0.2,
    )


def _react_prompt() -> PromptTemplate:
    """ReACT prompt with tools, tool_names, input, agent_scratchpad (LangChain convention)."""
    return PromptTemplate.from_template(
        REACT_SYSTEM_PROMPT
        + """

You have access to the following tools:

{tools}

Use this format:
Thought: consider what to do next
Action: the exact name of one tool from [{tool_names}]
Action Input: the input for the tool (single string)
Observation: the result will be inserted here
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: your answer for the user

Begin!

Question: {input}
{agent_scratchpad}"""
    )


def create_agent(
    tools: Optional[list[BaseTool]] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    papers_path: Optional[str] = None,
) -> AgentExecutor:
    """Build ReACT agent with optional overrides for API and papers path."""
    from pathlib import Path
    llm = _make_llm(api_url=api_url, api_key=api_key, model_name=model_name)
    tool_list = tools or get_tools(papers_path=Path(papers_path) if papers_path else None)
    prompt = _react_prompt()
    agent = create_react_agent(llm, tool_list, prompt)
    return AgentExecutor(agent=agent, tools=tool_list, handle_parsing_errors=True, max_iterations=10)


def run_agent(agent: AgentExecutor, user_message: str) -> str:
    """Run the agent and return the final answer string."""
    result = agent.invoke({"input": user_message})
    return result.get("output", "No response generated.")
