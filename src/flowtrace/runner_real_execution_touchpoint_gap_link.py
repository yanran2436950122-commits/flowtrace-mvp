from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_TOUCHPOINT_GAP_LINK_VERSION = "project_runner_real_execution_touchpoint_gap_links.v1"
RUNNER_REAL_EXECUTION_TOUCHPOINT_GAP_LINK_SCHEMA_VERSION = "runner_real_execution_touchpoint_gap_link_schema.v1"


def build_project_runner_real_execution_touchpoint_gap_links(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    touchpoint_coverage_index_collection: dict[str, Any],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    link_schema = runner_real_execution_touchpoint_gap_link_schema()
    link_entries = _link_entries(touchpoint_coverage_index_collection, evidence_gap_index_collection)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_GAP_LINK_VERSION,
        "context": project_context,
        "status": "touchpoint_gap_link_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(saved_profiles),
            "link_entry_count": len(link_entries),
            "locked_link_count": sum(1 for item in link_entries if item["current_permission"] == "locked"),
            "linked_gap_count": sum(1 for item in link_entries if item["linked_gap_count"] > 0),
            "coverage_index_status": touchpoint_coverage_index_collection.get("status", "missing"),
            "evidence_gap_status": evidence_gap_index_collection.get("status", "missing"),
            "launchable_count": 0,
        },
        "touchpoint_gap_link_schema": link_schema,
        "link_entries": link_entries,
        "reports": [_link_report(profile, link_entries, evidence_gap_index_collection) for profile in saved_profiles],
        "safety": _safety(),
        "next_action": {
            "title": "Use locked gap links",
            "action": (
                "Use these links to navigate from each real-execution touchpoint to the nearest evidence gap or audit "
                "stage. Do not implement, register, enable, execute, or persist any touchpoint before explicit unlock."
            ),
        },
    }


def runner_real_execution_touchpoint_gap_link_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_GAP_LINK_SCHEMA_VERSION,
        "link_state": {
            "read_only": True,
            "touchpoint_gap_link_only": True,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
        },
        "link_rules": [
            "match touchpoints to evidence gaps by owner stage",
            "fallback to the touchpoint coverage navigation target when no explicit gap exists",
            "keep every touchpoint locked until an explicit unlock round",
        ],
    }


def _link_entries(
    touchpoint_coverage_index_collection: dict[str, Any],
    evidence_gap_index_collection: dict[str, Any],
) -> list[dict[str, object]]:
    evidence_by_stage = _evidence_by_stage(evidence_gap_index_collection)
    entries = [
        item
        for item in touchpoint_coverage_index_collection.get("coverage_entries", [])
        if isinstance(item, dict) and item.get("key")
    ]
    return [_link_entry(item, evidence_by_stage.get(str(item.get("owner_stage_key")), [])) for item in entries]


def _evidence_by_stage(evidence_gap_index_collection: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for report in evidence_gap_index_collection.get("reports", []):
        if not isinstance(report, dict):
            continue
        for entry in report.get("index_entries", []):
            if not isinstance(entry, dict):
                continue
            stage_key = str(entry.get("owner_stage_key") or entry.get("navigation", {}).get("stage_key") or "")
            if stage_key:
                result.setdefault(stage_key, []).append(entry)
    return result


def _link_entry(touchpoint: dict[str, Any], evidence_entries: list[dict[str, Any]]) -> dict[str, object]:
    key = str(touchpoint.get("key") or "")
    owner_stage_key = str(touchpoint.get("owner_stage_key") or "")
    linked = evidence_entries[:3]
    return {
        "key": key,
        "kind": touchpoint.get("kind"),
        "target": touchpoint.get("target"),
        "owner_stage_key": owner_stage_key,
        "fixed_round": touchpoint.get("fixed_round"),
        "blocker_key": touchpoint.get("blocker_key"),
        "linked_gap_count": len(evidence_entries),
        "linked_gaps": [
            {
                "key": item.get("key"),
                "kind": item.get("kind"),
                "title": item.get("title"),
                "status": item.get("status"),
                "navigation": item.get("navigation"),
            }
            for item in linked
        ],
        "current_permission": "locked",
        "can_implement_now": False,
        "can_execute_now": False,
        "navigation": touchpoint.get("navigation"),
    }


def _link_report(
    profile: dict[str, Any],
    link_entries: list[dict[str, object]],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_touchpoint_gap_link:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "touchpoint_gap_link_locked",
        "evidence_gap_index_status": evidence_gap_index_collection.get("status", "missing"),
        "link_entries": link_entries,
        "checks": [
            _check("link_entries_declared", "pass", "Link entries declared", "Known touchpoints are linked to gaps or fallback stage navigation."),
            _check("links_remain_locked", "warn", "Links remain locked", "The link summary does not unlock implementation or execution."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only links in-memory touchpoint and evidence data."),
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
        "touchpoint_gap_link_only": True,
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
        "accepts_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
    }
