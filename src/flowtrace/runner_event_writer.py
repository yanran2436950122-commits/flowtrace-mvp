from __future__ import annotations

from typing import Any


RUNNER_EVENT_WRITER_VERSION = "project_runner_event_writers.v1"
RUNNER_EVENT_WRITER_SCHEMA_VERSION = "runner_event_writer_schema.v1"


def build_project_runner_event_writers(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
    runner_process_lifecycles: dict[str, Any],
    runner_stream_captures: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    executions_by_profile = _latest_by_profile(runner_real_executions.get("executions", []))
    lifecycle_by_profile = _report_by_profile(runner_process_lifecycles.get("reports", []))
    stream_by_profile = _report_by_profile(runner_stream_captures.get("reports", []))
    reports = [
        _event_writer_report(
            profile,
            executions_by_profile.get(str(profile.get("id"))),
            lifecycle_by_profile.get(str(profile.get("id"))),
            stream_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    projected_events = [event for report in reports for event in report.get("events", []) if isinstance(event, dict)]
    return {
        "schema_version": RUNNER_EVENT_WRITER_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "projected_event_count": len(projected_events),
            "pending_event_count": sum(1 for event in projected_events if event.get("event_type") == "runner.pending"),
            "terminal_event_count": sum(1 for event in projected_events if event.get("terminal")),
            "stream_event_count": sum(1 for event in projected_events if str(event.get("event_type", "")).startswith("runner.stream.")),
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
        },
        "event_writer_schema": runner_event_writer_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_event_writer_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EVENT_WRITER_SCHEMA_VERSION,
        "projection_only": True,
        "event_types": [
            "runner.pending",
            "runner.launch.completed",
            "runner.launch.failed",
            "runner.launch.cancelled",
            "runner.launch.timed_out",
            "runner.stream.stdout",
            "runner.stream.stderr",
        ],
        "implemented_now": {
            "event_shape_projection": True,
            "lifecycle_event_projection": True,
            "stream_event_projection": True,
            "terminal_event_projection": True,
        },
        "deferred": {
            "event_log_write": True,
            "append_only_persistence": True,
            "idempotent_retry": True,
            "redaction_pipeline": True,
            "audit_log_linkage": True,
        },
    }


def _event_writer_report(
    profile: dict[str, Any],
    latest_execution: dict[str, Any] | None,
    lifecycle_report: dict[str, Any] | None,
    stream_report: dict[str, Any] | None,
) -> dict[str, object]:
    session_state = lifecycle_report.get("session_state") if isinstance(lifecycle_report, dict) else {}
    streams = stream_report.get("streams") if isinstance(stream_report, dict) else []
    events = _project_events(profile, latest_execution, session_state if isinstance(session_state, dict) else {}, streams)
    has_terminal = any(event.get("terminal") for event in events)
    return {
        "id": f"runner_event_writer:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "event_projection_recorded" if has_terminal else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "latest_execution": latest_execution,
        "session_state": session_state if isinstance(session_state, dict) else {},
        "stream_capture_status": stream_report.get("status") if isinstance(stream_report, dict) else "missing",
        "events": events,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "event_projection_only",
                "pass",
                "Event projection only",
                "Events are UI-readable shapes derived from existing records; no event log is opened or written.",
            ),
            _check(
                "terminal_event_projection",
                "pass" if has_terminal or not latest_execution else "warn",
                "Terminal event projection",
                str(session_state.get("state") or "pending"),
            ),
        ],
    }


def _project_events(
    profile: dict[str, Any],
    latest_execution: dict[str, Any] | None,
    session_state: dict[str, Any],
    streams: Any,
) -> list[dict[str, object]]:
    if not latest_execution:
        return [
            _event(
                profile,
                None,
                "runner.pending",
                session_state.get("state") or "pending",
                False,
                {"reason": "no execution yet"},
            )
        ]
    events: list[dict[str, object]] = []
    for stream in streams if isinstance(streams, list) else []:
        if isinstance(stream, dict) and stream.get("capture_status") == "captured":
            events.append(
                _event(
                    profile,
                    latest_execution,
                    f"runner.stream.{stream.get('stream')}",
                    str(session_state.get("state") or "pending"),
                    False,
                    {
                        "stream": stream.get("stream"),
                        "preview_char_count": stream.get("preview_char_count"),
                        "preview_truncated": stream.get("preview_truncated"),
                        "source": stream.get("source"),
                    },
                )
            )
    state = str(session_state.get("state") or latest_execution.get("status") or "failed")
    terminal_type = {
        "completed": "runner.launch.completed",
        "failed": "runner.launch.failed",
        "cancelled": "runner.launch.cancelled",
        "timed_out": "runner.launch.timed_out",
    }.get(state, "runner.launch.failed")
    events.append(
        _event(
            profile,
            latest_execution,
            terminal_type,
            state,
            True,
            {
                "exit_code": latest_execution.get("exit_code"),
                "started_at": latest_execution.get("started_at"),
                "ended_at": latest_execution.get("ended_at"),
            },
        )
    )
    return events


def _event(
    profile: dict[str, Any],
    execution: dict[str, Any] | None,
    event_type: str,
    lifecycle_state: str,
    terminal: bool,
    payload: dict[str, object],
) -> dict[str, object]:
    launch_id = execution.get("launch_id") if isinstance(execution, dict) else None
    return {
        "event_id": f"{launch_id or profile.get('id')}:{event_type}",
        "profile_id": profile.get("id"),
        "launch_id": launch_id,
        "event_type": event_type,
        "lifecycle_state": lifecycle_state,
        "terminal": terminal,
        "payload": payload,
        "source": "projection_only",
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
    if any(report.get("status") == "event_projection_recorded" for report in reports):
        return "event_projection_records_present"
    return "event_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Event projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "event_projection_recorded" for report in reports):
        return {
            "title": "Review projected events",
            "action": "Use projected runner events to inspect lifecycle and stream event shapes.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Event projection is ready; terminal events appear after a minimal launch completes.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "event_writer_projection": True,
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
        "writes_user_project": False,
        "writes_trace_dir": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
