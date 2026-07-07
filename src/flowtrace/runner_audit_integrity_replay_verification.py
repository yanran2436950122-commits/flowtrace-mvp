from __future__ import annotations

from typing import Any


RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_VERSION = "project_runner_audit_integrity_replay_verifications.v1"
RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_SCHEMA_VERSION = "runner_audit_integrity_replay_verification_schema.v1"


def build_project_runner_audit_integrity_replay_verifications(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_audit_persistences: dict[str, Any],
    runner_event_writers: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    audit_by_profile = _report_by_profile(runner_audit_persistences.get("reports", []))
    event_by_profile = _report_by_profile(runner_event_writers.get("reports", []))
    reports = [
        _integrity_replay_report(
            profile,
            audit_by_profile.get(str(profile.get("id"))),
            event_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    integrity_checks = [
        check for report in reports for check in report.get("integrity_checks", []) if isinstance(check, dict)
    ]
    replay_checks = [check for report in reports for check in report.get("replay_checks", []) if isinstance(check, dict)]
    consistency_checks = [
        check for report in reports for check in report.get("consistency_checks", []) if isinstance(check, dict)
    ]
    return {
        "schema_version": RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "integrity_check_count": len(integrity_checks),
            "replay_check_count": len(replay_checks),
            "consistency_check_count": len(consistency_checks),
            "passed_check_count": sum(
                1
                for check in [*integrity_checks, *replay_checks, *consistency_checks]
                if check.get("status") == "pass"
            ),
            "blocked_check_count": sum(
                1
                for check in [*integrity_checks, *replay_checks, *consistency_checks]
                if check.get("status") == "blocked"
            ),
            "audit_read_count": 0,
            "event_read_count": 0,
            "launchable_count": runner_audit_persistences.get("summary", {}).get("launchable_count", 0),
        },
        "integrity_replay_schema": runner_audit_integrity_replay_verification_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_audit_integrity_replay_verification_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_AUDIT_INTEGRITY_REPLAY_VERIFICATION_SCHEMA_VERSION,
        "projection_only": True,
        "check_groups": [
            "audit_record_integrity",
            "event_replay_sequence",
            "terminal_state_consistency",
        ],
        "implemented_now": {
            "audit_record_reference_projection": True,
            "event_replay_sequence_projection": True,
            "terminal_state_consistency_projection": True,
        },
        "deferred": {
            "audit_log_read": True,
            "event_log_read": True,
            "cryptographic_hashing": True,
            "real_replay_execution": True,
            "discrepancy_report_write": True,
        },
    }


def _integrity_replay_report(
    profile: dict[str, Any],
    audit_report: dict[str, Any] | None,
    event_report: dict[str, Any] | None,
) -> dict[str, object]:
    audit_records = audit_report.get("audit_records") if isinstance(audit_report, dict) else []
    events = event_report.get("events") if isinstance(event_report, dict) else []
    audit_items = [item for item in audit_records if isinstance(item, dict)]
    event_items = [item for item in events if isinstance(item, dict)]
    integrity_checks = _integrity_checks(profile, audit_items)
    replay_checks = _replay_checks(profile, audit_items, event_items)
    consistency_checks = _consistency_checks(profile, audit_items, event_items)
    all_checks = [*integrity_checks, *replay_checks, *consistency_checks]
    return {
        "id": f"runner_audit_integrity_replay_verification:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "integrity_replay_projection_recorded" if any(check["status"] == "pass" for check in all_checks) else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "audit_persistence_status": audit_report.get("status") if isinstance(audit_report, dict) else "missing",
        "event_writer_status": event_report.get("status") if isinstance(event_report, dict) else "missing",
        "integrity_checks": integrity_checks,
        "replay_checks": replay_checks,
        "consistency_checks": consistency_checks,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "integrity_replay_projection_only",
                "pass",
                "Integrity replay projection only",
                "Checks are derived from in-memory projection records; no audit/event/log file is opened or read.",
            ),
        ],
    }


def _integrity_checks(profile: dict[str, Any], audit_records: list[dict[str, Any]]) -> list[dict[str, object]]:
    if not audit_records:
        return [_projected_check(profile, "audit_record_integrity", "pending", "No projected audit records yet.")]
    return [
        _projected_check(
            profile,
            "audit_record_integrity",
            "pass" if record.get("audit_record_id") and record.get("persisted") is False else "blocked",
            str(record.get("audit_record_id") or "missing audit record id"),
        )
        for record in audit_records
    ]


def _replay_checks(
    profile: dict[str, Any],
    audit_records: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> list[dict[str, object]]:
    if not audit_records:
        return [_projected_check(profile, "event_replay_sequence", "pending", "No projected audit records yet.")]
    terminal_events = [event for event in events if event.get("terminal")]
    terminal_records = [record for record in audit_records if record.get("terminal")]
    return [
        _projected_check(
            profile,
            "event_replay_sequence",
            "pass" if terminal_events or not terminal_records else "blocked",
            f"terminal_events={len(terminal_events)} terminal_records={len(terminal_records)}",
        )
    ]


def _consistency_checks(
    profile: dict[str, Any],
    audit_records: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> list[dict[str, object]]:
    if not audit_records:
        return [_projected_check(profile, "terminal_state_consistency", "pending", "No projected audit records yet.")]
    audit_launch_ids = {str(record.get("launch_id")) for record in audit_records if record.get("launch_id")}
    event_launch_ids = {str(event.get("launch_id")) for event in events if event.get("launch_id")}
    return [
        _projected_check(
            profile,
            "terminal_state_consistency",
            "pass" if not audit_launch_ids or audit_launch_ids.issubset(event_launch_ids or audit_launch_ids) else "blocked",
            f"audit_launch_ids={len(audit_launch_ids)} event_launch_ids={len(event_launch_ids)}",
        )
    ]


def _projected_check(profile: dict[str, Any], check_type: str, status: str, detail: str) -> dict[str, object]:
    return {
        "check_id": f"{profile.get('id')}:{check_type}",
        "profile_id": profile.get("id"),
        "check_type": check_type,
        "status": status,
        "detail": detail,
        "source": "projection_only",
        "read_from_log": False,
        "wrote_report": False,
    }


def _report_by_profile(items: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and item.get("profile_id"):
            result[str(item["profile_id"])] = item
    return result


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "integrity_replay_projection_recorded" for report in reports):
        return "integrity_replay_projection_records_present"
    return "integrity_replay_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Integrity replay projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "integrity_replay_projection_recorded" for report in reports):
        return {
            "title": "Review projected replay checks",
            "action": "Use projected checks to inspect audit record references, replay sequence, and terminal consistency.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Integrity replay projection is ready; concrete checks appear after a minimal launch completes.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "integrity_replay_projection": True,
        "opens_audit_log": False,
        "reads_audit_log": False,
        "writes_audit_log": False,
        "reads_audit_records": False,
        "stores_audit_records": False,
        "reads_runner_events": False,
        "writes_runner_events": False,
        "opens_runner_event_log": False,
        "writes_event_log": False,
        "reads_config_snapshots": False,
        "performs_integrity_checks": False,
        "performs_replay_checks": False,
        "performs_consistency_checks": False,
        "reads_log_files": False,
        "writes_logs": False,
        "opens_stdout_stderr": False,
        "reads_stdout_stderr": False,
        "controls_process": False,
        "cancels_process": False,
        "schedules_timeout": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "stores_authorization": False,
        "writes_user_project": False,
        "writes_trace_dir": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
