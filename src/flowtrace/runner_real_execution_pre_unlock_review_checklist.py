from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEW_CHECKLIST_VERSION = (
    "project_runner_real_execution_pre_unlock_review_checklists.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEW_CHECKLIST_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_review_checklist_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_review_checklists(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    pre_unlock_evidence_packet_index_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    checklist_schema = runner_real_execution_pre_unlock_review_checklist_schema()
    checklist_items = _checklist_items(pre_unlock_evidence_packet_index_collection)
    reports = [
        _checklist_report(profile, checklist_items, pre_unlock_evidence_packet_index_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEW_CHECKLIST_VERSION,
        "context": project_context,
        "status": "pre_unlock_review_checklist_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "checklist_item_count": len(checklist_items),
            "pending_item_count": sum(1 for item in checklist_items if item["answer_status"] == "pending"),
            "accepted_item_count": 0,
            "ready_item_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "evidence_packet_status": pre_unlock_evidence_packet_index_collection.get("status", "missing"),
            "evidence_packet_section_count": pre_unlock_evidence_packet_index_collection.get("summary", {}).get(
                "packet_section_count",
                0,
            ),
        },
        "pre_unlock_review_checklist_schema": checklist_schema,
        "checklist_items": checklist_items,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review locked pre-unlock checklist",
            "action": (
                "Use this checklist to inspect the questions that must be answered before any future explicit unlock. "
                "This layer does not accept answers, authorization, permissions, or implementation changes."
            ),
        },
    }


def runner_real_execution_pre_unlock_review_checklist_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_REVIEW_CHECKLIST_SCHEMA_VERSION,
        "checklist_state": {
            "read_only": True,
            "pre_unlock_review_checklist_only": True,
            "accepts_answers_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_review_topics": [
            "touchpoint gaps remain linked and understood",
            "touchpoint unlock conditions remain locked and complete",
            "explicit unlock phrase remains unaccepted",
            "no side-effect boundary remains intact",
        ],
        "blocked_actions": [
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


def _checklist_items(pre_unlock_evidence_packet_index_collection: dict[str, Any]) -> list[dict[str, object]]:
    sections = [
        item
        for item in pre_unlock_evidence_packet_index_collection.get("packet_sections", [])
        if isinstance(item, dict) and item.get("key")
    ]
    items: list[dict[str, object]] = []
    for section in sections:
        items.extend(_section_questions(section))
    return items


def _section_questions(section: dict[str, Any]) -> list[dict[str, object]]:
    section_key = str(section.get("key") or "unknown")
    navigation = section.get("navigation") if isinstance(section.get("navigation"), dict) else {}
    return [
        _question(
            section_key,
            "source_loaded",
            f"Is the {section.get('title', section_key)} source loaded and visible?",
            "The source status must be reviewed before explicit unlock.",
            navigation,
        ),
        _question(
            section_key,
            "locked_state_preserved",
            f"Does {section.get('title', section_key)} remain locked and unaccepted?",
            "The review must confirm no packet, phrase, authorization, implementation, or execution has been accepted.",
            navigation,
        ),
        _question(
            section_key,
            "side_effect_boundary_preserved",
            f"Does {section.get('title', section_key)} preserve the no-side-effect boundary?",
            "The review must confirm no command, process, adapter, stream, event, log, audit, authorization, permission, or user-project write side effect.",
            navigation,
        ),
    ]


def _question(
    section_key: str,
    question_key: str,
    question: str,
    expected_answer: str,
    navigation: dict[str, Any],
) -> dict[str, object]:
    return {
        "key": f"{section_key}:{question_key}",
        "section_key": section_key,
        "question": question,
        "expected_answer": expected_answer,
        "answer_status": "pending",
        "accepted_now": False,
        "ready_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "current_permission": "locked",
        "navigation": {
            "stage_key": navigation.get("stage_key") or "runner_real_execution_pre_unlock_evidence_packet_indexes",
            "evidence_group": "Pre-unlock review checklist",
            "item_key": f"{section_key}:{question_key}",
        },
    }


def _checklist_report(
    profile: dict[str, Any],
    checklist_items: list[dict[str, object]],
    pre_unlock_evidence_packet_index_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_review_checklist:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_review_checklist_locked",
        "evidence_packet_status": pre_unlock_evidence_packet_index_collection.get("status", "missing"),
        "checklist_items": checklist_items,
        "checks": [
            _check("checklist_items_declared", "pass", "Checklist items declared", "Pre-unlock packet sections have review questions."),
            _check("answers_not_accepted", "warn", "Answers not accepted", "The checklist is read-only and cannot unlock implementation."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No authorization, phrase, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only indexes read-only review questions."),
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
        "pre_unlock_review_checklist_only": True,
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
