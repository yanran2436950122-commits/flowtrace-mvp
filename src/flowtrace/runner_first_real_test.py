from __future__ import annotations

from typing import Any


RUNNER_FIRST_REAL_TEST_VERSION = "project_runner_first_real_tests.v1"
RUNNER_FIRST_REAL_TEST_SCHEMA_VERSION = "runner_first_real_test_schema.v1"


def build_project_runner_first_real_tests(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_real_executions: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    executions = [
        item for item in runner_real_executions.get("executions", []) if isinstance(item, dict) and item.get("launch_id")
    ]
    reports = [_report(profile, executions) for profile in saved_profiles]
    completed_reports = [report for report in reports if report["status"] == "first_real_test_completed"]
    failed_reports = [report for report in reports if report["status"] == "first_real_test_failed"]
    return {
        "schema_version": RUNNER_FIRST_REAL_TEST_VERSION,
        "context": project_context,
        "status": _collection_status(saved_profiles, completed_reports, failed_reports),
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "execution_count": len(executions),
            "first_real_test_completed_count": len(completed_reports),
            "first_real_test_failed_count": len(failed_reports),
            "launchable_count": runner_real_executions.get("summary", {}).get("launchable_count", 0),
            "registered_endpoint_count": 0,
        },
        "first_real_test_schema": runner_first_real_test_schema(),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(saved_profiles, completed_reports, failed_reports),
    }


def runner_first_real_test_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_FIRST_REAL_TEST_SCHEMA_VERSION,
        "result_source": "runner_real_executions",
        "requires_existing_launch_record": True,
        "does_not_register_new_endpoint": True,
        "does_not_start_process": True,
        "accepted_terminal_states": ["completed", "failed", "cancelled", "timed_out"],
        "completion_terminal_states": ["completed"],
        "failure_terminal_states": ["failed", "cancelled", "timed_out"],
    }


def _report(profile: dict[str, Any], executions: list[dict[str, Any]]) -> dict[str, object]:
    profile_executions = [
        item for item in executions if str(item.get("profile_id") or "") == str(profile.get("id") or "")
    ]
    latest_execution = profile_executions[0] if profile_executions else None
    status = _report_status(latest_execution)
    return {
        "id": f"runner_first_real_test:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "latest_execution": latest_execution,
        "execution_count": len(profile_executions),
        "checks": [
            _check("saved_profile", "pass", "Saved profile present", str(profile.get("saved_at") or "available")),
            _check(
                "existing_launch_record",
                "pass" if latest_execution else "warn",
                "Existing launch record",
                str(latest_execution.get("launch_id")) if latest_execution else "missing",
            ),
            _check(
                "first_real_test_terminal",
                "pass" if status == "first_real_test_completed" else "warn",
                "First real test terminal state",
                str(latest_execution.get("status")) if latest_execution else "not_started",
            ),
        ],
    }


def _report_status(latest_execution: dict[str, Any] | None) -> str:
    if not latest_execution:
        return "first_real_test_not_started"
    if latest_execution.get("status") == "completed":
        return "first_real_test_completed"
    return "first_real_test_failed"


def _collection_status(
    saved_profiles: list[dict[str, Any]],
    completed_reports: list[dict[str, object]],
    failed_reports: list[dict[str, object]],
) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if completed_reports:
        return "first_real_test_completed"
    if failed_reports:
        return "first_real_test_failed"
    return "first_real_test_not_started"


def _next_action(
    saved_profiles: list[dict[str, Any]],
    completed_reports: list[dict[str, object]],
    failed_reports: list[dict[str, object]],
) -> dict[str, object]:
    if not saved_profiles:
        return {"title": "Save a run profile first", "action": "First real test reporting appears after a profile is saved."}
    if completed_reports:
        return {"title": "First real test recorded", "action": "The minimal low-risk sample launch has a completed result."}
    if failed_reports:
        return {"title": "Review first real test result", "action": "The latest low-risk sample launch reached a non-completed terminal state."}
    return {
        "title": "Run first real test",
        "action": "Use the existing guarded launch path with RUN TARGET PROJECT for one low-risk sample profile.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": True,
        "launch_enabled": True,
        "launch_api_available": True,
        "first_real_test_report": True,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "imports_adapter": False,
        "calls_execution_adapter": False,
        "controls_process": False,
        "cancels_process": False,
        "sends_process_signal": False,
        "kills_process": False,
        "opens_stdout_stderr": False,
        "reads_log_files": False,
        "writes_logs": False,
        "writes_runner_events": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "stores_authorization": False,
        "writes_user_project": False,
    }


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}
