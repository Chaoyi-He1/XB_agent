"""Web search tool using DuckDuckGo (no API key required)."""

from langchain_core.tools import tool


@tool
def web_search_tool(query: str) -> str:
    """Search the web for current information. Use for recent papers, tutorials,
    memristor crossbar design, signal processing, or hardware/software resources.
    Input should be a clear search query string."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
        if not results:
            return "No web results found for that query."
        lines = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            lines.append(f"Title: {title}\nSnippet: {body}\nURL: {href}")
        return "\n\n---\n\n".join(lines)
    except Exception as e:
        return f"Web search failed: {e}"
