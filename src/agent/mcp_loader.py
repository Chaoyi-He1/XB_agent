"""Load tools from MCP (Model Context Protocol) servers.

Configure servers in config/mcp_servers.json (or path from MCP_SERVERS_FILE).
Format: { "server_name": { "transport": "stdio"|"http", "command"?, "args"?, "url"?, "headers"? }, ... }
See config/mcp_servers.json.example. Requires: pip install langchain-mcp-adapters
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool


def _get_mcp_config_path() -> Path | None:
    try:
        from config import get_settings
        path = get_settings().mcp_servers_file
        if path:
            return Path(path).expanduser().resolve()
    except Exception:
        pass
    base = Path(__file__).resolve().parent.parent.parent
    return base / "config" / "mcp_servers.json"


async def _load_mcp_tools_async(config_path: Path) -> list[BaseTool]:
    with open(config_path, encoding="utf-8") as f:
        servers = json.load(f)
    if not servers or not isinstance(servers, dict):
        return []
    from langchain_mcp_adapters.client import MultiServerMCPClient
    client = MultiServerMCPClient(servers)
    return await client.get_tools()


def load_mcp_tools() -> list[BaseTool]:
    """Load LangChain tools from all MCP servers in config. Returns [] if disabled or on error."""
    config_path = _get_mcp_config_path()
    if not config_path or not config_path.exists():
        return []
    try:
        return asyncio.run(_load_mcp_tools_async(config_path))
    except ImportError:
        return []
    except Exception:
        return []
