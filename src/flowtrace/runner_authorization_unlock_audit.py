from __future__ import annotations

from typing import Any


RUNNER_AUTHORIZATION_UNLOCK_AUDIT_VERSION = "project_runner_authorization_unlock_audits.v1"
RUNNER_AUTHORIZATION_UNLOCK_AUDIT_SCHEMA_VERSION = "runner_authorization_unlock_audit_schema.v1"


def build_project_runner_authorization_unlock_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    final_block_matrices: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    final_by_profile = {
        str(report.get("profile_id")): report
        for report in final_block_matrices.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_authorization_unlock_audit_schema()
    reports = [
        _authorization_unlock_report(profile, final_by_profile.get(str(profile.get("id"))), audit_schema)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_AUTHORIZATION_UNLOCK_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "authorization_required_count": sum(
                1 for report in reports if report["status"] == "authorization_unlock_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "future_unlock_count": sum(len(report.get("unlock_items", [])) for report in reports),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("unlock_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "launchable_count": 0,
        },
        "authorization_audit_schema": audit_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "authorization_unlock_audit_only": True,
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


def runner_authorization_unlock_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_AUTHORIZATION_UNLOCK_AUDIT_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "audit_state": {
            "read_only": True,
            "authorization_collected_now": False,
            "permission_granted_now": False,
            "can_unlock_now": False,
        },
        "required_authorization_records": [
            "human authorization round id",
            "operator identity",
            "approved profile id",
            "approved launch snapshot id",
            "typed consent phrase",
            "approval timestamp",
            "scope of permission",
            "revocation policy",
        ],
        "required_evidence": [
            "implemented execution adapter review",
            "registered launch POST API review",
            "service flag enabled review",
            "valid runner config check",
            "fresh launch snapshot",
            "stdout/stderr sink review",
            "runner event writer review",
            "audit-log persistence review",
            "cancel and timeout endpoint review",
        ],
        "unlock_item_states": [
            "missing",
            "declared_only",
            "future_review_required",
        ],
        "blocked_actions": [
            "collecting or storing human authorization",
            "granting launch permission",
            "registering POST /api/project/runner/launch",
            "loading execution adapter",
            "calling execution adapter",
            "creating subprocess",
            "opening stdout/stderr files",
            "writing runner events",
            "writing audit logs",
            "writing user project files",
        ],
    }


def _authorization_unlock_report(
    profile: dict[str, Any],
    final_block_report: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    unlocks = _unlock_items(final_block_report, audit_schema)
    checks = [
        _check_saved_profile(profile),
        _check_final_block_matrix(final_block_report),
        _check_authorization_not_collected(),
        _check_no_permission_grant(),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_authorization_unlock_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "final_block_matrix_status": (
            final_block_report.get("status") if isinstance(final_block_report, dict) else "missing"
        ),
        "authorization_state": {
            "authorization_collected_now": False,
            "permission_granted_now": False,
            "can_unlock_now": False,
            "authorization_storage": "not_implemented",
        },
        "unlock_items": unlocks,
        "required_authorization_records": audit_schema["required_authorization_records"],
        "required_evidence": audit_schema["required_evidence"],
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits future authorization and unlock evidence. It does not collect authorization, "
            "grant launch permission, register launch APIs, load or call adapters, create processes, execute commands, "
            "read/write logs, write audit logs, or modify the user project."
        ),
    }


def _unlock_items(final_block_report: dict[str, Any] | None, audit_schema: dict[str, object]) -> list[dict[str, object]]:
    future_unlocks = []
    if isinstance(final_block_report, dict):
        future_unlocks = [
            str(item) for item in final_block_report.get("required_future_unlocks", []) if str(item).strip()
        ]
    if not future_unlocks:
        future_unlocks = [str(item) for item in audit_schema.get("required_evidence", [])]
    return [
        {
            "key": _normalize_key(item),
            "title": item,
            "state": "future_review_required",
            "evidence_status": "missing",
            "authorization_status": "not_collected",
            "can_unlock_now": False,
        }
        for item in future_unlocks
    ]


def _normalize_key(value: str) -> str:
    return "_".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Authorization audit requires a saved run profile.")


def _check_final_block_matrix(final_block_report: dict[str, Any] | None) -> dict[str, object]:
    if not final_block_report:
        return _check("final_block_matrix", "error", "Missing final block matrix", "Generate the final block matrix first.")
    if final_block_report.get("status") == "final_block_required":
        return _check("final_block_matrix", "pass", "Final blockers declared", "Authorization unlock audit can remain read-only.")
    return _check(
        "final_block_matrix",
        "error",
        "Final block matrix is blocked",
        str(final_block_report.get("status") or "unknown"),
    )


def _check_authorization_not_collected() -> dict[str, object]:
    return _check(
        "authorization_not_collected",
        "pass",
        "Authorization is not collected",
        "This layer only lists required future authorization records.",
    )


def _check_no_permission_grant() -> dict[str, object]:
    return _check("no_permission_grant", "pass", "No permission grant", "No current state can unlock real launch.")


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
    return "authorization_unlock_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "authorization_unlock_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Authorization unlock audit is blocked",
        "authorization_unlock_required": "Authorization and unlock evidence are still required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and generate final block matrices before auditing authorization unlocks.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix authorization audit blocker",
                "action": failed.get("detail") or "Complete the final block matrix first.",
            }
    return {
        "title": "Authorization unlock remains read-only",
        "action": "A separate implementation and explicit human authorization round are required before any launch permission can be granted.",
    }
