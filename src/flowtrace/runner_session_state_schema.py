from __future__ import annotations

from typing import Any


RUNNER_SESSION_STATE_SCHEMA_VERSION = "project_runner_session_state_schemas.v1"
RUNNER_SESSION_STATE_SCHEMA_SCHEMA_VERSION = "runner_session_state_schema.v1"


def build_project_runner_session_state_schemas(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    cancel_timeout_contracts: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    cancel_timeout_by_profile = {
        str(report.get("profile_id")): report
        for report in cancel_timeout_contracts.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    state_schema = runner_session_state_schema()
    reports = [
        _session_state_schema_report(
            profile,
            cancel_timeout_by_profile.get(str(profile.get("id"))),
            state_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_SESSION_STATE_SCHEMA_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "state_schema_required_count": sum(
                1 for report in reports if report["status"] == "session_state_schema_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "state_count": len(state_schema["allowed_states"]) * len(reports),
            "persisted_session_count": 0,
            "active_session_count": 0,
            "launchable_count": 0,
        },
        "session_state_schema": state_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "session_state_schema_only": True,
            "registers_post_api": False,
            "registers_launch_api": False,
            "registers_cancel_api": False,
            "registers_timeout_api": False,
            "implements_runner": False,
            "imports_adapter": False,
            "calls_execution_adapter": False,
            "creates_session": False,
            "stores_session_state": False,
            "mutates_session_state": False,
            "reads_session_state_store": False,
            "writes_session_state_store": False,
            "cancels_process": False,
            "sends_process_signal": False,
            "kills_process": False,
            "schedules_timeout": False,
            "opens_stdout_stderr": False,
            "writes_runner_events": False,
            "reads_log_files": False,
            "writes_logs": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "renames_logs": False,
            "truncates_logs": False,
            "scans_log_directory": False,
            "writes_audit_log": False,
            "reads_audit_log": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def runner_session_state_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_SESSION_STATE_SCHEMA_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "schema_state": {
            "read_only": True,
            "session_store_available_now": False,
            "session_created_now": False,
            "session_mutated_now": False,
            "active_session_now": False,
        },
        "identity_fields": [
            "runner_session_id",
            "launch_request_id",
            "run_profile_id",
            "launch_snapshot_id",
            "idempotency_key",
        ],
        "required_future_fields": [
            "status",
            "created_at",
            "updated_at",
            "started_at",
            "finished_at",
            "exit_code",
            "failure_reason",
            "cancel_reason",
            "timeout_policy_id",
            "stdout_stream_ref",
            "stderr_stream_ref",
            "audit_event_refs",
        ],
        "forbidden_current_fields": [
            "pid",
            "process_handle",
            "shell_command",
            "live_stdout_path",
            "live_stderr_path",
        ],
        "allowed_states": [
            "draft",
            "queued",
            "launching",
            "running",
            "cancelling",
            "cancelled",
            "timing_out",
            "timeout",
            "completed",
            "failed",
        ],
        "allowed_future_transitions": [
            "draft -> queued",
            "queued -> launching",
            "launching -> running",
            "running -> completed",
            "running -> failed",
            "running -> cancelling",
            "cancelling -> cancelled",
            "running -> timing_out",
            "timing_out -> timeout",
        ],
        "terminal_states": ["cancelled", "timeout", "completed", "failed"],
        "required_future_guards": [
            "saved_run_profile_required",
            "launch_snapshot_required",
            "authorization_required",
            "idempotency_key_required",
            "single_active_session_per_launch_request",
            "terminal_state_written_once",
            "audit_event_before_state_change",
            "audit_event_after_state_change",
        ],
        "required_future_events": [
            "session_drafted",
            "session_queued",
            "session_launching",
            "session_running",
            "session_completed",
            "session_failed",
            "session_cancelled",
            "session_timeout",
        ],
        "blocked_actions": [
            "creating or storing runner sessions",
            "mutating runner session state",
            "registering launch/cancel/timeout POST APIs",
            "creating processes",
            "sending process signals",
            "calling execution adapters",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _session_state_schema_report(
    profile: dict[str, Any],
    cancel_timeout_report: dict[str, Any] | None,
    state_schema: dict[str, object],
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_cancel_timeout_contract(cancel_timeout_report),
        _check_states_declared(state_schema),
        _check_no_session_store(state_schema),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_session_state_schema:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "cancel_timeout_contract_status": (
            cancel_timeout_report.get("status") if isinstance(cancel_timeout_report, dict) else "missing"
        ),
        "schema_state": state_schema["schema_state"],
        "identity_fields": state_schema["identity_fields"],
        "required_future_fields": state_schema["required_future_fields"],
        "forbidden_current_fields": state_schema["forbidden_current_fields"],
        "allowed_states": state_schema["allowed_states"],
        "allowed_future_transitions": state_schema["allowed_future_transitions"],
        "terminal_states": state_schema["terminal_states"],
        "required_future_guards": state_schema["required_future_guards"],
        "required_future_events": state_schema["required_future_events"],
        "blocked_actions": state_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only declares future runner session state. It does not create sessions, persist state, "
            "mutate state, register launch/cancel/timeout APIs, create processes, call adapters, open streams, "
            "write runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Session state schema requires a saved run profile.")


def _check_cancel_timeout_contract(cancel_timeout_report: dict[str, Any] | None) -> dict[str, object]:
    if not cancel_timeout_report:
        return _check(
            "cancel_timeout_contract",
            "error",
            "Missing cancel/timeout contract",
            "Declare cancel/timeout contracts before session state schema.",
        )
    if cancel_timeout_report.get("status") == "cancel_timeout_contract_required":
        return _check(
            "cancel_timeout_contract",
            "pass",
            "Cancel/timeout contracts declared",
            "Session state can be declared read-only.",
        )
    return _check(
        "cancel_timeout_contract",
        "error",
        "Cancel/timeout contract is blocked",
        str(cancel_timeout_report.get("status") or "unknown"),
    )


def _check_states_declared(state_schema: dict[str, object]) -> dict[str, object]:
    states = state_schema.get("allowed_states")
    required = {"draft", "queued", "launching", "running", "completed", "failed", "cancelled", "timeout"}
    if isinstance(states, list) and required.issubset({str(item) for item in states}):
        return _check("states_declared", "pass", "Session states declared", "Future lifecycle states are explicit.")
    return _check("states_declared", "error", "Session states incomplete", "Missing required future lifecycle state.")


def _check_no_session_store(state_schema: dict[str, object]) -> dict[str, object]:
    schema_state = state_schema.get("schema_state")
    if isinstance(schema_state, dict) and not schema_state.get("session_store_available_now"):
        return _check("no_session_store", "pass", "No session store available", "This layer does not persist sessions.")
    return _check("no_session_store", "error", "Session store enabled unexpectedly", "Session persistence must remain unavailable.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or state mutation",
        "No launch API, subprocess, state write, stream open, runner event write, audit persistence, log write, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "session_state_schema_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "session_state_schema_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Session state schema is blocked",
        "session_state_schema_required": "Runner session state schema is required before real testing",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and declare cancel/timeout contracts before session state schema.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix session state schema blocker",
                "action": failed.get("detail") or "Complete cancel/timeout contracts first.",
            }
    return {
        "title": "Session state remains a schema only",
        "action": "Implement session persistence, state mutation, runner events, and audit persistence in a separate authorized round.",
    }
