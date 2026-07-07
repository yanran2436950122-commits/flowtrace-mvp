from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_FILENAMES = ("flowtrace.config.json", ".flowtrace.json")


@dataclass(frozen=True)
class ProjectContext:
    root: Path
    trace_dir: Path
    source: str
    config_file: Path | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "schema_version": "project_context.v1",
            "root": str(self.root),
            "trace_dir": str(self.trace_dir),
            "source": self.source,
            "config_file": str(self.config_file) if self.config_file else None,
        }


def load_project_context(
    project_root: str | None = None,
    config_file: str | None = None,
    trace_dir: str | None = None,
    cwd: Path | None = None,
) -> ProjectContext:
    base_dir = (cwd or Path.cwd()).resolve()
    if project_root:
        root = _resolve_path(project_root, base_dir)
        return _validated_context(root, _resolve_trace_dir(root, trace_dir, None, base_dir), "cli")

    config_path = _find_config(config_file, base_dir)
    if config_path:
        config = _read_config(config_path)
        configured_root = _read_project_root(config)
        if configured_root:
            root = _resolve_path(configured_root, config_path.parent)
            configured_trace_dir = trace_dir or _read_trace_dir(config)
            return _validated_context(root, _resolve_trace_dir(root, configured_trace_dir, config_path.parent, base_dir), "config", config_path)

    return _validated_context(base_dir, _resolve_trace_dir(base_dir, trace_dir, None, base_dir), "cwd")


def _find_config(config_file: str | None, cwd: Path) -> Path | None:
    if config_file:
        path = _resolve_path(config_file, cwd)
        return path if path.exists() else None
    for filename in CONFIG_FILENAMES:
        path = cwd / filename
        if path.exists():
            return path
    return None


def _read_config(config_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_project_root(payload: dict[str, Any]) -> str | None:

    direct_root = payload.get("project_root")
    if isinstance(direct_root, str) and direct_root.strip():
        return direct_root

    project = payload.get("project")
    if isinstance(project, dict):
        nested_root: Any = project.get("root")
        if isinstance(nested_root, str) and nested_root.strip():
            return nested_root
    return None


def _read_trace_dir(payload: dict[str, Any]) -> str | None:
    direct_trace_dir = payload.get("trace_dir")
    if isinstance(direct_trace_dir, str) and direct_trace_dir.strip():
        return direct_trace_dir

    project = payload.get("project")
    if isinstance(project, dict):
        nested_trace_dir: Any = project.get("trace_dir")
        if isinstance(nested_trace_dir, str) and nested_trace_dir.strip():
            return nested_trace_dir
    return None


def _resolve_trace_dir(root: Path, trace_dir: str | None, config_dir: Path | None, cwd: Path) -> Path:
    configured = trace_dir or os.environ.get("FLOWTRACE_DIR")
    if configured:
        return _resolve_path(configured, config_dir or cwd)
    return (root / ".flowtrace").resolve()


def _resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _validated_context(root: Path, trace_dir: Path, source: str, config_file: Path | None = None) -> ProjectContext:
    if not root.exists():
        raise ValueError(f"FlowTrace project root does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"FlowTrace project root is not a directory: {root}")
    return ProjectContext(root=root, trace_dir=trace_dir, source=source, config_file=config_file)
