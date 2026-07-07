from __future__ import annotations

from typing import Any


RUNNER_LOG_CLEANUP_EXECUTION_PLAN_VERSION = "project_runner_log_cleanup_execution_plans.v1"
RUNNER_LOG_CLEANUP_EXECUTION_PLAN_SCHEMA_VERSION = "runner_log_cleanup_execution_plan_schema.v1"


def build_project_runner_log_cleanup_execution_plans(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    cleanup_audit_trails: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    audit_trail_by_profile = {
        str(report.get("profile_id")): report
        for report in cleanup_audit_trails.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _cleanup_execution_plan_report(profile, audit_trail_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_CLEANUP_EXECUTION_PLAN_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "execution_plan_required_count": sum(
                1 for report in reports if report["status"] == "cleanup_execution_plan_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "planned_operation_count": 0,
            "stored_plan_count": 0,
            "launchable_count": 0,
        },
        "cleanup_execution_plan_schema": log_cleanup_execution_plan_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "cleanup_execution_plan_only": True,
            "stores_execution_plan": False,
            "executes_cleanup": False,
            "generates_candidate_manifest": False,
            "stores_candidate_manifest": False,
            "reads_candidate_manifest": False,
            "stores_audit_events": False,
            "writes_audit_log": False,
            "reads_audit_log": False,
            "scans_log_directory": False,
            "reads_log_files": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "renames_logs": False,
            "truncates_logs": False,
            "writes_logs": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def log_cleanup_execution_plan_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_CLEANUP_EXECUTION_PLAN_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "plan_state": {
            "write_now": False,
            "read_now": False,
            "execute_now": False,
        },
        "candidate_manifest": {
            "generate_now": False,
            "store_now": False,
            "read_now": False,
            "requires_hash": True,
            "hash_algorithm": "sha256",
        },
        "allowed_future_operation_types": [
            "delete_listed_log_file",
            "rotate_listed_log_file",
        ],
        "forbidden_future_operation_types": [
            "delete_directory",
            "recursive_delete",
            "truncate_log_file",
            "write_log_file",
            "rename_unlisted_file",
        ],
        "required_future_plan_fields": [
            "plan_id",
            "created_at",
            "profile_id",
            "run_profile_fingerprint",
            "trace_dir",
            "candidate_manifest_hash",
            "confirmation_id",
            "audit_sink",
            "operation_type",
            "target_path",
            "rollback_note",
            "risk_level",
        ],
        "required_future_gates": [
            "cleanup_preview_required",
            "cleanup_confirmation_required",
            "cleanup_audit_trail_required",
            "candidate_manifest_hash_required",
            "typed_consent_required",
            "audit_event_before_each_operation",
            "audit_event_after_each_operation",
        ],
        "blocked_actions": [
            "Path.iterdir",
            "Path.stat",
            "Path.read_text(log_file)",
            "Path.write_text",
            "Path.unlink",
            "Path.rename",
            "shutil.rmtree",
            "open(audit_log, append)",
            "persist cleanup execution plan",
            "execute cleanup plan",
            "launch POST API registration",
        ],
    }


def _cleanup_execution_plan_report(
    profile: dict[str, Any],
    cleanup_audit_trail_report: dict[str, Any] | None,
) -> dict[str, object]:
    schema = log_cleanup_execution_plan_schema()
    checks = [
        _check_saved_profile(profile),
        _check_cleanup_audit_trail(cleanup_audit_trail_report),
        _check_plan_schema_declared(schema),
        _check_candidate_manifest_contract(schema),
        _check_no_plan_storage(),
        _check_no_filesystem_inspection(),
        _check_no_cleanup_mutation(),
        _check_no_audit_persistence(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_log_cleanup_execution_plan:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "cleanup_audit_trail_status": (
            cleanup_audit_trail_report.get("status") if isinstance(cleanup_audit_trail_report, dict) else "missing"
        ),
        "plan_state": {
            "status": "not_planned",
            "stored": False,
            "operation_count": 0,
            "can_execute_now": False,
            "reason": "This layer only declares the future cleanup execution plan contract.",
        },
        "candidate_manifest": schema["candidate_manifest"],
        "allowed_future_operation_types": schema["allowed_future_operation_types"],
        "forbidden_future_operation_types": schema["forbidden_future_operation_types"],
        "required_future_plan_fields": schema["required_future_plan_fields"],
        "required_future_gates": schema["required_future_gates"],
        "planned_operations": [],
        "checks": checks,
        "execution_boundary": (
            "Current layer only declares a future cleanup execution plan. It does not scan directories, read log files, "
            "generate a candidate manifest, persist a plan, write audit logs, delete, rotate, rename, truncate, write logs, "
            "execute commands, create processes, or expose a launch API."
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Cleanup execution planning requires a saved run profile.")


def _check_cleanup_audit_trail(cleanup_audit_trail_report: dict[str, Any] | None) -> dict[str, object]:
    if not cleanup_audit_trail_report:
        return _check("cleanup_audit_trail", "error", "Missing cleanup audit trail report", "Generate the cleanup audit trail read-only report first.")
    if cleanup_audit_trail_report.get("status") == "cleanup_audit_trail_required":
        return _check("cleanup_audit_trail", "pass", "Cleanup audit trail requirements declared", "Execution planning remains read-only.")
    return _check(
        "cleanup_audit_trail",
        "error",
        "Cleanup audit trail is blocked",
        str(cleanup_audit_trail_report.get("status") or "unknown"),
    )


def _check_plan_schema_declared(schema: dict[str, object]) -> dict[str, object]:
    fields = schema.get("required_future_plan_fields")
    if isinstance(fields, list) and {"plan_id", "candidate_manifest_hash", "operation_type"}.issubset(set(fields)):
        return _check("plan_schema", "pass", "Execution plan schema declared", "Future cleanup operations must be structured and auditable.")
    return _check("plan_schema", "error", "Execution plan schema incomplete", "Required future fields are missing.")


def _check_candidate_manifest_contract(schema: dict[str, object]) -> dict[str, object]:
    manifest = schema.get("candidate_manifest")
    if isinstance(manifest, dict) and manifest.get("requires_hash") and not manifest.get("generate_now"):
        return _check("candidate_manifest_contract", "pass", "Candidate manifest contract declared", "Current layer does not generate or read a real manifest.")
    return _check("candidate_manifest_contract", "error", "Candidate manifest contract unsafe", "The manifest must require a hash and remain read-only now.")


def _check_no_plan_storage() -> dict[str, object]:
    return _check("no_plan_storage", "pass", "No execution plan storage", "This layer does not persist cleanup plans or operation manifests.")


def _check_no_filesystem_inspection() -> dict[str, object]:
    return _check("no_filesystem_inspection", "pass", "No filesystem inspection", "No directory listing, stat, or log file read is performed.")


def _check_no_cleanup_mutation() -> dict[str, object]:
    return _check("no_cleanup_mutation", "pass", "No cleanup mutation", "Delete, rotate, rename, truncate, and write operations remain disabled.")


def _check_no_audit_persistence() -> dict[str, object]:
    return _check("no_audit_persistence", "pass", "No audit persistence", "Audit events are not stored, read, or appended by this layer.")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "cleanup_execution_plan_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "cleanup_execution_plan_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Cleanup execution planning is blocked",
        "cleanup_execution_plan_required": "Cleanup execution plan contract required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete cleanup audit trail requirements before declaring cleanup execution plans.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix cleanup execution plan blocker",
                "action": failed.get("detail") or "Complete prerequisite cleanup governance layers first.",
            }
    return {
        "title": "Cleanup execution plan contract declared",
        "action": "Continue with read-only governance only; real cleanup execution, file scanning, and audit-log persistence remain disabled.",
    }
