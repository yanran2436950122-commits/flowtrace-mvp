from __future__ import annotations

from typing import Any


RUNNER_STREAM_CAPTURE_VERSION = "project_runner_stream_captures.v1"
RUNNER_STREAM_CAPTURE_SCHEMA_VERSION = "runner_stream_capture_schema.v1"
MAX_PREVIEW_CHARS = 4096


def build_project_runner_stream_captures(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
    runner_process_lifecycles: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    lifecycle_by_profile = {
        str(report.get("profile_id")): report
        for report in runner_process_lifecycles.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    executions = [
        item
        for item in runner_real_executions.get("executions", [])
        if isinstance(item, dict) and item.get("launch_id") and item.get("profile_id")
    ]
    latest_by_profile: dict[str, dict[str, Any]] = {}
    for execution in executions:
        profile_id = str(execution.get("profile_id") or "")
        if profile_id and profile_id not in latest_by_profile:
            latest_by_profile[profile_id] = execution
    reports = [
        _stream_capture_report(
            profile,
            latest_by_profile.get(str(profile.get("id"))),
            lifecycle_by_profile.get(str(profile.get("id"))),
        )
        for profile in saved_profiles
    ]
    streams = [stream for report in reports for stream in report.get("streams", []) if isinstance(stream, dict)]
    return {
        "schema_version": RUNNER_STREAM_CAPTURE_VERSION,
        "context": project_context,
        "status": _collection_status(reports, saved_profiles),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "stream_count": len(streams),
            "stdout_stream_count": sum(1 for stream in streams if stream.get("stream") == "stdout"),
            "stderr_stream_count": sum(1 for stream in streams if stream.get("stream") == "stderr"),
            "captured_stream_count": sum(1 for stream in streams if stream.get("capture_status") == "captured"),
            "pending_stream_count": sum(1 for stream in streams if stream.get("capture_status") == "pending"),
            "terminal_stream_count": sum(1 for stream in streams if stream.get("terminal")),
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
        },
        "stream_capture_schema": runner_stream_capture_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(reports, saved_profiles),
    }


def runner_stream_capture_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_STREAM_CAPTURE_SCHEMA_VERSION,
        "streams": ["stdout", "stderr"],
        "projection_only": True,
        "max_preview_chars": MAX_PREVIEW_CHARS,
        "implemented_now": {
            "stdout_stderr_path_projection": True,
            "bounded_preview_projection": True,
            "terminal_state_correlation": True,
            "pending_stream_state_for_unlaunched_profiles": True,
        },
        "deferred": {
            "live_stream_open": True,
            "live_stream_read": True,
            "chunk_event_writer": True,
            "redaction_pipeline": True,
            "retention_cleanup": True,
            "cancel_timeout_stream_closure": True,
        },
    }


def _stream_capture_report(
    profile: dict[str, Any],
    latest_execution: dict[str, Any] | None,
    lifecycle_report: dict[str, Any] | None,
) -> dict[str, object]:
    lifecycle_state = {}
    if isinstance(lifecycle_report, dict) and isinstance(lifecycle_report.get("session_state"), dict):
        lifecycle_state = lifecycle_report["session_state"]
    streams = [
        _stream_state("stdout", latest_execution, lifecycle_state),
        _stream_state("stderr", latest_execution, lifecycle_state),
    ]
    has_capture = any(stream["capture_status"] == "captured" for stream in streams)
    return {
        "id": f"runner_stream_capture:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "stream_capture_recorded" if has_capture else "pending_launch",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "lifecycle_status": lifecycle_report.get("status") if isinstance(lifecycle_report, dict) else "missing",
        "session_state": lifecycle_state,
        "latest_execution": latest_execution,
        "streams": streams,
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "execution_record_linked",
                "pass" if latest_execution else "warn",
                "Execution record linkage",
                str(latest_execution.get("launch_id") if latest_execution else "no execution yet"),
            ),
            _check(
                "bounded_preview_projection",
                "pass",
                "Bounded preview projection available",
                f"Previews are capped to {MAX_PREVIEW_CHARS} characters and projected from stored execution records.",
            ),
        ],
    }


def _stream_state(
    stream: str,
    latest_execution: dict[str, Any] | None,
    lifecycle_state: dict[str, Any],
) -> dict[str, object]:
    preview_key = f"{stream}_preview"
    log_key = f"{stream}_log"
    preview = str(latest_execution.get(preview_key) or "") if isinstance(latest_execution, dict) else ""
    log_path = latest_execution.get(log_key) if isinstance(latest_execution, dict) else None
    truncated = len(preview) > MAX_PREVIEW_CHARS
    return {
        "stream": stream,
        "capture_status": "captured" if log_path or preview else "pending",
        "terminal": bool(lifecycle_state.get("terminal")),
        "lifecycle_state": lifecycle_state.get("state") or "pending",
        "launch_id": latest_execution.get("launch_id") if isinstance(latest_execution, dict) else None,
        "log_path": log_path,
        "preview": preview[-MAX_PREVIEW_CHARS:],
        "preview_char_count": min(len(preview), MAX_PREVIEW_CHARS),
        "preview_truncated": truncated,
        "source": "stored_execution_record",
    }


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "stream_capture_recorded" for report in reports):
        return "stream_capture_records_present"
    return "stream_capture_projection_ready"


def _next_action(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> dict[str, object]:
    if not saved_profiles:
        return {
            "title": "Save a run profile first",
            "action": "Stream capture projection appears after a saved profile exists.",
        }
    if any(report.get("status") == "stream_capture_recorded" for report in reports):
        return {
            "title": "Review captured output",
            "action": "Use the stream projection to inspect bounded stdout/stderr previews from minimal launches.",
        }
    return {
        "title": "Launch prerequisites next",
        "action": "Stream projection is ready; captured output appears after a minimal launch completes.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "stream_capture_projection": True,
        "opens_stdout_stderr": False,
        "reads_stdout_stderr": False,
        "captures_stdout_stderr": False,
        "reads_log_files": False,
        "writes_logs": False,
        "writes_runner_events": False,
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
