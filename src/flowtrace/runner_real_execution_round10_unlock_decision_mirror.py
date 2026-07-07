from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_ROUND10_UNLOCK_DECISION_MIRROR_VERSION = (
    "project_runner_real_execution_round10_unlock_decision_mirrors.v1"
)
RUNNER_REAL_EXECUTION_ROUND10_UNLOCK_DECISION_MIRROR_SCHEMA_VERSION = (
    "runner_real_execution_round10_unlock_decision_mirror_schema.v1"
)


def build_project_runner_real_execution_round10_unlock_decision_mirrors(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    round10_explicit_unlock_checkpoint_collection: dict[str, Any],
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    decision_schema = runner_real_execution_round10_unlock_decision_mirror_schema()
    decision_entries = _decision_entries(
        round10_explicit_unlock_checkpoint_collection,
        pre_round10_locked_handoff_summary_collection,
    )
    reports = [
        _decision_report(
            profile,
            decision_entries,
            round10_explicit_unlock_checkpoint_collection,
            pre_round10_locked_handoff_summary_collection,
        )
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_ROUND10_UNLOCK_DECISION_MIRROR_VERSION,
        "context": project_context,
        "status": "round10_unlock_decision_mirror_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "decision_entry_count": len(decision_entries),
            "locked_decision_count": len(decision_entries),
            "not_allowed_decision_count": len(decision_entries),
            "accepted_decision_count": 0,
            "ready_decision_count": 0,
            "external_unlock_satisfied_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "decision": "locked_not_allowed",
            "can_enter_round_10": False,
            "round10_explicit_unlock_checkpoint_status": (
                round10_explicit_unlock_checkpoint_collection.get("status", "missing")
            ),
            "pre_round10_locked_handoff_summary_status": (
                pre_round10_locked_handoff_summary_collection.get("status", "missing")
            ),
        },
        "round10_unlock_decision_mirror_schema": decision_schema,
        "decision_entries": decision_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked round-10 unlock decision",
            "action": (
                "Use this read-only mirror to see the current round-10 entry decision. "
                "It mirrors existing locked evidence and cannot collect, accept, or grant unlock permission."
            ),
        },
    }


def runner_real_execution_round10_unlock_decision_mirror_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_ROUND10_UNLOCK_DECISION_MIRROR_SCHEMA_VERSION,
        "decision_state": {
            "read_only": True,
            "round10_unlock_decision_mirror_only": True,
            "mirrors_decision_only": True,
            "decision_now": "locked_not_allowed",
            "collects_unlock_now": False,
            "stores_unlock_now": False,
            "accepts_unlock_now": False,
            "accepts_unlock_phrase_now": False,
            "accepts_authorization_now": False,
            "grants_permission_now": False,
            "round_10_allowed_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "blocked_actions": [
            "collecting unlock input",
            "storing unlock input",
            "accepting unlock phrases or authorization",
            "granting round-10 implementation permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "importing or calling an execution adapter",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _decision_entries(
    round10_explicit_unlock_checkpoint_collection: dict[str, Any],
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
) -> list[dict[str, object]]:
    checkpoint_summary = round10_explicit_unlock_checkpoint_collection.get("summary", {})
    handoff_summary = pre_round10_locked_handoff_summary_collection.get("summary", {})
    return [
        _entry(
            "checkpoint_locked",
            "Round-10 checkpoint remains locked",
            f"{checkpoint_summary.get('checkpoint_entry_count', 0)} checkpoint entries; decision remains locked.",
            "runner_real_execution_round10_explicit_unlock_checkpoints",
        ),
        _entry(
            "external_unlock_unsatisfied",
            "External unlock is unsatisfied",
            f"external_unlock_satisfied={checkpoint_summary.get('external_unlock_satisfied', False)}",
            "runner_real_execution_round10_explicit_unlock_checkpoints",
        ),
        _entry(
            "handoff_summary_locked",
            "Pre-round-10 handoff summary remains locked",
            f"{handoff_summary.get('handoff_summary_entry_count', 0)} summary entries; {handoff_summary.get('round_10_allowed_count', 0)} round-10 allowed.",
            "runner_real_execution_pre_round10_locked_handoff_summaries",
        ),
        _entry(
            "permission_not_granted",
            "Round-10 permission has not been granted",
            "No accepted unlock input, authorization, or permission grant is present in this layer.",
            "runner_real_execution_round10_explicit_unlock_checkpoints",
        ),
        _entry(
            "runtime_surface_absent",
            "Runtime execution surface remains absent",
            "No launch POST, process creation, adapter call, stream capture, event write, log write, or audit write is available.",
            "runner_real_execution_pre_round10_locked_handoff_summaries",
        ),
    ]


def _entry(key: str, title: str, detail: str, stage_key: str) -> dict[str, object]:
    return {
        "key": f"round10_unlock_decision_mirror:{key}",
        "title": title,
        "detail": detail,
        "current_permission": "locked",
        "decision": "not_allowed",
        "not_allowed_now": True,
        "externally_satisfied_now": False,
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Round-10 unlock decision mirror",
            "item_key": key,
        },
    }


def _decision_report(
    profile: dict[str, Any],
    decision_entries: list[dict[str, object]],
    round10_explicit_unlock_checkpoint_collection: dict[str, Any],
    pre_round10_locked_handoff_summary_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_round10_unlock_decision_mirror:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "round10_unlock_decision_mirror_locked",
        "decision": "locked_not_allowed",
        "round10_explicit_unlock_checkpoint_status": round10_explicit_unlock_checkpoint_collection.get(
            "status",
            "missing",
        ),
        "pre_round10_locked_handoff_summary_status": pre_round10_locked_handoff_summary_collection.get(
            "status",
            "missing",
        ),
        "decision_entries": decision_entries,
        "checks": [
            _check("decision_entries_declared", "pass", "Decision entries declared", "Round-10 decision state is visible."),
            _check("decision_locked", "warn", "Decision locked", "The mirrored decision is locked_not_allowed."),
            _check("round_10_not_allowed", "warn", "Round 10 not allowed", "Allowed counts remain zero."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only mirrors a locked decision."),
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
        "round10_unlock_decision_mirror_only": True,
        "mirrors_decision_only": True,
        "collects_unlock_input": False,
        "stores_unlock_input": False,
        "accepts_unlock_input": False,
        "external_unlock_satisfied": False,
        "accepts_unlock_phrase": False,
        "accepts_authorization": False,
        "grants_permission": False,
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
        "writes_user_project": False,
    }
