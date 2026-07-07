from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now
from .run_confirmation_store import profile_fingerprint


RUNNER_LAUNCH_SNAPSHOT_STORE_VERSION = "runner_launch_snapshot_store.v1"
RUNNER_LAUNCH_SNAPSHOT_STORE_FILENAME = "runner_launch_snapshots.json"


def load_runner_launch_snapshots(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    snapshots = [item for item in payload.get("snapshots", []) if isinstance(item, dict) and item.get("profile_id")]
    return {
        "schema_version": RUNNER_LAUNCH_SNAPSHOT_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "snapshots": sorted(snapshots, key=lambda item: str(item.get("created_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in snapshots),
    }


def prepare_runner_launch_snapshot(
    trace_dir: Path,
    profile: dict[str, Any],
    runner_session_report: dict[str, Any],
) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_runner_launch_snapshots(trace_dir)
    snapshots = [item for item in store["snapshots"] if item.get("profile_id") != profile_id]
    session = runner_session_report.get("session") if isinstance(runner_session_report.get("session"), dict) else {}
    snapshots.append(
        {
            "snapshot_id": runner_launch_snapshot_id(profile_id),
            "profile_id": profile_id,
            "session_id": session.get("session_id"),
            "request_id": session.get("request_id") or runner_session_report.get("request_id"),
            "snapshot_fingerprint": runner_launch_snapshot_fingerprint(profile, runner_session_report),
            "created_at": utc_now(),
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "working_directory": profile.get("working_directory"),
            "argv": profile.get("argv") if isinstance(profile.get("argv"), list) else [],
            "env_keys": sorted((profile.get("env") or {}).keys()) if isinstance(profile.get("env"), dict) else [],
            "executes_commands": False,
            "creates_process": False,
            "launch_enabled": False,
        }
    )
    return _write_store(trace_dir, snapshots)


def remove_runner_launch_snapshot(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_runner_launch_snapshots(trace_dir)
    snapshots = [item for item in store["snapshots"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, snapshots)


def runner_launch_snapshot_state(
    profile: dict[str, Any],
    runner_session_report: dict[str, Any] | None,
    snapshot_store: dict[str, object] | None,
) -> dict[str, object]:
    snapshots = snapshot_store.get("snapshots", []) if isinstance(snapshot_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in snapshots if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not runner_session_report:
        if match:
            return _stale(match, "Runner 会话报告已不存在，需要移除启动前快照。")
        return {"status": "blocked", "snapshotted": False, "stale": False, "reason": "缺少 runner 会话报告。"}
    session = runner_session_report.get("session") if isinstance(runner_session_report.get("session"), dict) else {}
    if session.get("status") != "drafted":
        if match:
            return _stale(match, "Runner 会话草案已不再有效，需要移除或重新生成启动前快照。")
        return {
            "status": "blocked",
            "snapshotted": False,
            "stale": False,
            "reason": "启动前快照只能基于已生成的 runner 会话草案创建。",
        }
    if not match:
        return {"status": "none", "snapshotted": False, "stale": False}
    current_fingerprint = runner_launch_snapshot_fingerprint(profile, runner_session_report)
    if match.get("snapshot_fingerprint") != current_fingerprint:
        return _stale(match, "运行配置、执行请求、runner 会话或事件 schema 已变化，需要重新生成启动前快照。")
    return {
        "status": "snapshotted",
        "snapshot_id": match.get("snapshot_id"),
        "session_id": match.get("session_id"),
        "request_id": match.get("request_id"),
        "snapshotted": True,
        "created_at": match.get("created_at"),
        "stale": False,
    }


def runner_launch_snapshot_fingerprint(profile: dict[str, Any], runner_session_report: dict[str, Any]) -> str:
    session = runner_session_report.get("session") if isinstance(runner_session_report.get("session"), dict) else {}
    payload = {
        "profile_fingerprint": profile_fingerprint(profile),
        "runner_session_status": session.get("status"),
        "runner_session_id": session.get("session_id"),
        "runner_session_created_at": session.get("created_at"),
        "request_id": runner_session_report.get("request_id") or session.get("request_id"),
        "request_status": runner_session_report.get("request_status"),
        "runner_session_report_status": runner_session_report.get("status"),
        "launch_snapshot_schema": "runner_launch_snapshot_schema.v1",
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def runner_launch_snapshot_id(profile_id: str) -> str:
    return f"runner_launch_snapshot:{profile_id.strip()}"


def _stale(match: dict[str, object], reason: str) -> dict[str, object]:
    return {
        "status": "stale",
        "snapshot_id": match.get("snapshot_id"),
        "session_id": match.get("session_id"),
        "request_id": match.get("request_id"),
        "snapshotted": False,
        "created_at": match.get("created_at"),
        "stale": True,
        "reason": reason,
    }


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUNNER_LAUNCH_SNAPSHOT_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LAUNCH_SNAPSHOT_STORE_VERSION,
        "updated_at": None,
        "snapshots": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, snapshots: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUNNER_LAUNCH_SNAPSHOT_STORE_VERSION,
        "updated_at": utc_now(),
        "snapshots": sorted(snapshots, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_runner_launch_snapshots(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
