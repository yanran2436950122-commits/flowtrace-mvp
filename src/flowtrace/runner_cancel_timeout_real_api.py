from __future__ import annotations

from typing import Any


RUNNER_CANCEL_TIMEOUT_REAL_API_VERSION = "project_runner_cancel_timeout_real_apis.v1"
RUNNER_CANCEL_TIMEOUT_REAL_API_SCHEMA_VERSION = "runner_cancel_timeout_real_api_schema.v1"


def build_project_runner_cancel_timeout_real_apis(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
    active_processes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    reports = [_report(profile, active_processes or []) for profile in saved_profiles]
    return {
        "schema_version": RUNNER_CANCEL_TIMEOUT_REAL_API_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "registered_endpoint_count": 2 if saved_profiles else 0,
            "active_process_count": len(active_processes or []),
            "cancelled_count": runner_real_executions.get("summary", {}).get("cancelled_count", 0),
            "timed_out_count": runner_real_executions.get("summary", {}).get("timed_out_count", 0),
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
        },
        "cancel_timeout_real_api_schema": runner_cancel_timeout_real_api_schema(),
        "reports": reports,
        "active_processes": active_processes or [],
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_cancel_timeout_real_api_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_CANCEL_TIMEOUT_REAL_API_SCHEMA_VERSION,
        "projection_only": False,
        "registered_endpoints": [
            {
                "id": "runner_cancel",
                "method": "POST",
                "path": "/api/project/runner/cancel",
                "typed_consent": "CONTROL TARGET PROJECT",
                "requires_launch_id": True,
            },
            {
                "id": "runner_timeout",
                "method": "POST",
                "path": "/api/project/runner/timeout",
                "typed_consent": "CONTROL TARGET PROJECT",
                "requires_launch_id": True,
            },
        ],
        "control_boundary": {
            "active_process_only": True,
            "low_risk_sample_launch_only": True,
            "uses_existing_launch_id": True,
            "does_not_accept_pid": True,
            "does_not_accept_shell": True,
            "does_not_write_user_project": True,
        },
    }


def _report(profile: dict[str, Any], active_processes: list[dict[str, object]]) -> dict[str, object]:
    profile_active = [item for item in active_processes if item.get("profile_id") == profile.get("id")]
    return {
        "id": f"runner_cancel_timeout_real_api:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "active_process_control_available" if profile_active else "api_registered_no_active_process",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "active_processes": profile_active,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "cancel_timeout_endpoints_registered",
                "pass",
                "Cancel/timeout endpoints registered",
                "POST cancel and timeout endpoints are available for active low-risk sample launches.",
            ),
            _check(
                "active_launch_id_required",
                "pass",
                "Active launch_id required",
                "Requests cannot provide pid, shell, cwd, or command overrides.",
            ),
        ],
    }


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "active_process_control_available" for report in reports):
        return "active_process_control_available"
    return "cancel_timeout_api_available"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Cancel/timeout controls appear after a saved low-risk sample profile exists.",
        }
    if any(report.get("status") == "active_process_control_available" for report in reports):
        return {
            "title": "Active process can be controlled",
            "action": "Use launch_id with typed consent CONTROL TARGET PROJECT to cancel or timeout the active process.",
        }
    return {
        "title": "Cancel/timeout API is available",
        "action": "Controls require a currently active low-risk sample launch_id.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "cancel_timeout_real_api": True,
        "registers_post_api": True,
        "registers_cancel_api": True,
        "registers_timeout_api": True,
        "controls_process": True,
        "cancels_process": True,
        "sends_process_signal": True,
        "kills_process": False,
        "schedules_timeout": False,
        "accepts_pid": False,
        "accepts_shell": False,
        "calls_execution_adapter": False,
        "writes_runner_events": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "reads_log_files": False,
        "writes_logs": False,
        "stores_authorization": False,
        "writes_user_project": False,
        "writes_trace_dir": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
