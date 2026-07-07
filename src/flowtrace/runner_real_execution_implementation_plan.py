from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_IMPLEMENTATION_PLAN_VERSION = "project_runner_real_execution_implementation_plans.v1"
RUNNER_REAL_EXECUTION_IMPLEMENTATION_PLAN_SCHEMA_VERSION = "runner_real_execution_implementation_plan_schema.v1"


def build_project_runner_real_execution_implementation_plans(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_execution_unlock_material_reviews: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    unlock_review_by_profile = {
        str(report.get("profile_id")): report
        for report in real_execution_unlock_material_reviews.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    plan_schema = runner_real_execution_implementation_plan_schema()
    reports = [
        _implementation_plan_report(
            profile,
            unlock_review_by_profile.get(str(profile.get("id"))),
            plan_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_IMPLEMENTATION_PLAN_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "implementation_plan_required_count": sum(
                1 for report in reports if report["status"] == "implementation_plan_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "planned_module_count": sum(len(report.get("implementation_modules", [])) for report in reports),
            "ready_module_count": sum(
                1
                for report in reports
                for module in report.get("implementation_modules", [])
                if module.get("evidence_status") == "ready"
            ),
            "missing_evidence_count": sum(
                1
                for report in reports
                for module in report.get("implementation_modules", [])
                if module.get("evidence_status") == "missing"
            ),
            "launchable_count": 0,
        },
        "implementation_plan_schema": plan_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_execution_implementation_plan_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_IMPLEMENTATION_PLAN_SCHEMA_VERSION,
        "plan_state": {
            "read_only": True,
            "implements_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "implementation_modules": [
            _module_schema(
                "execution_adapter",
                "执行适配器",
                "A reviewed adapter implementation that accepts a structured launch request without shell strings.",
            ),
            _module_schema(
                "launch_api",
                "启动 API",
                "Explicit launch endpoint contract, handler, validation, and disabled-by-default service flag.",
            ),
            _module_schema(
                "process_lifecycle",
                "进程生命周期",
                "Process creation, PID ownership, terminal-state capture, and cleanup semantics.",
            ),
            _module_schema(
                "session_state_store",
                "会话状态存储",
                "Durable session state transitions with stale-session recovery and mutation guards.",
            ),
            _module_schema(
                "stdout_stderr_capture",
                "stdout/stderr 捕获",
                "Bounded stream capture, redaction, retention, and backpressure behavior.",
            ),
            _module_schema(
                "runner_event_writer",
                "Runner 事件写入",
                "Structured runner events with ordering, schema versioning, and write-failure handling.",
            ),
            _module_schema(
                "audit_persistence",
                "审计持久化",
                "Human authorization evidence and real launch decisions persisted to an explicit audit destination.",
            ),
            _module_schema(
                "cancel_timeout_control",
                "取消/超时控制",
                "Cancel and timeout endpoints, signals, race handling, and idempotent terminal writes.",
            ),
            _module_schema(
                "execution_console_ui",
                "执行控制台 UI",
                "Operator UI for launch, cancel, timeout, streams, audit evidence, and disabled-state explanations.",
            ),
        ],
        "blocked_actions": [
            "writing runner implementation code",
            "registering launch/cancel/timeout POST APIs",
            "importing or calling execution adapters",
            "creating or controlling processes",
            "opening stdout/stderr streams",
            "writing runner events",
            "reading or writing log files",
            "writing audit logs",
            "collecting or storing authorization",
            "granting launch permission",
            "writing user project files",
        ],
    }


def _implementation_plan_report(
    profile: dict[str, Any],
    unlock_review: dict[str, Any] | None,
    plan_schema: dict[str, object],
) -> dict[str, object]:
    modules = _implementation_modules(plan_schema, unlock_review)
    checks = [
        _check_saved_profile(profile),
        _check_unlock_material_review(unlock_review),
        _check_modules_declared(modules),
        _check_no_implementation_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_execution_implementation_plan:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "unlock_material_review_status": (
            unlock_review.get("status") if isinstance(unlock_review, dict) else "missing"
        ),
        "stage_boundary_review_status": (
            unlock_review.get("stage_boundary_review_status") if isinstance(unlock_review, dict) else "missing"
        ),
        "ui_preview_status": (
            unlock_review.get("ui_preview_status") if isinstance(unlock_review, dict) else "missing"
        ),
        "final_checklist_status": (
            unlock_review.get("final_checklist_status") if isinstance(unlock_review, dict) else "missing"
        ),
        "sandbox_policy_status": (
            unlock_review.get("sandbox_policy_status") if isinstance(unlock_review, dict) else "missing"
        ),
        "authorization_package_status": (
            unlock_review.get("authorization_package_status")
            if isinstance(unlock_review, dict)
            else "missing"
        ),
        "authorization_checklist_status": (
            unlock_review.get("authorization_checklist_status")
            if isinstance(unlock_review, dict)
            else "missing"
        ),
        "plan_state": plan_schema["plan_state"],
        "implementation_modules": modules,
        "blocked_actions": plan_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only decomposes future real execution implementation work. It does not write runner code, "
            "register launch/cancel/timeout APIs, import or call adapters, create processes, create or mutate sessions, "
            "open stdout/stderr, write runner events, read/write logs, write audit logs, collect authorization, grant "
            "permission, or modify the user project."
        ),
    }


def _implementation_modules(
    plan_schema: dict[str, object],
    unlock_review: dict[str, Any] | None,
) -> list[dict[str, object]]:
    modules = [item for item in plan_schema.get("implementation_modules", []) if isinstance(item, dict)]
    unlock_status = unlock_review.get("status") if isinstance(unlock_review, dict) else "missing"
    return [
        {
            **module,
            "unlock_material_review_status": unlock_status,
            "stage_boundary_review_status": (
                unlock_review.get("stage_boundary_review_status") if isinstance(unlock_review, dict) else "missing"
            ),
            "ui_preview_status": (
                unlock_review.get("ui_preview_status") if isinstance(unlock_review, dict) else "missing"
            ),
            "final_checklist_status": (
                unlock_review.get("final_checklist_status") if isinstance(unlock_review, dict) else "missing"
            ),
            "sandbox_policy_status": (
                unlock_review.get("sandbox_policy_status") if isinstance(unlock_review, dict) else "missing"
            ),
            "authorization_package_status": (
                unlock_review.get("authorization_package_status")
                if isinstance(unlock_review, dict)
                else "missing"
            ),
            "authorization_checklist_status": (
                unlock_review.get("authorization_checklist_status")
                if isinstance(unlock_review, dict)
                else "missing"
            ),
            "implementation_status": "not_started",
            "evidence_status": "missing",
            "can_execute_now": False,
            "requires_future_code_change": True,
            "requires_future_review": True,
        }
        for module in modules
    ]


def _module_schema(key: str, title: str, minimum_evidence: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "minimum_evidence": minimum_evidence,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Implementation planning requires a saved run profile.")


def _check_unlock_material_review(unlock_review: dict[str, Any] | None) -> dict[str, object]:
    if not unlock_review:
        return _check(
            "unlock_material_review",
            "error",
            "Missing unlock material review",
            "Review real execution unlock materials before implementation planning.",
        )
    if unlock_review.get("status") == "unlock_material_review_required":
        return _check(
            "unlock_material_review",
            "pass",
            "Unlock material review declared",
            "Required unlock materials are listed while real execution implementation remains locked.",
        )
    return _check(
        "unlock_material_review",
        "error",
        "Unlock material review status is unexpected",
        str(unlock_review.get("status") or "unknown"),
    )


def _check_modules_declared(modules: list[dict[str, object]]) -> dict[str, object]:
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
    present = {str(module.get("key")) for module in modules}
    if required.issubset(present):
        return _check("implementation_modules_declared", "pass", "Implementation modules declared", "Future real execution work is decomposed.")
    return _check("implementation_modules_declared", "error", "Implementation modules incomplete", "Missing future implementation modules.")


def _check_no_implementation_or_execution() -> dict[str, object]:
    return _check(
        "no_implementation_or_execution",
        "pass",
        "No implementation or execution",
        "No runner code, POST API registration, adapter import/call, process, stream, event, log, audit, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "implementation_plan_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "implementation_plan_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real execution implementation plan is blocked",
        "implementation_plan_required": "Real execution implementation plan is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete unlock material review before implementation planning.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix implementation planning blocker",
                "action": failed.get("detail") or "Complete the unlock material review first.",
            }
    return {
        "title": "Implementation plan remains read-only",
        "action": "Use this module list as the future authorized implementation scope; no real execution is enabled now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "implementation_plan_only": True,
        "writes_code": False,
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
