from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_UI_PREVIEW_VERSION = "project_runner_real_test_ui_previews.v1"
RUNNER_REAL_TEST_UI_PREVIEW_SCHEMA_VERSION = "runner_real_test_ui_preview_schema.v1"


def build_project_runner_real_test_ui_previews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_final_checklists: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    checklist_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_final_checklists.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    preview_schema = runner_real_test_ui_preview_schema()
    reports = [
        _ui_preview_report(
            profile,
            checklist_by_profile.get(str(profile.get("id"))),
            preview_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_UI_PREVIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ui_preview_required_count": sum(1 for report in reports if report["status"] == "ui_preview_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "preview_item_count": sum(len(report.get("preview_items", [])) for report in reports),
            "disabled_control_count": sum(len(report.get("disabled_controls", [])) for report in reports),
            "missing_evidence_count": sum(
                1
                for report in reports
                for item in report.get("preview_items", [])
                if item.get("evidence_status") == "missing"
            ),
            "launchable_count": 0,
        },
        "ui_preview_schema": preview_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_test_ui_preview_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_TEST_UI_PREVIEW_SCHEMA_VERSION,
        "preview_state": {
            "read_only": True,
            "renders_preview_now": True,
            "launch_button_enabled_now": False,
            "cancel_button_enabled_now": False,
            "timeout_button_enabled_now": False,
            "can_launch_now": False,
            "requires_future_explicit_authorization": True,
        },
        "preview_sections": [
            _section("command_preview", "Future command and argv preview"),
            _section("working_directory_preview", "Future working directory preview"),
            _section("sandbox_boundary_preview", "Future sandbox and permission boundary preview"),
            _section("log_and_audit_preview", "Future log, event, and audit destination preview"),
            _section("missing_evidence_preview", "Remaining evidence and blocker preview"),
            _section("disabled_controls_preview", "Disabled launch, cancel, and timeout controls"),
        ],
        "disabled_controls": [
            _disabled_control("launch", "Launch", "Real launch remains unavailable."),
            _disabled_control("cancel", "Cancel", "No process exists to cancel."),
            _disabled_control("timeout", "Timeout", "No process exists to time out."),
        ],
        "blocked_actions": [
            "enabling launch button",
            "enabling cancel button",
            "enabling timeout button",
            "registering launch/cancel/timeout POST APIs",
            "starting a target project process",
            "executing commands",
            "calling execution adapters",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _ui_preview_report(
    profile: dict[str, Any],
    final_checklist: dict[str, Any] | None,
    preview_schema: dict[str, object],
) -> dict[str, object]:
    preview_items = _preview_items(preview_schema, profile, final_checklist)
    checks = [
        _check_saved_profile(profile),
        _check_final_checklist(final_checklist),
        _check_preview_sections(preview_items),
        _check_controls_disabled(preview_schema),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_ui_preview:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "final_checklist_status": final_checklist.get("status") if isinstance(final_checklist, dict) else "missing",
        "sandbox_policy_status": (
            final_checklist.get("sandbox_policy_status") if isinstance(final_checklist, dict) else "missing"
        ),
        "authorization_package_status": (
            final_checklist.get("authorization_package_status") if isinstance(final_checklist, dict) else "missing"
        ),
        "authorization_checklist_status": (
            final_checklist.get("authorization_checklist_status") if isinstance(final_checklist, dict) else "missing"
        ),
        "preview_state": preview_schema["preview_state"],
        "preview_items": preview_items,
        "disabled_controls": preview_schema["disabled_controls"],
        "blocked_actions": preview_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only renders a future real-test UI preview. It does not enable launch/cancel/timeout "
            "controls, register POST APIs, execute commands, start processes, call adapters, open stdout/stderr, write "
            "runner events, read/write logs, write audit logs, or modify the user project."
        ),
    }


def _preview_items(
    preview_schema: dict[str, object],
    profile: dict[str, Any],
    final_checklist: dict[str, Any] | None,
) -> list[dict[str, object]]:
    checklist_status = final_checklist.get("status") if isinstance(final_checklist, dict) else "missing"
    values = {
        "command_preview": profile.get("display_command") or "",
        "working_directory_preview": profile.get("working_directory") or "",
        "sandbox_boundary_preview": final_checklist.get("sandbox_policy_status") if isinstance(final_checklist, dict) else "missing",
        "log_and_audit_preview": "future trace directory destinations only",
        "missing_evidence_preview": checklist_status,
        "disabled_controls_preview": "launch/cancel/timeout disabled",
    }
    sections = [item for item in preview_schema.get("preview_sections", []) if isinstance(item, dict)]
    return [
        {
            **section,
            "value": values.get(str(section.get("key")), ""),
            "source_status": checklist_status,
            "evidence_status": "missing",
            "can_execute_now": False,
        }
        for section in sections
    ]


def _section(key: str, title: str) -> dict[str, object]:
    return {"key": key, "title": title}


def _disabled_control(key: str, label: str, reason: str) -> dict[str, object]:
    return {
        "key": key,
        "label": label,
        "enabled_now": False,
        "reason": reason,
        "requires_future_authorization": True,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "UI preview requires a saved run profile.")


def _check_final_checklist(final_checklist: dict[str, Any] | None) -> dict[str, object]:
    if not final_checklist:
        return _check(
            "final_checklist",
            "error",
            "Missing final checklist",
            "Generate the real-test final checklist before the UI preview.",
        )
    if final_checklist.get("status") == "final_checklist_required":
        return _check(
            "final_checklist",
            "pass",
            "Final checklist declared",
            "UI preview can show the future launch surface while keeping controls disabled.",
        )
    return _check(
        "final_checklist",
        "error",
        "Final checklist status is unexpected",
        str(final_checklist.get("status") or "unknown"),
    )


def _check_preview_sections(items: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "command_preview",
        "working_directory_preview",
        "sandbox_boundary_preview",
        "log_and_audit_preview",
        "missing_evidence_preview",
        "disabled_controls_preview",
    }
    present = {str(item.get("key")) for item in items}
    if required.issubset(present):
        return _check("preview_sections_declared", "pass", "UI preview sections declared", "All minimum preview sections are explicit.")
    return _check("preview_sections_declared", "error", "UI preview incomplete", "Missing minimum UI preview sections.")


def _check_controls_disabled(preview_schema: dict[str, object]) -> dict[str, object]:
    state = preview_schema.get("preview_state")
    controls = preview_schema.get("disabled_controls")
    all_disabled = isinstance(controls, list) and controls and all(
        isinstance(item, dict) and not item.get("enabled_now") for item in controls
    )
    if isinstance(state, dict) and not state.get("launch_button_enabled_now") and not state.get("can_launch_now") and all_disabled:
        return _check("controls_disabled", "pass", "Preview controls are disabled", "Launch, cancel, and timeout controls remain disabled.")
    return _check("controls_disabled", "error", "Preview controls enabled", "This layer must not enable real controls.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No UI enablement, command execution, subprocess, adapter call, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "ui_preview_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "ui_preview_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test UI preview is blocked",
        "ui_preview_required": "Real-test UI preview is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and prepare the final checklist before reviewing the UI preview.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix UI preview blocker",
                "action": failed.get("detail") or "Complete the final checklist first.",
            }
    return {
        "title": "UI preview remains disabled",
        "action": "Review the future launch surface; launch, cancel, and timeout controls remain disabled now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "ui_preview_only": True,
        "enables_launch_ui": False,
        "enables_cancel_ui": False,
        "enables_timeout_ui": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "implements_runner": False,
        "imports_adapter": False,
        "calls_execution_adapter": False,
        "creates_session": False,
        "stores_session_state": False,
        "mutates_session_state": False,
        "reads_session_state_store": False,
        "writes_session_state_store": False,
        "opens_stdout_stderr": False,
        "writes_runner_events": False,
        "scans_log_directory": False,
        "reads_log_files": False,
        "writes_logs": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
        "creates_config_file": False,
    }
