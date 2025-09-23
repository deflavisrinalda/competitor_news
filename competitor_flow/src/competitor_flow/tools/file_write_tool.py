# file: src/competitor_flow/tools/file_writer.py
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from crewai.tools import BaseTool


# ------------------------- Utils -------------------------
def _project_root(start: Optional[Path] = None) -> Path:
    """Heuristic: climb up from `start` (or CWD) until we find pyproject.toml or .git."""
    p = (start or Path.cwd()).resolve()
    for parent in [p] + list(p.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return p


def _sanitize_filename(name: str) -> str:
    """Keep filename safe/cross-platform. Preserve extension if present."""
    name = name.strip()
    # Split extension (last dot)
    stem, dot, ext = name.partition(".")
    safe_stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-._")
    safe_ext = re.sub(r"[^a-zA-Z0-9]+", "", ext)
    if safe_ext:
        return f"{safe_stem}.{safe_ext}"
    return safe_stem or "output"


def _ensure_unique(path: Path) -> Path:
    """If path exists, add numeric suffix before extension."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


# ------------------------- Args schema -------------------------
class FileWriterArgs(BaseModel):
    filename: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ] = Field(..., description="Target filename (e.g., report.json)")
    content: str = Field(..., description="File content to write")
    directory: Optional[str] = Field(
        default="reports",
        description="Relative or absolute directory where the file will be saved",
    )
    overwrite: bool = Field(
        default=True, description="If false and file exists, create a unique name"
    )
    append: bool = Field(
        default=False, description="If true, append to file instead of overwrite"
    )
    encoding: str = Field(default="utf-8", description="Text encoding for the file")


# ------------------------- Tool -------------------------
class FileWriterTool(BaseTool):
    """Write text content to disk safely. Returns a JSON string with file info."""

    name: str = "file_writer"
    description: str = (
        "Persist text content to disk. Args: "
        "{ filename: str, content: str, directory?: str='reports', "
        "overwrite?: bool=True, append?: bool=False, encoding?: str='utf-8' }. "
        "Returns JSON: { 'path': str, 'bytes': int, 'created': bool, 'appended': bool }."
    )
    args_schema: type = FileWriterArgs

    def _run(self, **kwargs) -> str:
        try:
            args = FileWriterArgs(**kwargs)
        except Exception as e:
            return json.dumps({"error": f"invalid_args: {e}"}, ensure_ascii=False)

        root = _project_root()
        base_dir = Path(args.directory)
        dir_path = base_dir if base_dir.is_absolute() else (root / base_dir)
        dir_path.mkdir(parents=True, exist_ok=True)

        filename = _sanitize_filename(args.filename)
        path = dir_path / filename

        mode = "a" if args.append else "w"
        created = not path.exists()

        if not args.overwrite and not args.append and path.exists():
            path = _ensure_unique(path)
            created = True

        try:
            if args.append:
                # Simple append
                with path.open(mode=mode, encoding=args.encoding, newline="") as f:
                    f.write(args.content)
                written = len(args.content.encode(args.encoding))
            else:
                # Atomic write: temp file then replace
                with tempfile.NamedTemporaryFile(
                    "w", delete=False, encoding=args.encoding, newline=""
                ) as tmp:
                    tmp.write(args.content)
                    tmp_path = Path(tmp.name)
                os.replace(tmp_path, path)  # atomic on most OS/filesystems
                written = len(args.content.encode(args.encoding))

            return json.dumps(
                {
                    "path": str(path.resolve()),
                    "bytes": written,
                    "created": created,
                    "appended": bool(args.append),
                },
                ensure_ascii=False,
            )
        except Exception as e:
            # Clean up temp file if present
            try:
                if "tmp_path" in locals() and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            return json.dumps({"error": f"write_failed: {e}"}, ensure_ascii=False)
