# Memristor Crossbar Design Assistant

A **ReACT agent** that helps design memristor crossbar systems for signal processing. It can search the **web** and your **local papers** (PDF/TXT in a folder) and uses a configurable **LLM API** (URL + API key in `.env`).

## Features

- **ReACT agent**: reasons and uses tools in a loop (web search, local papers). Asks for clarification when the request is underspecified.
- **Web search**: via `ddgs` (no API key).
- **Local papers**: put PDFs or TXT files in `papers/`; the agent searches them by keyword.
- **Chat UI**: ChatGPT-style light interface—sidebar with “New chat”, “Search chats”, and **Your chats** list; centered input bar; model dropdown in the header (model list configurable in `.env`).
- **Configurable API**: set `API_URL`, `API_KEY`, `MODEL_NAME`, and `MODEL_LIST` in `.env` (no API fields in the UI).
- **Chat history**: past chats are listed in the left sidebar and persisted under `DATA_DIR` (default `./data`); you can search and reopen any conversation.
- **MCP servers**: optional tools from [Model Context Protocol](https://modelcontextprotocol.io/) servers; configure in `config/mcp_servers.json` (see [MCP servers](#mcp-servers)).
- **Skills**: optional extra system-prompt text loaded from the `skills/` directory; add a subfolder per skill with `skill.yaml` (see [Skills](#skills)).

## Project layout (easy to extend)

```
├── config/                 # Settings from env
│   ├── settings.py
│   ├── mcp_servers.json    # MCP server definitions (optional; copy from mcp_servers.json.example)
│   └── mcp_servers.json.example
├── src/
│   ├── agent/              # ReACT agent, tools, MCP loader, skills loader
│   │   ├── prompts.py
│   │   ├── react_agent.py
│   │   ├── mcp_loader.py
│   │   ├── skills_loader.py
│   │   └── tools/
│   │       ├── web_search.py
│   │       └── local_papers.py
│   ├── conversation/       # Session state and persistence
│   │   └── state.py
│   └── api/                # Backend
│       ├── main.py
│       └── routes.py
├── skills/                 # Optional skills (each subfolder = one skill with skill.yaml)
│   ├── README.md
│   └── memristor_basics/
│       └── skill.yaml
├── frontend/               # Chat UI
│   ├── index.html
│   └── static/
├── papers/                 # Default folder for local papers (create and add PDFs)
├── data/                   # Stored chat sessions (created automatically; optional DATA_DIR in .env)
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## Setup

1. **Clone / open the project** and go to the project root.

2. **Use a conda env** (e.g. `general_test`) or a venv:

   **Conda:**
   ```bash
   conda activate /opt/anaconda3/envs/general_test
   pip install -r requirements.txt
   ```

   **Or with a new venv:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the LLM API** (e.g. OpenAI-compatible) and optional paths:

   ```bash
   cp .env.example .env
   # Edit .env:
   # API_URL=https://api.openai.com/v1
   # API_KEY=your-api-key
   # MODEL_NAME=gpt-4o-mini
   # MODEL_LIST=gpt-4o-mini,gpt-4o,gpt-4-turbo,gpt-4,gpt-3.5-turbo   # list shown in UI dropdown
   # PAPERS_PATH=./papers   # optional
   # DATA_DIR=./data        # optional; where chat sessions are stored
   # MCP_SERVERS_FILE=config/mcp_servers.json   # optional; MCP server config
   # SKILLS_DIR=skills      # optional; directory of skill.yaml skills
   ```

4. **Optional: add local papers**  
   Put PDF or TXT files in `papers/`. The agent will search them when you ask design-related questions.

## Run

From the **project root** (so `config` and `src` are on the Python path). If using conda, activate first:

```bash
conda activate /opt/anaconda3/envs/general_test
python run.py
```

The server listens on **all interfaces** (`0.0.0.0:8000`), so you can:

- **On the same machine:** open **http://localhost:8000** in your browser.
- **From another PC on the network:** open **http://\<server-ip\>:8000**, e.g. `http://192.168.1.100:8000`.  
  On the server machine, find its IP with `ipconfig` (Windows) or `ifconfig` / `ip addr` (macOS/Linux). Ensure your firewall allows inbound TCP on port 8000.

Optional env overrides: `HOST=0.0.0.0 PORT=8000`. API URL and API key are read only from `.env`; the UI shows only **model selection** from the list defined by `MODEL_LIST`.

## API

- **POST /api/chat**  
  Body: `{ "message": "your question", "session_id?", "model_name?" }`  
  Returns: `{ "reply": "...", "session_id": "...", "session_title?": "...", "needs_clarification?": false }`.

- **GET /api/sessions**  
  Returns a list of saved chats: `[{ "id", "title", "updated_at" }, ...]`.

- **GET /api/sessions/{id}**  
  Returns one chat: `{ "id", "title", "messages", "updated_at" }`.

- **GET /api/models**  
  Returns `{ "models": ["gpt-4o-mini", ...], "default": "gpt-4o-mini" }` (from `MODEL_LIST` and `MODEL_NAME` in `.env`).

- **GET /api/health**  
  Returns `{ "status": "ok" }`.

## MCP servers

You can attach tools from **MCP (Model Context Protocol)** servers so the agent can call external APIs, filesystems, or custom tools.

1. Install the adapter: `pip install langchain-mcp-adapters`
2. Copy and edit the config: `cp config/mcp_servers.json.example config/mcp_servers.json`
3. Define servers in `config/mcp_servers.json` as a JSON object: each key is a server name, each value is a connection config:
   - **stdio** (local process): `{ "transport": "stdio", "command": "python", "args": ["/path/to/mcp_server.py"] }`
   - **HTTP** (remote): `{ "transport": "http", "url": "http://localhost:8000/mcp" }`
4. Optional: set `MCP_SERVERS_FILE` in `.env` to a different config path.

If the file is missing or empty `{}`, or the adapter is not installed, the agent simply uses the built-in tools (web search, local papers). See [config/mcp_servers.json.example](config/mcp_servers.json.example) and [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters).

## Skills

**Skills** add extra system-prompt text to the agent (e.g. domain rules, notation, or task guidance). They do not add new tools; use MCP for that.

1. Create a subfolder under `skills/`, e.g. `skills/my_domain/`.
2. Add `skill.yaml` (or `skill.yml`) with at least:
   ```yaml
   name: my_domain
   system_prompt: |
     Your extra instructions here. The agent will see this in addition to the base prompt.
   ```
3. Optional: set `SKILLS_DIR` in `.env` to a different directory.

All skills are loaded and merged in alphabetical order by folder name. See [skills/README.md](skills/README.md) and the example [skills/memristor_basics/skill.yaml](skills/memristor_basics/skill.yaml).

## Extending the project

- **New tools**: add a tool in `src/agent/tools/`, register it in `get_tools()` in `src/agent/tools/__init__.py`; the ReACT agent will use it.
- **MCP tools**: add server entries in `config/mcp_servers.json` and install `langchain-mcp-adapters`.
- **New skills**: add a folder under `skills/` with `skill.yaml` and a `system_prompt` field.
- **New routes**: add endpoints in `src/api/routes.py` or a new router and include it in `src/api/main.py`.
- **Different LLM**: use `ChatOpenAI` with `base_url`/`api_key` for any OpenAI-compatible endpoint, or swap in another LangChain LLM in `src/agent/react_agent.py`.
- **Frontend**: edit `frontend/index.html` and `frontend/static/` (e.g. streaming, themes, or new pages). Session list and model list are driven by the API.

## Push to GitHub

To create a new GitHub repo and push this project, see **[GITHUB_SETUP.md](GITHUB_SETUP.md)**.

## License

Use and extend as you like.
