from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_FINAL_CHECKLIST_VERSION = "project_runner_real_test_final_checklists.v1"
RUNNER_REAL_TEST_FINAL_CHECKLIST_SCHEMA_VERSION = "runner_real_test_final_checklist_schema.v1"


def build_project_runner_real_test_final_checklists(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_sandbox_policies: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    sandbox_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_sandbox_policies.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    checklist_schema = runner_real_test_final_checklist_schema()
    reports = [
        _final_checklist_report(
            profile,
            sandbox_by_profile.get(str(profile.get("id"))),
            checklist_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_FINAL_CHECKLIST_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "final_checklist_required_count": sum(
                1 for report in reports if report["status"] == "final_checklist_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "check_item_count": sum(len(report.get("checklist_items", [])) for report in reports),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("checklist_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "passed_item_count": 0,
            "launchable_count": 0,
        },
        "final_checklist_schema": checklist_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_test_final_checklist_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_TEST_FINAL_CHECKLIST_SCHEMA_VERSION,
        "checklist_state": {
            "read_only": True,
            "checklist_completed_now": False,
            "can_launch_now": False,
            "requires_future_explicit_authorization": True,
        },
        "required_sections": [
            _section("configuration", "Runner configuration and compatibility evidence"),
            _section("authorization", "Human authorization package and risk acknowledgement evidence"),
            _section("sandbox", "Workspace, environment, timeout, log, and permission policy evidence"),
            _section("process_lifecycle", "Process lifecycle, cancellation, timeout, and terminal-state evidence"),
            _section("stream_capture", "stdout/stderr capture, redaction, retention, and backpressure evidence"),
            _section("events_and_audit", "Runner event writer, audit persistence, integrity, and replay evidence"),
            _section("ui_and_operator_controls", "Launch-disabled UI, cancel/timeout controls, and operator preview evidence"),
            _section("safety_boundaries", "No accidental launch API, process, adapter, stream, log, audit, or project-write behavior"),
        ],
        "blocked_actions": [
            "marking checklist complete",
            "granting launch permission",
            "registering launch/cancel/timeout POST APIs",
            "starting a target project process",
            "executing commands",
            "calling execution adapters",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _final_checklist_report(
    profile: dict[str, Any],
    sandbox_report: dict[str, Any] | None,
    checklist_schema: dict[str, object],
) -> dict[str, object]:
    items = _checklist_items(checklist_schema, sandbox_report)
    checks = [
        _check_saved_profile(profile),
        _check_sandbox_policy(sandbox_report),
        _check_sections_declared(items),
        _check_checklist_not_completed(checklist_schema),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_final_checklist:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "sandbox_policy_status": sandbox_report.get("status") if isinstance(sandbox_report, dict) else "missing",
        "authorization_package_status": (
            sandbox_report.get("authorization_package_status") if isinstance(sandbox_report, dict) else "missing"
        ),
        "authorization_checklist_status": (
            sandbox_report.get("authorization_checklist_status") if isinstance(sandbox_report, dict) else "missing"
        ),
        "checklist_state": checklist_schema["checklist_state"],
        "checklist_items": items,
        "blocked_actions": checklist_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only assembles the future real-test final checklist. It does not mark the checklist complete, "
            "grant launch permission, register launch/cancel/timeout APIs, execute commands, start processes, call "
            "adapters, open stdout/stderr, write runner events, read/write logs, write audit logs, or modify the user "
            "project."
        ),
    }


def _checklist_items(
    checklist_schema: dict[str, object],
    sandbox_report: dict[str, Any] | None,
) -> list[dict[str, object]]:
    sandbox_status = sandbox_report.get("status") if isinstance(sandbox_report, dict) else "missing"
    sections = [item for item in checklist_schema.get("required_sections", []) if isinstance(item, dict)]
    return [
        {
            **section,
            "source_status": sandbox_status,
            "evidence_status": "missing",
            "passed_now": False,
            "required_before_real_test": True,
        }
        for section in sections
    ]


def _section(key: str, title: str) -> dict[str, object]:
    return {"key": key, "title": title}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Final checklist requires a saved run profile.")


def _check_sandbox_policy(sandbox_report: dict[str, Any] | None) -> dict[str, object]:
    if not sandbox_report:
        return _check(
            "sandbox_policy",
            "error",
            "Missing sandbox policy",
            "Generate the real-test sandbox policy before the final checklist.",
        )
    if sandbox_report.get("status") == "sandbox_policy_required":
        return _check(
            "sandbox_policy",
            "pass",
            "Sandbox policy declared",
            "Final checklist can now aggregate the pre-test evidence boundary.",
        )
    return _check(
        "sandbox_policy",
        "error",
        "Sandbox policy status is unexpected",
        str(sandbox_report.get("status") or "unknown"),
    )


def _check_sections_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "configuration",
        "authorization",
        "sandbox",
        "process_lifecycle",
        "stream_capture",
        "events_and_audit",
        "ui_and_operator_controls",
        "safety_boundaries",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("checklist_sections_declared", "pass", "Final checklist sections declared", "All minimum pre-test sections are explicit.")
    return _check("checklist_sections_declared", "error", "Final checklist incomplete", "Missing minimum real-test checklist sections.")


def _check_checklist_not_completed(checklist_schema: dict[str, object]) -> dict[str, object]:
    state = checklist_schema.get("checklist_state")
    if isinstance(state, dict) and not state.get("checklist_completed_now") and not state.get("can_launch_now"):
        return _check("checklist_not_completed", "pass", "Checklist is read-only", "No completion or launch permission is granted.")
    return _check("checklist_not_completed", "error", "Checklist was completed", "This layer must remain read-only.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No checklist completion, permission grant, command execution, subprocess, adapter call, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "final_checklist_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "final_checklist_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test final checklist is blocked",
        "final_checklist_required": "Real-test final checklist is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and prepare the sandbox policy before reviewing the final checklist.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix final checklist blocker",
                "action": failed.get("detail") or "Complete the sandbox policy first.",
            }
    return {
        "title": "Final checklist remains read-only",
        "action": "Use these sections as the future real-test preflight checklist; no launch permission is granted now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "final_checklist_only": True,
        "marks_checklist_complete": False,
        "grants_launch_permission": False,
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
        "opens_stdout_stderr": False,
        "writes_runner_events": False,
        "scans_log_directory": False,
        "reads_log_files": False,
        "writes_logs": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
        "creates_config_file": False,
    }
