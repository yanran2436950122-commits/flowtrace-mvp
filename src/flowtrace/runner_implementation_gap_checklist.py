from __future__ import annotations

from typing import Any


RUNNER_IMPLEMENTATION_GAP_CHECKLIST_VERSION = "project_runner_implementation_gap_checklists.v1"
RUNNER_IMPLEMENTATION_GAP_CHECKLIST_SCHEMA_VERSION = "runner_implementation_gap_checklist_schema.v1"


def build_project_runner_implementation_gap_checklists(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    authorization_unlock_audits: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    authorization_by_profile = {
        str(report.get("profile_id")): report
        for report in authorization_unlock_audits.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    checklist_schema = runner_implementation_gap_checklist_schema()
    reports = [
        _implementation_gap_report(profile, authorization_by_profile.get(str(profile.get("id"))), checklist_schema)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_IMPLEMENTATION_GAP_CHECKLIST_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "implementation_required_count": sum(
                1 for report in reports if report["status"] == "implementation_gap_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "component_count": sum(len(report.get("implementation_components", [])) for report in reports),
            "gap_count": sum(
                1
                for report in reports
                for item in report.get("implementation_components", [])
                if item.get("implementation_status") == "missing"
            ),
            "launchable_count": 0,
        },
        "implementation_gap_schema": checklist_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "implementation_gap_checklist_only": True,
            "implements_runner": False,
            "writes_code": False,
            "registers_post_api": False,
            "imports_adapter": False,
            "calls_execution_adapter": False,
            "grants_permission": False,
            "collects_human_authorization": False,
            "stores_authorization": False,
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


def runner_implementation_gap_checklist_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_IMPLEMENTATION_GAP_CHECKLIST_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "checklist_state": {
            "read_only": True,
            "implements_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_components": [
            {
                "key": "execution_adapter",
                "title": "Execution adapter implementation",
                "required_before_real_test": True,
                "minimum_evidence": "tokenized argv process adapter with shell strings rejected",
            },
            {
                "key": "launch_post_api",
                "title": "Launch POST API implementation",
                "required_before_real_test": True,
                "minimum_evidence": "idempotent launch endpoint guarded by profile, snapshot, and authorization checks",
            },
            {
                "key": "runner_session_state",
                "title": "Runner session state persistence",
                "required_before_real_test": True,
                "minimum_evidence": "pending/running/completed/failed/cancelled/timeout states persisted",
            },
            {
                "key": "stdout_stderr_streams",
                "title": "stdout/stderr stream capture",
                "required_before_real_test": True,
                "minimum_evidence": "bounded stdout/stderr chunk capture and UI-readable stream state",
            },
            {
                "key": "runner_event_log",
                "title": "Runner event log writer",
                "required_before_real_test": True,
                "minimum_evidence": "structured runner events for launch, chunks, exit, failure, cancel, and timeout",
            },
            {
                "key": "cancel_timeout_endpoints",
                "title": "Cancel and timeout endpoints",
                "required_before_real_test": True,
                "minimum_evidence": "idempotent cancel and deterministic timeout finalization",
            },
            {
                "key": "audit_persistence",
                "title": "Audit persistence",
                "required_before_real_test": True,
                "minimum_evidence": "append-only audit events for authorization, launch, cancel, timeout, and completion",
            },
            {
                "key": "execution_console_ui",
                "title": "Execution console UI",
                "required_before_real_test": True,
                "minimum_evidence": "status, blockers, logs, cancel, timeout, and result summary visible to the user",
            },
        ],
        "blocked_actions": [
            "implementing runner adapter in this layer",
            "registering POST /api/project/runner/launch",
            "starting target project process",
            "calling execution adapter",
            "opening stdout/stderr files",
            "writing runner event logs",
            "writing audit logs",
            "writing user project files",
        ],
    }


def _implementation_gap_report(
    profile: dict[str, Any],
    authorization_report: dict[str, Any] | None,
    checklist_schema: dict[str, object],
) -> dict[str, object]:
    components = _implementation_components(checklist_schema)
    checks = [
        _check_saved_profile(profile),
        _check_authorization_audit(authorization_report),
        _check_components_declared(components),
        _check_no_implementation(),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_implementation_gap_checklist:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "authorization_unlock_audit_status": (
            authorization_report.get("status") if isinstance(authorization_report, dict) else "missing"
        ),
        "implementation_state": {
            "runner_implemented_now": False,
            "launch_api_registered_now": False,
            "can_start_real_test_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "implementation_components": components,
        "blocked_actions": checklist_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only lists implementation gaps before real Runner work. It does not implement a runner, "
            "register launch APIs, load or call adapters, create processes, execute commands, open stdout/stderr files, "
            "write runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _implementation_components(checklist_schema: dict[str, object]) -> list[dict[str, object]]:
    components = checklist_schema.get("required_components", [])
    if not isinstance(components, list):
        return []
    result = []
    for item in components:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "key": item.get("key"),
                "title": item.get("title"),
                "required_before_real_test": bool(item.get("required_before_real_test")),
                "minimum_evidence": item.get("minimum_evidence"),
                "implementation_status": "missing",
                "evidence_status": "missing",
                "can_execute_now": False,
            }
        )
    return result


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Implementation gap checklist requires a saved run profile.")


def _check_authorization_audit(authorization_report: dict[str, Any] | None) -> dict[str, object]:
    if not authorization_report:
        return _check("authorization_unlock_audit", "error", "Missing authorization unlock audit", "Generate the authorization unlock audit first.")
    if authorization_report.get("status") == "authorization_unlock_required":
        return _check("authorization_unlock_audit", "pass", "Authorization audit declared", "Implementation gaps can be listed read-only.")
    return _check(
        "authorization_unlock_audit",
        "error",
        "Authorization unlock audit is blocked",
        str(authorization_report.get("status") or "unknown"),
    )


def _check_components_declared(components: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "execution_adapter",
        "launch_post_api",
        "runner_session_state",
        "stdout_stderr_streams",
        "runner_event_log",
        "cancel_timeout_endpoints",
        "audit_persistence",
        "execution_console_ui",
    }
    present = {str(item.get("key")) for item in components}
    if required.issubset(present):
        return _check("components_declared", "pass", "Implementation components declared", "All minimum real-test gaps are explicit.")
    return _check("components_declared", "error", "Implementation components incomplete", "Missing minimum real-test components.")


def _check_no_implementation() -> dict[str, object]:
    return _check("no_implementation", "pass", "No implementation in this layer", "This layer only reports gaps and writes no runner code.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No launch API, adapter call, subprocess, log write, audit persistence, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "implementation_gap_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "implementation_gap_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Implementation gap checklist is blocked",
        "implementation_gap_required": "Runner implementation gaps remain before real testing",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and generate authorization unlock audits before listing implementation gaps.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix implementation gap checklist blocker",
                "action": failed.get("detail") or "Complete the authorization unlock audit first.",
            }
    return {
        "title": "Real testing still needs implementation work",
        "action": "Implement the runner adapter, launch API, streams, events, cancel/timeout, audit persistence, and execution console in a separate authorized round.",
    }
