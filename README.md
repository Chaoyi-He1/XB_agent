# Memristor Crossbar Design Assistant

A **ReACT agent** that helps design memristor crossbar systems for signal processing. It can search the **web** and your **local papers** (PDF/TXT in a folder) and uses a configurable **LLM API** (URL + API key).

## Features

- **ReACT agent**: reasons and uses tools in a loop (web search, local papers).
- **Web search**: DuckDuckGo (no API key).
- **Local papers**: put PDFs or TXT files in a folder; the agent searches them by keyword.
- **Chat UI**: ChatGPT-style chat in the browser.
- **Configurable API**: set `API_URL`, `API_KEY`, and optionally `MODEL_NAME` via env or in the UI.

## Project layout (easy to extend)

```
├── config/                 # Settings from env
│   └── settings.py
├── src/
│   ├── agent/              # ReACT agent and tools
│   │   ├── prompts.py
│   │   ├── react_agent.py
│   │   └── tools/
│   │       ├── web_search.py
│   │       └── local_papers.py
│   └── api/                # Backend
│       ├── main.py
│       └── routes.py
├── frontend/               # Chat UI
│   ├── index.html
│   └── static/
├── papers/                 # Default folder for local papers (create and add PDFs)
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

3. **Configure the LLM API** (e.g. OpenAI-compatible):

   ```bash
   cp .env.example .env
   # Edit .env and set:
   # API_URL=https://api.openai.com/v1
   # API_KEY=your-api-key
   # MODEL_NAME=gpt-4o-mini
   # PAPERS_PATH=./papers   # optional; default is ./papers
   ```

4. **Optional: add local papers**  
   Create a `papers` folder and put PDF or TXT files there. The agent will search them when you ask design-related questions.

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

Optional env overrides: `HOST=0.0.0.0 PORT=8000` (defaults are already set for network access).

You can set API URL, API key, and model in the **API settings** in the UI (they override env for that session).

## API

- **POST /api/chat**  
  Body: `{ "message": "your question", "api_url?", "api_key?", "model_name?" }`  
  Returns: `{ "reply": "..." }`.

- **GET /api/health**  
  Returns `{ "status": "ok" }`.

## Extending the project

- **New tools**: add a tool in `src/agent/tools/`, register it in `get_tools()` in `src/agent/tools/__init__.py`, and the ReACT agent will use it.
- **New routes**: add endpoints in `src/api/routes.py` or a new router and include it in `src/api/main.py`.
- **Different LLM**: keep using `ChatOpenAI` with `base_url`/`api_key` for any OpenAI-compatible endpoint, or swap in another LangChain LLM in `src/agent/react_agent.py`.
- **Frontend**: edit `frontend/index.html` and `frontend/static/` (e.g. add streaming, themes, or a new page).

## Push to GitHub

To create a new GitHub repo and push this project, see **[GITHUB_SETUP.md](GITHUB_SETUP.md)**.

## License

Use and extend as you like.
