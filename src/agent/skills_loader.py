"""Load skills from the skills/ directory.

Each skill is a subfolder containing skill.yaml with:
  name: string
  description: optional string
  system_prompt: string (appended to the agent system prompt)

All skills' system_prompt fields are concatenated and merged into the agent prompt.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


def _get_skills_dir() -> Path | None:
    try:
        from config import get_settings
        path = getattr(get_settings(), "skills_dir", None)
        if path:
            return Path(path).expanduser().resolve()
    except Exception:
        pass
    base = Path(__file__).resolve().parent.parent.parent
    candidate = base / "skills"
    return candidate if candidate.is_dir() else None


def load_skills_prompt() -> str:
    """Load all skills and return concatenated system_prompt text. Returns '' if no skills or on error."""
    skills_dir = _get_skills_dir()
    if not skills_dir:
        return ""
    if not yaml:
        return ""
    parts: list[str] = []
    for subdir in sorted(skills_dir.iterdir()):
        if not subdir.is_dir():
            continue
        yaml_path = subdir / "skill.yaml"
        if not yaml_path.exists():
            yaml_path = subdir / "skill.yml"
        if not yaml_path.exists():
            continue
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and data.get("system_prompt"):
                parts.append(data["system_prompt"].strip())
        except Exception:
            continue
    if not parts:
        return ""
    return "\n\n".join(parts)
