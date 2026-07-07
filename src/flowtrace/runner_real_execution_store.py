from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .context import utc_now


RUNNER_REAL_EXECUTION_STORE_VERSION = "runner_real_execution_store.v1"
RUNNER_REAL_EXECUTION_STORE_FILENAME = "runner_real_executions.json"


def load_runner_real_executions(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    executions = [
        item
        for item in payload.get("executions", [])
        if isinstance(item, dict) and item.get("launch_id") and item.get("profile_id")
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "executions": sorted(executions, key=lambda item: str(item.get("started_at") or ""), reverse=True),
        "profile_ids": sorted({str(item["profile_id"]) for item in executions}),
    }


def append_runner_real_execution(trace_dir: Path, execution: dict[str, Any]) -> dict[str, object]:
    store = load_runner_real_executions(trace_dir)
    executions = [item for item in store["executions"] if isinstance(item, dict)]
    executions.append({**execution, "recorded_at": utc_now()})
    return _write_store(trace_dir, executions)


def build_project_runner_real_executions(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_dry_runs: dict[str, Any],
    real_execution_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    dry_run_by_profile = {
        str(report.get("profile_id")): report
        for report in runner_dry_runs.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    executions = real_execution_store.get("executions", []) if isinstance(real_execution_store, dict) else []
    latest_by_profile: dict[str, dict[str, object]] = {}
    for execution in executions:
        if not isinstance(execution, dict):
            continue
        profile_id = str(execution.get("profile_id") or "")
        if profile_id and profile_id not in latest_by_profile:
            latest_by_profile[profile_id] = execution
    reports = [
        _real_execution_report(
            profile,
            dry_run_by_profile.get(str(profile.get("id"))),
            latest_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    return {
        "schema_version": "project_runner_real_executions.v1",
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "launchable_count": sum(1 for report in reports if report["can_launch"]),
            "completed_count": sum(1 for item in executions if isinstance(item, dict) and item.get("status") == "completed"),
            "failed_count": sum(1 for item in executions if isinstance(item, dict) and item.get("status") == "failed"),
            "cancelled_count": sum(1 for item in executions if isinstance(item, dict) and item.get("status") == "cancelled"),
            "timed_out_count": sum(1 for item in executions if isinstance(item, dict) and item.get("status") == "timed_out"),
            "execution_count": len(executions),
        },
        "reports": reports,
        "executions": executions,
        "safety": {
            "executes_commands": True,
            "creates_process": True,
            "runner_implemented": True,
            "launch_enabled": True,
            "launch_api_available": True,
            "requires_low_risk_sample_project": True,
            "requires_prepared_dry_run": True,
            "requires_typed_consent": True,
            "uses_shell": False,
            "writes_user_project": False,
            "writes_trace_dir": True,
        },
        "next_action": _next_action(reports),
    }


def _real_execution_report(
    profile: dict[str, Any],
    dry_run_report: dict[str, Any] | None,
    latest_execution: dict[str, object] | None,
) -> dict[str, object]:
    dry_run = dry_run_report.get("dry_run") if isinstance(dry_run_report, dict) and isinstance(dry_run_report.get("dry_run"), dict) else {}
    can_launch = profile.get("mode") == "command" and dry_run.get("status") == "prepared"
    return {
        "id": f"runner_real_execution:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "ready_to_launch" if can_launch else "blocked",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "dry_run_status": dry_run.get("status") or "missing",
        "latest_execution": latest_execution,
        "can_launch": can_launch,
        "checks": [
            _check(
                "command_profile",
                "pass" if profile.get("mode") == "command" else "error",
                "Command profile required",
                str(profile.get("mode") or "missing"),
            ),
            _check(
                "dry_run_prepared",
                "pass" if dry_run.get("status") == "prepared" else "error",
                "Prepared dry-run required",
                str(dry_run.get("status") or "missing"),
            ),
            _check("typed_consent_required", "warn", "Typed consent required", "POST launch must include RUN TARGET PROJECT."),
        ],
    }


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("can_launch") for report in reports):
        return "launch_available"
    return "blocked"


def _next_action(reports: list[dict[str, object]]) -> dict[str, object]:
    if any(report.get("can_launch") for report in reports):
        return {
            "title": "Minimal real launch is available",
            "action": "Launch requires an explicit typed consent POST and is limited to the current low-risk sample project.",
        }
    return {
        "title": "Prepare launch prerequisites",
        "action": "Save a command profile, complete confirmation, create a session, snapshot, and dry-run before launching.",
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUNNER_REAL_EXECUTION_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_STORE_VERSION,
        "updated_at": None,
        "executions": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, executions: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUNNER_REAL_EXECUTION_STORE_VERSION,
        "updated_at": utc_now(),
        "executions": sorted(executions, key=lambda item: str(item.get("started_at") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_runner_real_executions(trace_dir)
