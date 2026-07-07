from __future__ import annotations

from typing import Any


RUNNER_PROCESS_LIFECYCLE_IMPLEMENTATION_AUDIT_VERSION = "project_runner_process_lifecycle_implementation_audits.v1"
RUNNER_PROCESS_LIFECYCLE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION = (
    "runner_process_lifecycle_implementation_audit_schema.v1"
)


def build_project_runner_process_lifecycle_implementation_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    adapter_audit_collection: dict[str, Any],
    process_lifecycle_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    adapter_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in adapter_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    lifecycle_by_profile = {
        str(report.get("profile_id")): report
        for report in (process_lifecycle_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    lifecycle_projection_available = process_lifecycle_collection is not None
    audit_schema = runner_process_lifecycle_implementation_audit_schema()
    reports = [
        _process_lifecycle_audit_report(
            profile,
            adapter_audit_by_profile.get(str(profile.get("id"))),
            lifecycle_by_profile.get(str(profile.get("id"))),
            lifecycle_projection_available,
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_PROCESS_LIFECYCLE_IMPLEMENTATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "process_lifecycle_audit_required_count": sum(
                1 for report in reports if report["status"] == "process_lifecycle_audit_required"
            ),
            "implemented_count": sum(1 for report in reports if report["status"] == "process_lifecycle_minimal_implemented"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "audit_item_count": sum(len(report.get("audit_items", [])) for report in reports),
            "ready_item_count": sum(
                1
                for report in reports
                for item in report.get("audit_items", [])
                if item.get("evidence_status") == "ready"
            ),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("audit_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "launchable_count": 0,
        },
        "process_lifecycle_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(lifecycle_projection_available),
        "next_action": _next_action(status, reports),
    }


def runner_process_lifecycle_implementation_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_PROCESS_LIFECYCLE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": False,
            "process_created_now": False,
            "pid_recorded_now": False,
            "process_control_enabled_now": False,
            "cancellation_enabled_now": False,
            "timeout_enabled_now": False,
            "cleanup_executed_now": False,
            "minimal_lifecycle_projection_now": True,
            "can_launch_now": True,
            "requires_new_authorized_implementation_round": False,
        },
        "required_process_lifecycle_evidence": [
            _audit_item_schema(
                "spawn_contract",
                "进程创建合约",
                "Structured spawn inputs, argv tokens, working directory, env allowlist, service flag, and no-shell guarantee.",
            ),
            _audit_item_schema(
                "pid_ownership_contract",
                "PID 归属合约",
                "Parent/child PID ownership, process identity recording, stale PID detection, and reuse protection.",
            ),
            _audit_item_schema(
                "process_group_contract",
                "进程组边界",
                "Process group/session rules, child process ownership, signal scope, and platform differences.",
            ),
            _audit_item_schema(
                "lifecycle_state_model",
                "生命周期状态模型",
                "Pending, launching, running, cancelling, timed_out, failed, exited, and cleanup states with allowed transitions.",
            ),
            _audit_item_schema(
                "terminal_state_contract",
                "终止态合约",
                "Exit code, signal, timeout, cancellation, crash, stream closure, and final event write semantics.",
            ),
            _audit_item_schema(
                "cancellation_contract",
                "取消合约",
                "Idempotent cancel requests, signal escalation, race handling, and already-terminal behavior.",
            ),
            _audit_item_schema(
                "timeout_contract",
                "超时合约",
                "Timeout scheduling, cancellation of timers, escalation policy, and terminal-state precedence.",
            ),
            _audit_item_schema(
                "cleanup_contract",
                "清理合约",
                "Resource cleanup ownership, stream close, temp resource policy, and no user-project writes.",
            ),
            _audit_item_schema(
                "orphan_recovery_contract",
                "孤儿进程恢复",
                "Server restart recovery, stale session detection, orphan decision rules, and operator-facing evidence.",
            ),
            _audit_item_schema(
                "concurrency_idempotency_contract",
                "并发与幂等",
                "Duplicate launch prevention, concurrent cancel/timeout handling, lock ownership, and retry-safe writes.",
            ),
        ],
        "blocked_actions": [
            "controlling or signalling processes",
            "cancelling processes",
            "killing processes",
            "scheduling real timeouts",
            "registering cancel/timeout POST APIs",
            "opening live stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "writing user project files",
        ],
    }


def _process_lifecycle_audit_report(
    profile: dict[str, Any],
    adapter_audit_report: dict[str, Any] | None,
    lifecycle_report: dict[str, Any] | None,
    lifecycle_projection_available: bool,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, adapter_audit_report, lifecycle_report, lifecycle_projection_available)
    checks = [
        _check_saved_profile(profile),
        _check_adapter_audit(adapter_audit_report),
        _check_process_boundary_item(adapter_audit_report),
        _check_lifecycle_projection(lifecycle_report, lifecycle_projection_available),
        _check_audit_items_declared(audit_items),
        _check_no_process_or_execution(),
    ]
    status = _report_status(checks) if lifecycle_projection_available else _legacy_report_status(checks)
    return {
        "id": f"runner_process_lifecycle_implementation_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "adapter_audit_status": adapter_audit_report.get("status") if isinstance(adapter_audit_report, dict) else "missing",
        "process_lifecycle_status": lifecycle_report.get("status") if isinstance(lifecycle_report, dict) else "missing",
        "session_state": lifecycle_report.get("session_state") if isinstance(lifecycle_report, dict) else None,
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer verifies the minimal process lifecycle projection from real execution records. It does not "
            "control, signal, cancel, or kill processes, schedule real timeouts, register cancel/timeout APIs, open live "
            "stdout/stderr, write runner events, write audit logs, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    adapter_audit_report: dict[str, Any] | None,
    lifecycle_report: dict[str, Any] | None,
    lifecycle_projection_available: bool,
) -> list[dict[str, object]]:
    adapter_audit_status = adapter_audit_report.get("status") if isinstance(adapter_audit_report, dict) else "missing"
    lifecycle_ready = lifecycle_projection_available and isinstance(lifecycle_report, dict) and lifecycle_report.get("session_state")
    implemented_keys = {"lifecycle_state_model", "terminal_state_contract"} if lifecycle_ready else set()
    items = [item for item in audit_schema.get("required_process_lifecycle_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "adapter_audit_status": adapter_audit_status,
            "process_lifecycle_status": lifecycle_report.get("status") if isinstance(lifecycle_report, dict) else "missing",
            "evidence_status": "ready" if item.get("key") in implemented_keys else "missing",
            "implementation_status": "implemented" if item.get("key") in implemented_keys else "deferred",
            "can_execute_now": False,
            "requires_future_code_change": item.get("key") not in implemented_keys,
            "requires_future_review": item.get("key") not in implemented_keys,
        }
        for item in items
    ]


def _audit_item_schema(key: str, title: str, minimum_evidence: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "minimum_evidence": minimum_evidence,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Process lifecycle audit requires a saved run profile.")


def _check_adapter_audit(adapter_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not adapter_audit_report:
        return _check(
            "adapter_implementation_audit",
            "error",
            "Missing adapter implementation audit",
            "Generate the execution adapter implementation audit before process lifecycle audit.",
        )
    if adapter_audit_report.get("status") in {"adapter_implementation_audit_required", "adapter_minimal_implemented"}:
        return _check(
            "adapter_implementation_audit",
            "pass",
            "Adapter implementation evidence available",
            "Adapter prerequisites are available for process lifecycle projection.",
        )
    return _check(
        "adapter_implementation_audit",
        "error",
        "Adapter implementation audit status is unexpected",
        str(adapter_audit_report.get("status") or "unknown"),
    )


def _check_process_boundary_item(adapter_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = set()
    if isinstance(adapter_audit_report, dict):
        audit_keys = {str(item.get("key")) for item in adapter_audit_report.get("audit_items", []) if isinstance(item, dict)}
    if "process_boundary_contract" in audit_keys:
        return _check(
            "process_boundary_contract",
            "pass",
            "Process boundary adapter evidence declared",
            "Adapter audit includes process boundary evidence for lifecycle audit.",
        )
    return _check(
        "process_boundary_contract",
        "error",
        "Process boundary adapter evidence missing",
        "Adapter audit must include process_boundary_contract before lifecycle audit.",
    )


def _check_lifecycle_projection(
    lifecycle_report: dict[str, Any] | None,
    lifecycle_projection_available: bool,
) -> dict[str, object]:
    if not lifecycle_projection_available:
        return _check(
            "process_lifecycle_projection",
            "warn",
            "Minimal process lifecycle projection not supplied",
            "This audit is running in compatibility mode before the round-11 projection is wired.",
        )
    if isinstance(lifecycle_report, dict) and isinstance(lifecycle_report.get("session_state"), dict):
        return _check(
            "process_lifecycle_projection",
            "pass",
            "Minimal process lifecycle projection present",
            str(lifecycle_report["session_state"].get("state") or "unknown"),
        )
    return _check(
        "process_lifecycle_projection",
        "error",
        "Missing process lifecycle projection",
        "Generate the minimal lifecycle projection before marking round 11 implemented.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "spawn_contract",
        "pid_ownership_contract",
        "process_group_contract",
        "lifecycle_state_model",
        "terminal_state_contract",
        "cancellation_contract",
        "timeout_contract",
        "cleanup_contract",
        "orphan_recovery_contract",
        "concurrency_idempotency_contract",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("process_lifecycle_audit_items_declared", "pass", "Process lifecycle audit items declared", "Future process lifecycle evidence is explicit.")
    return _check("process_lifecycle_audit_items_declared", "error", "Process lifecycle audit items incomplete", "Missing future process lifecycle evidence items.")


def _check_no_process_or_execution() -> dict[str, object]:
    return _check(
        "no_process_or_execution",
        "pass",
        "No additional process control",
        "Lifecycle projection does not add process control/signal/cancel/kill, timeout scheduling, cancel/timeout APIs, live stream open, runner event, audit, or user-project write behavior.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "process_lifecycle_minimal_implemented"


def _legacy_report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "process_lifecycle_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if all(report.get("status") == "process_lifecycle_audit_required" for report in reports):
        return "process_lifecycle_audit_required"
    return "process_lifecycle_minimal_implemented"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Process lifecycle implementation audit is blocked",
        "process_lifecycle_audit_required": "Process lifecycle implementation audit is required",
        "process_lifecycle_minimal_implemented": "Minimal process lifecycle projection is implemented",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the execution adapter implementation audit before process lifecycle audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix process lifecycle audit blocker",
                "action": failed.get("detail") or "Complete the adapter implementation audit first.",
            }
    return {
        "title": "Minimal lifecycle implemented",
        "action": "Use the lifecycle projection for pending and terminal states; cancel/timeout and live process control remain locked.",
    }


def _safety(lifecycle_projection_available: bool = True) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": lifecycle_projection_available,
        "launch_enabled": lifecycle_projection_available,
        "launch_api_available": lifecycle_projection_available,
        "process_lifecycle_audit_only": not lifecycle_projection_available,
        "process_lifecycle_projection": lifecycle_projection_available,
        "writes_code": lifecycle_projection_available,
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
        "controls_process": False,
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
