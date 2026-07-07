from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_ROUND10_MINIMAL_SCOPE_PREVIEW_VERSION = (
    "project_runner_real_execution_pre_unlock_round10_minimal_scope_previews.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_ROUND10_MINIMAL_SCOPE_PREVIEW_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_round10_minimal_scope_preview_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    implementation_entry_readiness_ledger_collection: dict[str, Any],
    execution_adapter_contract_collection: dict[str, Any],
    real_execution_implementation_plan_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    preview_schema = runner_real_execution_pre_unlock_round10_minimal_scope_preview_schema()
    preview_entries = _preview_entries(
        implementation_entry_readiness_ledger_collection,
        execution_adapter_contract_collection,
        real_execution_implementation_plan_collection,
    )
    reports = [
        _preview_report(profile, preview_entries, implementation_entry_readiness_ledger_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_ROUND10_MINIMAL_SCOPE_PREVIEW_VERSION,
        "context": project_context,
        "status": "pre_unlock_round10_minimal_scope_preview_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "preview_entry_count": len(preview_entries),
            "minimal_touch_count": sum(1 for item in preview_entries if item["round_10_scope"] == "minimal_touch"),
            "explicitly_deferred_count": sum(1 for item in preview_entries if item["round_10_scope"] == "explicitly_deferred"),
            "accepted_preview_count": 0,
            "ready_preview_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "implementation_entry_ledger_status": implementation_entry_readiness_ledger_collection.get("status", "missing"),
            "execution_adapter_contract_status": execution_adapter_contract_collection.get("status", "missing"),
        },
        "pre_unlock_round10_minimal_scope_preview_schema": preview_schema,
        "preview_entries": preview_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked round-10 minimal scope preview",
            "action": (
                "Use this preview to inspect what round 10 would minimally touch after explicit unlock. This layer "
                "does not accept unlock, authorization, permissions, POST APIs, processes, or adapter implementation."
            ),
        },
    }


def runner_real_execution_pre_unlock_round10_minimal_scope_preview_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_ROUND10_MINIMAL_SCOPE_PREVIEW_SCHEMA_VERSION,
        "preview_state": {
            "read_only": True,
            "pre_unlock_round10_minimal_scope_preview_only": True,
            "round_10_allowed_now": False,
            "accepts_unlock_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "round_10_key": "execution_adapter_minimal_implementation",
        "blocked_actions": [
            "accepting unlock",
            "implementing the execution adapter",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _preview_entries(
    implementation_entry_readiness_ledger_collection: dict[str, Any],
    execution_adapter_contract_collection: dict[str, Any],
    real_execution_implementation_plan_collection: dict[str, Any],
) -> list[dict[str, object]]:
    return [
        _entry(
            "adapter_interface_skeleton",
            "Execution adapter interface skeleton",
            "minimal_touch",
            "Would add only the minimal adapter interface surface after explicit unlock.",
            "runner_execution_adapter_contracts",
            execution_adapter_contract_collection.get("status", "missing"),
        ),
        _entry(
            "launch_request_snapshot_contract",
            "Launch request snapshot contract",
            "minimal_touch",
            "Would consume existing launch snapshot and execution request contracts without starting processes.",
            "runner_launch_snapshot",
            real_execution_implementation_plan_collection.get("status", "missing"),
        ),
        _entry(
            "config_policy_inputs",
            "Configuration and policy inputs",
            "minimal_touch",
            "Would read already-declared config and policy inputs as structured data after unlock.",
            "runner_execution_configs",
            real_execution_implementation_plan_collection.get("status", "missing"),
        ),
        _entry(
            "launch_api_registration",
            "Launch API registration",
            "explicitly_deferred",
            "POST launch/cancel/timeout registration remains outside round 10 preview.",
            "runner_launch_api_contracts",
            implementation_entry_readiness_ledger_collection.get("status", "missing"),
        ),
        _entry(
            "process_stream_event_audit_runtime",
            "Process, stream, event, and audit runtime",
            "explicitly_deferred",
            "Process lifecycle, stdout/stderr, runner events, and audit persistence stay in later locked rounds.",
            "runner_development_path_anchors",
            implementation_entry_readiness_ledger_collection.get("status", "missing"),
        ),
        _entry(
            "round10_verification_boundary",
            "Round-10 verification boundary",
            "minimal_touch",
            "Would verify the adapter surface is inert until later launch/runtime rounds are unlocked.",
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers",
            implementation_entry_readiness_ledger_collection.get("status", "missing"),
        ),
    ]


def _entry(key: str, title: str, scope: str, detail: str, stage_key: str, source_status: object) -> dict[str, object]:
    return {
        "key": f"round10_minimal_scope_preview:{key}",
        "title": title,
        "round_10_scope": scope,
        "detail": detail,
        "source_status": source_status,
        "current_permission": "locked",
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Pre-unlock round-10 minimal scope preview",
            "item_key": key,
        },
    }


def _preview_report(
    profile: dict[str, Any],
    preview_entries: list[dict[str, object]],
    implementation_entry_readiness_ledger_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_round10_minimal_scope_preview:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_round10_minimal_scope_preview_locked",
        "implementation_entry_ledger_status": implementation_entry_readiness_ledger_collection.get("status", "missing"),
        "preview_entries": preview_entries,
        "checks": [
            _check("preview_entries_declared", "pass", "Preview entries declared", "Round-10 minimal scope is visible."),
            _check("round_10_not_allowed", "warn", "Round 10 not allowed", "This preview cannot unlock implementation."),
            _check("post_api_not_registered", "pass", "POST APIs not registered", "Launch/cancel/timeout POST APIs remain deferred."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only previews future minimal scope."),
        ],
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "pre_unlock_round10_minimal_scope_preview_only": True,
        "allows_round_10_entry": False,
        "accepts_unlock_phrase": False,
        "accepts_authorization": False,
        "allows_real_execution_implementation": False,
        "writes_code": False,
        "creates_files": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "enables_launch_ui": False,
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
        "grants_permission": False,
        "writes_user_project": False,
    }
