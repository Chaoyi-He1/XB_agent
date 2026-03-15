"""Local papers search: index PDFs in a folder and search by keyword."""

from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


def _ensure_str(path: Path) -> str:
    return str(path) if path else ""


def _index_folder(folder: Path) -> list[tuple[str, str]]:
    """Return list of (file_path, extracted_text) for PDFs and .txt in folder."""
    if not folder or not folder.is_dir():
        return []
    out = []
    for ext in ("*.pdf", "*.txt"):
        for f in folder.glob(ext):
            try:
                if f.suffix.lower() == ".pdf":
                    from pypdf import PdfReader
                    reader = PdfReader(f)
                    text = "\n".join(
                        p.extract_text() or "" for p in reader.pages[:50]
                    )
                else:
                    text = f.read_text(encoding="utf-8", errors="replace")
                if text.strip():
                    out.append((_ensure_str(f), text.strip()[:50000]))
            except Exception:
                continue
    return out


def _search_papers(papers_path: Optional[Path], query: str) -> str:
    if papers_path is None:
        try:
            from config import get_settings
            papers_path = get_settings().papers_path
        except Exception:
            papers_path = None
    papers_path = Path(papers_path) if papers_path else None
    if not papers_path or not papers_path.is_dir():
        return "Local papers folder is not configured or does not exist. Add PDF or TXT files to the papers folder and set PAPERS_PATH."
    indexed = _index_folder(papers_path)
    if not indexed:
        return "No PDF or TXT files found in the papers folder."
    q = query.lower()
    results = []
    for path, text in indexed:
        if q in text.lower():
            # Return a snippet around the match
            idx = text.lower().find(q)
            start = max(0, idx - 200)
            end = min(len(text), idx + len(q) + 400)
            snippet = text[start:end].replace("\n", " ")
            results.append(f"File: {path}\nSnippet: ...{snippet}...")
    if not results:
        return "No local papers matched the query. Try different keywords or add relevant papers to the folder."
    return "\n\n---\n\n".join(results[:10])


def build_local_papers_tool(papers_path: Optional[Path] = None):
    """Build the local_papers tool with optional path override."""

    @tool
    def local_papers_tool(query: str) -> str:
        """Search local papers (PDF and TXT) in the configured papers folder.
        Use for design equations, architectures, or citations from your own library.
        Input: search query string (keywords or short phrase)."""
        return _search_papers(papers_path, query)

    return local_papers_tool


# Default instance uses config at runtime when path is None
local_papers_tool = build_local_papers_tool(None)
