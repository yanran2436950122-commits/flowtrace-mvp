from __future__ import annotations

from typing import Any


RUNNER_VERIFICATION_DISCREPANCY_REPORT_VERSION = "project_runner_verification_discrepancy_reports.v1"
RUNNER_VERIFICATION_DISCREPANCY_REPORT_SCHEMA_VERSION = "runner_verification_discrepancy_report_schema.v1"


def build_project_runner_verification_discrepancy_reports(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    integrity_replay_verification_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    replay_by_profile = _report_by_profile(integrity_replay_verification_collection.get("reports", []))
    reports = [
        _discrepancy_report(
            profile,
            replay_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    discrepancy_items = [
        item for report in reports for item in report.get("discrepancy_reports", []) if isinstance(item, dict)
    ]
    return {
        "schema_version": RUNNER_VERIFICATION_DISCREPANCY_REPORT_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "discrepancy_report_count": len(discrepancy_items),
            "blocking_decision_count": 0,
            "operator_message_count": sum(1 for item in discrepancy_items if item.get("operator_message")),
            "warning_report_count": sum(1 for item in discrepancy_items if item.get("severity") == "warning"),
            "blocked_report_count": sum(1 for item in discrepancy_items if item.get("severity") == "blocked"),
            "launchable_count": integrity_replay_verification_collection.get("summary", {}).get("launchable_count", 0),
        },
        "discrepancy_report_schema": runner_verification_discrepancy_report_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_verification_discrepancy_report_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_VERIFICATION_DISCREPANCY_REPORT_SCHEMA_VERSION,
        "projection_only": True,
        "report_types": [
            "discrepancy.pending",
            "discrepancy.integrity.blocked",
            "discrepancy.replay.blocked",
            "discrepancy.consistency.blocked",
            "discrepancy.no_issue_preview",
        ],
        "implemented_now": {
            "operator_message_projection": True,
            "machine_readable_report_projection": True,
            "evidence_link_projection": True,
        },
        "deferred": {
            "real_report_file_generation": True,
            "launch_blocking_decision": True,
            "audit_or_event_log_read": True,
            "report_persistence": True,
        },
    }


def _discrepancy_report(profile: dict[str, Any], replay_report: dict[str, Any] | None) -> dict[str, object]:
    integrity_checks = replay_report.get("integrity_checks") if isinstance(replay_report, dict) else []
    replay_checks = replay_report.get("replay_checks") if isinstance(replay_report, dict) else []
    consistency_checks = replay_report.get("consistency_checks") if isinstance(replay_report, dict) else []
    discrepancy_reports = _project_discrepancies(
        profile,
        integrity_checks if isinstance(integrity_checks, list) else [],
        replay_checks if isinstance(replay_checks, list) else [],
        consistency_checks if isinstance(consistency_checks, list) else [],
    )
    has_concrete_report = any(item.get("report_type") != "discrepancy.pending" for item in discrepancy_reports)
    return {
        "id": f"runner_verification_discrepancy_report:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "discrepancy_projection_recorded" if has_concrete_report else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "integrity_replay_status": replay_report.get("status") if isinstance(replay_report, dict) else "missing",
        "discrepancy_reports": discrepancy_reports,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "discrepancy_projection_only",
                "pass",
                "Discrepancy projection only",
                "Discrepancy reports are preview records derived from projected checks; no report file or launch block is created.",
            ),
        ],
    }


def _project_discrepancies(
    profile: dict[str, Any],
    integrity_checks: list[Any],
    replay_checks: list[Any],
    consistency_checks: list[Any],
) -> list[dict[str, object]]:
    all_checks = [
        *[(item, "integrity") for item in integrity_checks if isinstance(item, dict)],
        *[(item, "replay") for item in replay_checks if isinstance(item, dict)],
        *[(item, "consistency") for item in consistency_checks if isinstance(item, dict)],
    ]
    if not all_checks:
        return [
            _report(
                profile,
                "discrepancy.pending",
                "info",
                "No projected verification checks yet.",
                [],
            )
        ]
    blocked = [(item, group) for item, group in all_checks if item.get("status") == "blocked"]
    if not blocked:
        return [
            _report(
                profile,
                "discrepancy.no_issue_preview",
                "info",
                "Projected checks do not indicate a discrepancy.",
                [str(item.get("check_id")) for item, _group in all_checks if item.get("check_id")],
            )
        ]
    return [
        _report(
            profile,
            f"discrepancy.{group}.blocked",
            "warning",
            str(item.get("detail") or "Projected verification check is blocked."),
            [str(item.get("check_id"))] if item.get("check_id") else [],
        )
        for item, group in blocked
    ]


def _report(
    profile: dict[str, Any],
    report_type: str,
    severity: str,
    operator_message: str,
    evidence_ids: list[str],
) -> dict[str, object]:
    return {
        "discrepancy_report_id": f"{profile.get('id')}:{report_type}",
        "profile_id": profile.get("id"),
        "report_type": report_type,
        "severity": severity,
        "operator_message": operator_message,
        "evidence_ids": evidence_ids,
        "source": "projection_only",
        "persisted": False,
        "blocking_decision": False,
        "wrote_report_file": False,
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
    if any(report.get("status") == "discrepancy_projection_recorded" for report in reports):
        return "discrepancy_projection_records_present"
    return "discrepancy_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Discrepancy projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "discrepancy_projection_recorded" for report in reports):
        return {
            "title": "Review projected discrepancy reports",
            "action": "Use projected reports to inspect operator messages and evidence links.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Discrepancy projection is ready; reports appear after projected verification checks exist.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "discrepancy_report_projection": True,
        "opens_audit_log": False,
        "reads_audit_log": False,
        "writes_audit_log": False,
        "reads_audit_records": False,
        "reads_runner_events": False,
        "writes_runner_events": False,
        "opens_runner_event_log": False,
        "writes_event_log": False,
        "reads_config_snapshots": False,
        "performs_integrity_checks": False,
        "performs_replay_checks": False,
        "performs_consistency_checks": False,
        "generates_discrepancy_reports": False,
        "makes_blocking_decisions": False,
        "writes_report_files": False,
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
