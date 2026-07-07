from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_SIGNOFF_RUBRIC_VERSION = (
    "project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_SIGNOFF_RUBRIC_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_reviewer_signoff_rubric_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    pre_unlock_reviewer_role_map_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    rubric_schema = runner_real_execution_pre_unlock_reviewer_signoff_rubric_schema()
    rubric_entries = _rubric_entries(pre_unlock_reviewer_role_map_collection)
    reports = [
        _rubric_report(profile, rubric_entries, pre_unlock_reviewer_role_map_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_SIGNOFF_RUBRIC_VERSION,
        "context": project_context,
        "status": "pre_unlock_reviewer_signoff_rubric_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "rubric_entry_count": len(rubric_entries),
            "unique_role_count": len({item["reviewer_role"] for item in rubric_entries}),
            "required_signoff_count": len(rubric_entries),
            "accepted_signoff_count": 0,
            "ready_signoff_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "pre_unlock_reviewer_role_map_status": pre_unlock_reviewer_role_map_collection.get("status", "missing"),
            "pre_unlock_reviewer_role_map_entry_count": pre_unlock_reviewer_role_map_collection.get("summary", {}).get(
                "role_entry_count",
                0,
            ),
        },
        "pre_unlock_reviewer_signoff_rubric_schema": rubric_schema,
        "rubric_entries": rubric_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked sign-off rubric",
            "action": (
                "Use this rubric to inspect the sign-off criteria expected for each reviewer role before a future "
                "explicit unlock. This layer does not accept sign-off, authorization, permissions, or implementation."
            ),
        },
    }


def runner_real_execution_pre_unlock_reviewer_signoff_rubric_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_SIGNOFF_RUBRIC_SCHEMA_VERSION,
        "rubric_state": {
            "read_only": True,
            "pre_unlock_reviewer_signoff_rubric_only": True,
            "accepts_signoff_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "rubric_dimensions": [
            "source evidence is visible",
            "locked state is preserved",
            "hard boundary is preserved",
            "implementation remains disallowed",
        ],
        "blocked_actions": [
            "accepting reviewer sign-off",
            "accepting reviewer role assignments",
            "accepting checklist answers",
            "accepting the evidence packet",
            "accepting the explicit unlock phrase",
            "accepting authorization",
            "granting implementation permission",
            "granting launch permission",
            "registering launch/cancel/timeout POST APIs",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _rubric_entries(pre_unlock_reviewer_role_map_collection: dict[str, Any]) -> list[dict[str, object]]:
    role_entries = [
        item
        for item in pre_unlock_reviewer_role_map_collection.get("role_entries", [])
        if isinstance(item, dict) and item.get("key")
    ]
    seen_roles: set[str] = set()
    entries: list[dict[str, object]] = []
    for role_entry in role_entries:
        role_key = str(role_entry.get("reviewer_role") or "")
        if not role_key or role_key in seen_roles:
            continue
        seen_roles.add(role_key)
        entries.append(_rubric_entry(role_entry))
    return entries


def _rubric_entry(role_entry: dict[str, Any]) -> dict[str, object]:
    role_key = str(role_entry.get("reviewer_role") or "unknown")
    return {
        "key": f"reviewer_signoff_rubric:{role_key}",
        "reviewer_role": role_key,
        "reviewer_label": role_entry.get("reviewer_label") or role_key,
        "responsibility": role_entry.get("responsibility"),
        "criteria": _criteria(role_key),
        "current_permission": "locked",
        "signoff_required": True,
        "signoff_accepted_now": False,
        "ready_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": role_entry.get("navigation"),
    }


def _criteria(role_key: str) -> list[str]:
    common = [
        "Confirm the reviewed evidence remains read-only.",
        "Confirm no authorization, permission, implementation, execution, launch, or user-project side effect is accepted.",
    ]
    role_specific = {
        "governance_reviewer": [
            "Confirm source evidence, packet sections, and checklist topics are visible and linked.",
            "Confirm the explicit unlock phrase requirement is displayed but unaccepted.",
        ],
        "safety_reviewer": [
            "Confirm command execution, process creation, adapter calls, streams, events, logs, audit writes, authorization, permission grants, and user-project writes remain blocked.",
            "Confirm launch/cancel/timeout POST APIs remain unregistered.",
        ],
        "implementation_reviewer": [
            "Confirm real execution implementation remains locked before round 10.",
            "Confirm implementation_allowed_count, execution_allowed_count, and launchable_count remain zero.",
        ],
    }
    return role_specific.get(role_key, ["Confirm the role responsibility remains locked and review-only."]) + common


def _rubric_report(
    profile: dict[str, Any],
    rubric_entries: list[dict[str, object]],
    pre_unlock_reviewer_role_map_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_reviewer_signoff_rubric:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_reviewer_signoff_rubric_locked",
        "pre_unlock_reviewer_role_map_status": pre_unlock_reviewer_role_map_collection.get("status", "missing"),
        "rubric_entries": rubric_entries,
        "checks": [
            _check("rubric_entries_declared", "pass", "Rubric entries declared", "Reviewer roles have non-accepting sign-off criteria."),
            _check("signoff_not_accepted", "warn", "Sign-off not accepted", "The rubric is read-only and cannot unlock implementation."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No sign-off, authorization, phrase, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only maps read-only sign-off criteria."),
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
        "pre_unlock_reviewer_signoff_rubric_only": True,
        "accepts_reviewer_signoff": False,
        "accepts_reviewer_roles": False,
        "accepts_checklist_answers": False,
        "accepts_evidence_packet": False,
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
        "stores_unlock_phrase": False,
        "grants_permission": False,
        "writes_user_project": False,
    }
