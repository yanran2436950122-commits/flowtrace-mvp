from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_STAGE_BOUNDARY_REVIEW_VERSION = "project_runner_real_execution_stage_boundary_reviews.v1"
RUNNER_REAL_EXECUTION_STAGE_BOUNDARY_REVIEW_SCHEMA_VERSION = "runner_real_execution_stage_boundary_review_schema.v1"


def build_project_runner_real_execution_stage_boundary_reviews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_ui_previews: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    preview_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_ui_previews.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    review_schema = runner_real_execution_stage_boundary_review_schema()
    reports = [
        _stage_boundary_review_report(
            profile,
            preview_by_profile.get(str(profile.get("id"))),
            review_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_STAGE_BOUNDARY_REVIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "stage_boundary_review_required_count": sum(
                1 for report in reports if report["status"] == "stage_boundary_review_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "unlock_requirement_count": sum(len(report.get("unlock_requirements", [])) for report in reports),
            "missing_unlock_count": sum(
                1
                for report in reports
                for item in report.get("unlock_requirements", [])
                if item.get("evidence_status") == "missing"
            ),
            "authorized_unlock_count": 0,
            "implementation_allowed_count": 0,
            "launchable_count": 0,
        },
        "stage_boundary_review_schema": review_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_execution_stage_boundary_review_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_STAGE_BOUNDARY_REVIEW_SCHEMA_VERSION,
        "review_state": {
            "read_only": True,
            "stage_three_unlocked_now": False,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
            "requires_explicit_user_unlock": True,
            "requires_new_development_scope_confirmation": True,
        },
        "unlock_requirements": [
            _unlock_requirement("explicit_user_unlock", "Explicit user instruction to enter real execution implementation"),
            _unlock_requirement("implementation_scope", "Confirmed implementation scope and allowed files"),
            _unlock_requirement("rollback_plan", "Rollback and stop plan for implementation work"),
            _unlock_requirement("test_target", "Low-risk target project and profile selected for first real test"),
            _unlock_requirement("audit_destination", "Audit destination and retention policy accepted"),
            _unlock_requirement("safety_review", "Hard-boundary review acknowledges new write and process permissions"),
        ],
        "blocked_actions": [
            "writing runner execution implementation",
            "importing execution adapters",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch/cancel/timeout UI controls",
            "granting launch permission",
            "creating sessions for real execution",
            "starting a target project process",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _stage_boundary_review_report(
    profile: dict[str, Any],
    ui_preview: dict[str, Any] | None,
    review_schema: dict[str, object],
) -> dict[str, object]:
    requirements = _unlock_requirements(review_schema, ui_preview)
    checks = [
        _check_saved_profile(profile),
        _check_ui_preview(ui_preview),
        _check_unlock_requirements(requirements),
        _check_stage_not_unlocked(review_schema),
        _check_no_implementation_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_execution_stage_boundary_review:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "ui_preview_status": ui_preview.get("status") if isinstance(ui_preview, dict) else "missing",
        "final_checklist_status": (
            ui_preview.get("final_checklist_status") if isinstance(ui_preview, dict) else "missing"
        ),
        "sandbox_policy_status": (
            ui_preview.get("sandbox_policy_status") if isinstance(ui_preview, dict) else "missing"
        ),
        "authorization_package_status": (
            ui_preview.get("authorization_package_status") if isinstance(ui_preview, dict) else "missing"
        ),
        "authorization_checklist_status": (
            ui_preview.get("authorization_checklist_status") if isinstance(ui_preview, dict) else "missing"
        ),
        "review_state": review_schema["review_state"],
        "unlock_requirements": requirements,
        "blocked_actions": review_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only reviews whether the project may enter the real execution implementation stage. It does "
            "not write runner implementation code, import adapters, register launch/cancel/timeout APIs, enable "
            "launch UI, grant permission, create sessions, execute commands, start processes, open stdout/stderr, write "
            "runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _unlock_requirements(
    review_schema: dict[str, object],
    ui_preview: dict[str, Any] | None,
) -> list[dict[str, object]]:
    preview_status = ui_preview.get("status") if isinstance(ui_preview, dict) else "missing"
    requirements = [item for item in review_schema.get("unlock_requirements", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "source_status": preview_status,
            "evidence_status": "missing",
            "satisfied_now": False,
            "required_before_real_execution_implementation": True,
        }
        for item in requirements
    ]


def _unlock_requirement(key: str, title: str) -> dict[str, object]:
    return {"key": key, "title": title}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Stage boundary review requires a saved run profile.")


def _check_ui_preview(ui_preview: dict[str, Any] | None) -> dict[str, object]:
    if not ui_preview:
        return _check(
            "ui_preview",
            "error",
            "Missing UI preview",
            "Generate the real-test UI preview before reviewing the stage boundary.",
        )
    if ui_preview.get("status") == "ui_preview_required":
        return _check(
            "ui_preview",
            "pass",
            "UI preview declared",
            "Stage boundary can review whether real execution implementation is explicitly unlocked.",
        )
    return _check("ui_preview", "error", "UI preview status is unexpected", str(ui_preview.get("status") or "unknown"))


def _check_unlock_requirements(requirements: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "explicit_user_unlock",
        "implementation_scope",
        "rollback_plan",
        "test_target",
        "audit_destination",
        "safety_review",
    }
    present = {str(item.get("key")) for item in requirements}
    if required.issubset(present):
        return _check("unlock_requirements_declared", "pass", "Unlock requirements declared", "All minimum implementation unlock requirements are explicit.")
    return _check("unlock_requirements_declared", "error", "Unlock requirements incomplete", "Missing minimum implementation unlock requirement.")


def _check_stage_not_unlocked(review_schema: dict[str, object]) -> dict[str, object]:
    state = review_schema.get("review_state")
    if (
        isinstance(state, dict)
        and not state.get("stage_three_unlocked_now")
        and not state.get("implementation_allowed_now")
        and not state.get("launch_allowed_now")
    ):
        return _check("stage_not_unlocked", "warn", "Real execution stage is not unlocked", "A separate explicit unlock is required before implementation.")
    return _check("stage_not_unlocked", "error", "Real execution stage was unlocked", "This read-only review must not unlock implementation.")


def _check_no_implementation_or_execution() -> dict[str, object]:
    return _check(
        "no_implementation_or_execution",
        "pass",
        "No implementation or execution",
        "No runner code, adapter import, POST API registration, UI enablement, permission grant, session creation, command execution, subprocess, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "stage_boundary_review_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "stage_boundary_review_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real execution stage boundary review is blocked",
        "stage_boundary_review_required": "Real execution stage boundary review is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the UI preview before reviewing the real execution stage boundary.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix stage boundary blocker",
                "action": failed.get("detail") or "Complete the UI preview first.",
            }
    return {
        "title": "Real execution implementation remains locked",
        "action": "Do not implement execution adapters or launch APIs until the user explicitly unlocks the real execution stage.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "stage_boundary_review_only": True,
        "stage_three_unlocked": False,
        "allows_real_execution_implementation": False,
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
