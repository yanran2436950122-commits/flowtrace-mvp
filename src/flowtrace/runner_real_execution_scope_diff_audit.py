from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_SCOPE_DIFF_AUDIT_VERSION = "project_runner_real_execution_scope_diff_audits.v1"
RUNNER_REAL_EXECUTION_SCOPE_DIFF_AUDIT_SCHEMA_VERSION = "runner_real_execution_scope_diff_audit_schema.v1"


def build_project_runner_real_execution_scope_diff_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    implementation_plan_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    plan_by_profile = {
        str(report.get("profile_id")): report
        for report in implementation_plan_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_real_execution_scope_diff_audit_schema()
    reports = [
        _scope_diff_report(
            profile,
            plan_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_SCOPE_DIFF_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "scope_diff_audit_required_count": sum(
                1 for report in reports if report["status"] == "scope_diff_audit_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "scope_item_count": sum(len(report.get("scope_diff_items", [])) for report in reports),
            "locked_scope_item_count": sum(
                1
                for report in reports
                for item in report.get("scope_diff_items", [])
                if item.get("current_permission") == "locked"
            ),
            "allowed_scope_item_count": 0,
            "implementation_allowed_count": 0,
            "launchable_count": 0,
        },
        "scope_diff_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_execution_scope_diff_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_SCOPE_DIFF_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "compares_scope_only": True,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
            "requires_future_unlock": True,
        },
        "scope_rules": [
            _scope_rule("execution_adapter", "adapter implementation and adapter calls remain locked"),
            _scope_rule("launch_api", "launch/cancel/timeout POST API registration remains locked"),
            _scope_rule("process_lifecycle", "process creation, control, cancellation, and timeout remain locked"),
            _scope_rule("session_state_store", "real execution session creation and mutation remain locked"),
            _scope_rule("stdout_stderr_capture", "stdout/stderr stream opening and capture remain locked"),
            _scope_rule("runner_event_writer", "runner event writing remains locked"),
            _scope_rule("audit_persistence", "real execution audit persistence remains locked"),
            _scope_rule("cancel_timeout_control", "cancel and timeout controls remain locked"),
            _scope_rule("execution_console_ui", "launch/cancel/timeout UI enablement remains locked"),
        ],
        "blocked_actions": [
            "writing runner implementation code",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch/cancel/timeout UI controls",
            "importing or calling execution adapters",
            "creating or mutating real execution sessions",
            "creating or controlling processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events",
            "reading or writing log files",
            "writing audit logs",
            "collecting or storing authorization",
            "granting launch permission",
            "writing user project files",
        ],
    }


def _scope_diff_report(
    profile: dict[str, Any],
    implementation_plan: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    scope_items = _scope_diff_items(audit_schema, implementation_plan)
    checks = [
        _check_saved_profile(profile),
        _check_implementation_plan(implementation_plan),
        _check_scope_rules_declared(scope_items),
        _check_scope_still_locked(audit_schema),
        _check_no_implementation_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_execution_scope_diff_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "implementation_plan_status": (
            implementation_plan.get("status") if isinstance(implementation_plan, dict) else "missing"
        ),
        "unlock_material_review_status": (
            implementation_plan.get("unlock_material_review_status")
            if isinstance(implementation_plan, dict)
            else "missing"
        ),
        "stage_boundary_review_status": (
            implementation_plan.get("stage_boundary_review_status")
            if isinstance(implementation_plan, dict)
            else "missing"
        ),
        "audit_state": audit_schema["audit_state"],
        "implementation_modules": (
            implementation_plan.get("implementation_modules", []) if isinstance(implementation_plan, dict) else []
        ),
        "scope_diff_items": scope_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only compares future implementation scope against the still-locked hard boundary. It does "
            "not write runner code, register launch/cancel/timeout APIs, enable launch UI, import or call adapters, "
            "create or mutate sessions, create processes, execute commands, open stdout/stderr, write runner events, "
            "read/write logs, write audit logs, collect authorization, grant permission, or modify the user project."
        ),
    }


def _scope_diff_items(
    audit_schema: dict[str, object],
    implementation_plan: dict[str, Any] | None,
) -> list[dict[str, object]]:
    module_by_key = {
        str(module.get("key")): module
        for module in (implementation_plan.get("implementation_modules", []) if isinstance(implementation_plan, dict) else [])
        if isinstance(module, dict) and module.get("key")
    }
    rules = [item for item in audit_schema.get("scope_rules", []) if isinstance(item, dict)]
    return [
        {
            **rule,
            "implementation_module_status": module_by_key.get(str(rule.get("key")), {}).get(
                "implementation_status",
                "missing",
            ),
            "evidence_status": module_by_key.get(str(rule.get("key")), {}).get("evidence_status", "missing"),
            "current_permission": "locked",
            "future_permission_required": True,
            "can_implement_now": False,
            "can_execute_now": False,
        }
        for rule in rules
    ]


def _scope_rule(key: str, locked_reason: str) -> dict[str, object]:
    return {"key": key, "locked_reason": locked_reason}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Scope diff audit requires a saved run profile.")


def _check_implementation_plan(implementation_plan: dict[str, Any] | None) -> dict[str, object]:
    if not implementation_plan:
        return _check(
            "implementation_plan",
            "error",
            "Missing implementation plan",
            "Generate the real execution implementation plan before auditing scope differences.",
        )
    if implementation_plan.get("status") == "implementation_plan_required":
        return _check(
            "implementation_plan",
            "pass",
            "Implementation plan declared",
            "Future implementation modules are available for scope comparison.",
        )
    return _check(
        "implementation_plan",
        "error",
        "Implementation plan status is unexpected",
        str(implementation_plan.get("status") or "unknown"),
    )


def _check_scope_rules_declared(scope_items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "execution_adapter",
        "launch_api",
        "process_lifecycle",
        "session_state_store",
        "stdout_stderr_capture",
        "runner_event_writer",
        "audit_persistence",
        "cancel_timeout_control",
        "execution_console_ui",
    }
    present = {str(item.get("key")) for item in scope_items}
    if required.issubset(present):
        return _check("scope_rules_declared", "pass", "Scope rules declared", "All future implementation modules are mapped to locked boundary rules.")
    return _check("scope_rules_declared", "error", "Scope rules incomplete", "Missing future implementation scope rules.")


def _check_scope_still_locked(audit_schema: dict[str, object]) -> dict[str, object]:
    state = audit_schema.get("audit_state")
    if (
        isinstance(state, dict)
        and state.get("compares_scope_only")
        and not state.get("implementation_allowed_now")
        and not state.get("launch_allowed_now")
    ):
        return _check("scope_still_locked", "warn", "Future implementation scope is still locked", "A later explicit unlock is required before any implementation work.")
    return _check("scope_still_locked", "error", "Implementation scope was unlocked", "This read-only audit must not unlock implementation.")


def _check_no_implementation_or_execution() -> dict[str, object]:
    return _check(
        "no_implementation_or_execution",
        "pass",
        "No implementation or execution",
        "No runner code, POST API registration, UI enablement, adapter call, session, process, command, stream, event, log, audit, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "scope_diff_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "scope_diff_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real execution scope diff audit is blocked",
        "scope_diff_audit_required": "Real execution scope diff audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and generate the implementation plan before auditing scope differences.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix scope diff blocker",
                "action": failed.get("detail") or "Complete the implementation plan first.",
            }
    return {
        "title": "Implementation scope remains locked",
        "action": "Use the locked scope list to constrain future implementation; no real execution work is enabled now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "scope_diff_audit_only": True,
        "compares_scope_only": True,
        "allows_real_execution_implementation": False,
        "writes_code": False,
        "enables_launch_ui": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "implements_runner": False,
        "implements_adapter": False,
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
