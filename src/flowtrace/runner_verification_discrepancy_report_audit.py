from __future__ import annotations

from typing import Any


RUNNER_VERIFICATION_DISCREPANCY_REPORT_AUDIT_VERSION = (
    "project_runner_verification_discrepancy_report_audits.v1"
)
RUNNER_VERIFICATION_DISCREPANCY_REPORT_AUDIT_SCHEMA_VERSION = (
    "runner_verification_discrepancy_report_audit_schema.v1"
)


def build_project_runner_verification_discrepancy_report_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    integrity_replay_audit_collection: dict[str, Any],
    discrepancy_report_collection: dict[str, Any] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    integrity_replay_by_profile = {
        str(report.get("profile_id")): report
        for report in integrity_replay_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    discrepancy_by_profile = {
        str(report.get("profile_id")): report
        for report in (discrepancy_report_collection or {}).get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_verification_discrepancy_report_audit_schema()
    reports = [
        _discrepancy_report(
            profile,
            integrity_replay_by_profile.get(str(profile.get("id"))),
            discrepancy_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_VERIFICATION_DISCREPANCY_REPORT_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "discrepancy_report_audit_required_count": sum(
                1 for report in reports if report["status"] == "discrepancy_report_audit_required"
            ),
            "discrepancy_projection_implemented_count": sum(
                1 for report in reports if report["status"] == "discrepancy_projection_implemented"
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
            "discrepancy_report_count": sum(len(report.get("discrepancy_reports", [])) for report in reports),
            "blocking_decision_count": 0,
            "operator_message_count": sum(
                1
                for report in reports
                for item in report.get("discrepancy_reports", [])
                if isinstance(item, dict) and item.get("operator_message")
            ),
            "launchable_count": (discrepancy_report_collection or {}).get("summary", {}).get("launchable_count", 0),
        },
        "discrepancy_report_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(discrepancy_report_collection is not None),
        "next_action": _next_action(status, reports),
    }


def runner_verification_discrepancy_report_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_VERIFICATION_DISCREPANCY_REPORT_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "discrepancy_report_implemented_now": False,
            "discrepancy_report_generated_now": False,
            "blocking_decision_made_now": False,
            "operator_message_generated_now": False,
            "audit_log_opened_now": False,
            "audit_record_read_now": False,
            "runner_event_read_now": False,
            "verification_executed_now": False,
            "can_launch_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_discrepancy_report_evidence": [
            _audit_item_schema(
                "discrepancy_taxonomy_contract",
                "差异分类合约",
                "Canonical categories for missing events, duplicate events, audit mismatch, config mismatch, terminal-state mismatch, tampering, and redaction mismatch.",
            ),
            _audit_item_schema(
                "severity_policy_contract",
                "严重级别策略合约",
                "Severity mapping, escalation rules, launch-blocking threshold, and operator-visible priority labels.",
            ),
            _audit_item_schema(
                "blocking_decision_contract",
                "阻断决策合约",
                "How future discrepancy outcomes decide whether real launch, retry, cleanup, or audit export must be blocked.",
            ),
            _audit_item_schema(
                "evidence_link_contract",
                "证据关联合约",
                "How future reports reference audit records, event IDs, config snapshots, failed checks, and redacted field locations.",
            ),
            _audit_item_schema(
                "operator_message_contract",
                "操作者消息合约",
                "Clear user-facing summary, recommended next action, non-technical cause, and no raw secret exposure.",
            ),
            _audit_item_schema(
                "machine_readable_contract",
                "机器可读合约",
                "Stable report schema, code fields, severity enum, related evidence IDs, and deterministic sorting.",
            ),
            _audit_item_schema(
                "redaction_contract",
                "差异报告脱敏合约",
                "Secret masking, raw-output exclusion, path normalization, and safe snippets for discrepancy context.",
            ),
            _audit_item_schema(
                "no_mutation_reporting_contract",
                "无副作用报告合约",
                "Future discrepancy reporting remains append/read-only aware and never repairs, deletes, rewrites, or replays data by itself.",
            ),
            _audit_item_schema(
                "ui_presentation_contract",
                "界面展示合约",
                "How discrepancy reports appear in Runner Workbench, onboarding, detail panels, filters, and collapsed long sections.",
            ),
            _audit_item_schema(
                "fixture_matrix",
                "差异报告夹具矩阵",
                "Future tests for missing event, duplicate event, config mismatch, terminal mismatch, tampering, redaction mismatch, and blocking decisions.",
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
            "performing integrity checks",
            "performing replay checks",
            "performing consistency checks",
            "generating real discrepancy reports",
            "making launch blocking decisions",
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


def _discrepancy_report(
    profile: dict[str, Any],
    integrity_replay_report: dict[str, Any] | None,
    discrepancy_report: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, integrity_replay_report, discrepancy_report)
    checks = [
        _check_saved_profile(profile),
        _check_integrity_replay_audit(integrity_replay_report),
        _check_discrepancy_reporting_item(integrity_replay_report),
        _check_discrepancy_projection(discrepancy_report),
        _check_audit_items_declared(audit_items),
        _check_no_read_write_report_or_block(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_verification_discrepancy_report_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "integrity_replay_audit_status": (
            integrity_replay_report.get("status") if isinstance(integrity_replay_report, dict) else "missing"
        ),
        "discrepancy_projection_status": (
            discrepancy_report.get("status") if isinstance(discrepancy_report, dict) else "missing"
        ),
        "discrepancy_reports": (
            discrepancy_report.get("discrepancy_reports", []) if isinstance(discrepancy_report, dict) else []
        ),
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits future verification discrepancy report implementation prerequisites. It does not "
            "read audit logs, read audit records, read runner events, read config snapshots, perform integrity/replay/"
            "consistency checks, generate real discrepancy reports, make launch-blocking decisions, write audit logs, "
            "write runner events, write logs, open stdout/stderr, create or control processes, schedule timeouts, "
            "register launch/cancel/timeout APIs, import or call adapters, mutate sessions, collect authorization, "
            "grant permission, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    integrity_replay_report: dict[str, Any] | None,
    discrepancy_report: dict[str, Any] | None,
) -> list[dict[str, object]]:
    integrity_replay_status = (
        integrity_replay_report.get("status") if isinstance(integrity_replay_report, dict) else "missing"
    )
    projection_available = isinstance(discrepancy_report, dict)
    ready_keys = {
        "discrepancy_taxonomy_contract",
        "evidence_link_contract",
        "operator_message_contract",
        "machine_readable_contract",
    }
    items = [item for item in audit_schema.get("required_discrepancy_report_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "integrity_replay_audit_status": integrity_replay_status,
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
    return _check("saved_profile", "error", "Missing saved run profile", "Discrepancy report audit requires a saved run profile.")


def _check_integrity_replay_audit(integrity_replay_report: dict[str, Any] | None) -> dict[str, object]:
    if not integrity_replay_report:
        return _check(
            "integrity_replay_audit",
            "error",
            "Missing integrity replay audit",
            "Generate the integrity replay verification audit before discrepancy report audit.",
        )
    if integrity_replay_report.get("status") in {
        "integrity_replay_audit_required",
        "integrity_replay_projection_implemented",
    }:
        return _check(
            "integrity_replay_audit",
            "pass",
            "Integrity replay audit declared",
            "Discrepancy reporting evidence is available for future report planning.",
        )
    return _check(
        "integrity_replay_audit",
        "error",
        "Integrity replay audit status is unexpected",
        str(integrity_replay_report.get("status") or "unknown"),
    )


def _check_discrepancy_reporting_item(integrity_replay_report: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = set()
    if isinstance(integrity_replay_report, dict):
        audit_keys = {str(item.get("key")) for item in integrity_replay_report.get("audit_items", []) if isinstance(item, dict)}
    if "discrepancy_reporting_contract" in audit_keys:
        return _check(
            "discrepancy_reporting_contract",
            "pass",
            "Discrepancy reporting evidence declared",
            "Integrity replay audit includes discrepancy reporting evidence for future operator-facing reports.",
        )
    return _check(
        "discrepancy_reporting_contract",
        "error",
        "Discrepancy reporting evidence missing",
        "Integrity replay audit must include discrepancy_reporting_contract before discrepancy report audit.",
    )


def _check_discrepancy_projection(discrepancy_report: dict[str, Any] | None) -> dict[str, object]:
    if not discrepancy_report:
        return _check(
            "discrepancy_projection",
            "warn",
            "Discrepancy projection not supplied",
            "Legacy audit-only mode remains valid until the projection collection is wired into this audit.",
        )
    reports = discrepancy_report.get("discrepancy_reports", [])
    if isinstance(reports, list) and all(
        isinstance(item, dict)
        and not item.get("persisted")
        and not item.get("blocking_decision")
        and not item.get("wrote_report_file")
        for item in reports
    ):
        return _check(
            "discrepancy_projection",
            "pass",
            "Discrepancy projection supplied",
            "Projected discrepancy reports are present and marked as non-persisted, non-blocking, and not file-written.",
        )
    return _check(
        "discrepancy_projection",
        "error",
        "Discrepancy projection invalid",
        "Projected reports must not be persisted, block launch, or write report files.",
    )


def _check_audit_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "discrepancy_taxonomy_contract",
        "severity_policy_contract",
        "blocking_decision_contract",
        "evidence_link_contract",
        "operator_message_contract",
        "machine_readable_contract",
        "redaction_contract",
        "no_mutation_reporting_contract",
        "ui_presentation_contract",
        "fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("discrepancy_report_items_declared", "pass", "Discrepancy report items declared", "Future discrepancy reporting evidence is explicit.")
    return _check("discrepancy_report_items_declared", "error", "Discrepancy report items incomplete", "Missing future discrepancy report evidence items.")


def _check_no_read_write_report_or_block() -> dict[str, object]:
    return _check(
        "no_read_write_report_or_block",
        "pass",
        "No read, write, report, or block",
        "No audit log read/open/write, audit record read/store, runner event read/write, config snapshot read, verification execution, real discrepancy report generation, launch-blocking decision, log read/write, stdout/stderr open/read, process creation/control, timeout scheduling, POST API registration, adapter call, session mutation, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if any(check.get("key") == "discrepancy_projection" and check.get("status") == "pass" for check in checks):
        return "discrepancy_projection_implemented"
    return "discrepancy_report_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "discrepancy_projection_implemented" for report in reports):
        return "discrepancy_projection_implemented"
    return "discrepancy_report_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Verification discrepancy report audit is blocked",
        "discrepancy_projection_implemented": "Verification discrepancy projection is implemented",
        "discrepancy_report_audit_required": "Verification discrepancy report audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the integrity replay verification audit before discrepancy report audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix discrepancy report blocker",
                "action": failed.get("detail") or "Complete the integrity replay audit first.",
            }
    return {
        "title": "Discrepancy reporting remains projection-only",
        "action": "Use projected discrepancy reports to review operator messages and evidence links; no report is written and no launch block is decided.",
    }


def _safety(projection_enabled: bool = False) -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": projection_enabled,
        "launch_enabled": projection_enabled,
        "launch_api_available": projection_enabled,
        "discrepancy_report_audit_only": not projection_enabled,
        "discrepancy_report_projection": projection_enabled,
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
        "generates_discrepancy_reports": False,
        "makes_blocking_decisions": False,
        "generates_operator_messages": False,
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
