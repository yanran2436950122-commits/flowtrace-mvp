from __future__ import annotations

from typing import Any


RUNNER_FINAL_BLOCK_MATRIX_VERSION = "project_runner_final_block_matrices.v1"
RUNNER_FINAL_BLOCK_MATRIX_SCHEMA_VERSION = "runner_final_block_matrix_schema.v1"


def build_project_runner_final_block_matrices(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_adapter_reviews: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    review_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_adapter_reviews.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    matrix_schema = runner_final_block_matrix_schema()
    reports = [
        _final_block_report(profile, review_by_profile.get(str(profile.get("id"))), matrix_schema)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_FINAL_BLOCK_MATRIX_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "final_block_required_count": sum(1 for report in reports if report["status"] == "final_block_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "blocking_reason_count": sum(len(report.get("blocking_reasons", [])) for report in reports),
            "launchable_count": 0,
        },
        "block_matrix_schema": matrix_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "final_block_matrix_only": True,
            "registers_post_api": False,
            "imports_adapter": False,
            "calls_execution_adapter": False,
            "scans_code": False,
            "reads_environment": False,
            "parses_process_args": False,
            "opens_stdout_stderr": False,
            "writes_runner_events": False,
            "stores_launch_state": False,
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


def runner_final_block_matrix_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_FINAL_BLOCK_MATRIX_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "matrix_state": {
            "read_only": True,
            "can_launch_now": False,
            "requires_new_implementation_round": True,
        },
        "blocking_dimensions": [
            "launch_api_not_registered",
            "runner_adapter_not_implemented",
            "adapter_review_is_preimplementation",
            "process_creation_disabled",
            "command_execution_disabled",
            "stdout_stderr_writes_disabled",
            "runner_event_writes_disabled",
            "log_cleanup_execution_disabled",
            "audit_log_persistence_disabled",
            "user_project_writes_disabled",
        ],
        "required_future_unlocks": [
            "explicit service flag enablement",
            "valid runner configuration file",
            "fresh launch snapshot",
            "implemented execution adapter",
            "registered launch POST API",
            "live stdout/stderr sink",
            "runner event log writer",
            "cancel and timeout endpoints",
            "audit-log persistence",
            "new human authorization round",
        ],
        "blocked_actions": [
            "registering POST /api/project/runner/launch",
            "loading execution adapter",
            "calling execution adapter",
            "subprocess.Popen",
            "os.system",
            "shell=True",
            "opening stdout/stderr files",
            "writing runner event logs",
            "reading log files",
            "writing audit logs",
            "deleting or rotating logs",
            "writing user project files",
        ],
    }


def _final_block_report(
    profile: dict[str, Any],
    adapter_review_report: dict[str, Any] | None,
    matrix_schema: dict[str, object],
) -> dict[str, object]:
    blocking_reasons = _blocking_reasons(adapter_review_report, matrix_schema)
    checks = [
        _check_saved_profile(profile),
        _check_adapter_review(adapter_review_report),
        _check_matrix_declared(matrix_schema),
        _check_required_unlocks(matrix_schema),
        _check_no_launch_surface(),
        _check_no_execution(),
        _check_no_log_or_audit_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_final_block_matrix:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "execution_adapter_review_status": (
            adapter_review_report.get("status") if isinstance(adapter_review_report, dict) else "missing"
        ),
        "launch_state": {
            "launchable": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "reason": "The final block matrix is read-only and still reports no real runner implementation.",
        },
        "matrix_state": matrix_schema["matrix_state"],
        "blocking_dimensions": matrix_schema["blocking_dimensions"],
        "blocking_reasons": blocking_reasons,
        "required_future_unlocks": matrix_schema["required_future_unlocks"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only aggregates final launch blockers. It does not register launch APIs, load or call adapters, "
            "create processes, execute commands, open stdout/stderr files, read/write logs, write audit logs, delete or rotate logs, "
            "or modify the user project."
        ),
    }


def _blocking_reasons(adapter_review_report: dict[str, Any] | None, matrix_schema: dict[str, object]) -> list[dict[str, object]]:
    reasons = [
        {
            "key": "launch_api_not_registered",
            "severity": "blocker",
            "title": "Launch API is not registered",
            "detail": "No real POST /api/project/runner/launch endpoint exists.",
        },
        {
            "key": "runner_adapter_not_implemented",
            "severity": "blocker",
            "title": "Execution adapter is not implemented",
            "detail": "The current adapter review is pre-implementation and does not load or call an adapter.",
        },
        {
            "key": "process_creation_disabled",
            "severity": "blocker",
            "title": "Process creation remains disabled",
            "detail": "No subprocess, shell, or command execution is allowed by the current boundary.",
        },
        {
            "key": "log_writes_disabled",
            "severity": "blocker",
            "title": "Runtime log writes remain disabled",
            "detail": "stdout/stderr, runner events, cleanup logs, and audit-log persistence are not enabled.",
        },
    ]
    if not adapter_review_report:
        reasons.append(
            {
                "key": "missing_adapter_review",
                "severity": "blocker",
                "title": "Execution adapter review is missing",
                "detail": "Generate the execution adapter review read-only report first.",
            }
        )
    elif adapter_review_report.get("status") != "adapter_review_required":
        reasons.append(
            {
                "key": "adapter_review_blocked",
                "severity": "blocker",
                "title": "Execution adapter review is blocked",
                "detail": str(adapter_review_report.get("status") or "unknown"),
            }
        )
    declared_dimensions = matrix_schema.get("blocking_dimensions")
    if isinstance(declared_dimensions, list):
        declared = {str(item) for item in declared_dimensions}
        for reason in reasons:
            reason["declared"] = reason["key"] in declared or reason["key"] in {"log_writes_disabled", "missing_adapter_review", "adapter_review_blocked"}
    return reasons


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Final block matrix requires a saved run profile.")


def _check_adapter_review(adapter_review_report: dict[str, Any] | None) -> dict[str, object]:
    if not adapter_review_report:
        return _check("execution_adapter_review", "error", "Missing execution adapter review", "Generate the adapter review read-only report first.")
    if adapter_review_report.get("status") == "adapter_review_required":
        return _check("execution_adapter_review", "pass", "Execution adapter review declared", "Final blockers can be aggregated read-only.")
    return _check(
        "execution_adapter_review",
        "error",
        "Execution adapter review is blocked",
        str(adapter_review_report.get("status") or "unknown"),
    )


def _check_matrix_declared(matrix_schema: dict[str, object]) -> dict[str, object]:
    dimensions = matrix_schema.get("blocking_dimensions")
    required = {"launch_api_not_registered", "runner_adapter_not_implemented", "process_creation_disabled"}
    if isinstance(dimensions, list) and required.issubset(set(str(item) for item in dimensions)):
        return _check("matrix_declared", "pass", "Final block matrix declared", "Launch blockers are explicit and deterministic.")
    return _check("matrix_declared", "error", "Final block matrix incomplete", "Missing required launch blocking dimensions.")


def _check_required_unlocks(matrix_schema: dict[str, object]) -> dict[str, object]:
    unlocks = matrix_schema.get("required_future_unlocks")
    required = {"implemented execution adapter", "registered launch POST API", "new human authorization round"}
    if isinstance(unlocks, list) and required.issubset(set(str(item) for item in unlocks)):
        return _check("required_unlocks", "pass", "Future unlocks declared", "Real launch still requires a separate implementation and authorization round.")
    return _check("required_unlocks", "error", "Future unlocks incomplete", "Missing future launch unlock requirements.")


def _check_no_launch_surface() -> dict[str, object]:
    return _check("no_launch_surface", "pass", "No launch surface exists", "No launch POST API is registered by this layer.")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "No command execution", "No adapter loading, process creation, subprocess, shell, or command execution occurs.")


def _check_no_log_or_audit_mutation() -> dict[str, object]:
    return _check("no_log_or_audit_mutation", "pass", "No log or audit mutation", "No log files, runner events, audit logs, or user project files are read or written.")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "final_block_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "final_block_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Final block matrix is blocked",
        "final_block_required": "Final block matrix keeps real launch disabled",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the runner governance chain before aggregating final blockers.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix final block matrix blocker",
                "action": failed.get("detail") or "Complete prerequisite read-only runner governance layers first.",
            }
    return {
        "title": "Real launch remains blocked",
        "action": "A separate implementation and authorization round is still required before any real launch API, adapter call, process creation, or log writing can exist.",
    }
