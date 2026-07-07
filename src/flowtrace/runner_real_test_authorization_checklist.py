from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_AUTHORIZATION_CHECKLIST_VERSION = "project_runner_real_test_authorization_checklists.v1"
RUNNER_REAL_TEST_AUTHORIZATION_SCHEMA_VERSION = "runner_real_test_authorization_checklist_schema.v1"


def build_project_runner_real_test_authorization_checklists(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_readiness: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    readiness_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_readiness.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    checklist_schema = runner_real_test_authorization_checklist_schema()
    reports = [
        _authorization_checklist_report(
            profile,
            readiness_by_profile.get(str(profile.get("id"))),
            checklist_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_AUTHORIZATION_CHECKLIST_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "authorization_required_count": sum(
                1 for report in reports if report["status"] == "authorization_checklist_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "check_item_count": sum(len(report.get("authorization_items", [])) for report in reports),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("authorization_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "collected_authorization_count": 0,
            "permission_granted_count": 0,
            "launchable_count": 0,
        },
        "authorization_checklist_schema": checklist_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "authorization_checklist_only": True,
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
            "reads_log_files": False,
            "writes_logs": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "renames_logs": False,
            "truncates_logs": False,
            "scans_log_directory": False,
            "writes_audit_log": False,
            "reads_audit_log": False,
            "collects_human_authorization": False,
            "stores_authorization": False,
            "grants_permission": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def runner_real_test_authorization_checklist_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_TEST_AUTHORIZATION_SCHEMA_VERSION,
        "authorization_state": {
            "read_only": True,
            "authorization_collected_now": False,
            "authorization_stored_now": False,
            "permission_granted_now": False,
            "can_launch_now": False,
        },
        "required_authorization_records": [
            "human_authorization_round_id",
            "operator_identity",
            "target_project_root",
            "run_profile_id",
            "launch_snapshot_id",
            "typed_real_test_consent",
            "risk_acknowledgement",
            "rollback_or_stop_plan",
            "audit_log_destination",
            "approval_timestamp",
        ],
        "required_evidence_from_readiness": True,
        "blocked_actions": [
            "collecting human authorization",
            "storing authorization records",
            "granting launch permission",
            "registering launch/cancel/timeout POST APIs",
            "starting a target project process",
            "calling execution adapters",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _authorization_checklist_report(
    profile: dict[str, Any],
    readiness_report: dict[str, Any] | None,
    checklist_schema: dict[str, object],
) -> dict[str, object]:
    authorization_items = _authorization_items(readiness_report)
    checks = [
        _check_saved_profile(profile),
        _check_real_test_readiness(readiness_report),
        _check_authorization_records_declared(checklist_schema),
        _check_authorization_items_declared(authorization_items),
        _check_no_authorization_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_authorization_checklist:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "real_test_readiness_status": readiness_report.get("status") if isinstance(readiness_report, dict) else "missing",
        "authorization_state": checklist_schema["authorization_state"],
        "required_authorization_records": checklist_schema["required_authorization_records"],
        "authorization_items": authorization_items,
        "blocked_actions": checklist_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only lists future real-test authorization evidence. It does not collect or store authorization, "
            "grant launch permission, register launch/cancel/timeout APIs, start processes, call adapters, open streams, "
            "write runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _authorization_items(readiness_report: dict[str, Any] | None) -> list[dict[str, object]]:
    readiness_gates = []
    if isinstance(readiness_report, dict):
        readiness_gates = [item for item in readiness_report.get("readiness_gates", []) if isinstance(item, dict)]
    result = []
    for gate in readiness_gates:
        result.append(
            {
                "key": gate.get("key"),
                "title": gate.get("title"),
                "minimum_evidence": gate.get("minimum_evidence"),
                "source_status": gate.get("status"),
                "evidence_status": "missing",
                "authorization_required": True,
                "authorization_collected_now": False,
                "permission_granted_now": False,
            }
        )
    return result


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Authorization checklist requires a saved run profile.")


def _check_real_test_readiness(readiness_report: dict[str, Any] | None) -> dict[str, object]:
    if not readiness_report:
        return _check(
            "real_test_readiness",
            "error",
            "Missing real-test readiness report",
            "Generate the real-test readiness report before authorization checklist.",
        )
    if readiness_report.get("status") == "real_test_blocked":
        return _check(
            "real_test_readiness",
            "pass",
            "Real-test blockers declared",
            "Authorization checklist can enumerate the future evidence items.",
        )
    return _check(
        "real_test_readiness",
        "error",
        "Real-test readiness status is unexpected",
        str(readiness_report.get("status") or "unknown"),
    )


def _check_authorization_records_declared(checklist_schema: dict[str, object]) -> dict[str, object]:
    records = checklist_schema.get("required_authorization_records")
    required = {"human_authorization_round_id", "typed_real_test_consent", "risk_acknowledgement"}
    if isinstance(records, list) and required.issubset({str(item) for item in records}):
        return _check("authorization_records_declared", "pass", "Authorization records declared", "Future approval records are explicit.")
    return _check("authorization_records_declared", "error", "Authorization records incomplete", "Missing minimum authorization records.")


def _check_authorization_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {"launch_api_registered", "execution_adapter_implemented", "fresh_human_authorization_recorded"}
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("authorization_items_declared", "pass", "Authorization evidence items declared", "Readiness gates are mirrored for future authorization.")
    return _check("authorization_items_declared", "error", "Authorization evidence incomplete", "Missing real-test authorization evidence items.")


def _check_no_authorization_or_execution() -> dict[str, object]:
    return _check(
        "no_authorization_or_execution",
        "pass",
        "No authorization or execution",
        "No authorization collection, permission grant, launch API, adapter call, subprocess, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "authorization_checklist_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "authorization_checklist_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test authorization checklist is blocked",
        "authorization_checklist_required": "Real-test authorization evidence is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete real-test readiness before reviewing authorization evidence.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix authorization checklist blocker",
                "action": failed.get("detail") or "Complete real-test readiness first.",
            }
    return {
        "title": "Authorization checklist remains read-only",
        "action": "Review the listed evidence in a future explicit authorization round before any real test can be enabled.",
    }
