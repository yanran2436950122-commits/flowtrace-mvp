from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_ROUND10_EXPLICIT_UNLOCK_CHECKPOINT_VERSION = (
    "project_runner_real_execution_round10_explicit_unlock_checkpoints.v1"
)
RUNNER_REAL_EXECUTION_ROUND10_EXPLICIT_UNLOCK_CHECKPOINT_SCHEMA_VERSION = (
    "runner_real_execution_round10_explicit_unlock_checkpoint_schema.v1"
)


def build_project_runner_real_execution_round10_explicit_unlock_checkpoints(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
    explicit_unlock_handoff_receipt_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    checkpoint_schema = runner_real_execution_round10_explicit_unlock_checkpoint_schema()
    checkpoint_entries = _checkpoint_entries(
        pre_round10_locked_handoff_summary_collection,
        explicit_unlock_handoff_receipt_collection,
    )
    reports = [
        _checkpoint_report(profile, checkpoint_entries, pre_round10_locked_handoff_summary_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_ROUND10_EXPLICIT_UNLOCK_CHECKPOINT_VERSION,
        "context": project_context,
        "status": "round10_explicit_unlock_checkpoint_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "checkpoint_entry_count": len(checkpoint_entries),
            "required_checkpoint_count": len(checkpoint_entries),
            "externally_satisfied_checkpoint_count": 0,
            "accepted_checkpoint_count": 0,
            "ready_checkpoint_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "external_unlock_satisfied": False,
            "pre_round10_locked_handoff_summary_status": pre_round10_locked_handoff_summary_collection.get(
                "status",
                "missing",
            ),
            "explicit_unlock_handoff_receipt_status": explicit_unlock_handoff_receipt_collection.get(
                "status",
                "missing",
            ),
        },
        "round10_explicit_unlock_checkpoint_schema": checkpoint_schema,
        "checkpoint_entries": checkpoint_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked round-10 explicit unlock checkpoint",
            "action": (
                "Use this read-only checkpoint to see whether an external explicit unlock has been satisfied. "
                "This layer does not collect, store, accept, or grant unlock permission."
            ),
        },
    }


def runner_real_execution_round10_explicit_unlock_checkpoint_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_ROUND10_EXPLICIT_UNLOCK_CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_state": {
            "read_only": True,
            "round10_explicit_unlock_checkpoint_only": True,
            "collects_unlock_now": False,
            "stores_unlock_now": False,
            "accepts_unlock_now": False,
            "external_unlock_satisfied_now": False,
            "round_10_allowed_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_external_conditions": [
            "exact unlock phrase must be supplied outside this read-only layer",
            "low-risk sample project scope must be confirmed outside this read-only layer",
            "minimal implementation mode must be confirmed outside this read-only layer",
            "all allowed counts must remain zero until unlock is explicitly accepted by a future authorized layer",
        ],
        "blocked_actions": [
            "collecting unlock input",
            "storing unlock input",
            "accepting unlock",
            "granting round-10 implementation permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _checkpoint_entries(
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
    explicit_unlock_handoff_receipt_collection: dict[str, Any],
) -> list[dict[str, object]]:
    handoff_summary = pre_round10_locked_handoff_summary_collection.get("summary", {})
    receipt_summary = explicit_unlock_handoff_receipt_collection.get("summary", {})
    return [
        _entry(
            "handoff_summary_locked",
            "Pre-round-10 handoff summary remains locked",
            f"{handoff_summary.get('handoff_summary_entry_count', 0)} summary entries; {handoff_summary.get('round_10_allowed_count', 0)} round-10 allowed",
            "runner_real_execution_pre_round10_locked_handoff_summaries",
        ),
        _entry(
            "receipt_not_observed",
            "Explicit unlock receipt has not been observed",
            f"{receipt_summary.get('observed_receipt_count', 0)} observed receipts",
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts",
        ),
        _entry(
            "receipt_not_accepted",
            "Explicit unlock receipt has not been accepted",
            f"{receipt_summary.get('accepted_receipt_count', 0)} accepted receipts",
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts",
        ),
        _entry(
            "external_unlock_not_satisfied",
            "External unlock is not satisfied",
            "external_unlock_satisfied=false",
            "runner_real_execution_pre_round10_locked_handoff_summaries",
        ),
        _entry(
            "round10_still_blocked",
            "Round 10 remains blocked",
            "round_10_allowed_count=0, implementation_allowed_count=0, execution_allowed_count=0, launchable_count=0",
            "runner_development_path_anchors",
        ),
    ]


def _entry(key: str, title: str, detail: str, stage_key: str) -> dict[str, object]:
    return {
        "key": f"round10_explicit_unlock_checkpoint:{key}",
        "title": title,
        "detail": detail,
        "current_permission": "locked",
        "required_before_round": 10,
        "externally_satisfied_now": False,
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Round-10 explicit unlock checkpoint",
            "item_key": key,
        },
    }


def _checkpoint_report(
    profile: dict[str, Any],
    checkpoint_entries: list[dict[str, object]],
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_round10_explicit_unlock_checkpoint:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "round10_explicit_unlock_checkpoint_locked",
        "pre_round10_locked_handoff_summary_status": pre_round10_locked_handoff_summary_collection.get(
            "status",
            "missing",
        ),
        "checkpoint_entries": checkpoint_entries,
        "checks": [
            _check("checkpoint_entries_declared", "pass", "Checkpoint entries declared", "Round-10 unlock checkpoint state is visible."),
            _check("external_unlock_not_satisfied", "warn", "External unlock not satisfied", "No external unlock is accepted here."),
            _check("round_10_not_allowed", "warn", "Round 10 not allowed", "Allowed counts remain zero."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only reports the locked checkpoint state."),
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
        "round10_explicit_unlock_checkpoint_only": True,
        "collects_unlock_input": False,
        "stores_unlock_input": False,
        "accepts_unlock_input": False,
        "external_unlock_satisfied": False,
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
