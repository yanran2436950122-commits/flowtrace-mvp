from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now
from .run_confirmation_store import profile_fingerprint


RUNNER_SESSION_STORE_VERSION = "runner_session_store.v1"
RUNNER_SESSION_STORE_FILENAME = "runner_sessions.json"


def load_runner_sessions(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    sessions = [item for item in payload.get("sessions", []) if isinstance(item, dict) and item.get("profile_id")]
    return {
        "schema_version": RUNNER_SESSION_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "sessions": sorted(sessions, key=lambda item: str(item.get("created_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in sessions),
    }


def prepare_runner_session(trace_dir: Path, profile: dict[str, Any], execution_report: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_runner_sessions(trace_dir)
    sessions = [item for item in store["sessions"] if item.get("profile_id") != profile_id]
    request = execution_report.get("request") if isinstance(execution_report.get("request"), dict) else {}
    sessions.append(
        {
            "session_id": runner_session_id(profile_id),
            "profile_id": profile_id,
            "request_id": request.get("request_id"),
            "session_fingerprint": runner_session_fingerprint(profile, execution_report),
            "created_at": utc_now(),
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "planned_event_schema": "runner_event_schema.v1",
            "executes_commands": False,
            "creates_process": False,
        }
    )
    return _write_store(trace_dir, sessions)


def remove_runner_session(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_runner_sessions(trace_dir)
    sessions = [item for item in store["sessions"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, sessions)


def runner_session_state(
    profile: dict[str, Any],
    execution_report: dict[str, Any] | None,
    session_store: dict[str, object] | None,
) -> dict[str, object]:
    sessions = session_store.get("sessions", []) if isinstance(session_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in sessions if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not execution_report:
        if match:
            return {
                "status": "stale",
                "session_id": match.get("session_id"),
                "request_id": match.get("request_id"),
                "drafted": False,
                "created_at": match.get("created_at"),
                "stale": True,
                "reason": "执行请求报告已不存在，需要移除会话草案。",
            }
        return {"status": "blocked", "drafted": False, "stale": False, "reason": "缺少执行请求报告。"}
    request = execution_report.get("request") if isinstance(execution_report.get("request"), dict) else {}
    if request.get("status") != "second_confirmed":
        if match:
            return {
                "status": "stale",
                "session_id": match.get("session_id"),
                "request_id": match.get("request_id"),
                "drafted": False,
                "created_at": match.get("created_at"),
                "stale": True,
                "reason": "执行请求已不再处于二次确认状态，需要移除或重新生成会话草案。",
            }
        return {
            "status": "blocked",
            "drafted": False,
            "stale": False,
            "reason": "runner 会话草案只能基于已二次确认的执行请求生成。",
        }
    if not match:
        return {"status": "none", "drafted": False, "stale": False}
    current_fingerprint = runner_session_fingerprint(profile, execution_report)
    if match.get("session_fingerprint") != current_fingerprint:
        return {
            "status": "stale",
            "session_id": match.get("session_id"),
            "request_id": match.get("request_id"),
            "drafted": False,
            "created_at": match.get("created_at"),
            "stale": True,
            "reason": "执行请求、运行配置或事件 schema 已变化，需要重新生成会话草案。",
        }
    return {
        "status": "drafted",
        "session_id": match.get("session_id"),
        "request_id": match.get("request_id"),
        "drafted": True,
        "created_at": match.get("created_at"),
        "stale": False,
    }


def runner_session_fingerprint(profile: dict[str, Any], execution_report: dict[str, Any]) -> str:
    request = execution_report.get("request") if isinstance(execution_report.get("request"), dict) else {}
    payload = {
        "profile_fingerprint": profile_fingerprint(profile),
        "execution_request_status": request.get("status"),
        "execution_request_id": request.get("request_id"),
        "execution_request_second_confirmed_at": request.get("second_confirmed_at"),
        "execution_report_status": execution_report.get("status"),
        "event_schema": "runner_event_schema.v1",
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def runner_session_id(profile_id: str) -> str:
    return f"runner_session:{profile_id.strip()}"


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUNNER_SESSION_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUNNER_SESSION_STORE_VERSION,
        "updated_at": None,
        "sessions": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, sessions: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUNNER_SESSION_STORE_VERSION,
        "updated_at": utc_now(),
        "sessions": sorted(sessions, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_runner_sessions(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
