from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_PRE_UNLOCK_EVIDENCE_PACKET_INDEX_VERSION = (
    "project_runner_real_execution_pre_unlock_evidence_packet_indexes.v1"
)
RUNNER_REAL_EXECUTION_PRE_UNLOCK_EVIDENCE_PACKET_INDEX_SCHEMA_VERSION = (
    "runner_real_execution_pre_unlock_evidence_packet_index_schema.v1"
)


def build_project_runner_real_execution_pre_unlock_evidence_packet_indexes(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    touchpoint_gap_link_collection: dict[str, Any],
    touchpoint_unlock_matrix_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    packet_schema = runner_real_execution_pre_unlock_evidence_packet_index_schema()
    packet_sections = _packet_sections(
        touchpoint_gap_link_collection,
        touchpoint_unlock_matrix_collection,
        unlock_phrase_readiness_collection,
    )
    reports = [
        _packet_report(
            profile,
            packet_sections,
            touchpoint_gap_link_collection,
            touchpoint_unlock_matrix_collection,
            unlock_phrase_readiness_collection,
        )
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_EVIDENCE_PACKET_INDEX_VERSION,
        "context": project_context,
        "status": "pre_unlock_evidence_packet_index_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "packet_section_count": len(packet_sections),
            "touchpoint_gap_link_entry_count": touchpoint_gap_link_collection.get("summary", {}).get(
                "link_entry_count",
                0,
            ),
            "touchpoint_unlock_matrix_entry_count": touchpoint_unlock_matrix_collection.get("summary", {}).get(
                "matrix_entry_count",
                0,
            ),
            "required_phrase_count": unlock_phrase_readiness_collection.get("summary", {}).get(
                "required_phrase_count",
                0,
            ),
            "accepted_phrase_count": 0,
            "review_packet_ready_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
        },
        "pre_unlock_evidence_packet_index_schema": packet_schema,
        "packet_sections": packet_sections,
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Review pre-unlock evidence packet",
            "action": (
                "Use this read-only packet index to review touchpoint gaps, touchpoint unlock conditions, and the "
                "explicit unlock phrase requirement before any future unlock. Do not accept authorization or enter "
                "real execution implementation from this layer."
            ),
        },
    }


def runner_real_execution_pre_unlock_evidence_packet_index_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_PRE_UNLOCK_EVIDENCE_PACKET_INDEX_SCHEMA_VERSION,
        "packet_state": {
            "read_only": True,
            "pre_unlock_evidence_packet_index_only": True,
            "accepts_packet_now": False,
            "accepts_authorization_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_packet_sections": [
            "locked touchpoint gap links",
            "locked touchpoint unlock matrix",
            "explicit unlock phrase readiness",
        ],
        "blocked_actions": [
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


def _packet_sections(
    touchpoint_gap_link_collection: dict[str, Any],
    touchpoint_unlock_matrix_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
) -> list[dict[str, object]]:
    return [
        _section(
            "touchpoint_gap_links",
            "Locked touchpoint gap links",
            touchpoint_gap_link_collection.get("status", "missing"),
            touchpoint_gap_link_collection.get("summary", {}).get("link_entry_count", 0),
            "runner_real_execution_touchpoint_gap_links",
        ),
        _section(
            "touchpoint_unlock_matrix",
            "Locked touchpoint unlock matrix",
            touchpoint_unlock_matrix_collection.get("status", "missing"),
            touchpoint_unlock_matrix_collection.get("summary", {}).get("matrix_entry_count", 0),
            "runner_real_execution_touchpoint_unlock_matrices",
        ),
        _section(
            "unlock_phrase_readiness",
            "Explicit unlock phrase readiness",
            unlock_phrase_readiness_collection.get("status", "missing"),
            unlock_phrase_readiness_collection.get("summary", {}).get("required_phrase_count", 0),
            "runner_real_execution_unlock_phrase_readiness",
        ),
    ]


def _section(key: str, title: str, source_status: object, item_count: object, stage_key: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "source_status": source_status,
        "item_count": item_count,
        "current_permission": "locked",
        "accepted_now": False,
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": {
            "stage_key": stage_key,
            "evidence_group": "Pre-unlock evidence packet",
            "item_key": key,
        },
    }


def _packet_report(
    profile: dict[str, Any],
    packet_sections: list[dict[str, object]],
    touchpoint_gap_link_collection: dict[str, Any],
    touchpoint_unlock_matrix_collection: dict[str, Any],
    unlock_phrase_readiness_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_pre_unlock_evidence_packet_index:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "pre_unlock_evidence_packet_index_locked",
        "packet_sections": packet_sections,
        "source_statuses": {
            "touchpoint_gap_links": touchpoint_gap_link_collection.get("status", "missing"),
            "touchpoint_unlock_matrix": touchpoint_unlock_matrix_collection.get("status", "missing"),
            "unlock_phrase_readiness": unlock_phrase_readiness_collection.get("status", "missing"),
        },
        "required_unlock_phrase": unlock_phrase_readiness_collection.get("required_unlock_phrase"),
        "checks": [
            _check("packet_sections_declared", "pass", "Packet sections declared", "The required pre-unlock review sections are indexed."),
            _check("packet_not_accepted", "warn", "Packet not accepted", "The packet index is read-only and does not unlock implementation."),
            _check("authorization_not_accepted", "pass", "Authorization not accepted", "No authorization, phrase, or permission is accepted here."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only indexes already-declared read-only evidence."),
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
        "pre_unlock_evidence_packet_index_only": True,
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
