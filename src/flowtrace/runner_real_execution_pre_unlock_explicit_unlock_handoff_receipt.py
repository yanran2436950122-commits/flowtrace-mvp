from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_EXPLICIT_UNLOCK_HANDOFF_RECEIPT_VERSION = (
    "project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_EXPLICIT_UNLOCK_HANDOFF_RECEIPT_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
    round10_minimal_scope_preview_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    receipt_schema = runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_schema()
    receipt_entries = _receipt_entries(
        unlock_phrase_readiness_collection,
        round10_minimal_scope_preview_collection,
    )
    reports = [
        _receipt_report(profile, receipt_entries, unlock_phrase_readiness_collection, round10_minimal_scope_preview_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_EXPLICIT_UNLOCK_HANDOFF_RECEIPT_VERSION,
        "context": project_context,
        "status": "pre_unlock_explicit_unlock_handoff_receipt_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "receipt_entry_count": len(receipt_entries),
            "required_receipt_count": len(receipt_entries),
            "observed_receipt_count": 0,
            "accepted_receipt_count": 0,
            "ready_receipt_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "unlock_phrase_readiness_status": unlock_phrase_readiness_collection.get("status", "missing"),
            "round10_minimal_scope_preview_status": round10_minimal_scope_preview_collection.get("status", "missing"),
        },
        "pre_unlock_explicit_unlock_handoff_receipt_schema": receipt_schema,
        "receipt_entries": receipt_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked explicit-unlock handoff receipt",
            "action": (
                "Use this read-only receipt to inspect what must be explicitly acknowledged before round 10. "
                "This layer does not collect, store, accept, or act on the unlock phrase."
            ),
        },
    }


def runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_EXPLICIT_UNLOCK_HANDOFF_RECEIPT_SCHEMA_VERSION,
        "receipt_state": {
            "read_only": True,
            "pre_unlock_explicit_unlock_handoff_receipt_only": True,
            "collects_receipt_now": False,
            "stores_receipt_now": False,
            "accepts_receipt_now": False,
            "round_10_allowed_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "blocked_actions": [
            "collecting explicit unlock receipt input",
            "storing explicit unlock receipt input",
            "accepting explicit unlock",
            "granting implementation permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _receipt_entries(
    unlock_phrase_readiness_collection: dict[str, Any],
    round10_minimal_scope_preview_collection: dict[str, Any],
) -> list[dict[str, object]]:
    required_phrase = unlock_phrase_readiness_collection.get("required_unlock_phrase", {})
    preview_summary = round10_minimal_scope_preview_collection.get("summary", {})
    return [
        _entry(
            "exact_unlock_phrase_visible",
            "Exact unlock phrase must be visible",
            str(required_phrase.get("exact_phrase") or "missing"),
            "runner_real_execution_unlock_phrase_readiness",
        ),
        _entry(
            "low_risk_scope_only",
            "Scope must remain low-risk sample project only",
            str(required_phrase.get("scope") or "missing"),
            "runner_real_execution_unlock_phrase_readiness",
        ),
        _entry(
            "minimal_implementation_mode",
            "Implementation mode must remain minimal",
            str(required_phrase.get("minimum_implementation_mode") or "missing"),
            "runner_real_execution_unlock_phrase_readiness",
        ),
        _entry(
            "round10_minimal_touch_preview",
            "Round-10 minimal-touch items must be reviewed",
            f"{preview_summary.get('minimal_touch_count', 0)} minimal-touch preview entries",
            "runner_real_execution_pre_unlock_round10_minimal_scope_previews",
        ),
        _entry(
            "round10_deferred_items_preview",
            "Deferred runtime items must remain deferred",
            f"{preview_summary.get('explicitly_deferred_count', 0)} explicitly deferred preview entries",
            "runner_real_execution_pre_unlock_round10_minimal_scope_previews",
        ),
        _entry(
            "zero_allowed_counts",
            "Allowed counts must remain zero before explicit unlock",
            "round_10_allowed_count=0, implementation_allowed_count=0, execution_allowed_count=0, launchable_count=0",
            "runner_real_execution_pre_unlock_round10_minimal_scope_previews",
        ),
        _entry(
            "hard_boundary_acknowledgement",
            "Hard boundary must be acknowledged before implementation",
            "No POST APIs, processes, adapter calls, streams, events, logs, audit writes, authorization storage, permission grants, or user-project writes are accepted here.",
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers",
        ),
    ]


def _entry(key: str, title: str, requirement: str, stage_key: str) -> dict[str, object]:
    return {
        "key": f"explicit_unlock_handoff_receipt:{key}",
        "title": title,
        "requirement": requirement,
        "current_permission": "locked",
        "required_before_round": 10,
        "observed_now": False,
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Pre-unlock explicit unlock handoff receipt",
            "item_key": key,
        },
    }


def _receipt_report(
    profile: dict[str, Any],
    receipt_entries: list[dict[str, object]],
    unlock_phrase_readiness_collection: dict[str, Any],
    round10_minimal_scope_preview_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_explicit_unlock_handoff_receipt_locked",
        "unlock_phrase_readiness_status": unlock_phrase_readiness_collection.get("status", "missing"),
        "round10_minimal_scope_preview_status": round10_minimal_scope_preview_collection.get("status", "missing"),
        "receipt_entries": receipt_entries,
        "checks": [
            _check("receipt_entries_declared", "pass", "Receipt entries declared", "Explicit unlock handoff requirements are visible."),
            _check("receipt_not_collected", "pass", "Receipt not collected", "This layer does not collect or store receipt input."),
            _check("unlock_not_accepted", "warn", "Unlock not accepted", "Round 10 remains locked from this layer."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only displays the handoff receipt requirements."),
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
        "pre_unlock_explicit_unlock_handoff_receipt_only": True,
        "collects_unlock_receipt": False,
        "stores_unlock_receipt": False,
        "accepts_unlock_receipt": False,
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
