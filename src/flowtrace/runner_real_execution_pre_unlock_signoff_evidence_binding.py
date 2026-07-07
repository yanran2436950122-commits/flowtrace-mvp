from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_SIGNOFF_EVIDENCE_BINDING_VERSION = (
    "project_runner_real_execution_pre_unlock_signoff_evidence_bindings.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_SIGNOFF_EVIDENCE_BINDING_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_signoff_evidence_binding_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    pre_unlock_reviewer_signoff_rubric_collection: dict[str, Any],
    pre_unlock_reviewer_role_map_collection: dict[str, Any],
    pre_unlock_review_checklist_collection: dict[str, Any],
    pre_unlock_evidence_packet_index_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    binding_schema = runner_real_execution_pre_unlock_signoff_evidence_binding_schema()
    binding_entries = _binding_entries(
        pre_unlock_reviewer_signoff_rubric_collection,
        pre_unlock_reviewer_role_map_collection,
        pre_unlock_review_checklist_collection,
        pre_unlock_evidence_packet_index_collection,
    )
    reports = [
        _binding_report(profile, binding_entries, pre_unlock_reviewer_signoff_rubric_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_SIGNOFF_EVIDENCE_BINDING_VERSION,
        "context": project_context,
        "status": "pre_unlock_signoff_evidence_binding_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "binding_entry_count": len(binding_entries),
            "unique_role_count": len({item["reviewer_role"] for item in binding_entries}),
            "checklist_link_count": sum(len(item["checklist_links"]) for item in binding_entries),
            "packet_section_link_count": len(
                {
                    link["section_key"]
                    for item in binding_entries
                    for link in item["packet_section_links"]
                    if link.get("section_key")
                }
            ),
            "accepted_binding_count": 0,
            "ready_binding_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "pre_unlock_reviewer_signoff_rubric_status": (
                pre_unlock_reviewer_signoff_rubric_collection.get("status", "missing")
            ),
            "pre_unlock_review_checklist_item_count": pre_unlock_review_checklist_collection.get("summary", {}).get(
                "checklist_item_count",
                0,
            ),
            "pre_unlock_evidence_packet_section_count": pre_unlock_evidence_packet_index_collection.get(
                "summary",
                {},
            ).get("packet_section_count", 0),
        },
        "pre_unlock_signoff_evidence_binding_schema": binding_schema,
        "binding_entries": binding_entries,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked sign-off evidence bindings",
            "action": (
                "Use these bindings to trace each non-accepting reviewer sign-off rubric back to its checklist "
                "items and packet sections. This layer does not accept sign-off, evidence, authorization, "
                "permissions, or implementation."
            ),
        },
    }


def runner_real_execution_pre_unlock_signoff_evidence_binding_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_SIGNOFF_EVIDENCE_BINDING_SCHEMA_VERSION,
        "binding_state": {
            "read_only": True,
            "pre_unlock_signoff_evidence_binding_only": True,
            "accepts_binding_now": False,
            "accepts_signoff_now": False,
            "accepts_evidence_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_binding_sources": [
            "pre-unlock reviewer sign-off rubric",
            "pre-unlock reviewer role map",
            "pre-unlock review checklist",
            "pre-unlock evidence packet index",
        ],
        "blocked_actions": [
            "accepting sign-off evidence bindings",
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


def _binding_entries(
    pre_unlock_reviewer_signoff_rubric_collection: dict[str, Any],
    pre_unlock_reviewer_role_map_collection: dict[str, Any],
    pre_unlock_review_checklist_collection: dict[str, Any],
    pre_unlock_evidence_packet_index_collection: dict[str, Any],
) -> list[dict[str, object]]:
    rubric_entries = [
        item
        for item in pre_unlock_reviewer_signoff_rubric_collection.get("rubric_entries", [])
        if isinstance(item, dict) and item.get("reviewer_role")
    ]
    role_entries = [
        item
        for item in pre_unlock_reviewer_role_map_collection.get("role_entries", [])
        if isinstance(item, dict) and item.get("reviewer_role")
    ]
    checklist_items = {
        item.get("key"): item
        for item in pre_unlock_review_checklist_collection.get("checklist_items", [])
        if isinstance(item, dict) and item.get("key")
    }
    packet_sections = {
        item.get("key"): item
        for item in pre_unlock_evidence_packet_index_collection.get("packet_sections", [])
        if isinstance(item, dict) and item.get("key")
    }
    return [
        _binding_entry(rubric_entry, role_entries, checklist_items, packet_sections)
        for rubric_entry in rubric_entries
    ]


def _binding_entry(
    rubric_entry: dict[str, Any],
    role_entries: list[dict[str, Any]],
    checklist_items: dict[object, dict[str, Any]],
    packet_sections: dict[object, dict[str, Any]],
) -> dict[str, object]:
    reviewer_role = str(rubric_entry.get("reviewer_role") or "unknown")
    matching_roles = [item for item in role_entries if item.get("reviewer_role") == reviewer_role]
    checklist_links = [_checklist_link(item, checklist_items.get(item.get("checklist_item_key"))) for item in matching_roles]
    section_keys = sorted({str(link["section_key"]) for link in checklist_links if link.get("section_key")})
    packet_section_links = [_packet_section_link(section_key, packet_sections.get(section_key)) for section_key in section_keys]
    return {
        "key": f"signoff_evidence_binding:{reviewer_role}",
        "reviewer_role": reviewer_role,
        "reviewer_label": rubric_entry.get("reviewer_label") or reviewer_role,
        "rubric_key": rubric_entry.get("key"),
        "rubric_criteria_count": len(rubric_entry.get("criteria", [])),
        "checklist_links": checklist_links,
        "packet_section_links": packet_section_links,
        "source_status": "bound_read_only",
        "current_permission": "locked",
        "binding_accepted_now": False,
        "signoff_accepted_now": False,
        "evidence_accepted_now": False,
        "ready_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": rubric_entry.get("navigation"),
    }


def _checklist_link(role_entry: dict[str, Any], checklist_item: dict[str, Any] | None) -> dict[str, object]:
    return {
        "role_entry_key": role_entry.get("key"),
        "checklist_item_key": role_entry.get("checklist_item_key"),
        "section_key": role_entry.get("section_key"),
        "question": role_entry.get("question"),
        "expected_answer": role_entry.get("expected_answer"),
        "checklist_status": checklist_item.get("answer_status", "missing") if checklist_item else "missing",
        "accepted_now": False,
        "ready_now": False,
        "navigation": role_entry.get("navigation"),
    }


def _packet_section_link(section_key: str, packet_section: dict[str, Any] | None) -> dict[str, object]:
    return {
        "section_key": section_key,
        "title": packet_section.get("title", section_key) if packet_section else section_key,
        "source_status": packet_section.get("source_status", "missing") if packet_section else "missing",
        "item_count": packet_section.get("item_count", 0) if packet_section else 0,
        "accepted_now": False,
        "ready_now": False,
        "navigation": packet_section.get("navigation") if packet_section else None,
    }


def _binding_report(
    profile: dict[str, Any],
    binding_entries: list[dict[str, object]],
    pre_unlock_reviewer_signoff_rubric_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_signoff_evidence_binding:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_signoff_evidence_binding_locked",
        "pre_unlock_reviewer_signoff_rubric_status": (
            pre_unlock_reviewer_signoff_rubric_collection.get("status", "missing")
        ),
        "binding_entries": binding_entries,
        "checks": [
            _check("bindings_declared", "pass", "Bindings declared", "Reviewer sign-off rubric entries are linked to source evidence."),
            _check("bindings_not_accepted", "warn", "Bindings not accepted", "The binding layer is read-only and cannot unlock implementation."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No sign-off, evidence, authorization, phrase, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only binds existing read-only review evidence."),
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
        "pre_unlock_signoff_evidence_binding_only": True,
        "accepts_signoff_evidence_bindings": False,
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
