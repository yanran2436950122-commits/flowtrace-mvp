from __future__ import annotations

from typing import Any


RUNNER_AUDIT_PERSISTENCE_IMPLEMENTATION_AUDIT_VERSION = "project_runner_audit_persistence_implementation_audits.v1"
RUNNER_AUDIT_PERSISTENCE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION = "runner_audit_persistence_implementation_audit_schema.v1"


def build_project_runner_audit_persistence_implementation_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    event_writer_audit_collection: dict[str, Any],
    audit_persistence_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    event_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in event_writer_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_persistence_by_profile = {
        str(report.get("profile_id")): report
        for report in (audit_persistence_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_audit_persistence_implementation_audit_schema()
    reports = [
        _audit_persistence_report(
            profile,
            event_audit_by_profile.get(str(profile.get("id"))),
            audit_persistence_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_AUDIT_PERSISTENCE_IMPLEMENTATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "audit_persistence_audit_required_count": sum(
                1 for report in reports if report["status"] == "audit_persistence_audit_required"
            ),
            "audit_persistence_projection_implemented_count": sum(
                1 for report in reports if report["status"] == "audit_persistence_projection_implemented"
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
            "audit_record_count": sum(
                len(report.get("audit_records", [])) for report in reports
            ),
            "audit_write_count": 0,
            "audit_read_count": 0,
            "launchable_count": (audit_persistence_collection or {}).get("summary", {}).get("launchable_count", 0),
        },
        "audit_persistence_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(audit_persistence_collection is not None),
        "next_action": _next_action(status, reports),
    }


def runner_audit_persistence_implementation_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_AUDIT_PERSISTENCE_IMPLEMENTATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "audit_persistence_implemented_now": False,
            "audit_record_written_now": False,
            "audit_log_opened_now": False,
            "audit_record_persisted_now": False,
            "audit_record_read_now": False,
            "event_written_now": False,
            "log_written_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_audit_persistence_evidence": [
            _audit_item_schema(
                "authorization_evidence_contract",
                "授权证据合约",
                "How future human authorization, typed consent, operator identity, timestamp, and scope are referenced without collecting authorization in this layer.",
            ),
            _audit_item_schema(
                "launch_decision_contract",
                "启动决策合约",
                "How future launch allow/deny decisions link to config checks, service flags, gates, and explicit blockers.",
            ),
            _audit_item_schema(
                "event_chain_summary_contract",
                "事件链摘要合约",
                "How future runner event IDs, terminal states, stream summaries, and write failures are summarized for audit records.",
            ),
            _audit_item_schema(
                "failure_reason_contract",
                "失败原因合约",
                "Canonical failure categories for denied launch, process failure, timeout, cancellation, event write failure, and audit write failure.",
            ),
            _audit_item_schema(
                "audit_record_schema_contract",
                "审计记录 schema 合约",
                "Audit record envelope, versioning, correlation IDs, immutable fields, required references, and validation rules.",
            ),
            _audit_item_schema(
                "append_only_contract",
                "追加写入合约",
                "Append-only behavior, duplicate prevention, retry semantics, and no in-place mutation of audit records.",
            ),
            _audit_item_schema(
                "integrity_contract",
                "完整性合约",
                "Record integrity checks, chain-of-custody metadata, clock source, ordering guarantees, and tamper evidence.",
            ),
            _audit_item_schema(
                "retention_contract",
                "审计保留合约",
                "Retention windows, cleanup responsibility, export boundaries, and how retention differs from runner logs.",
            ),
            _audit_item_schema(
                "access_redaction_contract",
                "访问与脱敏合约",
                "Who may view future audit records, what fields are redacted, and how secrets from events/configs are excluded.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "审计持久化夹具矩阵",
                "Future tests for allowed launch, denied launch, failure, timeout, cancellation, event write failure, audit write failure, and redaction.",
            ),
        ],
        "blocked_actions": [
            "writing audit records",
            "opening audit logs",
            "reading audit logs",
            "persisting audit records",
            "writing runner events",
            "opening runner event logs",
            "writing event logs",
            "writing log files",
            "reading or scanning log directories",
            "opening or reading stdout/stderr streams",
            "creating or controlling processes",
            "scheduling real timeouts",
            "registering launch/cancel/timeout POST APIs",
            "importing or calling execution adapters",
            "creating or mutating runner sessions",
            "collecting or storing authorization",
            "granting launch permission",
            "writing user project files",
        ],
    }


def _audit_persistence_report(
    profile: dict[str, Any],
    event_audit_report: dict[str, Any] | None,
    audit_persistence_report: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, event_audit_report, audit_persistence_report)
    checks = [
        _check_saved_profile(profile),
        _check_event_writer_audit(event_audit_report),
        _check_audit_link_item(event_audit_report),
        _check_audit_persistence_projection(audit_persistence_report),
        _check_audit_items_declared(audit_items),
        _check_no_audit_or_event_write(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_audit_persistence_implementation_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "event_writer_audit_status": (
            event_audit_report.get("status") if isinstance(event_audit_report, dict) else "missing"
        ),
        "audit_persistence_status": (
            audit_persistence_report.get("status") if isinstance(audit_persistence_report, dict) else "missing"
        ),
        "audit_records": (
            audit_persistence_report.get("audit_records", []) if isinstance(audit_persistence_report, dict) else []
        ),
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits future runner audit persistence implementation prerequisites. It does not write "
            "audit records, open or read audit logs, persist audit records, write runner events, open event logs, write "
            "logs, open or read stdout/stderr, create or control processes, schedule real timeouts, register launch/"
            "cancel/timeout APIs, import or call adapters, create or mutate sessions, collect authorization, grant "
            "permission, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    event_audit_report: dict[str, Any] | None,
    audit_persistence_report: dict[str, Any] | None,
) -> list[dict[str, object]]:
    event_audit_status = event_audit_report.get("status") if isinstance(event_audit_report, dict) else "missing"
    projection_available = isinstance(audit_persistence_report, dict)
    ready_keys = {
        "launch_decision_contract",
        "event_chain_summary_contract",
        "audit_record_schema_contract",
    }
    items = [item for item in audit_schema.get("required_audit_persistence_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "event_writer_audit_status": event_audit_status,
            "evidence_status": "ready" if projection_available and item.get("key") in ready_keys else "missing",
            "implementation_status": (
                "projection_implemented" if projection_available and item.get("key") in ready_keys else "not_started"
            ),
            "can_execute_now": False,
            "requires_future_code_change": not (projection_available and item.get("key") in ready_keys),
            "requires_future_review": True,
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
    return _check("saved_profile", "error", "Missing saved run profile", "Audit persistence audit requires a saved run profile.")


def _check_event_writer_audit(event_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not event_audit_report:
        return _check(
            "event_writer_audit",
            "error",
            "Missing event writer audit",
            "Generate the event writer implementation audit before audit persistence audit.",
        )
    if event_audit_report.get("status") in {"event_writer_audit_required", "event_writer_projection_implemented"}:
        return _check(
            "event_writer_audit",
            "pass",
            "Event writer audit declared",
            "Event audit-link evidence is available for future audit persistence planning.",
        )
    return _check(
        "event_writer_audit",
        "error",
        "Event writer audit status is unexpected",
        str(event_audit_report.get("status") or "unknown"),
    )


def _check_audit_link_item(event_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = set()
    if isinstance(event_audit_report, dict):
        audit_keys = {str(item.get("key")) for item in event_audit_report.get("audit_items", []) if isinstance(item, dict)}
    if "audit_link_contract" in audit_keys:
        return _check(
            "audit_link_contract",
            "pass",
            "Audit-link evidence declared",
            "Event writer audit includes audit-link evidence for future audit persistence.",
        )
    return _check(
        "audit_link_contract",
        "error",
        "Audit-link evidence missing",
        "Event writer audit must include audit_link_contract before audit persistence audit.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "authorization_evidence_contract",
        "launch_decision_contract",
        "event_chain_summary_contract",
        "failure_reason_contract",
        "audit_record_schema_contract",
        "append_only_contract",
        "integrity_contract",
        "retention_contract",
        "access_redaction_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("audit_persistence_items_declared", "pass", "Audit persistence items declared", "Future audit persistence evidence is explicit.")
    return _check("audit_persistence_items_declared", "error", "Audit persistence items incomplete", "Missing future audit persistence evidence items.")


def _check_audit_persistence_projection(audit_persistence_report: dict[str, Any] | None) -> dict[str, object]:
    if not audit_persistence_report:
        return _check(
            "audit_persistence_projection",
            "warn",
            "Audit persistence projection not supplied",
            "Legacy audit-only mode remains valid until the projection collection is wired into this audit.",
        )
    records = audit_persistence_report.get("audit_records", [])
    if isinstance(records, list) and all(isinstance(record, dict) and not record.get("persisted") for record in records):
        return _check(
            "audit_persistence_projection",
            "pass",
            "Audit persistence projection supplied",
            "Projected audit records are present and marked as not persisted.",
        )
    return _check(
        "audit_persistence_projection",
        "error",
        "Audit persistence projection invalid",
        "Projected audit records must be list-shaped and must not be persisted.",
    )


def _check_no_audit_or_event_write() -> dict[str, object]:
    return _check(
        "no_audit_or_event_write",
        "pass",
        "No audit or event write",
        "No audit record write, audit log open/read, audit persistence, runner event write, event log open/write, log write/read, stdout/stderr open/read, process creation/control, timeout scheduling, POST API registration, adapter call, session mutation, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if any(check.get("key") == "audit_persistence_projection" and check.get("status") == "pass" for check in checks):
        return "audit_persistence_projection_implemented"
    return "audit_persistence_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "audit_persistence_projection_implemented" for report in reports):
        return "audit_persistence_projection_implemented"
    return "audit_persistence_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Audit persistence implementation audit is blocked",
        "audit_persistence_projection_implemented": "Audit persistence projection is implemented",
        "audit_persistence_audit_required": "Audit persistence implementation audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the event writer implementation audit before audit persistence audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix audit persistence blocker",
                "action": failed.get("detail") or "Complete the event writer audit first.",
            }
    return {
        "title": "Audit persistence remains projection-only",
        "action": "Use projected audit records to review launch, lifecycle, stream, and event summaries; no audit record is written now.",
    }


def _safety(projection_enabled: bool = False) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": projection_enabled,
        "launch_enabled": projection_enabled,
        "launch_api_available": projection_enabled,
        "audit_persistence_audit_only": not projection_enabled,
        "audit_persistence_projection": projection_enabled,
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
        "controls_process": False,
        "schedules_timeout": False,
        "opens_stdout_stderr": False,
        "reads_stdout_stderr": False,
        "captures_stdout_stderr": False,
        "writes_runner_events": False,
        "opens_runner_event_log": False,
        "writes_event_log": False,
        "opens_audit_log": False,
        "reads_audit_log": False,
        "writes_audit_log": False,
        "stores_audit_records": False,
        "reads_audit_records": False,
        "scans_log_directory": False,
        "reads_log_files": False,
        "writes_logs": False,
        "deletes_logs": False,
        "rotates_logs": False,
        "renames_logs": False,
        "truncates_logs": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
        "creates_config_file": False,
    }
