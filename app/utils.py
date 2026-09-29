import re
import tempfile
import shutil
from pathlib import Path


WORKSPACE_BASE = Path(tempfile.gettempdir()) / "latex_compiler"


def create_workspace() -> Path:
    WORKSPACE_BASE.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="latex_", dir=WORKSPACE_BASE))
    return path


def cleanup_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def _safe_rel_path(rel: str) -> str | None:
    if not rel or not isinstance(rel, str):
        return None
    p = rel.strip().replace("\\", "/").lstrip("/")
    if ".." in p:
        return None
    return p


def resolve_file_path(workdir: Path, raw_name: str) -> Path:
    safe = _safe_rel_path(raw_name)
    if safe is None:
        raise ValueError(f"Invalid file path: {raw_name}")
    return validate_path(workdir, safe)


def validate_path(base_dir: Path, target: str) -> Path:
    base = base_dir.resolve()
    full = (base / target).resolve()
    if not str(full).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {target}")
    return full


def detect_main_tex(files: list[dict]) -> str | None:
    for f in files:
        name = f.get("path") or f.get("name") or ""
        if name.lower().endswith(".tex"):
            content = f.get("content", "")
            if r"\documentclass" in content:
                return name
    for f in files:
        name = f.get("path") or f.get("name") or ""
        if name.lower().endswith(".tex"):
            return name
    return None

