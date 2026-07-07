from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path
from typing import Any, Iterable


DEFAULT_TRACE_DIR = ".flowtrace"
EXTERNAL_RUNTIME_PREFIX = "external_runtime_"
EXTERNAL_RUNTIME_EXTENSIONS = {".json", ".jsonl", ".log", ".txt"}
EXTERNAL_RUNTIME_MAX_FILES = 200
EXTERNAL_RUNTIME_MAX_DEPTH = 3
EXTERNAL_RUNTIME_MAX_GROUPS = 200


def get_trace_dir() -> Path:
    return Path(os.environ.get("FLOWTRACE_DIR", DEFAULT_TRACE_DIR)).resolve()


def get_run_dir(run_id: str, trace_dir: Path | None = None) -> Path:
    root = trace_dir or get_trace_dir()
    return root / "runs" / run_id


def append_event(event: dict[str, Any], trace_dir: Path | None = None) -> Path:
    run_id = event["run_id"]
    run_dir = get_run_dir(run_id, trace_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    event_file = run_dir / "events.jsonl"
    with event_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event_file


def read_events(run_id: str, trace_dir: Path | None = None) -> list[dict[str, Any]]:
    if run_id.startswith(EXTERNAL_RUNTIME_PREFIX):
        return _read_external_runtime_events(run_id, trace_dir)

    event_file = get_run_dir(run_id, trace_dir) / "events.jsonl"
    if not event_file.exists():
        return []

    events: list[dict[str, Any]] = []
    with event_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def list_runs(trace_dir: Path | None = None) -> list[dict[str, Any]]:
    root = (trace_dir or get_trace_dir()) / "runs"
    if not root.exists():
        return _list_external_runtime_runs(trace_dir)

    runs: list[dict[str, Any]] = []
    for run_dir in root.iterdir():
        if not run_dir.is_dir():
            continue
        events = read_events(run_dir.name, trace_dir)
        first_event = events[0] if events else {}
        last_event = events[-1] if events else {}
        runs.append(
            {
                "run_id": run_dir.name,
                "event_count": len(events),
                "started_at": first_event.get("timestamp"),
                "ended_at": last_event.get("timestamp"),
                "label": first_event.get("run_label") or run_dir.name,
            }
        )
    if runs:
        return sorted(runs, key=lambda item: item.get("started_at") or "", reverse=True)
    return _list_external_runtime_runs(trace_dir)


def iter_events(trace_dir: Path | None = None) -> Iterable[dict[str, Any]]:
    for run in list_runs(trace_dir):
        yield from read_events(run["run_id"], trace_dir)


def _list_external_runtime_runs(trace_dir: Path | None = None) -> list[dict[str, Any]]:
    root = trace_dir or get_trace_dir()
    if not root.exists() or not root.is_dir():
        return []

    runs = []
    for group in _external_runtime_groups(root):
        runs.append(
            {
                "run_id": group["run_id"],
                "event_count": len(group["files"]) + 2,
                "started_at": group["started_at"],
                "ended_at": group["ended_at"],
                "label": group["label"],
                "source": "external_runtime",
                "format": "runtime_group_projection",
                "runtime_kind": group["kind"],
                "file_count": len(group["files"]),
                "categories": group["categories"],
            }
        )
    return sorted(runs, key=lambda item: item.get("started_at") or "", reverse=True)


def _read_external_runtime_events(run_id: str, trace_dir: Path | None = None) -> list[dict[str, Any]]:
    root = trace_dir or get_trace_dir()
    if not root.exists() or not root.is_dir():
        return []

    for group in _external_runtime_groups(root):
        if group["run_id"] == run_id:
            return _external_runtime_group_events(root, group)
    return []


def _external_runtime_groups(root: Path) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for path in _external_runtime_files(root):
        group_key, kind, label, metadata = _external_runtime_group_key(root, path)
        group = groups.setdefault(
            group_key,
            {
                "key": group_key,
                "run_id": f"{EXTERNAL_RUNTIME_PREFIX}{hashlib.sha1(group_key.encode('utf-8')).hexdigest()[:16]}",
                "kind": kind,
                "label": label,
                "files": [],
                "categories": set(),
                "metadata": {},
                "started_at": None,
                "ended_at": None,
            },
        )
        stat = path.stat()
        timestamp = _timestamp_from_mtime(stat.st_mtime)
        rel_path = _relative_posix(root, path)
        category = path.relative_to(root).parts[0] if path.relative_to(root).parts else "root"
        group["files"].append(
            {
                "path": rel_path,
                "size_bytes": stat.st_size,
                "modified_at": timestamp,
                "format": path.suffix.lower().lstrip(".") or "file",
                "summary": _external_runtime_file_summary(path),
            }
        )
        group["categories"].add(category)
        group["metadata"].update({key: value for key, value in metadata.items() if value not in (None, "")})
        group["started_at"] = min(filter(None, [group["started_at"], timestamp]), default=timestamp)
        group["ended_at"] = max(filter(None, [group["ended_at"], timestamp]), default=timestamp)

    normalized = []
    for group in groups.values():
        group["files"].sort(key=lambda item: item["modified_at"])
        group["categories"] = sorted(group["categories"])
        normalized.append(group)
    return sorted(normalized, key=lambda item: item.get("ended_at") or "", reverse=True)[:EXTERNAL_RUNTIME_MAX_GROUPS]


def _external_runtime_group_key(root: Path, path: Path) -> tuple[str, str, str, dict[str, Any]]:
    rel = path.relative_to(root)
    parts = rel.parts
    category = parts[0] if parts else "root"
    payload = _read_json_object(path) if path.suffix.lower() == ".json" else {}
    analysis_id = str(payload.get("analysis_id") or "").strip()
    job_id = str(payload.get("job_id") or "").strip()
    file_id = str(payload.get("file_id") or "").strip()
    file_name = str(payload.get("file_name") or payload.get("original_filename") or "").strip()

    if category == "reports" and path.name != "report_index.json":
        key = analysis_id or path.stem
        return (
            f"analysis:{key}",
            "analysis_report",
            f"分析报告 / {file_name or key} / {key[:8]}",
            {"analysis_id": key, "file_id": file_id, "file_name": file_name},
        )
    if len(parts) >= 3 and category == "audit" and parts[1] == "analysis_timing":
        key = job_id or path.stem
        return (
            f"analysis:{key}",
            "analysis_run",
            f"分析运行 / {file_name or key} / {key[:8]}",
            {"job_id": key, "file_id": file_id, "file_name": file_name, "analysis_type": payload.get("analysis_type")},
        )
    if len(parts) >= 3 and category == "audit" and parts[1] == "llm_performance":
        key = path.stem.removesuffix("_llm_performance")
        return (
            f"analysis:{key}",
            "analysis_run",
            f"分析运行 / {file_name or key} / {key[:8]}",
            {"analysis_id": key, "file_id": file_id, "file_name": file_name},
        )
    if category == "verification" and len(parts) >= 2:
        key = parts[1]
        return (
            f"verification:{key}",
            "verification_batch",
            f"验证批次 / {key}",
            {"batch": key},
        )
    if category == "rag":
        if len(parts) >= 2 and parts[1] == "uploads":
            key = "rag:uploads"
            label = "RAG 上传语料"
        elif len(parts) >= 2 and parts[1] == "cache":
            key = "rag:cache"
            label = "RAG 缓存"
        else:
            key = "rag:index"
            label = "RAG 知识库索引"
        return key, "rag_store", label, {}
    if category == "audit" and len(parts) >= 2:
        key = f"audit:{parts[1]}"
        return key, "audit_bucket", f"审计分类 / {parts[1]}", {}
    if category == "reports":
        return "reports:index", "report_index", "报告索引", {}
    if category == "root":
        return "service:logs", "service_logs", "服务日志", {}
    return f"{category}:{'/'.join(parts[:2])}", "runtime_bucket", f"运行分类 / {' / '.join(parts[:2])}", {}


def _external_runtime_files(root: Path) -> list[Path]:
    files: list[Path] = []
    try:
        iterator = root.rglob("*")
        for path in iterator:
            if not path.is_file():
                continue
            if len(path.relative_to(root).parts) > EXTERNAL_RUNTIME_MAX_DEPTH:
                continue
            if path.suffix.lower() not in EXTERNAL_RUNTIME_EXTENSIONS:
                continue
            if path.name == "report_index.json":
                continue
            files.append(path)
    except OSError:
        return []
    return sorted(files, key=lambda item: item.stat().st_mtime if item.exists() else 0, reverse=True)[:EXTERNAL_RUNTIME_MAX_FILES]


def _external_runtime_file_events(root: Path, path: Path, run_id: str) -> list[dict[str, Any]]:
    stat = path.stat()
    timestamp = _timestamp_from_mtime(stat.st_mtime)
    rel_path = _relative_posix(root, path)
    trace_id = f"trace_{run_id.removeprefix(EXTERNAL_RUNTIME_PREFIX)}"
    payload = {
        "path": rel_path,
        "size_bytes": stat.st_size,
        "modified_at": timestamp,
        "format": path.suffix.lower().lstrip(".") or "file",
        "projection": "external_runtime_file",
        "summary": _external_runtime_file_summary(path),
    }
    return [
        _external_runtime_event(
            run_id,
            trace_id,
            "start",
            timestamp,
            "run_start",
            "external_runtime.start",
            {"label": _external_runtime_label(root, path), "source": "external_runtime"},
        ),
        _external_runtime_event(
            run_id,
            trace_id,
            "file",
            timestamp,
            "user_action",
            "external_runtime.file_observed",
            payload,
        ),
        _external_runtime_event(
            run_id,
            trace_id,
            "end",
            timestamp,
            "run_end",
            "external_runtime.end",
            {"label": _external_runtime_label(root, path), "source": "external_runtime"},
        ),
    ]


def _external_runtime_group_events(root: Path, group: dict[str, Any]) -> list[dict[str, Any]]:
    run_id = str(group["run_id"])
    trace_id = f"trace_{run_id.removeprefix(EXTERNAL_RUNTIME_PREFIX)}"
    started_at = str(group.get("started_at") or "")
    ended_at = str(group.get("ended_at") or started_at)
    base_payload = {
        "label": group["label"],
        "source": "external_runtime",
        "projection": "external_runtime_group",
        "runtime_kind": group["kind"],
        "categories": group["categories"],
        "file_count": len(group["files"]),
        "metadata": group.get("metadata", {}),
    }
    events = [
        _external_runtime_event(
            run_id,
            trace_id,
            "start",
            started_at,
            "run_start",
            "external_runtime.group_start",
            base_payload,
        )
    ]
    for index, file_record in enumerate(group["files"], start=1):
        events.append(
            _external_runtime_event(
                run_id,
                trace_id,
                f"file_{index}",
                str(file_record["modified_at"]),
                "user_action",
                "external_runtime.file_observed",
                {
                    **file_record,
                    "projection": "external_runtime_group_file",
                    "runtime_kind": group["kind"],
                    "group_label": group["label"],
                },
            )
        )
    events.append(
        _external_runtime_event(
            run_id,
            trace_id,
            "end",
            ended_at,
            "run_end",
            "external_runtime.group_end",
            base_payload,
        )
    )
    return events


def _external_runtime_event(
    run_id: str,
    trace_id: str,
    suffix: str,
    timestamp: str,
    event_type: str,
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event_id": f"evt_{run_id}_{suffix}",
        "run_id": run_id,
        "trace_id": trace_id,
        "span_id": None,
        "parent_span_id": None,
        "timestamp": timestamp,
        "actor": "external_runtime",
        "action": action,
        "event_type": event_type,
        "source_node": None,
        "target_node": None,
        "payload": payload,
        "input": None,
        "output": None,
        "duration_ms": None,
        "error": None,
        "validation": None,
        "diff": None,
        "tags": ["external_runtime", "file_projection"],
        "source": "external_runtime",
        "confidence": 0.35,
        "run_label": payload.get("label"),
    }


def _external_runtime_file_summary(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".json", ".jsonl"}:
        return _json_file_summary(path)
    return {"kind": "text_log", "content_read": False}


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_file_summary(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return {"kind": "json", "readable": False, "reason": "encoding"}
    except OSError:
        return {"kind": "json", "readable": False, "reason": "io"}

    if path.suffix.lower() == ".jsonl":
        lines = [line for line in text.splitlines() if line.strip()]
        return {"kind": "jsonl", "line_count": len(lines), "content_read": False}

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"kind": "json", "readable": False, "reason": "decode"}

    if isinstance(payload, dict):
        return {"kind": "json", "top_level_type": "object", "keys": sorted(str(key) for key in payload.keys())[:30]}
    if isinstance(payload, list):
        return {"kind": "json", "top_level_type": "array", "item_count": len(payload)}
    return {"kind": "json", "top_level_type": type(payload).__name__}


def _external_runtime_run_id(root: Path, path: Path) -> str:
    digest = hashlib.sha1(_relative_posix(root, path).encode("utf-8")).hexdigest()[:16]
    return f"{EXTERNAL_RUNTIME_PREFIX}{digest}"


def _external_runtime_label(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    if len(rel.parts) > 1:
        return " / ".join(rel.parts[-2:])
    return path.name


def _relative_posix(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _timestamp_from_mtime(mtime: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")
