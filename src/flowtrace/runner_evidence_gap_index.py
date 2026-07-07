from __future__ import annotations

from typing import Any


RUNNER_EVIDENCE_GAP_INDEX_VERSION = "project_runner_evidence_gap_indexes.v1"
RUNNER_EVIDENCE_GAP_INDEX_SCHEMA_VERSION = "runner_evidence_gap_index_schema.v1"


def build_project_runner_evidence_gap_indexes(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    final_gate_audit_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    final_gate_by_profile = {
        str(report.get("profile_id")): report
        for report in final_gate_audit_collection.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    index_schema = runner_evidence_gap_index_schema()
    reports = [
        _index_report(
            profile,
            final_gate_by_profile.get(str(profile.get("id"))),
            index_schema,
        )
        for profile in saved_profiles
    ]
    entries = [entry for report in reports for entry in report.get("index_entries", [])]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EVIDENCE_GAP_INDEX_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "evidence_index_required_count": sum(1 for report in reports if report["status"] == "evidence_index_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "index_entry_count": len(entries),
            "missing_evidence_count": sum(1 for entry in entries if entry.get("kind") == "missing_evidence"),
            "pre_launch_blocker_count": sum(1 for entry in entries if entry.get("kind") == "pre_launch_blocker"),
            "required_layer_count": sum(1 for entry in entries if entry.get("kind") == "required_layer"),
            "navigation_target_count": sum(1 for entry in entries if entry.get("navigation")),
            "unresolved_gap_count": sum(1 for entry in entries if entry.get("resolution_status") == "unresolved"),
            "real_launch_ready_count": 0,
            "registered_endpoint_count": 0,
            "launchable_count": 0,
        },
        "evidence_gap_index_schema": index_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_evidence_gap_index_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EVIDENCE_GAP_INDEX_SCHEMA_VERSION,
        "index_state": {
            "read_only": True,
            "index_generated_from_in_memory_payload": True,
            "log_file_read_now": False,
            "runner_event_read_now": False,
            "audit_log_read_now": False,
            "audit_record_read_now": False,
            "config_snapshot_read_now": False,
            "launch_decision_made_now": False,
            "launch_api_registered_now": False,
            "launch_ui_enabled_now": False,
            "process_created_now": False,
            "adapter_called_now": False,
            "authorization_collected_now": False,
            "requires_new_authorized_implementation_round": True,
        },
        "entry_kinds": [
            "missing_evidence",
            "pre_launch_blocker",
            "required_layer",
        ],
        "required_navigation_contract": [
            _contract_item(
                "stage_key",
                "Every index entry must name the owning Runner Workbench stage key.",
            ),
            _contract_item(
                "evidence_group",
                "Every index entry must identify the UI evidence group or section where the user should look next.",
            ),
            _contract_item(
                "source_report_id",
                "Every index entry must reference the in-memory report id that produced the gap.",
            ),
            _contract_item(
                "resolution_hint",
                "Every index entry must explain the next remediation target without executing or mutating anything.",
            ),
            _contract_item(
                "no_side_effect_navigation",
                "Navigation may select UI sections only; it must not read logs, run checks, create sessions, or launch processes.",
            ),
        ],
        "blocked_actions": [
            "reading log files",
            "scanning log directories",
            "reading runner events",
            "opening runner event logs",
            "writing runner events",
            "reading audit logs",
            "opening audit logs",
            "writing audit logs",
            "reading or storing audit records",
            "reading config snapshots",
            "performing integrity checks",
            "performing replay checks",
            "generating discrepancy reports",
            "making launch decisions",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch UI",
            "creating or controlling processes",
            "importing or calling execution adapters",
            "creating or mutating runner sessions",
            "opening stdout/stderr",
            "collecting or storing authorization",
            "granting permission",
            "writing code",
            "writing config files",
            "writing user project files",
        ],
    }


def _index_report(
    profile: dict[str, Any],
    final_gate_report: dict[str, Any] | None,
    index_schema: dict[str, object],
) -> dict[str, object]:
    entries = _index_entries(final_gate_report)
    checks = [
        _check_saved_profile(profile),
        _check_final_gate_report(final_gate_report),
        _check_index_entries(entries),
        _check_navigation_contract(index_schema),
        _check_no_side_effects(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_evidence_gap_index:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "final_gate_audit_status": final_gate_report.get("status") if isinstance(final_gate_report, dict) else "missing",
        "index_state": index_schema["index_state"],
        "index_entries": entries,
        "navigation_contract": index_schema["required_navigation_contract"],
        "blocked_actions": index_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only indexes in-memory final gate gaps into UI navigation targets. It does not read logs, "
            "scan directories, read runner events, read audit logs or records, read config snapshots, perform checks, "
            "generate discrepancy reports, make launch decisions, register launch APIs, enable launch UI, create "
            "processes, call adapters, mutate sessions, open stdout/stderr, collect authorization, write code, write "
            "config files, or modify the user project."
        ),
    }


def _index_entries(final_gate_report: dict[str, Any] | None) -> list[dict[str, object]]:
    if not isinstance(final_gate_report, dict):
        return []
    entries: list[dict[str, object]] = []
    source_report_id = str(final_gate_report.get("id") or "")
    for item in final_gate_report.get("audit_items", []):
        if not isinstance(item, dict) or item.get("evidence_status") != "missing":
            continue
        key = str(item.get("key") or "missing_evidence")
        owner_stage_key = _owner_stage_for_evidence(key)
        entries.append(
            _entry(
                final_gate_report,
                kind="missing_evidence",
                key=key,
                title=str(item.get("title") or key),
                detail=str(item.get("minimum_evidence") or "Evidence is missing."),
                status="missing",
                owner_stage_key=owner_stage_key,
                evidence_group="只读证据",
                source_report_id=source_report_id,
                resolution_hint="Complete the owning read-only evidence contract in a future authorized implementation round.",
            )
        )
    for item in final_gate_report.get("pre_launch_blockers", []):
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "pre_launch_blocker")
        owner_stage_key = _owner_stage_for_blocker(key)
        entries.append(
            _entry(
                final_gate_report,
                kind="pre_launch_blocker",
                key=key,
                title=str(item.get("title") or key),
                detail=str(item.get("detail") or "Pre-launch blocker remains unresolved."),
                status=str(item.get("status") or "blocked"),
                owner_stage_key=owner_stage_key,
                evidence_group="阻断动作",
                source_report_id=source_report_id,
                resolution_hint="Use the owning stage to inspect the blocker; do not unlock real launch in this layer.",
            )
        )
    for layer in final_gate_report.get("required_layers", []):
        key = str(layer)
        owner_stage_key = _owner_stage_for_layer(key)
        entries.append(
            _entry(
                final_gate_report,
                kind="required_layer",
                key=key,
                title=key,
                detail="Required prerequisite layer for future real launch readiness.",
                status="required",
                owner_stage_key=owner_stage_key,
                evidence_group="必备层",
                source_report_id=source_report_id,
                resolution_hint="Review this prerequisite layer before any future real-launch implementation discussion.",
            )
        )
    return entries


def _entry(
    final_gate_report: dict[str, Any],
    *,
    kind: str,
    key: str,
    title: str,
    detail: str,
    status: str,
    owner_stage_key: str,
    evidence_group: str,
    source_report_id: str,
    resolution_hint: str,
) -> dict[str, object]:
    profile_id = str(final_gate_report.get("profile_id") or "")
    return {
        "id": f"{kind}:{profile_id}:{key}",
        "profile_id": final_gate_report.get("profile_id"),
        "kind": kind,
        "key": key,
        "title": title,
        "detail": detail,
        "status": status,
        "owner_stage_key": owner_stage_key,
        "resolution_status": "unresolved",
        "resolution_hint": resolution_hint,
        "navigation": {
            "stage_key": owner_stage_key,
            "evidence_group": evidence_group,
            "item_key": key,
            "source_stage_key": "runner_real_launch_final_gate_audits",
            "source_report_id": source_report_id,
        },
    }


def _owner_stage_for_evidence(key: str) -> str:
    mapping = {
        "launch_api_absence_contract": "runner_launch_api_contracts",
        "authorization_boundary_contract": "runner_authorization_unlock_audits",
        "implementation_unlock_sequence": "runner_real_execution_implementation_plans",
        "ui_navigation_contract": "runner_real_launch_final_gate_audits",
        "safety_invariant_matrix": "runner_real_launch_final_gate_audits",
        "missing_evidence_rollup_contract": "runner_real_launch_final_gate_audits",
        "pre_launch_gate_contract": "runner_real_launch_final_gate_audits",
        "prerequisite_layer_manifest": "runner_real_launch_final_gate_audits",
        "operator_final_summary_contract": "runner_real_launch_final_gate_audits",
        "regression_fixture_matrix": "runner_real_launch_final_gate_audits",
    }
    return mapping.get(key, "runner_real_launch_final_gate_audits")


def _owner_stage_for_blocker(key: str) -> str:
    mapping = {
        "real_launch_api_absent": "runner_launch_api_contracts",
        "launch_permission_absent": "runner_authorization_unlock_audits",
        "implementation_not_unlocked": "runner_real_execution_stage_boundary_reviews",
        "upstream_discrepancy_audit_required": "runner_verification_discrepancy_report_audits",
        "final_gate_evidence_missing": "runner_real_launch_final_gate_audits",
    }
    return mapping.get(key, "runner_real_launch_final_gate_audits")


def _owner_stage_for_layer(key: str) -> str:
    mapping = {
        "run_profile_saved": "run_profiles",
        "preflight_and_final_confirmation_chain": "run_execution_gate",
        "runner_governance_readiness": "runner_governance_readiness",
        "execution_adapter_contract_and_review": "runner_execution_adapter_reviews",
        "launch_api_contract_absence": "runner_launch_api_contracts",
        "authorization_unlock_audit": "runner_authorization_unlock_audits",
        "implementation_gap_checklist": "runner_implementation_gap_checklists",
        "cancel_timeout_contract": "runner_cancel_timeout_contracts",
        "session_state_schema": "runner_session_state_schemas",
        "real_test_readiness_and_authorization": "runner_real_test_authorization_checklists",
        "real_execution_stage_boundary_review": "runner_real_execution_stage_boundary_reviews",
        "real_execution_unlock_material_review": "runner_real_execution_unlock_material_reviews",
        "real_execution_implementation_plan": "runner_real_execution_implementation_plans",
        "real_execution_scope_diff_audit": "runner_real_execution_scope_diff_audits",
        "adapter_process_stream_event_audit_chain": "runner_process_lifecycle_implementation_audits",
        "audit_persistence_integrity_replay_chain": "runner_audit_integrity_replay_verification_audits",
        "verification_discrepancy_report_audit": "runner_verification_discrepancy_report_audits",
    }
    return mapping.get(key, "runner_real_launch_final_gate_audits")


def _contract_item(key: str, detail: str) -> dict[str, object]:
    return {"key": key, "detail": detail}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Evidence gap index requires a saved run profile.")


def _check_final_gate_report(final_gate_report: dict[str, Any] | None) -> dict[str, object]:
    if not final_gate_report:
        return _check(
            "final_gate_audit",
            "error",
            "Missing final gate audit",
            "Generate the real-launch final gate audit before evidence gap indexing.",
        )
    if final_gate_report.get("status") == "final_launch_gate_audit_required":
        return _check(
            "final_gate_audit",
            "pass",
            "Final gate audit declared",
            "Evidence gaps can be indexed from the in-memory final gate report.",
        )
    return _check(
        "final_gate_audit",
        "error",
        "Final gate audit status is unexpected",
        str(final_gate_report.get("status") or "unknown"),
    )


def _check_index_entries(entries: list[dict[str, object]]) -> dict[str, object]:
    if entries:
        return _check("index_entries", "pass", "Evidence index entries declared", f"{len(entries)} navigation entries are available.")
    return _check("index_entries", "error", "Evidence index entries missing", "Final gate audit gaps must be indexed.")


def _check_navigation_contract(index_schema: dict[str, object]) -> dict[str, object]:
    required = {"stage_key", "evidence_group", "source_report_id", "resolution_hint", "no_side_effect_navigation"}
    present = {
        str(item.get("key"))
        for item in index_schema.get("required_navigation_contract", [])
        if isinstance(item, dict)
    }
    if required.issubset(present):
        return _check("navigation_contract", "pass", "Navigation contract declared", "Index navigation stays UI-only and side-effect free.")
    return _check("navigation_contract", "error", "Navigation contract incomplete", "Evidence index navigation contract is incomplete.")


def _check_no_side_effects() -> dict[str, object]:
    return _check(
        "no_side_effects",
        "pass",
        "No side effects",
        "No logs, events, audit records, config snapshots, launch APIs, UI enablement, processes, adapters, sessions, authorization, code, config, or user-project files are read or mutated.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "evidence_index_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "evidence_index_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Evidence gap index is blocked",
        "evidence_index_required": "Evidence gap index is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and complete the final gate audit before evidence gap indexing.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix evidence index blocker",
                "action": failed.get("detail") or "Complete the final gate audit first.",
            }
    return {
        "title": "Evidence gap index remains read-only",
        "action": "Use the index to navigate gaps and blockers; no real launch action is enabled now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "evidence_gap_index_only": True,
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
