"""Tools used by the ReACT agent: web search, local papers, and optional MCP servers."""

from src.agent.tools.web_search import web_search_tool
from src.agent.tools.local_papers import local_papers_tool

__all__ = ["web_search_tool", "local_papers_tool", "get_tools"]


def get_tools(papers_path=None):
    """Return list of tools for the agent: base tools + any from MCP servers in config."""
    from src.agent.tools.local_papers import build_local_papers_tool
    from src.agent.mcp_loader import load_mcp_tools
    base = [web_search_tool, build_local_papers_tool(papers_path)]
    mcp_tools = load_mcp_tools()
    return base + mcp_tools
