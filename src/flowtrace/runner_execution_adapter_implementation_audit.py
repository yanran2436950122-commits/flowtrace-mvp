from __future__ import annotations

from typing import Any


RUNNER_EXECUTION_ADAPTER_IMPLEMENTATION_AUDIT_VERSION = "project_runner_execution_adapter_implementation_audits.v1"
RUNNER_EXECUTION_ADAPTER_IMPLEMENTATION_AUDIT_SCHEMA_VERSION = (
    "runner_execution_adapter_implementation_audit_schema.v1"
)


def build_project_runner_execution_adapter_implementation_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    scope_diff_audit_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    scope_diff_by_profile = {
        str(report.get("profile_id")): report
        for report in scope_diff_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_execution_adapter_implementation_audit_schema()
    reports = [
        _adapter_audit_report(
            profile,
            scope_diff_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_IMPLEMENTATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "adapter_audit_required_count": sum(
                1 for report in reports if report["status"] == "adapter_implementation_audit_required"
            ),
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
        "adapter_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_execution_adapter_implementation_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_IMPLEMENTATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "adapter_implemented_now": False,
            "adapter_imported_now": False,
            "adapter_called_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_adapter_evidence": [
            _audit_item_schema(
                "launch_request_contract",
                "启动请求合约",
                "Structured launch request fields, argv tokenization, working directory, env allowlist, and shell-string rejection.",
            ),
            _audit_item_schema(
                "launch_result_contract",
                "启动结果合约",
                "Session id, process identity, timestamps, terminal-state model, and safe status mapping.",
            ),
            _audit_item_schema(
                "error_contract",
                "错误合约",
                "Validation, adapter, process, timeout, cancellation, stream, and audit-write failures mapped without leaking secrets.",
            ),
            _audit_item_schema(
                "runner_event_contract",
                "Runner 事件合约",
                "Future event names, order, payload schemas, redaction rules, and write failure semantics.",
            ),
            _audit_item_schema(
                "audit_evidence_contract",
                "审计证据合约",
                "Human authorization linkage, approval snapshot, launch decision, and immutable audit destination.",
            ),
            _audit_item_schema(
                "stream_contract",
                "stdout/stderr 合约",
                "Bounded chunking, buffering, redaction, retention, and backpressure behavior.",
            ),
            _audit_item_schema(
                "process_boundary_contract",
                "进程边界合约",
                "PID ownership, process group rules, cancellation signals, timeout behavior, and cleanup ownership.",
            ),
            _audit_item_schema(
                "security_boundary_contract",
                "安全边界合约",
                "No shell interpolation, no user-project writes, no broad environment inheritance, and explicit path constraints.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "适配器夹具矩阵",
                "Future tests for success, validation failure, spawn failure, timeout, cancel, stream overflow, and audit failure.",
            ),
        ],
        "blocked_actions": [
            "writing adapter implementation code",
            "importing adapter modules",
            "calling execution adapters",
            "registering launch/cancel/timeout POST APIs",
            "creating or controlling processes",
            "creating or mutating runner sessions",
            "opening stdout/stderr streams",
            "writing runner events",
            "reading or writing log files",
            "writing audit logs",
            "collecting or storing authorization",
            "granting launch permission",
            "writing user project files",
        ],
    }


def _adapter_audit_report(
    profile: dict[str, Any],
    scope_diff_report: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, scope_diff_report)
    checks = [
        _check_saved_profile(profile),
        _check_scope_diff_audit(scope_diff_report),
        _check_execution_adapter_module(scope_diff_report),
        _check_audit_items_declared(audit_items),
        _check_no_adapter_or_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_execution_adapter_implementation_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "scope_diff_audit_status": (
            scope_diff_report.get("status") if isinstance(scope_diff_report, dict) else "missing"
        ),
        "implementation_plan_status": (
            scope_diff_report.get("implementation_plan_status") if isinstance(scope_diff_report, dict) else "missing"
        ),
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits future execution-adapter implementation prerequisites. It does not write adapter "
            "code, import or call adapters, register launch/cancel/timeout APIs, create processes, create or mutate "
            "sessions, open stdout/stderr, write runner events, read/write logs, write audit logs, collect authorization, "
            "grant permission, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    scope_diff_report: dict[str, Any] | None,
) -> list[dict[str, object]]:
    adapter_module_status = _adapter_module_status(scope_diff_report)
    scope_diff_status = scope_diff_report.get("status") if isinstance(scope_diff_report, dict) else "missing"
    items = [item for item in audit_schema.get("required_adapter_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "scope_diff_audit_status": scope_diff_status,
            "adapter_module_status": adapter_module_status,
            "evidence_status": "missing",
            "implementation_status": "not_started",
            "can_execute_now": False,
            "requires_future_code_change": True,
            "requires_future_review": True,
        }
        for item in items
    ]


def _adapter_module_status(scope_diff_report: dict[str, Any] | None) -> str:
    if not isinstance(scope_diff_report, dict):
        return "missing"
    for module in scope_diff_report.get("implementation_modules", []):
        if isinstance(module, dict) and module.get("key") == "execution_adapter":
            return str(module.get("implementation_status") or "not_started")
    return "missing"


def _audit_item_schema(key: str, title: str, minimum_evidence: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "minimum_evidence": minimum_evidence,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Adapter audit requires a saved run profile.")


def _check_scope_diff_audit(scope_diff_report: dict[str, Any] | None) -> dict[str, object]:
    if not scope_diff_report:
        return _check(
            "scope_diff_audit",
            "error",
            "Missing scope diff audit",
            "Generate the real execution scope diff audit before auditing adapter readiness.",
        )
    if scope_diff_report.get("status") == "scope_diff_audit_required":
        return _check(
            "scope_diff_audit",
            "pass",
            "Scope diff audit declared",
            "Future implementation scope has been compared against locked boundaries before adapter audit.",
        )
    return _check(
        "scope_diff_audit",
        "error",
        "Scope diff audit status is unexpected",
        str(scope_diff_report.get("status") or "unknown"),
    )


def _check_execution_adapter_module(scope_diff_report: dict[str, Any] | None) -> dict[str, object]:
    if _adapter_module_status(scope_diff_report) == "not_started":
        return _check(
            "execution_adapter_module",
            "pass",
            "Execution adapter module declared",
            "Adapter implementation remains not started and can be audited as future work.",
        )
    return _check(
        "execution_adapter_module",
        "error",
        "Execution adapter module missing",
        "Implementation plan must include an execution_adapter module.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "launch_request_contract",
        "launch_result_contract",
        "error_contract",
        "runner_event_contract",
        "audit_evidence_contract",
        "stream_contract",
        "process_boundary_contract",
        "security_boundary_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("adapter_audit_items_declared", "pass", "Adapter audit items declared", "Future adapter evidence is explicit.")
    return _check("adapter_audit_items_declared", "error", "Adapter audit items incomplete", "Missing future adapter evidence items.")


def _check_no_adapter_or_execution() -> dict[str, object]:
    return _check(
        "no_adapter_or_execution",
        "pass",
        "No adapter or execution",
        "No adapter code, adapter import/call, POST API registration, process, session mutation, stream open, runner event, log, audit, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "adapter_implementation_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "adapter_implementation_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Execution adapter implementation audit is blocked",
        "adapter_implementation_audit_required": "Execution adapter implementation audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the real execution scope diff audit before adapter audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix adapter audit blocker",
                "action": failed.get("detail") or "Complete the scope diff audit first.",
            }
    return {
        "title": "Adapter audit remains read-only",
        "action": "Use these audit items to prepare a future authorized adapter implementation; no adapter is enabled now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "adapter_implementation_audit_only": True,
        "writes_code": False,
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
