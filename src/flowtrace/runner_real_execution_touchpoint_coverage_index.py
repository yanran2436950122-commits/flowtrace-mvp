from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_TOUCHPOINT_COVERAGE_INDEX_VERSION = (
    "project_runner_real_execution_touchpoint_coverage_indexes.v1"
)
RUNNER_REAL_EXECUTION_TOUCHPOINT_COVERAGE_INDEX_SCHEMA_VERSION = (
    "runner_real_execution_touchpoint_coverage_index_schema.v1"
)


def build_project_runner_real_execution_touchpoint_coverage_indexes(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    touchpoint_inventory_collection: dict[str, Any],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    index_schema = runner_real_execution_touchpoint_coverage_index_schema()
    entries = _coverage_entries(touchpoint_inventory_collection, index_schema)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_COVERAGE_INDEX_VERSION,
        "context": project_context,
        "status": "touchpoint_coverage_index_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(saved_profiles),
            "coverage_entry_count": len(entries),
            "locked_entry_count": sum(1 for item in entries if item["current_permission"] == "locked"),
            "mapped_stage_count": len({item["owner_stage_key"] for item in entries}),
            "mapped_round_count": len({item["fixed_round"] for item in entries}),
            "evidence_gap_status": evidence_gap_index_collection.get("status", "missing"),
            "launchable_count": 0,
        },
        "coverage_index_schema": index_schema,
        "coverage_entries": entries,
        "reports": [_coverage_report(profile, entries, evidence_gap_index_collection) for profile in saved_profiles],
        "safety": _safety(),
        "next_action": {
            "title": "Use locked touchpoint navigation",
            "action": (
                "Use this index to navigate from locked real-execution touchpoints to the corresponding audit stage. "
                "Do not implement, register, enable, execute, or persist any touchpoint before explicit unlock."
            ),
        },
    }


def runner_real_execution_touchpoint_coverage_index_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_COVERAGE_INDEX_SCHEMA_VERSION,
        "index_state": {
            "read_only": True,
            "touchpoint_coverage_index_only": True,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
        },
        "stage_mapping": _stage_mapping(),
        "forbidden_actions": [
            "creating implementation files",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch/cancel/timeout UI controls",
            "creating or mutating runtime state",
            "creating or controlling processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, or audit logs",
            "collecting, storing, accepting, or granting authorization",
            "writing user project files",
        ],
    }


def _coverage_entries(
    touchpoint_inventory_collection: dict[str, Any],
    index_schema: dict[str, object],
) -> list[dict[str, object]]:
    touchpoints = touchpoint_inventory_collection.get("touchpoint_inventory_schema", {}).get("touchpoints", [])
    mapping = index_schema["stage_mapping"]
    return [_coverage_entry(item, mapping.get(str(item.get("key")), {})) for item in touchpoints if isinstance(item, dict)]


def _coverage_entry(touchpoint: dict[str, Any], mapping: dict[str, Any]) -> dict[str, object]:
    key = str(touchpoint.get("key") or "")
    owner_stage_key = str(mapping.get("owner_stage_key") or "runner_real_execution_touchpoint_inventories")
    fixed_round = int(mapping.get("fixed_round") or 10)
    return {
        "kind": touchpoint.get("kind"),
        "key": key,
        "target": touchpoint.get("target"),
        "owner_stage_key": owner_stage_key,
        "fixed_round": fixed_round,
        "blocker_key": mapping.get("blocker_key") or "real_execution_locked",
        "current_permission": "locked",
        "can_implement_now": False,
        "can_execute_now": False,
        "requires_future_unlock": True,
        "navigation": {
            "stage_key": owner_stage_key,
            "evidence_group": "Touchpoint coverage",
            "item_key": key,
        },
    }


def _coverage_report(
    profile: dict[str, Any],
    entries: list[dict[str, object]],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_touchpoint_coverage_index:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "touchpoint_coverage_index_locked",
        "evidence_gap_index_status": evidence_gap_index_collection.get("status", "missing"),
        "coverage_entries": entries,
        "checks": [
            _check("coverage_entries_declared", "pass", "Coverage entries declared", "Every known real-execution touchpoint has a navigation target."),
            _check("touchpoints_locked", "warn", "Touchpoints remain locked", "The index does not unlock implementation or execution."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only maps touchpoints to audit stages."),
        ],
    }


def _stage_mapping() -> dict[str, dict[str, object]]:
    return {
        "execution_adapter_module": _map("runner_execution_adapter_implementation_audits", 10, "adapter_locked"),
        "process_lifecycle_module": _map("runner_process_lifecycle_implementation_audits", 11, "process_locked"),
        "stream_capture_module": _map("runner_stream_capture_implementation_audits", 12, "stream_locked"),
        "runner_event_writer_module": _map("runner_event_writer_implementation_audits", 13, "event_writer_locked"),
        "audit_persistence_module": _map("runner_audit_persistence_implementation_audits", 14, "audit_persistence_locked"),
        "real_session_store_module": _map("runner_process_lifecycle_implementation_audits", 11, "session_state_locked"),
        "launch_post_api": _map("runner_launch_api_contracts", 10, "launch_api_locked"),
        "cancel_post_api": _map("runner_cancel_timeout_contracts", 17, "cancel_api_locked"),
        "timeout_post_api": _map("runner_cancel_timeout_contracts", 17, "timeout_api_locked"),
        "launch_button": _map("runner_real_test_ui_previews", 9, "launch_ui_locked"),
        "cancel_button": _map("runner_real_test_ui_previews", 17, "cancel_ui_locked"),
        "timeout_button": _map("runner_real_test_ui_previews", 17, "timeout_ui_locked"),
        "execution_console": _map("runner_real_test_ui_previews", 10, "execution_console_locked"),
        "session_status": _map("runner_session_state_schemas", 11, "session_status_locked"),
        "process_identity": _map("runner_process_lifecycle_implementation_audits", 11, "process_identity_locked"),
        "stdout_stderr_tail": _map("runner_stream_capture_implementation_audits", 12, "stream_tail_locked"),
        "audit_record_id": _map("runner_audit_persistence_implementation_audits", 14, "audit_record_locked"),
        "authorization_snapshot": _map("runner_real_execution_unlock_material_reviews", 10, "authorization_snapshot_locked"),
    }


def _map(owner_stage_key: str, fixed_round: int, blocker_key: str) -> dict[str, object]:
    return {"owner_stage_key": owner_stage_key, "fixed_round": fixed_round, "blocker_key": blocker_key}


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "touchpoint_coverage_index_only": True,
        "writes_code": False,
        "creates_files": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "enables_launch_ui": False,
        "enables_cancel_ui": False,
        "enables_timeout_ui": False,
        "implements_adapter": False,
        "imports_adapter": False,
        "calls_execution_adapter": False,
        "creates_session": False,
        "mutates_session_state": False,
        "opens_stdout_stderr": False,
        "writes_runner_events": False,
        "reads_log_files": False,
        "writes_logs": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "accepts_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
    }
