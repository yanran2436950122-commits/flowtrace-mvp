from __future__ import annotations

from typing import Any


RUNNER_STREAM_CAPTURE_IMPLEMENTATION_AUDIT_VERSION = "project_runner_stream_capture_implementation_audits.v1"
RUNNER_STREAM_CAPTURE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION = "runner_stream_capture_implementation_audit_schema.v1"


def build_project_runner_stream_capture_implementation_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    process_lifecycle_audit_collection: dict[str, Any],
    stream_capture_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    process_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in process_lifecycle_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    stream_capture_by_profile = {
        str(report.get("profile_id")): report
        for report in (stream_capture_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    stream_capture_projection_available = stream_capture_collection is not None
    audit_schema = runner_stream_capture_implementation_audit_schema()
    reports = [
        _stream_capture_audit_report(
            profile,
            process_audit_by_profile.get(str(profile.get("id"))),
            stream_capture_by_profile.get(str(profile.get("id"))),
            stream_capture_projection_available,
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_STREAM_CAPTURE_IMPLEMENTATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "stream_capture_audit_required_count": sum(
                1 for report in reports if report["status"] == "stream_capture_audit_required"
            ),
            "implemented_count": sum(1 for report in reports if report["status"] == "stream_capture_minimal_implemented"),
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
            "stream_open_count": 0,
            "log_write_count": 0,
            "launchable_count": 0,
        },
        "stream_capture_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(stream_capture_projection_available),
        "next_action": _next_action(status, reports),
    }


def runner_stream_capture_implementation_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_STREAM_CAPTURE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": False,
            "stdout_opened_now": False,
            "stderr_opened_now": False,
            "stream_capture_enabled_now": True,
            "stream_persisted_now": False,
            "log_written_now": False,
            "projection_only_now": True,
            "can_launch_now": True,
            "requires_new_authorized_implementation_round": False,
        },
        "required_stream_capture_evidence": [
            _audit_item_schema(
                "stream_open_contract",
                "流打开合约",
                "Future ownership for stdout/stderr handles, lifecycle timing, close semantics, and no current stream access.",
            ),
            _audit_item_schema(
                "chunking_contract",
                "分块合约",
                "Maximum chunk size, ordering, line boundaries, binary/encoding policy, and partial-line handling.",
            ),
            _audit_item_schema(
                "redaction_contract",
                "脱敏合约",
                "Secret patterns, environment redaction, token masking, and evidence that raw sensitive output is not persisted.",
            ),
            _audit_item_schema(
                "backpressure_contract",
                "背压合约",
                "Buffer limits, overflow behavior, slow consumer handling, and process safety when streams are noisy.",
            ),
            _audit_item_schema(
                "retention_contract",
                "保留策略合约",
                "In-memory and durable retention limits, truncation markers, and deletion/rotation responsibility.",
            ),
            _audit_item_schema(
                "terminal_correlation_contract",
                "终止态关联",
                "How stream closure, final chunks, exit status, timeout, cancellation, and crash states are correlated.",
            ),
            _audit_item_schema(
                "event_projection_contract",
                "事件投影合约",
                "Future runner event payloads for stdout/stderr chunks without writing events in this layer.",
            ),
            _audit_item_schema(
                "operator_view_contract",
                "操作员视图合约",
                "UI paging, tailing, collapsed noisy output, copy restrictions, and disabled-state explanations.",
            ),
            _audit_item_schema(
                "failure_contract",
                "捕获失败合约",
                "Read errors, decode errors, redaction failures, buffer overflow, and audit/write failure reporting.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "输出流夹具矩阵",
                "Future tests for stdout-only, stderr-only, interleaved output, long lines, secret output, overflow, and abrupt exit.",
            ),
        ],
        "blocked_actions": [
            "opening stdout/stderr streams",
            "reading stdout/stderr streams",
            "writing new stdout/stderr logs",
            "writing runner events",
            "reading or writing log files",
            "creating or controlling processes",
            "scheduling real timeouts",
            "registering launch/cancel/timeout POST APIs",
            "importing or calling execution adapters",
            "creating or mutating runner sessions",
            "writing audit logs",
            "collecting or storing authorization",
            "granting launch permission",
            "writing user project files",
        ],
    }


def _stream_capture_audit_report(
    profile: dict[str, Any],
    process_audit_report: dict[str, Any] | None,
    stream_capture_report: dict[str, Any] | None,
    stream_capture_projection_available: bool,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, process_audit_report, stream_capture_report, stream_capture_projection_available)
    checks = [
        _check_saved_profile(profile),
        _check_process_lifecycle_audit(process_audit_report),
        _check_terminal_state_item(process_audit_report),
        _check_stream_capture_projection(stream_capture_report, stream_capture_projection_available),
        _check_audit_items_declared(audit_items),
        _check_no_stream_or_log_access(),
    ]
    status = _report_status(checks) if stream_capture_projection_available else _legacy_report_status(checks)
    return {
        "id": f"runner_stream_capture_implementation_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "process_lifecycle_audit_status": (
            process_audit_report.get("status") if isinstance(process_audit_report, dict) else "missing"
        ),
        "stream_capture_status": stream_capture_report.get("status") if isinstance(stream_capture_report, dict) else "missing",
        "streams": stream_capture_report.get("streams") if isinstance(stream_capture_report, dict) else [],
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer verifies a stdout/stderr projection from stored execution records. It does not open or read "
            "live stdout/stderr streams, write new logs or runner events, create or control processes, schedule real "
            "timeouts, register cancel/timeout APIs, import or call adapters, write audit logs, collect authorization, "
            "grant permission, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    process_audit_report: dict[str, Any] | None,
    stream_capture_report: dict[str, Any] | None,
    stream_capture_projection_available: bool,
) -> list[dict[str, object]]:
    process_audit_status = process_audit_report.get("status") if isinstance(process_audit_report, dict) else "missing"
    stream_capture_ready = stream_capture_projection_available and isinstance(stream_capture_report, dict)
    implemented_keys = {"chunking_contract", "terminal_correlation_contract", "operator_view_contract"} if stream_capture_ready else set()
    items = [item for item in audit_schema.get("required_stream_capture_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "process_lifecycle_audit_status": process_audit_status,
            "stream_capture_status": stream_capture_report.get("status") if isinstance(stream_capture_report, dict) else "missing",
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
    return _check("saved_profile", "error", "Missing saved run profile", "Stream capture audit requires a saved run profile.")


def _check_process_lifecycle_audit(process_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not process_audit_report:
        return _check(
            "process_lifecycle_audit",
            "error",
            "Missing process lifecycle audit",
            "Generate the process lifecycle implementation audit before stream capture audit.",
        )
    if process_audit_report.get("status") in {"process_lifecycle_audit_required", "process_lifecycle_minimal_implemented"}:
        return _check(
            "process_lifecycle_audit",
            "pass",
            "Process lifecycle evidence available",
            "Process terminal-state evidence is available for stream capture projection.",
        )
    return _check(
        "process_lifecycle_audit",
        "error",
        "Process lifecycle audit status is unexpected",
        str(process_audit_report.get("status") or "unknown"),
    )


def _check_terminal_state_item(process_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = set()
    if isinstance(process_audit_report, dict):
        audit_keys = {str(item.get("key")) for item in process_audit_report.get("audit_items", []) if isinstance(item, dict)}
    if "terminal_state_contract" in audit_keys:
        return _check(
            "terminal_state_contract",
            "pass",
            "Terminal-state evidence declared",
            "Process lifecycle audit includes terminal-state evidence for stream correlation.",
        )
    return _check(
        "terminal_state_contract",
        "error",
        "Terminal-state evidence missing",
        "Process lifecycle audit must include terminal_state_contract before stream capture audit.",
    )


def _check_stream_capture_projection(
    stream_capture_report: dict[str, Any] | None,
    stream_capture_projection_available: bool,
) -> dict[str, object]:
    if not stream_capture_projection_available:
        return _check(
            "stream_capture_projection",
            "warn",
            "Stream capture projection not supplied",
            "This audit is running in compatibility mode before the round-12 projection is wired.",
        )
    if isinstance(stream_capture_report, dict) and isinstance(stream_capture_report.get("streams"), list):
        return _check(
            "stream_capture_projection",
            "pass",
            "Minimal stream capture projection present",
            str(stream_capture_report.get("status") or "unknown"),
        )
    return _check(
        "stream_capture_projection",
        "error",
        "Missing stream capture projection",
        "Generate the minimal stream capture projection before marking round 12 implemented.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "stream_open_contract",
        "chunking_contract",
        "redaction_contract",
        "backpressure_contract",
        "retention_contract",
        "terminal_correlation_contract",
        "event_projection_contract",
        "operator_view_contract",
        "failure_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("stream_capture_audit_items_declared", "pass", "Stream capture audit items declared", "Future stdout/stderr evidence is explicit.")
    return _check("stream_capture_audit_items_declared", "error", "Stream capture audit items incomplete", "Missing future stream capture evidence items.")


def _check_no_stream_or_log_access() -> dict[str, object]:
    return _check(
        "no_stream_or_log_access",
        "pass",
        "No live stream or log access",
        "Projection does not open/read stdout/stderr, write new logs, write runner events, create/control processes, schedule timeouts, register cancel/timeout APIs, call adapters, write audits, collect authorization, grant permission, or write user projects.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "stream_capture_minimal_implemented"


def _legacy_report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "stream_capture_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if all(report.get("status") == "stream_capture_audit_required" for report in reports):
        return "stream_capture_audit_required"
    return "stream_capture_minimal_implemented"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Stream capture implementation audit is blocked",
        "stream_capture_audit_required": "Stream capture implementation audit is required",
        "stream_capture_minimal_implemented": "Minimal stdout/stderr projection is implemented",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the process lifecycle implementation audit before stream capture audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix stream capture audit blocker",
                "action": failed.get("detail") or "Complete the process lifecycle audit first.",
            }
    return {
        "title": "Minimal stream projection implemented",
        "action": "Use bounded stdout/stderr previews from stored execution records; live streaming and log writes remain locked.",
    }


def _safety(stream_capture_projection_available: bool = True) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": stream_capture_projection_available,
        "launch_enabled": stream_capture_projection_available,
        "launch_api_available": stream_capture_projection_available,
        "stream_capture_audit_only": not stream_capture_projection_available,
        "stream_capture_projection": stream_capture_projection_available,
        "writes_code": stream_capture_projection_available,
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
        "reads_stdout_stderr": False,
        "captures_stdout_stderr": False,
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
