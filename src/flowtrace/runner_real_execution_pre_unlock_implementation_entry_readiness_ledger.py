from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_IMPLEMENTATION_ENTRY_READINESS_LEDGER_VERSION = (
    "project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_IMPLEMENTATION_ENTRY_READINESS_LEDGER_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    development_path_anchor_collection: dict[str, Any],
    pre_unlock_signoff_evidence_binding_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
    real_execution_implementation_plan_collection: dict[str, Any],
    real_execution_scope_diff_audit_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    ledger_schema = runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_schema()
    ledger_entries = _ledger_entries(
        development_path_anchor_collection,
        pre_unlock_signoff_evidence_binding_collection,
        unlock_phrase_readiness_collection,
        real_execution_implementation_plan_collection,
        real_execution_scope_diff_audit_collection,
    )
    reports = [
        _ledger_report(profile, ledger_entries, development_path_anchor_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_IMPLEMENTATION_ENTRY_READINESS_LEDGER_VERSION,
        "context": project_context,
        "status": "pre_unlock_implementation_entry_readiness_ledger_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ledger_entry_count": len(ledger_entries),
            "locked_entry_count": len(ledger_entries),
            "blocking_entry_count": len(ledger_entries),
            "accepted_entry_count": 0,
            "ready_entry_count": 0,
            "round_10_allowed_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "next_locked_round": "execution_adapter_minimal_implementation",
            "development_path_status": development_path_anchor_collection.get("status", "missing"),
            "signoff_evidence_binding_status": pre_unlock_signoff_evidence_binding_collection.get("status", "missing"),
        },
        "pre_unlock_implementation_entry_readiness_ledger_schema": ledger_schema,
        "ledger_entries": ledger_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked round-10 entry ledger",
            "action": (
                "Use this ledger to see the remaining locked prerequisites before round 10. It does not accept "
                "unlock phrases, sign-off, authorization, permissions, or implementation work."
            ),
        },
    }


def runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_IMPLEMENTATION_ENTRY_READINESS_LEDGER_SCHEMA_VERSION,
        "ledger_state": {
            "read_only": True,
            "pre_unlock_implementation_entry_readiness_ledger_only": True,
            "round_10_allowed_now": False,
            "accepts_unlock_phrase_now": False,
            "accepts_signoff_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_pre_round_10_topics": [
            "fixed path anchor remains locked",
            "sign-off evidence bindings remain traceable but unaccepted",
            "explicit unlock phrase remains unaccepted",
            "implementation plan remains a plan, not implementation",
            "scope diff audit remains locked with no allowed implementation items",
        ],
        "blocked_actions": [
            "entering round 10 implementation",
            "accepting unlock phrases",
            "accepting reviewer sign-off",
            "accepting authorization",
            "granting implementation permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _ledger_entries(
    development_path_anchor_collection: dict[str, Any],
    pre_unlock_signoff_evidence_binding_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
    real_execution_implementation_plan_collection: dict[str, Any],
    real_execution_scope_diff_audit_collection: dict[str, Any],
) -> list[dict[str, object]]:
    return [
        _entry(
            "fixed_path_anchor",
            "Fixed path anchor",
            development_path_anchor_collection.get("status", "missing"),
            "Round 10 remains locked until an explicit unlock is provided.",
            "runner_development_path_anchors",
            development_path_anchor_collection.get("summary", {}).get("locked_round_count", 0),
        ),
        _entry(
            "signoff_evidence_bindings",
            "Sign-off evidence bindings",
            pre_unlock_signoff_evidence_binding_collection.get("status", "missing"),
            "Reviewer sign-off evidence is traceable but not accepted.",
            "runner_real_execution_pre_unlock_signoff_evidence_bindings",
            pre_unlock_signoff_evidence_binding_collection.get("summary", {}).get("binding_entry_count", 0),
        ),
        _entry(
            "unlock_phrase",
            "Explicit unlock phrase",
            unlock_phrase_readiness_collection.get("status", "missing"),
            "The explicit unlock phrase is required but not observed or accepted.",
            "runner_real_execution_unlock_phrase_readiness",
            unlock_phrase_readiness_collection.get("summary", {}).get("accepted_phrase_count", 0),
        ),
        _entry(
            "implementation_plan",
            "Implementation plan",
            real_execution_implementation_plan_collection.get("status", "missing"),
            "The future implementation plan is review-only and does not write code.",
            "runner_real_execution_implementation_plans",
            real_execution_implementation_plan_collection.get("summary", {}).get("module_count", 0),
        ),
        _entry(
            "scope_diff_audit",
            "Scope diff audit",
            real_execution_scope_diff_audit_collection.get("status", "missing"),
            "All scope diff items remain locked and disallowed before round 10.",
            "runner_real_execution_scope_diff_audits",
            real_execution_scope_diff_audit_collection.get("summary", {}).get("locked_item_count", 0),
        ),
    ]


def _entry(key: str, title: str, source_status: object, blocker: str, stage_key: str, source_count: object) -> dict[str, object]:
    return {
        "key": f"implementation_entry_readiness:{key}",
        "title": title,
        "source_status": source_status,
        "source_count": source_count,
        "blocker": blocker,
        "current_permission": "locked",
        "accepted_now": False,
        "ready_now": False,
        "round_10_allowed_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Pre-unlock implementation entry readiness ledger",
            "item_key": key,
        },
    }


def _ledger_report(
    profile: dict[str, Any],
    ledger_entries: list[dict[str, object]],
    development_path_anchor_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_implementation_entry_readiness_ledger:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_implementation_entry_readiness_ledger_locked",
        "development_path_status": development_path_anchor_collection.get("status", "missing"),
        "ledger_entries": ledger_entries,
        "checks": [
            _check("ledger_entries_declared", "pass", "Ledger entries declared", "Pre-round-10 prerequisites are summarized."),
            _check("round_10_not_allowed", "warn", "Round 10 not allowed", "The ledger is read-only and cannot unlock implementation."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No phrase, sign-off, authorization, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only summarizes locked readiness prerequisites."),
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
        "pre_unlock_implementation_entry_readiness_ledger_only": True,
        "allows_round_10_entry": False,
        "accepts_unlock_phrase": False,
        "accepts_reviewer_signoff": False,
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
