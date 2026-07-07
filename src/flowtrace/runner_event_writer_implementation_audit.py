from __future__ import annotations

from typing import Any


RUNNER_EVENT_WRITER_IMPLEMENTATION_AUDIT_VERSION = "project_runner_event_writer_implementation_audits.v1"
RUNNER_EVENT_WRITER_IMPLEMENTATION_AUDIT_SCHEMA_VERSION = "runner_event_writer_implementation_audit_schema.v1"


def build_project_runner_event_writer_implementation_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    stream_capture_audit_collection: dict[str, Any],
    event_writer_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    stream_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in stream_capture_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    event_writer_by_profile = {
        str(report.get("profile_id")): report
        for report in (event_writer_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    event_writer_projection_available = event_writer_collection is not None
    audit_schema = runner_event_writer_implementation_audit_schema()
    reports = [
        _event_writer_audit_report(
            profile,
            stream_audit_by_profile.get(str(profile.get("id"))),
            event_writer_by_profile.get(str(profile.get("id"))),
            event_writer_projection_available,
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EVENT_WRITER_IMPLEMENTATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "event_writer_audit_required_count": sum(
                1 for report in reports if report["status"] == "event_writer_audit_required"
            ),
            "implemented_count": sum(1 for report in reports if report["status"] == "event_writer_projection_implemented"),
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
            "event_write_count": 0,
            "log_write_count": 0,
            "launchable_count": 0,
        },
        "event_writer_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(event_writer_projection_available),
        "next_action": _next_action(status, reports),
    }


def runner_event_writer_implementation_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EVENT_WRITER_IMPLEMENTATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": False,
            "event_writer_implemented_now": True,
            "event_written_now": False,
            "event_log_opened_now": False,
            "event_persisted_now": False,
            "log_written_now": False,
            "projection_only_now": True,
            "can_launch_now": True,
            "requires_new_authorized_implementation_round": False,
        },
        "required_event_writer_evidence": [
            _audit_item_schema(
                "event_schema_contract",
                "事件 schema 合约",
                "Event envelope, required fields, versioning, correlation IDs, timestamps, and payload validation.",
            ),
            _audit_item_schema(
                "event_ordering_contract",
                "事件顺序合约",
                "Ordering rules for launch intent, process start, stream chunks, errors, terminal states, and retries.",
            ),
            _audit_item_schema(
                "lifecycle_event_contract",
                "生命周期事件合约",
                "Future event mapping for requested, accepted, started, running, cancelled, timed out, failed, and completed states.",
            ),
            _audit_item_schema(
                "stream_event_contract",
                "输出流事件合约",
                "Future stdout/stderr chunk event shape, chunk indexes, redaction markers, truncation markers, and stream closure.",
            ),
            _audit_item_schema(
                "terminal_event_contract",
                "终止态事件合约",
                "Single terminal event ownership, exit code mapping, timeout/cancel/crash distinction, and final stream correlation.",
            ),
            _audit_item_schema(
                "idempotent_write_contract",
                "幂等写入合约",
                "Deduplication keys, retry behavior, duplicate terminal-event prevention, and append-only semantics.",
            ),
            _audit_item_schema(
                "write_failure_contract",
                "写入失败合约",
                "Failure handling for unavailable event storage, partial writes, validation errors, and operator-facing failure evidence.",
            ),
            _audit_item_schema(
                "redaction_contract",
                "事件脱敏合约",
                "Secret masking before event projection, environment redaction, raw-output exclusion, and sensitive metadata rules.",
            ),
            _audit_item_schema(
                "audit_link_contract",
                "审计关联合约",
                "How future run events link to authorization evidence, execution config checks, stream capture evidence, and audit trails.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "事件写入夹具矩阵",
                "Future tests for normal completion, failure, timeout, cancellation, stream interleaving, write retry, and redaction.",
            ),
        ],
        "blocked_actions": [
            "writing runner events",
            "opening runner event logs",
            "persisting runner events",
            "writing log files",
            "reading or scanning log directories",
            "opening or reading stdout/stderr streams",
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


def _event_writer_audit_report(
    profile: dict[str, Any],
    stream_audit_report: dict[str, Any] | None,
    event_writer_report: dict[str, Any] | None,
    event_writer_projection_available: bool,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, stream_audit_report, event_writer_report, event_writer_projection_available)
    checks = [
        _check_saved_profile(profile),
        _check_stream_capture_audit(stream_audit_report),
        _check_event_projection_item(stream_audit_report),
        _check_event_writer_projection(event_writer_report, event_writer_projection_available),
        _check_audit_items_declared(audit_items),
        _check_no_event_or_log_write(),
    ]
    status = _report_status(checks) if event_writer_projection_available else _legacy_report_status(checks)
    return {
        "id": f"runner_event_writer_implementation_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "stream_capture_audit_status": (
            stream_audit_report.get("status") if isinstance(stream_audit_report, dict) else "missing"
        ),
        "event_writer_status": event_writer_report.get("status") if isinstance(event_writer_report, dict) else "missing",
        "events": event_writer_report.get("events") if isinstance(event_writer_report, dict) else [],
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer verifies runner event shapes projected from existing launch, lifecycle, and stream records. "
            "It does not write runner events, open event logs, persist events, write logs, open or read stdout/stderr, "
            "create or control processes, schedule real timeouts, register cancel/timeout APIs, write audit logs, "
            "collect authorization, grant permission, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    stream_audit_report: dict[str, Any] | None,
    event_writer_report: dict[str, Any] | None,
    event_writer_projection_available: bool,
) -> list[dict[str, object]]:
    stream_audit_status = stream_audit_report.get("status") if isinstance(stream_audit_report, dict) else "missing"
    projection_ready = event_writer_projection_available and isinstance(event_writer_report, dict)
    implemented_keys = {
        "event_schema_contract",
        "lifecycle_event_contract",
        "stream_event_contract",
        "terminal_event_contract",
    } if projection_ready else set()
    items = [item for item in audit_schema.get("required_event_writer_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "stream_capture_audit_status": stream_audit_status,
            "event_writer_status": event_writer_report.get("status") if isinstance(event_writer_report, dict) else "missing",
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
    return _check("saved_profile", "error", "Missing saved run profile", "Event writer audit requires a saved run profile.")


def _check_stream_capture_audit(stream_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not stream_audit_report:
        return _check(
            "stream_capture_audit",
            "error",
            "Missing stream capture audit",
            "Generate the stream capture implementation audit before event writer audit.",
        )
    if stream_audit_report.get("status") in {"stream_capture_audit_required", "stream_capture_minimal_implemented"}:
        return _check(
            "stream_capture_audit",
            "pass",
            "Stream capture evidence available",
            "Stream event-projection evidence is available for event writer projection.",
        )
    return _check(
        "stream_capture_audit",
        "error",
        "Stream capture audit status is unexpected",
        str(stream_audit_report.get("status") or "unknown"),
    )


def _check_event_projection_item(stream_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = set()
    if isinstance(stream_audit_report, dict):
        audit_keys = {str(item.get("key")) for item in stream_audit_report.get("audit_items", []) if isinstance(item, dict)}
    if "event_projection_contract" in audit_keys:
        return _check(
            "event_projection_contract",
            "pass",
            "Event projection evidence declared",
            "Stream capture audit includes event projection evidence for future runner event writing.",
        )
    return _check(
        "event_projection_contract",
        "error",
        "Event projection evidence missing",
        "Stream capture audit must include event_projection_contract before event writer audit.",
    )


def _check_event_writer_projection(
    event_writer_report: dict[str, Any] | None,
    event_writer_projection_available: bool,
) -> dict[str, object]:
    if not event_writer_projection_available:
        return _check(
            "event_writer_projection",
            "warn",
            "Event writer projection not supplied",
            "This audit is running in compatibility mode before the round-13 projection is wired.",
        )
    if isinstance(event_writer_report, dict) and isinstance(event_writer_report.get("events"), list):
        return _check(
            "event_writer_projection",
            "pass",
            "Minimal event writer projection present",
            str(event_writer_report.get("status") or "unknown"),
        )
    return _check(
        "event_writer_projection",
        "error",
        "Missing event writer projection",
        "Generate the minimal event writer projection before marking round 13 implemented.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "event_schema_contract",
        "event_ordering_contract",
        "lifecycle_event_contract",
        "stream_event_contract",
        "terminal_event_contract",
        "idempotent_write_contract",
        "write_failure_contract",
        "redaction_contract",
        "audit_link_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("event_writer_audit_items_declared", "pass", "Event writer audit items declared", "Future runner event evidence is explicit.")
    return _check("event_writer_audit_items_declared", "error", "Event writer audit items incomplete", "Missing future event writer evidence items.")


def _check_no_event_or_log_write() -> dict[str, object]:
    return _check(
        "no_event_or_log_write",
        "pass",
        "No event or log write",
        "Projection does not write runner events, open event logs, persist events, write logs, open/read stdout/stderr, create/control processes, schedule timeouts, register cancel/timeout APIs, write audits, collect authorization, grant permission, or write user projects.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "event_writer_projection_implemented"


def _legacy_report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "event_writer_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if all(report.get("status") == "event_writer_audit_required" for report in reports):
        return "event_writer_audit_required"
    return "event_writer_projection_implemented"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Event writer implementation audit is blocked",
        "event_writer_audit_required": "Event writer implementation audit is required",
        "event_writer_projection_implemented": "Minimal runner event projection is implemented",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the stream capture implementation audit before event writer audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix event writer audit blocker",
                "action": failed.get("detail") or "Complete the stream capture audit first.",
            }
    return {
        "title": "Minimal event projection implemented",
        "action": "Use projected event shapes for UI review; event log writes and audit persistence remain locked.",
    }


def _safety(event_writer_projection_available: bool = True) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": event_writer_projection_available,
        "launch_enabled": event_writer_projection_available,
        "launch_api_available": event_writer_projection_available,
        "event_writer_audit_only": not event_writer_projection_available,
        "event_writer_projection": event_writer_projection_available,
        "writes_code": event_writer_projection_available,
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
        "opens_runner_event_log": False,
        "writes_event_log": False,
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
