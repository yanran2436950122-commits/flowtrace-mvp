from __future__ import annotations

from typing import Any


RUNNER_AUDIT_PERSISTENCE_VERSION = "project_runner_audit_persistences.v1"
RUNNER_AUDIT_PERSISTENCE_SCHEMA_VERSION = "runner_audit_persistence_schema.v1"


def build_project_runner_audit_persistences(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
    runner_process_lifecycles: dict[str, Any],
    runner_stream_captures: dict[str, Any],
    runner_event_writers: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    executions_by_profile = _latest_by_profile(runner_real_executions.get("executions", []))
    lifecycle_by_profile = _report_by_profile(runner_process_lifecycles.get("reports", []))
    stream_by_profile = _report_by_profile(runner_stream_captures.get("reports", []))
    event_by_profile = _report_by_profile(runner_event_writers.get("reports", []))
    reports = [
        _audit_persistence_report(
            profile,
            executions_by_profile.get(str(profile.get("id"))),
            lifecycle_by_profile.get(str(profile.get("id"))),
            stream_by_profile.get(str(profile.get("id"))),
            event_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    audit_records = [
        record for report in reports for record in report.get("audit_records", []) if isinstance(record, dict)
    ]
    return {
        "schema_version": RUNNER_AUDIT_PERSISTENCE_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "audit_record_count": len(audit_records),
            "pending_record_count": sum(1 for record in audit_records if record.get("record_type") == "audit.pending"),
            "terminal_record_count": sum(1 for record in audit_records if record.get("terminal")),
            "audit_write_count": 0,
            "audit_read_count": 0,
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
        },
        "audit_persistence_schema": runner_audit_persistence_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_audit_persistence_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_AUDIT_PERSISTENCE_SCHEMA_VERSION,
        "projection_only": True,
        "record_types": [
            "audit.pending",
            "audit.launch.summary",
            "audit.lifecycle.terminal",
            "audit.stream.summary",
            "audit.event.summary",
        ],
        "implemented_now": {
            "audit_record_shape_projection": True,
            "event_chain_summary_projection": True,
            "stream_summary_projection": True,
            "operator_preview_projection": True,
        },
        "deferred": {
            "audit_log_write": True,
            "append_only_persistence": True,
            "integrity_chain": True,
            "replay_verification": True,
            "retention_policy_enforcement": True,
        },
    }


def _audit_persistence_report(
    profile: dict[str, Any],
    latest_execution: dict[str, Any] | None,
    lifecycle_report: dict[str, Any] | None,
    stream_report: dict[str, Any] | None,
    event_report: dict[str, Any] | None,
) -> dict[str, object]:
    events = event_report.get("events") if isinstance(event_report, dict) else []
    streams = stream_report.get("streams") if isinstance(stream_report, dict) else []
    session_state = lifecycle_report.get("session_state") if isinstance(lifecycle_report, dict) else {}
    audit_records = _project_audit_records(
        profile,
        latest_execution,
        session_state if isinstance(session_state, dict) else {},
        streams if isinstance(streams, list) else [],
        events if isinstance(events, list) else [],
    )
    has_terminal = any(record.get("terminal") for record in audit_records)
    return {
        "id": f"runner_audit_persistence:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "audit_projection_recorded" if has_terminal else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "latest_execution": latest_execution,
        "lifecycle_status": lifecycle_report.get("status") if isinstance(lifecycle_report, dict) else "missing",
        "stream_capture_status": stream_report.get("status") if isinstance(stream_report, dict) else "missing",
        "event_writer_status": event_report.get("status") if isinstance(event_report, dict) else "missing",
        "audit_records": audit_records,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "audit_projection_only",
                "pass",
                "Audit projection only",
                "Audit records are preview shapes derived from existing records; no audit log is opened or written.",
            ),
            _check(
                "terminal_audit_projection",
                "pass" if has_terminal or not latest_execution else "warn",
                "Terminal audit projection",
                str((session_state if isinstance(session_state, dict) else {}).get("state") or "pending"),
            ),
        ],
    }


def _project_audit_records(
    profile: dict[str, Any],
    latest_execution: dict[str, Any] | None,
    session_state: dict[str, Any],
    streams: list[Any],
    events: list[Any],
) -> list[dict[str, object]]:
    if not latest_execution:
        return [
            _audit_record(
                profile,
                None,
                "audit.pending",
                False,
                {"reason": "no execution yet", "event_count": len([event for event in events if isinstance(event, dict)])},
            )
        ]
    stream_items = [stream for stream in streams if isinstance(stream, dict)]
    event_items = [event for event in events if isinstance(event, dict)]
    records = [
        _audit_record(
            profile,
            latest_execution,
            "audit.launch.summary",
            False,
            {
                "status": latest_execution.get("status"),
                "exit_code": latest_execution.get("exit_code"),
                "started_at": latest_execution.get("started_at"),
                "ended_at": latest_execution.get("ended_at"),
            },
        ),
        _audit_record(
            profile,
            latest_execution,
            "audit.lifecycle.terminal",
            True,
            {
                "state": session_state.get("state") or latest_execution.get("status"),
                "terminal": session_state.get("terminal", True),
                "duration_ms": latest_execution.get("duration_ms"),
            },
        ),
        _audit_record(
            profile,
            latest_execution,
            "audit.stream.summary",
            False,
            {
                "stream_count": len(stream_items),
                "captured_stream_count": sum(1 for stream in stream_items if stream.get("capture_status") == "captured"),
                "preview_char_count": sum(int(stream.get("preview_char_count") or 0) for stream in stream_items),
            },
        ),
        _audit_record(
            profile,
            latest_execution,
            "audit.event.summary",
            False,
            {
                "event_count": len(event_items),
                "terminal_event_count": sum(1 for event in event_items if event.get("terminal")),
                "event_types": sorted({str(event.get("event_type")) for event in event_items if event.get("event_type")}),
            },
        ),
    ]
    return records


def _audit_record(
    profile: dict[str, Any],
    execution: dict[str, Any] | None,
    record_type: str,
    terminal: bool,
    payload: dict[str, object],
) -> dict[str, object]:
    launch_id = execution.get("launch_id") if isinstance(execution, dict) else None
    return {
        "audit_record_id": f"{launch_id or profile.get('id')}:{record_type}",
        "profile_id": profile.get("id"),
        "launch_id": launch_id,
        "record_type": record_type,
        "terminal": terminal,
        "payload": payload,
        "source": "projection_only",
        "persisted": False,
    }


def _latest_by_profile(items: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and item.get("profile_id") and str(item.get("profile_id")) not in result:
            result[str(item["profile_id"])] = item
    return result


def _report_by_profile(items: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and item.get("profile_id"):
            result[str(item["profile_id"])] = item
    return result


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "audit_projection_recorded" for report in reports):
        return "audit_projection_records_present"
    return "audit_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Audit projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "audit_projection_recorded" for report in reports):
        return {
            "title": "Review projected audit records",
            "action": "Use projected audit records to inspect launch, lifecycle, stream, and event summaries.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Audit persistence projection is ready; terminal records appear after a minimal launch completes.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "audit_persistence_projection": True,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "opens_audit_log": False,
        "stores_audit_records": False,
        "reads_audit_records": False,
        "writes_runner_events": False,
        "opens_runner_event_log": False,
        "writes_event_log": False,
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
        "grants_permission": False,
        "writes_user_project": False,
        "writes_trace_dir": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
