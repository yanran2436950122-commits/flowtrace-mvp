from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_ROUND10_LOCKED_HANDOFF_SUMMARY_VERSION = (
    "project_runner_real_execution_pre_round10_locked_handoff_summaries.v1"
)
RUNNER_REAL_EXECUTION_PRE_ROUND10_LOCKED_HANDOFF_SUMMARY_SCHEMA_VERSION = (
    "runner_real_execution_pre_round10_locked_handoff_summary_schema.v1"
)


def build_project_runner_real_execution_pre_round10_locked_handoff_summaries(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    implementation_entry_readiness_ledger_collection: dict[str, Any],
    round10_minimal_scope_preview_collection: dict[str, Any],
    explicit_unlock_handoff_receipt_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    summary_schema = runner_real_execution_pre_round10_locked_handoff_summary_schema()
    handoff_summary_entries = _handoff_summary_entries(
        implementation_entry_readiness_ledger_collection,
        round10_minimal_scope_preview_collection,
        explicit_unlock_handoff_receipt_collection,
    )
    reports = [
        _summary_report(profile, handoff_summary_entries, explicit_unlock_handoff_receipt_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_ROUND10_LOCKED_HANDOFF_SUMMARY_VERSION,
        "context": project_context,
        "status": "pre_round10_locked_handoff_summary_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "handoff_summary_entry_count": len(handoff_summary_entries),
            "locked_entry_count": len(handoff_summary_entries),
            "blocking_entry_count": len(handoff_summary_entries),
            "accepted_summary_count": 0,
            "ready_summary_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "implementation_entry_ledger_status": implementation_entry_readiness_ledger_collection.get(
                "status",
                "missing",
            ),
            "round10_minimal_scope_preview_status": round10_minimal_scope_preview_collection.get(
                "status",
                "missing",
            ),
            "explicit_unlock_handoff_receipt_status": explicit_unlock_handoff_receipt_collection.get(
                "status",
                "missing",
            ),
        },
        "pre_round10_locked_handoff_summary_schema": summary_schema,
        "handoff_summary_entries": handoff_summary_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review final locked pre-round-10 summary",
            "action": (
                "Use this compact summary to confirm the current state before any explicit round-10 unlock. "
                "This layer does not collect, store, accept, or act on unlock material."
            ),
        },
    }


def runner_real_execution_pre_round10_locked_handoff_summary_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_ROUND10_LOCKED_HANDOFF_SUMMARY_SCHEMA_VERSION,
        "summary_state": {
            "read_only": True,
            "pre_round10_locked_handoff_summary_only": True,
            "accepts_summary_now": False,
            "accepts_unlock_now": False,
            "round_10_allowed_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "blocked_actions": [
            "accepting unlock",
            "accepting handoff summary",
            "granting implementation permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _handoff_summary_entries(
    implementation_entry_readiness_ledger_collection: dict[str, Any],
    round10_minimal_scope_preview_collection: dict[str, Any],
    explicit_unlock_handoff_receipt_collection: dict[str, Any],
) -> list[dict[str, object]]:
    ledger_summary = implementation_entry_readiness_ledger_collection.get("summary", {})
    preview_summary = round10_minimal_scope_preview_collection.get("summary", {})
    receipt_summary = explicit_unlock_handoff_receipt_collection.get("summary", {})
    return [
        _entry(
            "ledger_locked",
            "Implementation entry ledger is locked",
            f"{ledger_summary.get('ledger_entry_count', 0)} ledger entries, {ledger_summary.get('round_10_allowed_count', 0)} round-10 allowed",
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers",
        ),
        _entry(
            "round10_preview_locked",
            "Round-10 scope preview is locked",
            f"{preview_summary.get('minimal_touch_count', 0)} minimal-touch, {preview_summary.get('explicitly_deferred_count', 0)} deferred",
            "runner_real_execution_pre_unlock_round10_minimal_scope_previews",
        ),
        _entry(
            "unlock_receipt_locked",
            "Explicit unlock handoff receipt is locked",
            f"{receipt_summary.get('receipt_entry_count', 0)} receipt entries, {receipt_summary.get('accepted_receipt_count', 0)} accepted",
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts",
        ),
        _entry(
            "allowed_counts_zero",
            "Allowed counts remain zero",
            "round_10_allowed_count=0, implementation_allowed_count=0, execution_allowed_count=0, launchable_count=0",
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts",
        ),
        _entry(
            "runtime_capabilities_absent",
            "Runtime capabilities remain absent",
            "No launch POST, cancel POST, timeout POST, process creation, adapter call, stream capture, event write, or audit write.",
            "runner_real_execution_pre_unlock_round10_minimal_scope_previews",
        ),
        _entry(
            "next_action_requires_explicit_unlock",
            "Next action requires explicit unlock outside this layer",
            "Round 10 cannot begin from this summary; it remains an inert handoff view.",
            "runner_development_path_anchors",
        ),
    ]


def _entry(key: str, title: str, detail: str, stage_key: str) -> dict[str, object]:
    return {
        "key": f"pre_round10_locked_handoff_summary:{key}",
        "title": title,
        "detail": detail,
        "current_permission": "locked",
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Pre-round-10 locked handoff summary",
            "item_key": key,
        },
    }


def _summary_report(
    profile: dict[str, Any],
    handoff_summary_entries: list[dict[str, object]],
    explicit_unlock_handoff_receipt_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_round10_locked_handoff_summary:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_round10_locked_handoff_summary_locked",
        "explicit_unlock_handoff_receipt_status": explicit_unlock_handoff_receipt_collection.get("status", "missing"),
        "handoff_summary_entries": handoff_summary_entries,
        "checks": [
            _check("summary_entries_declared", "pass", "Summary entries declared", "Pre-round-10 locked state is summarized."),
            _check("summary_not_accepted", "warn", "Summary not accepted", "This summary cannot unlock implementation."),
            _check("round_10_not_allowed", "warn", "Round 10 not allowed", "Allowed counts remain zero."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only summarizes existing locked evidence."),
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
        "pre_round10_locked_handoff_summary_only": True,
        "accepts_handoff_summary": False,
        "accepts_unlock_phrase": False,
        "accepts_authorization": False,
        "allows_round_10_entry": False,
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
