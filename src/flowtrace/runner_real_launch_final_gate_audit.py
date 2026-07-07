from __future__ import annotations

from typing import Any


RUNNER_REAL_LAUNCH_FINAL_GATE_AUDIT_VERSION = "project_runner_real_launch_final_gate_audits.v1"
RUNNER_REAL_LAUNCH_FINAL_GATE_AUDIT_SCHEMA_VERSION = "runner_real_launch_final_gate_audit_schema.v1"


def build_project_runner_real_launch_final_gate_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    discrepancy_report_audit_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    discrepancy_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in discrepancy_report_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    audit_schema = runner_real_launch_final_gate_audit_schema()
    reports = [
        _final_gate_report(
            profile,
            discrepancy_audit_by_profile.get(str(profile.get("id"))),
            audit_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_LAUNCH_FINAL_GATE_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "final_gate_audit_required_count": sum(
                1 for report in reports if report["status"] == "final_launch_gate_audit_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "required_layer_count": len(audit_schema["required_layers"]),
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
            "pre_launch_blocker_count": sum(len(report.get("pre_launch_blockers", [])) for report in reports),
            "final_gate_decision_count": 0,
            "real_launch_ready_count": 0,
            "registered_endpoint_count": 0,
            "launchable_count": 0,
        },
        "final_gate_audit_schema": audit_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_launch_final_gate_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_LAUNCH_FINAL_GATE_AUDIT_SCHEMA_VERSION,
        "audit_state": {
            "read_only": True,
            "final_gate_implemented_now": False,
            "final_gate_decision_made_now": False,
            "real_launch_allowed_now": False,
            "real_launch_api_registered_now": False,
            "launch_button_enabled_now": False,
            "adapter_called_now": False,
            "process_created_now": False,
            "session_created_now": False,
            "stdout_stderr_opened_now": False,
            "runner_event_read_now": False,
            "audit_log_read_now": False,
            "config_snapshot_read_now": False,
            "authorization_collected_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "required_layers": [
            "run_profile_saved",
            "preflight_and_final_confirmation_chain",
            "runner_governance_readiness",
            "execution_adapter_contract_and_review",
            "launch_api_contract_absence",
            "authorization_unlock_audit",
            "implementation_gap_checklist",
            "cancel_timeout_contract",
            "session_state_schema",
            "real_test_readiness_and_authorization",
            "real_execution_stage_boundary_review",
            "real_execution_unlock_material_review",
            "real_execution_implementation_plan",
            "real_execution_scope_diff_audit",
            "adapter_process_stream_event_audit_chain",
            "audit_persistence_integrity_replay_chain",
            "verification_discrepancy_report_audit",
        ],
        "required_final_gate_evidence": [
            _audit_item_schema(
                "pre_launch_gate_contract",
                "Pre-launch gate contract",
                "Stable final gate schema, explicit pass/fail vocabulary, and no implicit launch permission.",
            ),
            _audit_item_schema(
                "prerequisite_layer_manifest",
                "Prerequisite layer manifest",
                "Complete list of upstream read-only layers and the expected terminal status for each layer.",
            ),
            _audit_item_schema(
                "safety_invariant_matrix",
                "Safety invariant matrix",
                "All launch, process, adapter, event, log, audit, config, authorization, and user-project mutation flags remain false.",
            ),
            _audit_item_schema(
                "missing_evidence_rollup_contract",
                "Missing evidence rollup contract",
                "How missing evidence is aggregated without reading events, logs, audit records, config snapshots, or stores.",
            ),
            _audit_item_schema(
                "launch_api_absence_contract",
                "Launch API absence contract",
                "Proof shape for keeping launch/cancel/timeout POST APIs absent until a separate authorized implementation round.",
            ),
            _audit_item_schema(
                "authorization_boundary_contract",
                "Authorization boundary contract",
                "How future human authorization is referenced without collecting, storing, granting, or reusing permission now.",
            ),
            _audit_item_schema(
                "implementation_unlock_sequence",
                "Implementation unlock sequence",
                "Ordered future sequence for adapter, process, stream, event, audit, verification, cancel, timeout, and UI unlocks.",
            ),
            _audit_item_schema(
                "operator_final_summary_contract",
                "Operator final summary contract",
                "User-facing final summary that explains why real launch remains disabled and what evidence is still missing.",
            ),
            _audit_item_schema(
                "ui_navigation_contract",
                "UI navigation contract",
                "How Runner Workbench links final gate blockers back to the exact upstream layer or evidence group.",
            ),
            _audit_item_schema(
                "regression_fixture_matrix",
                "Regression fixture matrix",
                "Tests for all-ready-but-disabled, missing evidence, accidental POST route, accidental process, and accidental log/event reads.",
            ),
        ],
        "blocked_actions": [
            "registering launch/cancel/timeout POST APIs",
            "enabling launch UI",
            "granting launch permission",
            "collecting or storing authorization",
            "importing or calling execution adapters",
            "creating or controlling processes",
            "creating or mutating runner sessions",
            "opening or reading stdout/stderr",
            "reading runner events",
            "writing runner events",
            "opening or writing runner event logs",
            "reading audit logs",
            "opening audit logs",
            "writing audit logs",
            "reading or storing audit records",
            "reading config snapshots",
            "performing integrity checks",
            "performing replay checks",
            "generating real discrepancy reports",
            "making real launch decisions",
            "reading, scanning, writing, deleting, rotating, renaming, or truncating logs",
            "writing code",
            "writing config files",
            "writing user project files",
        ],
    }


def _final_gate_report(
    profile: dict[str, Any],
    discrepancy_report_audit: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> dict[str, object]:
    audit_items = _audit_items(audit_schema, discrepancy_report_audit)
    pre_launch_blockers = _pre_launch_blockers(discrepancy_report_audit, audit_schema)
    checks = [
        _check_saved_profile(profile),
        _check_discrepancy_report_audit(discrepancy_report_audit),
        _check_discrepancy_required_item(discrepancy_report_audit),
        _check_final_gate_items_declared(audit_items),
        _check_launch_absence_invariant(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_launch_final_gate_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "verification_discrepancy_report_audit_status": (
            discrepancy_report_audit.get("status") if isinstance(discrepancy_report_audit, dict) else "missing"
        ),
        "audit_state": audit_schema["audit_state"],
        "audit_items": audit_items,
        "required_layers": audit_schema["required_layers"],
        "pre_launch_blockers": pre_launch_blockers,
        "blocked_actions": audit_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only audits the future real-launch final gate. It aggregates existing in-memory "
            "read-only payloads and does not register launch/cancel/timeout APIs, enable launch UI, grant "
            "permission, collect authorization, call adapters, create or control processes, create or mutate "
            "sessions, open stdout/stderr, read runner events, read audit logs, read config snapshots, perform "
            "integrity or replay checks, generate real discrepancy reports, make real launch decisions, read or "
            "write logs, write code, write config files, or modify the user project."
        ),
    }


def _audit_items(
    audit_schema: dict[str, object],
    discrepancy_report_audit: dict[str, Any] | None,
) -> list[dict[str, object]]:
    discrepancy_status = (
        discrepancy_report_audit.get("status") if isinstance(discrepancy_report_audit, dict) else "missing"
    )
    items = [item for item in audit_schema.get("required_final_gate_evidence", []) if isinstance(item, dict)]
    return [
        {
            **item,
            "verification_discrepancy_report_audit_status": discrepancy_status,
            "evidence_status": "missing",
            "implementation_status": "not_started",
            "can_launch_now": False,
            "requires_future_code_change": True,
            "requires_future_review": True,
        }
        for item in items
    ]


def _pre_launch_blockers(
    discrepancy_report_audit: dict[str, Any] | None,
    audit_schema: dict[str, object],
) -> list[dict[str, object]]:
    discrepancy_status = (
        discrepancy_report_audit.get("status") if isinstance(discrepancy_report_audit, dict) else "missing"
    )
    return [
        {
            "key": "real_launch_api_absent",
            "status": "blocked_by_design",
            "title": "Real launch API remains absent",
            "detail": "No launch/cancel/timeout POST API is registered in this read-only gate.",
        },
        {
            "key": "launch_permission_absent",
            "status": "blocked_by_design",
            "title": "Launch permission remains absent",
            "detail": "No permission is granted and no authorization is collected or stored now.",
        },
        {
            "key": "implementation_not_unlocked",
            "status": "blocked_by_design",
            "title": "Real implementation is not unlocked",
            "detail": "Adapter, process, stream, event, audit, verification, cancel, timeout, and UI unlock work remains future work.",
        },
        {
            "key": "upstream_discrepancy_audit_required",
            "status": discrepancy_status,
            "title": "Verification discrepancy report audit is still prerequisite evidence",
            "detail": "Final gate can only summarize the prerequisite chain; it does not generate reports or make launch decisions.",
        },
        {
            "key": "final_gate_evidence_missing",
            "status": "missing",
            "title": "Final gate evidence is missing",
            "detail": f"{len(audit_schema['required_final_gate_evidence'])} final gate evidence items still require future review.",
        },
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
    return _check("saved_profile", "error", "Missing saved run profile", "Final gate audit requires a saved run profile.")


def _check_discrepancy_report_audit(discrepancy_report_audit: dict[str, Any] | None) -> dict[str, object]:
    if not discrepancy_report_audit:
        return _check(
            "verification_discrepancy_report_audit",
            "error",
            "Missing verification discrepancy report audit",
            "Generate the verification discrepancy report audit before the real-launch final gate audit.",
        )
    if discrepancy_report_audit.get("status") in {
        "discrepancy_report_audit_required",
        "discrepancy_projection_implemented",
    }:
        return _check(
            "verification_discrepancy_report_audit",
            "pass",
            "Verification discrepancy report audit declared",
            "Final gate can aggregate the last read-only verification audit prerequisite.",
        )
    return _check(
        "verification_discrepancy_report_audit",
        "error",
        "Verification discrepancy report audit status is unexpected",
        str(discrepancy_report_audit.get("status") or "unknown"),
    )


def _check_discrepancy_required_item(discrepancy_report_audit: dict[str, Any] | None) -> dict[str, object]:
    audit_keys = _audit_keys(discrepancy_report_audit)
    required = {"blocking_decision_contract", "operator_message_contract", "no_mutation_reporting_contract"}
    if required.issubset(audit_keys):
        return _check(
            "discrepancy_report_gate_inputs",
            "pass",
            "Discrepancy report gate inputs declared",
            "Blocking, operator-message, and no-mutation contracts are visible to the final gate audit.",
        )
    return _check(
        "discrepancy_report_gate_inputs",
        "error",
        "Discrepancy report gate inputs missing",
        "Final gate audit requires blocking_decision_contract, operator_message_contract, and no_mutation_reporting_contract.",
    )


def _audit_keys(report: dict[str, Any] | None) -> set[str]:
    if not isinstance(report, dict):
        return set()
    return {str(item.get("key")) for item in report.get("audit_items", []) if isinstance(item, dict)}


def _check_final_gate_items_declared(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "pre_launch_gate_contract",
        "prerequisite_layer_manifest",
        "safety_invariant_matrix",
        "missing_evidence_rollup_contract",
        "launch_api_absence_contract",
        "authorization_boundary_contract",
        "implementation_unlock_sequence",
        "operator_final_summary_contract",
        "ui_navigation_contract",
        "regression_fixture_matrix",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("final_gate_items_declared", "pass", "Final gate items declared", "Future final gate evidence is explicit.")
    return _check("final_gate_items_declared", "error", "Final gate items incomplete", "Missing final gate evidence items.")


def _check_launch_absence_invariant() -> dict[str, object]:
    return _check(
        "launch_absence_invariant",
        "pass",
        "Real launch remains absent",
        "No launch API, launch UI enablement, adapter call, process creation, session mutation, stdout/stderr open, event/log/audit/config read, authorization, permission, or user-project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "final_launch_gate_audit_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "final_launch_gate_audit_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-launch final gate audit is blocked",
        "final_launch_gate_audit_required": "Real-launch final gate audit is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the verification discrepancy report audit before the final gate audit.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix final gate blocker",
                "action": failed.get("detail") or "Complete the verification discrepancy report audit first.",
            }
    return {
        "title": "Final real-launch gate remains read-only",
        "action": "Use this final gate audit to summarize missing evidence and hard blocks; no launch permission or API is created now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "final_launch_gate_audit_only": True,
        "writes_code": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "enables_launch_ui": False,
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
        "makes_launch_decisions": False,
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
