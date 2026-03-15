"""Tools used by the ReACT agent: web search and local papers search."""

from src.agent.tools.web_search import web_search_tool
from src.agent.tools.local_papers import local_papers_tool

__all__ = ["web_search_tool", "local_papers_tool"]

def get_tools(papers_path=None):
    """Return list of tools for the agent. papers_path can override config."""
    from src.agent.tools.local_papers import build_local_papers_tool
    return [web_search_tool, build_local_papers_tool(papers_path)]
