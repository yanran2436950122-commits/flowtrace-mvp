from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now
from .run_confirmation_store import profile_fingerprint


RUNNER_DRY_RUN_STORE_VERSION = "runner_dry_run_store.v1"
RUNNER_DRY_RUN_STORE_FILENAME = "runner_dry_runs.json"


def load_runner_dry_runs(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    dry_runs = [item for item in payload.get("dry_runs", []) if isinstance(item, dict) and item.get("profile_id")]
    return {
        "schema_version": RUNNER_DRY_RUN_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "dry_runs": sorted(dry_runs, key=lambda item: str(item.get("created_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in dry_runs),
    }


def prepare_runner_dry_run(
    trace_dir: Path,
    profile: dict[str, Any],
    launch_snapshot_report: dict[str, Any],
) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_runner_dry_runs(trace_dir)
    dry_runs = [item for item in store["dry_runs"] if item.get("profile_id") != profile_id]
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    dry_run_id = runner_dry_run_id(profile_id)
    dry_runs.append(
        {
            "dry_run_id": dry_run_id,
            "profile_id": profile_id,
            "snapshot_id": snapshot.get("snapshot_id"),
            "session_id": snapshot.get("session_id") or launch_snapshot_report.get("session_id"),
            "request_id": snapshot.get("request_id") or launch_snapshot_report.get("request_id"),
            "dry_run_fingerprint": runner_dry_run_fingerprint(profile, launch_snapshot_report),
            "created_at": utc_now(),
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "working_directory": profile.get("working_directory"),
            "argv": profile.get("argv") if isinstance(profile.get("argv"), list) else [],
            "planned_logs": _planned_logs(trace_dir, dry_run_id),
            "executes_commands": False,
            "creates_process": False,
            "dry_run_only": True,
        }
    )
    return _write_store(trace_dir, dry_runs)


def remove_runner_dry_run(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_runner_dry_runs(trace_dir)
    dry_runs = [item for item in store["dry_runs"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, dry_runs)


def runner_dry_run_state(
    profile: dict[str, Any],
    launch_snapshot_report: dict[str, Any] | None,
    dry_run_store: dict[str, object] | None,
) -> dict[str, object]:
    dry_runs = dry_run_store.get("dry_runs", []) if isinstance(dry_run_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in dry_runs if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not launch_snapshot_report:
        if match:
            return _stale(match, "启动前快照报告已不存在，需要移除 dry-run 记录。")
        return {"status": "blocked", "prepared": False, "stale": False, "reason": "缺少启动前快照报告。"}
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    if snapshot.get("status") != "snapshotted":
        if match:
            return _stale(match, "启动前快照已不再有效，需要移除或重新生成 dry-run 记录。")
        return {
            "status": "blocked",
            "prepared": False,
            "stale": False,
            "reason": "dry-run runner 只能基于已生成的启动前快照创建。",
        }
    if not match:
        return {"status": "none", "prepared": False, "stale": False}
    current_fingerprint = runner_dry_run_fingerprint(profile, launch_snapshot_report)
    if match.get("dry_run_fingerprint") != current_fingerprint:
        return _stale(match, "运行配置、启动前快照或 dry-run 策略已变化，需要重新生成 dry-run 记录。")
    return {
        "status": "prepared",
        "dry_run_id": match.get("dry_run_id"),
        "snapshot_id": match.get("snapshot_id"),
        "session_id": match.get("session_id"),
        "request_id": match.get("request_id"),
        "prepared": True,
        "created_at": match.get("created_at"),
        "planned_logs": match.get("planned_logs") if isinstance(match.get("planned_logs"), dict) else {},
        "stale": False,
    }


def runner_dry_run_fingerprint(profile: dict[str, Any], launch_snapshot_report: dict[str, Any]) -> str:
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    payload = {
        "profile_fingerprint": profile_fingerprint(profile),
        "snapshot_status": snapshot.get("status"),
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_created_at": snapshot.get("created_at"),
        "snapshot_report_status": launch_snapshot_report.get("status"),
        "dry_run_schema": "runner_dry_run_schema.v1",
        "dry_run_only": True,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def runner_dry_run_id(profile_id: str) -> str:
    return f"runner_dry_run:{profile_id.strip()}"


def _planned_logs(trace_dir: Path, dry_run_id: str) -> dict[str, object]:
    safe_id = dry_run_id.replace(":", "_").replace("/", "_").replace("\\", "_")
    run_dir = trace_dir / "runner" / safe_id
    return {
        "run_directory": str(run_dir),
        "event_log": str(run_dir / "runner_events.jsonl"),
        "stdout_log": str(run_dir / "stdout.log"),
        "stderr_log": str(run_dir / "stderr.log"),
        "summary_file": str(run_dir / "summary.json"),
        "creates_files_now": False,
    }


def _stale(match: dict[str, object], reason: str) -> dict[str, object]:
    return {
        "status": "stale",
        "dry_run_id": match.get("dry_run_id"),
        "snapshot_id": match.get("snapshot_id"),
        "session_id": match.get("session_id"),
        "request_id": match.get("request_id"),
        "prepared": False,
        "created_at": match.get("created_at"),
        "planned_logs": match.get("planned_logs") if isinstance(match.get("planned_logs"), dict) else {},
        "stale": True,
        "reason": reason,
    }


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUNNER_DRY_RUN_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUNNER_DRY_RUN_STORE_VERSION,
        "updated_at": None,
        "dry_runs": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, dry_runs: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUNNER_DRY_RUN_STORE_VERSION,
        "updated_at": utc_now(),
        "dry_runs": sorted(dry_runs, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_runner_dry_runs(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
