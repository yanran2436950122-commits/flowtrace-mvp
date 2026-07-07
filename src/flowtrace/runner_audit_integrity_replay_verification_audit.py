from __future__ import annotations

from typing import Any


RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_AUDIT_VERSION = (
    "project_runner_audit_integrity_replay_verification_audits.v1"
)
RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_AUDIT_SCHEMA_VERSION = (
    "runner_audit_integrity_replay_verification_audit_schema.v1"
)


def build_project_runner_audit_integrity_replay_verification_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    audit_persistence_audit_collection: dict[str, Any],
    integrity_replay_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    persistence_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in audit_persistence_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    integrity_replay_by_profile = {
        str(report.get("profile_id")): report
        for report in (integrity_replay_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_audit_integrity_replay_verification_audit_schema()
    reports = [
        _integrity_replay_report(
            profile,
            persistence_audit_by_profile.get(str(profile.get("id"))),
            integrity_replay_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "integrity_replay_audit_required_count": sum(
                1 for report in reports if report["status"] == "integrity_replay_audit_required"
            ),
            "integrity_replay_projection_implemented_count": sum(
                1 for report in reports if report["status"] == "integrity_replay_projection_implemented"
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
            "integrity_check_count": sum(len(report.get("integrity_checks", [])) for report in reports),
            "replay_check_count": sum(len(report.get("replay_checks", [])) for report in reports),
            "consistency_check_count": sum(len(report.get("consistency_checks", [])) for report in reports),
            "launchable_count": (integrity_replay_collection or {}).get("summary", {}).get("launchable_count", 0),
        },
        "integrity_replay_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(integrity_replay_collection is not None),
        "next_action": _next_action(status, reports),
    }


def runner_audit_integrity_replay_verification_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "integrity_verification_implemented_now": False,
            "replay_verification_implemented_now": False,
            "audit_log_opened_now": False,
            "audit_record_read_now": False,
            "runner_event_read_now": False,
            "config_snapshot_read_now": False,
            "integrity_checked_now": False,
            "replay_checked_now": False,
            "consistency_checked_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_integrity_replay_evidence": [
            _audit_item_schema(
                "audit_record_reference_contract",
                "审计记录引用合约",
                "How future verification locates immutable audit record IDs, event-chain references, launch decisions, and failure reasons.",
            ),
            _audit_item_schema(
                "event_replay_contract",
                "事件回放合约",
                "Replay order, expected event sequence, terminal-state reconstruction, and how missing or duplicate events are handled.",
            ),
            _audit_item_schema(
                "config_snapshot_contract",
                "配置快照合约",
                "How future verification compares launch configuration snapshots, service flags, and runtime policy evidence.",
            ),
            _audit_item_schema(
                "failure_reason_mapping_contract",
                "失败原因映射合约",
                "Canonical mapping between runner events, audit records, blocked launch reasons, and user-facing failure categories.",
            ),
            _audit_item_schema(
                "integrity_hash_contract",
                "完整性哈希合约",
                "Future checksum/hash inputs, canonical serialization, tamper evidence, and excluded sensitive fields.",
            ),
            _audit_item_schema(
                "ordering_validation_contract",
                "顺序校验合约",
                "Rules for validating monotonic timestamps, sequence numbers, append-only audit records, and terminal event uniqueness.",
            ),
            _audit_item_schema(
                "terminal_state_reconciliation_contract",
                "终止态对账合约",
                "How completed, failed, cancelled, timed out, and crashed states reconcile across events, sessions, and audit records.",
            ),
            _audit_item_schema(
                "redaction_consistency_contract",
                "脱敏一致性合约",
                "How verification proves sensitive values are excluded consistently from events, audit records, and operator summaries.",
            ),
            _audit_item_schema(
                "discrepancy_reporting_contract",
                "差异报告合约",
                "Future discrepancy categories, severity, operator messages, and no-mutation reporting behavior.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "完整性回放夹具矩阵",
                "Future tests for normal replay, missing events, duplicate events, mismatched config, tampering, timeout, cancellation, and redaction.",
            ),
        ],
        "blocked_actions": [
            "reading audit logs",
            "opening audit logs",
            "writing audit logs",
            "reading audit records",
            "storing audit records",
            "reading runner events",
            "writing runner events",
            "opening runner event logs",
            "writing event logs",
            "reading config snapshots",
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


def _integrity_replay_report(
    profile: dict[str, Any],
    persistence_audit_report: dict[str, Any] | None,
    integrity_replay_report: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, persistence_audit_report, integrity_replay_report)
    checks = [
        _check_saved_profile(profile),
        _check_audit_persistence_audit(persistence_audit_report),
        _check_integrity_item(persistence_audit_report),
        _check_audit_record_schema_item(persistence_audit_report),
        _check_integrity_replay_projection(integrity_replay_report),
        _check_audit_items_declared(audit_items),
        _check_no_read_write_or_replay(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_audit_integrity_replay_verification_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "audit_persistence_audit_status": (
            persistence_audit_report.get("status") if isinstance(persistence_audit_report, dict) else "missing"
        ),
        "integrity_replay_status": (
            integrity_replay_report.get("status") if isinstance(integrity_replay_report, dict) else "missing"
        ),
        "integrity_checks": (
            integrity_replay_report.get("integrity_checks", []) if isinstance(integrity_replay_report, dict) else []
        ),
        "replay_checks": (
            integrity_replay_report.get("replay_checks", []) if isinstance(integrity_replay_report, dict) else []
        ),
        "consistency_checks": (
            integrity_replay_report.get("consistency_checks", []) if isinstance(integrity_replay_report, dict) else []
        ),
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits future audit integrity and replay verification prerequisites. It does not read "
            "audit logs, open audit logs, read audit records, read runner events, read config snapshots, perform "
            "integrity checks, replay events, write audit logs, write runner events, write logs, open or read stdout/"
            "stderr, create or control processes, schedule real timeouts, register launch/cancel/timeout APIs, import "
            "or call adapters, create or mutate sessions, collect authorization, grant permission, or modify the user "
            "project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    persistence_audit_report: dict[str, Any] | None,
    integrity_replay_report: dict[str, Any] | None,
) -> list[dict[str, object]]:
    persistence_audit_status = (
        persistence_audit_report.get("status") if isinstance(persistence_audit_report, dict) else "missing"
    )
    projection_available = isinstance(integrity_replay_report, dict)
    ready_keys = {
        "audit_record_reference_contract",
        "event_replay_contract",
        "ordering_validation_contract",
        "terminal_state_reconciliation_contract",
    }
    items = [item for item in audit_schema.get("required_integrity_replay_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "audit_persistence_audit_status": persistence_audit_status,
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
    return _check("saved_profile", "error", "Missing saved run profile", "Integrity replay audit requires a saved run profile.")


def _check_audit_persistence_audit(persistence_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not persistence_audit_report:
        return _check(
            "audit_persistence_audit",
            "error",
            "Missing audit persistence audit",
            "Generate the audit persistence implementation audit before integrity replay audit.",
        )
    if persistence_audit_report.get("status") in {
        "audit_persistence_audit_required",
        "audit_persistence_projection_implemented",
    }:
        return _check(
            "audit_persistence_audit",
            "pass",
            "Audit persistence audit declared",
            "Audit record and integrity evidence is available for future replay verification planning.",
        )
    return _check(
        "audit_persistence_audit",
        "error",
        "Audit persistence audit status is unexpected",
        str(persistence_audit_report.get("status") or "unknown"),
    )


def _check_integrity_item(persistence_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = _audit_keys(persistence_audit_report)
    if "integrity_contract" in audit_keys:
        return _check(
            "integrity_contract",
            "pass",
            "Integrity evidence declared",
            "Audit persistence audit includes integrity evidence for future replay verification.",
        )
    return _check(
        "integrity_contract",
        "error",
        "Integrity evidence missing",
        "Audit persistence audit must include integrity_contract before replay verification audit.",
    )


def _check_audit_record_schema_item(persistence_audit_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = _audit_keys(persistence_audit_report)
    if "audit_record_schema_contract" in audit_keys:
        return _check(
            "audit_record_schema_contract",
            "pass",
            "Audit record schema evidence declared",
            "Audit persistence audit includes record schema evidence for future consistency checks.",
        )
    return _check(
        "audit_record_schema_contract",
        "error",
        "Audit record schema evidence missing",
        "Audit persistence audit must include audit_record_schema_contract before replay verification audit.",
    )


def _check_integrity_replay_projection(integrity_replay_report: dict[str, Any] | None) -> dict[str, object]:
    if not integrity_replay_report:
        return _check(
            "integrity_replay_projection",
            "warn",
            "Integrity replay projection not supplied",
            "Legacy audit-only mode remains valid until the projection collection is wired into this audit.",
        )
    checks = [
        item
        for key in ("integrity_checks", "replay_checks", "consistency_checks")
        for item in integrity_replay_report.get(key, [])
        if isinstance(item, dict)
    ]
    if all(not item.get("read_from_log") and not item.get("wrote_report") for item in checks):
        return _check(
            "integrity_replay_projection",
            "pass",
            "Integrity replay projection supplied",
            "Projected checks are present and marked as no log read and no report write.",
        )
    return _check(
        "integrity_replay_projection",
        "error",
        "Integrity replay projection invalid",
        "Projected checks must not read logs or write reports.",
    )


def _audit_keys(report: dict[str, Any] | None) -> set[str]:
    if not isinstance(report, dict):
        return set()
    return {str(item.get("key")) for item in report.get("audit_items", []) if isinstance(item, dict)}


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "audit_record_reference_contract",
        "event_replay_contract",
        "config_snapshot_contract",
        "failure_reason_mapping_contract",
        "integrity_hash_contract",
        "ordering_validation_contract",
        "terminal_state_reconciliation_contract",
        "redaction_consistency_contract",
        "discrepancy_reporting_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("integrity_replay_items_declared", "pass", "Integrity replay items declared", "Future verification evidence is explicit.")
    return _check("integrity_replay_items_declared", "error", "Integrity replay items incomplete", "Missing future verification evidence items.")


def _check_no_read_write_or_replay() -> dict[str, object]:
    return _check(
        "no_read_write_or_replay",
        "pass",
        "No read, write, or replay",
        "No audit log read/open/write, audit record read/store, runner event read/write, config snapshot read, replay check, integrity check, log read/write, stdout/stderr open/read, process creation/control, timeout scheduling, POST API registration, adapter call, session mutation, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if any(check.get("key") == "integrity_replay_projection" and check.get("status") == "pass" for check in checks):
        return "integrity_replay_projection_implemented"
    return "integrity_replay_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "integrity_replay_projection_implemented" for report in reports):
        return "integrity_replay_projection_implemented"
    return "integrity_replay_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Audit integrity replay verification audit is blocked",
        "integrity_replay_projection_implemented": "Audit integrity replay projection is implemented",
        "integrity_replay_audit_required": "Audit integrity replay verification audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the audit persistence implementation audit before replay verification audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix integrity replay blocker",
                "action": failed.get("detail") or "Complete the audit persistence audit first.",
            }
    return {
        "title": "Integrity replay remains projection-only",
        "action": "Use projected checks to review audit references, replay sequence, and terminal consistency; no logs are read now.",
    }


def _safety(projection_enabled: bool = False) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": projection_enabled,
        "launch_enabled": projection_enabled,
        "launch_api_available": projection_enabled,
        "integrity_replay_audit_only": not projection_enabled,
        "integrity_replay_projection": projection_enabled,
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
        "reads_runner_events": False,
        "writes_runner_events": False,
        "opens_runner_event_log": False,
        "writes_event_log": False,
        "opens_audit_log": False,
        "reads_audit_log": False,
        "writes_audit_log": False,
        "stores_audit_records": False,
        "reads_audit_records": False,
        "reads_config_snapshots": False,
        "performs_integrity_checks": False,
        "performs_replay_checks": False,
        "performs_consistency_checks": False,
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
