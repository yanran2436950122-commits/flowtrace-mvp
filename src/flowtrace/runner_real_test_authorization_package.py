from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_AUTHORIZATION_PACKAGE_VERSION = "project_runner_real_test_authorization_packages.v1"
RUNNER_REAL_TEST_AUTHORIZATION_PACKAGE_SCHEMA_VERSION = "runner_real_test_authorization_package_schema.v1"


def build_project_runner_real_test_authorization_packages(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_authorization_checklists: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    checklist_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_authorization_checklists.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    package_schema = runner_real_test_authorization_package_schema()
    reports = [
        _authorization_package_report(
            profile,
            checklist_by_profile.get(str(profile.get("id"))),
            package_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_AUTHORIZATION_PACKAGE_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "authorization_package_required_count": sum(
                1 for report in reports if report["status"] == "authorization_package_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "review_item_count": sum(len(report.get("review_items", [])) for report in reports),
            "risk_acknowledgement_count": sum(
                len(report.get("risk_acknowledgements", [])) for report in reports
            ),
            "required_record_count": sum(
                len(report.get("required_authorization_records", [])) for report in reports
            ),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("review_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "collected_authorization_count": 0,
            "stored_authorization_count": 0,
            "permission_granted_count": 0,
            "launchable_count": 0,
        },
        "authorization_package_schema": package_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_test_authorization_package_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_TEST_AUTHORIZATION_PACKAGE_SCHEMA_VERSION,
        "package_state": {
            "read_only": True,
            "authorization_collected_now": False,
            "authorization_stored_now": False,
            "permission_granted_now": False,
            "can_launch_now": False,
            "requires_future_explicit_authorization": True,
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
        "risk_acknowledgements": [
            _risk_acknowledgement(
                "process_creation",
                "Target process creation",
                "Future real testing will create a target process only after explicit authorization.",
            ),
            _risk_acknowledgement(
                "command_execution",
                "Command execution",
                "Future real testing will execute the selected profile command only in an authorized round.",
            ),
            _risk_acknowledgement(
                "stream_capture",
                "stdout/stderr capture",
                "Future real testing will capture bounded process output with retention and redaction rules.",
            ),
            _risk_acknowledgement(
                "event_and_audit_writes",
                "Runner event and audit writes",
                "Future real testing will persist execution facts to declared event and audit destinations.",
            ),
            _risk_acknowledgement(
                "cancel_timeout_control",
                "Cancel and timeout control",
                "Future real testing requires an operator-visible stop plan before launch can be enabled.",
            ),
        ],
        "blocked_actions": [
            "collecting human authorization",
            "storing authorization records",
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


def _authorization_package_report(
    profile: dict[str, Any],
    authorization_report: dict[str, Any] | None,
    package_schema: dict[str, object],
) -> dict[str, object]:
    review_items = _review_items(authorization_report)
    checks = [
        _check_saved_profile(profile),
        _check_authorization_checklist(authorization_report),
        _check_required_records(package_schema),
        _check_risk_acknowledgements(package_schema),
        _check_review_items(review_items),
        _check_no_authorization_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_authorization_package:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "authorization_checklist_status": (
            authorization_report.get("status") if isinstance(authorization_report, dict) else "missing"
        ),
        "package_state": package_schema["package_state"],
        "required_authorization_records": package_schema["required_authorization_records"],
        "risk_acknowledgements": package_schema["risk_acknowledgements"],
        "review_items": review_items,
        "blocked_actions": package_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only prepares a future real-test authorization review package. It does not collect or store "
            "authorization, grant launch permission, register launch/cancel/timeout APIs, execute commands, start "
            "processes, call adapters, open stdout/stderr, write runner events, read/write logs, write audit logs, or "
            "modify the user project."
        ),
    }


def _review_items(authorization_report: dict[str, Any] | None) -> list[dict[str, object]]:
    items = []
    if isinstance(authorization_report, dict):
        items = [item for item in authorization_report.get("authorization_items", []) if isinstance(item, dict)]
    return [
        {
            "key": item.get("key"),
            "title": item.get("title"),
            "minimum_evidence": item.get("minimum_evidence"),
            "source_status": item.get("source_status"),
            "evidence_status": item.get("evidence_status") or "missing",
            "authorization_required": True,
            "included_in_authorization_package": True,
            "authorization_collected_now": False,
            "permission_granted_now": False,
        }
        for item in items
    ]


def _risk_acknowledgement(key: str, title: str, detail: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "detail": detail,
        "acknowledged_now": False,
        "required_before_real_test": True,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Authorization package requires a saved run profile.")


def _check_authorization_checklist(authorization_report: dict[str, Any] | None) -> dict[str, object]:
    if not authorization_report:
        return _check(
            "authorization_checklist",
            "error",
            "Missing authorization checklist",
            "Generate the real-test authorization checklist before preparing the authorization package.",
        )
    if authorization_report.get("status") == "authorization_checklist_required":
        return _check(
            "authorization_checklist",
            "pass",
            "Authorization checklist declared",
            "Future authorization evidence can be packaged for review.",
        )
    return _check(
        "authorization_checklist",
        "error",
        "Authorization checklist status is unexpected",
        str(authorization_report.get("status") or "unknown"),
    )


def _check_required_records(package_schema: dict[str, object]) -> dict[str, object]:
    records = package_schema.get("required_authorization_records")
    required = {
        "human_authorization_round_id",
        "operator_identity",
        "typed_real_test_consent",
        "risk_acknowledgement",
        "rollback_or_stop_plan",
    }
    if isinstance(records, list) and required.issubset({str(item) for item in records}):
        return _check("required_records_declared", "pass", "Authorization records declared", "Future package records are explicit.")
    return _check("required_records_declared", "error", "Authorization records incomplete", "Missing minimum authorization package records.")


def _check_risk_acknowledgements(package_schema: dict[str, object]) -> dict[str, object]:
    risks = package_schema.get("risk_acknowledgements")
    required = {"process_creation", "command_execution", "stream_capture", "event_and_audit_writes"}
    present = {str(item.get("key")) for item in risks if isinstance(item, dict)} if isinstance(risks, list) else set()
    if required.issubset(present):
        return _check("risk_acknowledgements_declared", "pass", "Risk acknowledgements declared", "Future operator risk prompts are explicit.")
    return _check("risk_acknowledgements_declared", "error", "Risk acknowledgements incomplete", "Missing minimum real-test risk acknowledgements.")


def _check_review_items(items: list[dict[str, object]]) -> dict[str, object]:
    required = {"launch_api_registered", "execution_adapter_implemented", "fresh_human_authorization_recorded"}
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("review_items_declared", "pass", "Authorization review items declared", "Readiness evidence is included in the package.")
    return _check("review_items_declared", "error", "Authorization package review items incomplete", "Missing real-test review items.")


def _check_no_authorization_or_execution() -> dict[str, object]:
    return _check(
        "no_authorization_or_execution",
        "pass",
        "No authorization or execution",
        "No authorization collection, authorization storage, permission grant, command execution, launch API, adapter call, subprocess, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "authorization_package_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "authorization_package_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test authorization package is blocked",
        "authorization_package_required": "Real-test authorization package is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the authorization checklist before preparing an authorization package.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix authorization package blocker",
                "action": failed.get("detail") or "Complete the authorization checklist first.",
            }
    return {
        "title": "Authorization package remains read-only",
        "action": "Review this package in a future explicit authorization round; no launch permission is granted now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "authorization_package_only": True,
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
        "deletes_logs": False,
        "rotates_logs": False,
        "renames_logs": False,
        "truncates_logs": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
        "creates_config_file": False,
    }
