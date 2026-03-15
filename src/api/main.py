"""FastAPI app: chat API and static frontend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.api.routes import router as api_router

app = FastAPI(
    title="Memristor Crossbar Design Assistant",
    description="ReACT agent with web and local paper search for signal processing design.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api", tags=["chat"])

# Serve frontend static files and SPA fallback
static_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"
if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def index():
    """Serve the chat UI."""
    index_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)
    return {"message": "Frontend not found. Add frontend/index.html and frontend/static/."}
