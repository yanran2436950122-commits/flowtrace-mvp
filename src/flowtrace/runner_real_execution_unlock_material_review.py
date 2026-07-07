from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_UNLOCK_MATERIAL_REVIEW_VERSION = (
    "project_runner_real_execution_unlock_material_reviews.v1"
)
RUNNER_REAL_EXECUTION_UNLOCK_MATERIAL_REVIEW_SCHEMA_VERSION = (
    "runner_real_execution_unlock_material_review_schema.v1"
)


def build_project_runner_real_execution_unlock_material_reviews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_execution_stage_boundary_reviews: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    boundary_by_profile = {
        str(report.get("profile_id")): report
        for report in real_execution_stage_boundary_reviews.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    review_schema = runner_real_execution_unlock_material_review_schema()
    reports = [
        _unlock_material_review_report(
            profile,
            boundary_by_profile.get(str(profile.get("id"))),
            review_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_UNLOCK_MATERIAL_REVIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "unlock_material_review_required_count": sum(
                1 for report in reports if report["status"] == "unlock_material_review_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "material_item_count": sum(len(report.get("unlock_materials", [])) for report in reports),
            "missing_material_count": sum(
                1
                for report in reports
                for item in report.get("unlock_materials", [])
                if item.get("evidence_status") == "missing"
            ),
            "accepted_material_count": 0,
            "implementation_allowed_count": 0,
            "launchable_count": 0,
        },
        "unlock_material_review_schema": review_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_execution_unlock_material_review_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_UNLOCK_MATERIAL_REVIEW_SCHEMA_VERSION,
        "review_state": {
            "read_only": True,
            "collects_materials_now": False,
            "stores_materials_now": False,
            "materials_accepted_now": False,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
        },
        "material_contract": [
            _material_contract(
                "explicit_user_unlock",
                "Explicit unlock instruction",
                "A separate user instruction that explicitly allows entering real execution implementation.",
            ),
            _material_contract(
                "implementation_scope",
                "Implementation scope",
                "Allowed files, APIs, UI controls, and forbidden operations for the implementation round.",
            ),
            _material_contract(
                "rollback_plan",
                "Rollback and stop plan",
                "How to stop, revert, or disable the new implementation if validation fails.",
            ),
            _material_contract(
                "test_target",
                "Low-risk test target",
                "The project, profile, working directory, and command profile selected for first real testing.",
            ),
            _material_contract(
                "audit_destination",
                "Audit destination",
                "Where future real execution decisions, state transitions, and terminal outcomes will be persisted.",
            ),
            _material_contract(
                "safety_review",
                "Safety boundary review",
                "Acknowledgement that future rounds may require process, stream, event, and audit permissions.",
            ),
        ],
        "blocked_actions": [
            "collecting or accepting human authorization",
            "storing unlock material evidence",
            "granting launch permission",
            "writing runner execution implementation",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch/cancel/timeout UI controls",
            "importing or calling execution adapters",
            "creating sessions for real execution",
            "creating or controlling processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events",
            "reading or writing log files",
            "writing audit logs",
            "writing user project files",
        ],
    }


def _unlock_material_review_report(
    profile: dict[str, Any],
    boundary_review: dict[str, Any] | None,
    review_schema: dict[str, object],
) -> dict[str, object]:
    materials = _unlock_materials(review_schema, boundary_review)
    checks = [
        _check_saved_profile(profile),
        _check_stage_boundary_review(boundary_review),
        _check_material_contract(materials),
        _check_materials_not_collected(review_schema),
        _check_no_implementation_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_execution_unlock_material_review:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "stage_boundary_review_status": (
            boundary_review.get("status") if isinstance(boundary_review, dict) else "missing"
        ),
        "ui_preview_status": (
            boundary_review.get("ui_preview_status") if isinstance(boundary_review, dict) else "missing"
        ),
        "final_checklist_status": (
            boundary_review.get("final_checklist_status") if isinstance(boundary_review, dict) else "missing"
        ),
        "sandbox_policy_status": (
            boundary_review.get("sandbox_policy_status") if isinstance(boundary_review, dict) else "missing"
        ),
        "authorization_package_status": (
            boundary_review.get("authorization_package_status")
            if isinstance(boundary_review, dict)
            else "missing"
        ),
        "authorization_checklist_status": (
            boundary_review.get("authorization_checklist_status")
            if isinstance(boundary_review, dict)
            else "missing"
        ),
        "review_state": review_schema["review_state"],
        "unlock_materials": materials,
        "blocked_actions": review_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only lists the materials required before entering real execution implementation. It does "
            "not collect, accept, or store authorization, grant permission, write implementation code, register POST "
            "APIs, enable launch UI, import or call adapters, create sessions or processes, execute commands, open "
            "stdout/stderr, write runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _unlock_materials(
    review_schema: dict[str, object],
    boundary_review: dict[str, Any] | None,
) -> list[dict[str, object]]:
    boundary_status = boundary_review.get("status") if isinstance(boundary_review, dict) else "missing"
    boundary_requirements = {
        str(item.get("key")): item
        for item in (boundary_review.get("unlock_requirements", []) if isinstance(boundary_review, dict) else [])
        if isinstance(item, dict) and item.get("key")
    }
    contracts = [item for item in review_schema.get("material_contract", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "source_status": boundary_status,
            "boundary_requirement_status": boundary_requirements.get(str(item.get("key")), {}).get(
                "evidence_status",
                "missing",
            ),
            "evidence_status": "missing",
            "accepted_now": False,
            "stored_now": False,
            "required_before_real_execution_implementation": True,
        }
        for item in contracts
    ]


def _material_contract(key: str, title: str, minimum_evidence: str) -> dict[str, object]:
    return {"key": key, "title": title, "minimum_evidence": minimum_evidence}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Unlock material review requires a saved run profile.")


def _check_stage_boundary_review(boundary_review: dict[str, Any] | None) -> dict[str, object]:
    if not boundary_review:
        return _check(
            "stage_boundary_review",
            "error",
            "Missing stage boundary review",
            "Review the real execution stage boundary before listing unlock materials.",
        )
    if boundary_review.get("status") == "stage_boundary_review_required":
        return _check(
            "stage_boundary_review",
            "pass",
            "Stage boundary review declared",
            "Unlock materials can be listed while real execution implementation remains locked.",
        )
    return _check(
        "stage_boundary_review",
        "error",
        "Stage boundary review status is unexpected",
        str(boundary_review.get("status") or "unknown"),
    )


def _check_material_contract(materials: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "explicit_user_unlock",
        "implementation_scope",
        "rollback_plan",
        "test_target",
        "audit_destination",
        "safety_review",
    }
    present = {str(item.get("key")) for item in materials}
    if required.issubset(present):
        return _check("material_contract_declared", "pass", "Unlock material contract declared", "All minimum unlock material entries are explicit.")
    return _check("material_contract_declared", "error", "Unlock material contract incomplete", "Missing minimum unlock material entries.")


def _check_materials_not_collected(review_schema: dict[str, object]) -> dict[str, object]:
    state = review_schema.get("review_state")
    if (
        isinstance(state, dict)
        and not state.get("collects_materials_now")
        and not state.get("stores_materials_now")
        and not state.get("materials_accepted_now")
        and not state.get("implementation_allowed_now")
    ):
        return _check(
            "materials_not_collected",
            "warn",
            "Unlock materials are not collected",
            "This layer only lists required materials; it does not accept or store them.",
        )
    return _check("materials_not_collected", "error", "Unlock materials were accepted", "This read-only review must not accept unlock materials.")


def _check_no_implementation_or_execution() -> dict[str, object]:
    return _check(
        "no_implementation_or_execution",
        "pass",
        "No implementation or execution",
        "No authorization collection, permission grant, runner code, POST API registration, UI enablement, adapter call, session, process, command, stream, event, log, audit, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "unlock_material_review_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "unlock_material_review_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real execution unlock material review is blocked",
        "unlock_material_review_required": "Real execution unlock material review is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the stage boundary review before listing unlock materials.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix unlock material blocker",
                "action": failed.get("detail") or "Complete the stage boundary review first.",
            }
    return {
        "title": "Unlock materials remain unaccepted",
        "action": "Keep real execution implementation locked until a later explicit unlock round accepts the required materials.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "unlock_material_review_only": True,
        "stage_three_unlocked": False,
        "allows_real_execution_implementation": False,
        "collects_unlock_materials": False,
        "stores_unlock_materials": False,
        "accepts_unlock_materials": False,
        "writes_code": False,
        "enables_launch_ui": False,
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
