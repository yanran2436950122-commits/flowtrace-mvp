from __future__ import annotations

from typing import Any


RUNNER_PROCESS_LIFECYCLE_VERSION = "project_runner_process_lifecycles.v1"
RUNNER_PROCESS_LIFECYCLE_SCHEMA_VERSION = "runner_process_lifecycle_schema.v1"


def build_project_runner_process_lifecycles(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    executions = [
        item
        for item in runner_real_executions.get("executions", [])
        if isinstance(item, dict) and item.get("launch_id") and item.get("profile_id")
    ]
    latest_by_profile: dict[str, dict[str, Any]] = {}
    for execution in executions:
        profile_id = str(execution.get("profile_id") or "")
        if profile_id and profile_id not in latest_by_profile:
            latest_by_profile[profile_id] = execution
    reports = [_lifecycle_report(profile, latest_by_profile.get(str(profile.get("id")))) for profile in saved_profiles]
    session_states = [report["session_state"] for report in reports if isinstance(report.get("session_state"), dict)]
    return {
        "schema_version": RUNNER_PROCESS_LIFECYCLE_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "session_state_count": len(session_states),
            "pending_count": sum(1 for item in session_states if item.get("state") == "pending"),
            "running_count": sum(1 for item in session_states if item.get("state") == "running"),
            "completed_count": sum(1 for item in session_states if item.get("state") == "completed"),
            "failed_count": sum(1 for item in session_states if item.get("state") == "failed"),
            "cancelled_count": sum(1 for item in session_states if item.get("state") == "cancelled"),
            "timed_out_count": sum(1 for item in session_states if item.get("state") == "timed_out"),
            "terminal_count": sum(1 for item in session_states if item.get("terminal")),
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
        },
        "lifecycle_schema": runner_process_lifecycle_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_process_lifecycle_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_PROCESS_LIFECYCLE_SCHEMA_VERSION,
        "states": ["pending", "running", "completed", "failed", "cancelled", "timed_out"],
        "terminal_states": ["completed", "failed", "cancelled", "timed_out"],
        "implemented_now": {
            "session_state_projection": True,
            "terminal_state_mapping": True,
            "execution_record_linkage": True,
            "pending_state_for_unlaunched_profiles": True,
        },
        "deferred": {
            "long_running_process_tracking": True,
            "live_running_state": True,
            "cancel_api": True,
            "timeout_api": True,
            "process_signal_control": True,
            "runner_event_stream": True,
        },
    }


def _lifecycle_report(profile: dict[str, Any], latest_execution: dict[str, Any] | None) -> dict[str, object]:
    session_state = _session_state(profile, latest_execution)
    return {
        "id": f"runner_process_lifecycle:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "terminal_state_recorded" if session_state["terminal"] else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "session_state": session_state,
        "latest_execution": latest_execution,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "execution_record_linked",
                "pass" if latest_execution else "warn",
                "Execution record linkage",
                str(latest_execution.get("launch_id") if latest_execution else "no execution yet"),
            ),
            _check(
                "terminal_state_model",
                "pass",
                "Terminal state model available",
                "completed, failed, cancelled, and timed_out states are represented.",
            ),
        ],
    }


def _session_state(profile: dict[str, Any], latest_execution: dict[str, Any] | None) -> dict[str, object]:
    if not latest_execution:
        return {
            "session_id": f"runner_process_lifecycle:{profile.get('id')}",
            "profile_id": profile.get("id"),
            "state": "pending",
            "terminal": False,
            "launch_id": None,
            "exit_code": None,
            "started_at": None,
            "ended_at": None,
            "run_directory": None,
        }
    state = _map_execution_state(latest_execution)
    return {
        "session_id": latest_execution.get("launch_id"),
        "profile_id": latest_execution.get("profile_id"),
        "state": state,
        "terminal": state in {"completed", "failed", "cancelled", "timed_out"},
        "launch_id": latest_execution.get("launch_id"),
        "exit_code": latest_execution.get("exit_code"),
        "started_at": latest_execution.get("started_at"),
        "ended_at": latest_execution.get("ended_at"),
        "run_directory": latest_execution.get("run_directory"),
    }


def _map_execution_state(execution: dict[str, Any]) -> str:
    status = str(execution.get("status") or "")
    if status in {"completed", "failed", "cancelled", "timed_out"}:
        return status
    if status in {"running", "launching"}:
        return "running"
    return "failed"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "terminal_state_recorded" for report in reports):
        return "lifecycle_records_present"
    return "lifecycle_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Lifecycle projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "terminal_state_recorded" for report in reports):
        return {
            "title": "Review terminal state",
            "action": "Use the lifecycle projection to inspect completed or failed minimal launches.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Lifecycle projection is ready; launch still requires prepared dry-run and typed consent.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "process_lifecycle_projection": True,
        "stores_session_state": False,
        "mutates_session_state": False,
        "controls_process": False,
        "cancels_process": False,
        "sends_process_signal": False,
        "kills_process": False,
        "schedules_timeout": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "opens_stdout_stderr": False,
        "writes_runner_events": False,
        "writes_user_project": False,
        "writes_trace_dir": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
