from __future__ import annotations

from typing import Any


RUNNER_CANCEL_TIMEOUT_CONTRACT_VERSION = "project_runner_cancel_timeout_contracts.v1"
RUNNER_CANCEL_TIMEOUT_CONTRACT_SCHEMA_VERSION = "runner_cancel_timeout_contract_schema.v1"


def build_project_runner_cancel_timeout_contracts(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    implementation_gap_checklists: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    implementation_by_profile = {
        str(report.get("profile_id")): report
        for report in implementation_gap_checklists.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    contract_schema = runner_cancel_timeout_contract_schema()
    reports = [
        _cancel_timeout_contract_report(
            profile,
            implementation_by_profile.get(str(profile.get("id"))),
            contract_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_CANCEL_TIMEOUT_CONTRACT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "contract_required_count": sum(
                1 for report in reports if report["status"] == "cancel_timeout_contract_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "future_endpoint_count": len(contract_schema["future_endpoints"]) * len(reports),
            "registered_endpoint_count": 0,
            "launchable_count": 0,
        },
        "cancel_timeout_contract_schema": contract_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "cancel_timeout_contract_only": True,
            "registers_post_api": False,
            "registers_cancel_api": False,
            "registers_timeout_api": False,
            "implements_runner": False,
            "imports_adapter": False,
            "calls_execution_adapter": False,
            "cancels_process": False,
            "sends_process_signal": False,
            "kills_process": False,
            "schedules_timeout": False,
            "stores_launch_state": False,
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


def runner_cancel_timeout_contract_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_CANCEL_TIMEOUT_CONTRACT_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "contract_state": {
            "read_only": True,
            "endpoints_registered_now": False,
            "can_cancel_now": False,
            "can_timeout_now": False,
        },
        "future_endpoints": [
            {
                "id": "runner_cancel",
                "method": "POST",
                "path": "/api/project/runner/cancel",
                "registered_now": False,
                "idempotent": True,
                "required_fields": [
                    "runner_session_id",
                    "launch_request_id",
                    "idempotency_key",
                    "reason",
                    "typed_consent",
                ],
                "forbidden_fields": [
                    "pid",
                    "signal",
                    "shell",
                    "command_string",
                    "cwd_override",
                    "log_path_override",
                ],
            },
            {
                "id": "runner_timeout",
                "method": "POST",
                "path": "/api/project/runner/timeout",
                "registered_now": False,
                "idempotent": True,
                "required_fields": [
                    "runner_session_id",
                    "launch_request_id",
                    "timeout_policy_id",
                    "observed_duration_ms",
                    "idempotency_key",
                ],
                "forbidden_fields": [
                    "pid",
                    "signal",
                    "shell",
                    "command_string",
                    "cwd_override",
                    "log_path_override",
                ],
            },
        ],
        "allowed_future_state_transitions": [
            "running -> cancelling",
            "cancelling -> cancelled",
            "running -> timing_out",
            "timing_out -> timeout",
            "running -> completed",
            "running -> failed",
        ],
        "required_future_guards": [
            "runner_session_exists",
            "session_is_running",
            "request_matches_launch_snapshot",
            "idempotency_key_required",
            "authorization_record_required",
            "audit_event_before_action",
            "audit_event_after_action",
            "final_state_written_once",
        ],
        "required_future_events": [
            "cancel_requested",
            "cancel_accepted",
            "cancel_finalized",
            "timeout_detected",
            "timeout_accepted",
            "timeout_finalized",
        ],
        "blocked_actions": [
            "registering cancel or timeout POST APIs",
            "sending process signals",
            "killing processes",
            "calling execution adapter cancel/timeout hooks",
            "scheduling timeout workers",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _cancel_timeout_contract_report(
    profile: dict[str, Any],
    implementation_report: dict[str, Any] | None,
    contract_schema: dict[str, object],
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_implementation_gap(implementation_report),
        _check_endpoints_declared(contract_schema),
        _check_no_registered_endpoints(contract_schema),
        _check_no_process_control(),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_cancel_timeout_contract:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "implementation_gap_checklist_status": (
            implementation_report.get("status") if isinstance(implementation_report, dict) else "missing"
        ),
        "contract_state": contract_schema["contract_state"],
        "future_endpoints": contract_schema["future_endpoints"],
        "allowed_future_state_transitions": contract_schema["allowed_future_state_transitions"],
        "required_future_guards": contract_schema["required_future_guards"],
        "required_future_events": contract_schema["required_future_events"],
        "blocked_actions": contract_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only declares future cancel/timeout contracts. It does not register cancel or timeout APIs, "
            "send process signals, kill processes, call adapter hooks, schedule timeout workers, write runner events, "
            "read/write logs, write audit logs, or modify the user project."
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Cancel/timeout contract requires a saved run profile.")


def _check_implementation_gap(implementation_report: dict[str, Any] | None) -> dict[str, object]:
    if not implementation_report:
        return _check("implementation_gap_checklist", "error", "Missing implementation gap checklist", "Generate the implementation gap checklist first.")
    if implementation_report.get("status") == "implementation_gap_required":
        return _check("implementation_gap_checklist", "pass", "Implementation gaps declared", "Cancel/timeout contracts can be declared read-only.")
    return _check(
        "implementation_gap_checklist",
        "error",
        "Implementation gap checklist is blocked",
        str(implementation_report.get("status") or "unknown"),
    )


def _check_endpoints_declared(contract_schema: dict[str, object]) -> dict[str, object]:
    endpoints = contract_schema.get("future_endpoints")
    required = {"runner_cancel", "runner_timeout"}
    if isinstance(endpoints, list) and required.issubset({str(item.get("id")) for item in endpoints if isinstance(item, dict)}):
        return _check("endpoints_declared", "pass", "Cancel/timeout endpoints declared", "Future API contracts are explicit.")
    return _check("endpoints_declared", "error", "Cancel/timeout endpoints incomplete", "Missing cancel or timeout endpoint contract.")


def _check_no_registered_endpoints(contract_schema: dict[str, object]) -> dict[str, object]:
    endpoints = contract_schema.get("future_endpoints")
    registered = [
        item for item in endpoints if isinstance(item, dict) and item.get("registered_now")
    ] if isinstance(endpoints, list) else []
    if not registered:
        return _check("no_registered_endpoints", "pass", "No cancel/timeout endpoints registered", "This layer only declares future endpoints.")
    return _check("no_registered_endpoints", "error", "Endpoint registered unexpectedly", "Cancel/timeout endpoints must remain unavailable.")


def _check_no_process_control() -> dict[str, object]:
    return _check("no_process_control", "pass", "No process control", "No signal, kill, adapter cancel hook, or timeout worker is invoked.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No launch API, subprocess, runner event write, audit persistence, log write, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "cancel_timeout_contract_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "cancel_timeout_contract_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Cancel/timeout contract is blocked",
        "cancel_timeout_contract_required": "Cancel and timeout contracts are required before real testing",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and generate implementation gap checklists before declaring cancel/timeout contracts.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix cancel/timeout contract blocker",
                "action": failed.get("detail") or "Complete the implementation gap checklist first.",
            }
    return {
        "title": "Cancel/timeout behavior remains a contract only",
        "action": "Implement real cancel/timeout endpoints, process control, runner events, and audit persistence in a separate authorized round.",
    }
