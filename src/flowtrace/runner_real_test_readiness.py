from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_READINESS_VERSION = "project_runner_real_test_readiness.v1"
RUNNER_REAL_TEST_GATE_SCHEMA_VERSION = "runner_real_test_gate_schema.v1"


def build_project_runner_real_test_readiness(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    session_state_schemas: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    session_schema_by_profile = {
        str(report.get("profile_id")): report
        for report in session_state_schemas.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    gate_schema = runner_real_test_gate_schema()
    reports = [
        _real_test_readiness_report(
            profile,
            session_schema_by_profile.get(str(profile.get("id"))),
            gate_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_READINESS_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "real_test_blocked_count": sum(1 for report in reports if report["status"] == "real_test_blocked"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "gate_count": sum(len(report.get("readiness_gates", [])) for report in reports),
            "missing_gate_count": sum(
                1
                for report in reports
                for item in report.get("readiness_gates", [])
                if item.get("status") == "missing"
            ),
            "passed_gate_count": sum(
                1
                for report in reports
                for item in report.get("readiness_gates", [])
                if item.get("status") == "pass"
            ),
            "launchable_count": 0,
            "can_start_real_test_count": 0,
        },
        "real_test_gate_schema": gate_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "real_test_readiness_only": True,
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
            "collects_human_authorization": False,
            "stores_authorization": False,
            "grants_permission": False,
        },
        "next_action": _next_action(status, reports),
    }


def runner_real_test_gate_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_TEST_GATE_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "readiness_state": {
            "read_only": True,
            "can_start_real_test_now": False,
            "requires_new_authorized_implementation_round": True,
            "approval_collected_now": False,
        },
        "required_gates": [
            {
                "key": "implementation_gap_closed",
                "title": "Runner implementation gaps closed",
                "minimum_evidence": "all required components implemented and reviewed",
            },
            {
                "key": "launch_api_registered",
                "title": "Launch API registered",
                "minimum_evidence": "POST /api/project/runner/launch exists and is idempotent",
            },
            {
                "key": "execution_adapter_implemented",
                "title": "Execution adapter implemented",
                "minimum_evidence": "tokenized argv adapter rejects shell strings and cwd overrides",
            },
            {
                "key": "session_state_persistence_enabled",
                "title": "Session state persistence enabled",
                "minimum_evidence": "pending/running/terminal states are persisted once",
            },
            {
                "key": "stdout_stderr_capture_enabled",
                "title": "stdout/stderr capture enabled",
                "minimum_evidence": "bounded stream capture has safe UI references",
            },
            {
                "key": "runner_event_writer_enabled",
                "title": "Runner event writer enabled",
                "minimum_evidence": "launch, chunk, exit, failure, cancel, and timeout events are structured",
            },
            {
                "key": "audit_persistence_enabled",
                "title": "Audit persistence enabled",
                "minimum_evidence": "append-only audit records exist for authorization and state transitions",
            },
            {
                "key": "cancel_timeout_endpoints_registered",
                "title": "Cancel and timeout endpoints registered",
                "minimum_evidence": "idempotent cancel and deterministic timeout finalization are available",
            },
            {
                "key": "execution_console_ready",
                "title": "Execution console ready",
                "minimum_evidence": "status, logs, cancel, timeout, and result summary are visible",
            },
            {
                "key": "fresh_human_authorization_recorded",
                "title": "Fresh human authorization recorded",
                "minimum_evidence": "a separate explicit authorization round approved real testing",
            },
        ],
        "blocked_actions": [
            "starting a real test",
            "registering POST /api/project/runner/launch",
            "registering cancel or timeout POST APIs",
            "implementing or importing an execution adapter",
            "creating or controlling processes",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _real_test_readiness_report(
    profile: dict[str, Any],
    session_schema_report: dict[str, Any] | None,
    gate_schema: dict[str, object],
) -> dict[str, object]:
    gates = _readiness_gates(gate_schema)
    checks = [
        _check_saved_profile(profile),
        _check_session_state_schema(session_schema_report),
        _check_gates_declared(gates),
        _check_real_test_still_blocked(gates),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_readiness:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "session_state_schema_status": (
            session_schema_report.get("status") if isinstance(session_schema_report, dict) else "missing"
        ),
        "readiness_state": gate_schema["readiness_state"],
        "readiness_gates": gates,
        "blocked_actions": gate_schema["blocked_actions"],
        "launch_state": {
            "launchable": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "can_start_real_test_now": False,
            "reason": "Real testing remains blocked until the runner is implemented in a separate authorized round.",
        },
        "checks": checks,
        "execution_boundary": (
            "Current layer only evaluates real-test readiness. It does not register launch/cancel/timeout APIs, "
            "implement or import adapters, create or control processes, open stdout/stderr streams, write runner events, "
            "read/write logs, write audit logs, collect authorization, grant permission, or modify the user project."
        ),
    }


def _readiness_gates(gate_schema: dict[str, object]) -> list[dict[str, object]]:
    gates = gate_schema.get("required_gates", [])
    if not isinstance(gates, list):
        return []
    result = []
    for item in gates:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "key": item.get("key"),
                "title": item.get("title"),
                "minimum_evidence": item.get("minimum_evidence"),
                "status": "missing",
                "can_execute_now": False,
                "required_before_real_test": True,
            }
        )
    return result


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Real-test readiness requires a saved run profile.")


def _check_session_state_schema(session_schema_report: dict[str, Any] | None) -> dict[str, object]:
    if not session_schema_report:
        return _check(
            "session_state_schema",
            "error",
            "Missing session state schema",
            "Declare the Runner session state schema before real-test readiness can be evaluated.",
        )
    if session_schema_report.get("status") == "session_state_schema_required":
        return _check(
            "session_state_schema",
            "pass",
            "Session state schema declared",
            "Real-test readiness can now aggregate the remaining hard blockers.",
        )
    return _check(
        "session_state_schema",
        "error",
        "Session state schema is blocked",
        str(session_schema_report.get("status") or "unknown"),
    )


def _check_gates_declared(gates: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "implementation_gap_closed",
        "launch_api_registered",
        "execution_adapter_implemented",
        "session_state_persistence_enabled",
        "stdout_stderr_capture_enabled",
        "runner_event_writer_enabled",
        "audit_persistence_enabled",
        "cancel_timeout_endpoints_registered",
        "execution_console_ready",
        "fresh_human_authorization_recorded",
    }
    present = {str(item.get("key")) for item in gates}
    if required.issubset(present):
        return _check("readiness_gates_declared", "pass", "Real-test gates declared", "All minimum real-test gates are explicit.")
    return _check("readiness_gates_declared", "error", "Real-test gates incomplete", "Missing minimum real-test readiness gate.")


def _check_real_test_still_blocked(gates: list[dict[str, object]]) -> dict[str, object]:
    missing = [item for item in gates if item.get("status") != "pass"]
    if missing:
        return _check(
            "real_test_blocked",
            "warn",
            "Real testing remains blocked",
            f"{len(missing)} gates still require implementation evidence and a new authorization round.",
        )
    return _check("real_test_ready", "pass", "Real testing gates passed", "All read-only gates report available evidence.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No launch API, adapter import, subprocess, stream open, runner event write, audit persistence, log access, authorization storage, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if "warn" in statuses:
        return "real_test_blocked"
    return "real_test_ready"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "real_test_blocked" for report in reports):
        return "real_test_blocked"
    return "real_test_ready"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test readiness is blocked",
        "real_test_blocked": "Real testing is still blocked",
        "real_test_ready": "Real testing gates are ready",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the read-only Runner governance chain before evaluating real-test readiness.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix real-test readiness blocker",
                "action": failed.get("detail") or "Complete the prior Runner governance layer first.",
            }
    return {
        "title": "Real testing remains disabled",
        "action": "Implement runner execution, launch/cancel/timeout APIs, stream capture, events, audit persistence, execution console, and a fresh authorization round before any real test.",
    }
