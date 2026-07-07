from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_ROLE_MAP_VERSION = (
    "project_runner_real_execution_pre_unlock_reviewer_role_maps.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_ROLE_MAP_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_reviewer_role_map_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_reviewer_role_maps(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    pre_unlock_review_checklist_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    role_map_schema = runner_real_execution_pre_unlock_reviewer_role_map_schema()
    role_entries = _role_entries(pre_unlock_review_checklist_collection)
    reports = [
        _role_map_report(profile, role_entries, pre_unlock_review_checklist_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_ROLE_MAP_VERSION,
        "context": project_context,
        "status": "pre_unlock_reviewer_role_map_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "role_entry_count": len(role_entries),
            "unique_role_count": len({item["reviewer_role"] for item in role_entries}),
            "assigned_role_count": 0,
            "accepted_role_count": 0,
            "ready_role_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "pre_unlock_review_checklist_status": pre_unlock_review_checklist_collection.get("status", "missing"),
            "pre_unlock_review_checklist_item_count": pre_unlock_review_checklist_collection.get("summary", {}).get(
                "checklist_item_count",
                0,
            ),
        },
        "pre_unlock_reviewer_role_map_schema": role_map_schema,
        "role_entries": role_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked role responsibilities",
            "action": (
                "Use this map to see which reviewer responsibility belongs to each pre-unlock checklist topic. "
                "This layer does not assign permissions, accept roles, or unlock implementation."
            ),
        },
    }


def runner_real_execution_pre_unlock_reviewer_role_map_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEWER_ROLE_MAP_SCHEMA_VERSION,
        "role_map_state": {
            "read_only": True,
            "pre_unlock_reviewer_role_map_only": True,
            "assigns_roles_now": False,
            "accepts_roles_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "reviewer_roles": [
            _role("governance_reviewer", "Governance reviewer", "Confirms source visibility and read-only chain integrity."),
            _role("safety_reviewer", "Safety reviewer", "Confirms no-side-effect and hard-boundary preservation."),
            _role("implementation_reviewer", "Implementation reviewer", "Confirms implementation remains locked and scoped."),
        ],
        "blocked_actions": [
            "assigning reviewer permissions",
            "accepting reviewer sign-off",
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


def _role_entries(pre_unlock_review_checklist_collection: dict[str, Any]) -> list[dict[str, object]]:
    items = [
        item
        for item in pre_unlock_review_checklist_collection.get("checklist_items", [])
        if isinstance(item, dict) and item.get("key")
    ]
    return [_role_entry(item) for item in items]


def _role_entry(checklist_item: dict[str, Any]) -> dict[str, object]:
    item_key = str(checklist_item.get("key") or "")
    role_key = _role_for_item(item_key)
    return {
        "key": f"reviewer_role:{item_key}",
        "checklist_item_key": item_key,
        "section_key": checklist_item.get("section_key"),
        "reviewer_role": role_key,
        "reviewer_label": _role_label(role_key),
        "responsibility": _responsibility(role_key),
        "question": checklist_item.get("question"),
        "expected_answer": checklist_item.get("expected_answer"),
        "current_permission": "locked",
        "assigned_now": False,
        "accepted_now": False,
        "ready_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": checklist_item.get("navigation"),
    }


def _role_for_item(item_key: str) -> str:
    if item_key.endswith(":side_effect_boundary_preserved"):
        return "safety_reviewer"
    if item_key.endswith(":locked_state_preserved"):
        return "implementation_reviewer"
    return "governance_reviewer"


def _role_label(role_key: str) -> str:
    labels = {
        "governance_reviewer": "Governance reviewer",
        "safety_reviewer": "Safety reviewer",
        "implementation_reviewer": "Implementation reviewer",
    }
    return labels.get(role_key, role_key)


def _responsibility(role_key: str) -> str:
    responsibilities = {
        "governance_reviewer": "Review source visibility, evidence linkage, and read-only completeness.",
        "safety_reviewer": "Review hard-boundary preservation and no-side-effect guarantees.",
        "implementation_reviewer": "Review locked implementation state and confirm no execution capability is enabled.",
    }
    return responsibilities.get(role_key, "Review the locked pre-unlock checklist item.")


def _role(key: str, label: str, responsibility: str) -> dict[str, object]:
    return {"key": key, "label": label, "responsibility": responsibility, "accepted_now": False}


def _role_map_report(
    profile: dict[str, Any],
    role_entries: list[dict[str, object]],
    pre_unlock_review_checklist_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_reviewer_role_map:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_reviewer_role_map_locked",
        "pre_unlock_review_checklist_status": pre_unlock_review_checklist_collection.get("status", "missing"),
        "role_entries": role_entries,
        "checks": [
            _check("role_entries_declared", "pass", "Role entries declared", "Checklist topics are mapped to reviewer responsibilities."),
            _check("roles_not_assigned", "warn", "Roles not assigned", "The role map is read-only and does not assign permissions."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No role, authorization, phrase, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only maps read-only reviewer responsibilities."),
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
        "pre_unlock_reviewer_role_map_only": True,
        "assigns_reviewer_roles": False,
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
