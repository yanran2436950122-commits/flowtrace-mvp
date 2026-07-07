from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_TOUCHPOINT_INVENTORY_VERSION = "project_runner_real_execution_touchpoint_inventories.v1"
RUNNER_REAL_EXECUTION_TOUCHPOINT_INVENTORY_SCHEMA_VERSION = "runner_real_execution_touchpoint_inventory_schema.v1"


def build_project_runner_real_execution_touchpoint_inventories(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    development_path_anchor_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    inventory_schema = runner_real_execution_touchpoint_inventory_schema()
    touchpoints = inventory_schema["touchpoints"]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_INVENTORY_VERSION,
        "context": project_context,
        "status": "touchpoint_inventory_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(saved_profiles),
            "touchpoint_count": len(touchpoints),
            "locked_touchpoint_count": sum(1 for item in touchpoints if item["current_permission"] == "locked"),
            "file_touchpoint_count": _count_kind(touchpoints, "file"),
            "api_touchpoint_count": _count_kind(touchpoints, "api"),
            "ui_touchpoint_count": _count_kind(touchpoints, "ui"),
            "state_touchpoint_count": _count_kind(touchpoints, "state"),
            "path_anchor_status": development_path_anchor_collection.get("status", "missing"),
            "current_phase": development_path_anchor_collection.get("summary", {}).get(
                "current_phase",
                "unknown",
            ),
            "launchable_count": 0,
        },
        "touchpoint_inventory_schema": inventory_schema,
        "reports": [
            _inventory_report(profile, inventory_schema, development_path_anchor_collection)
            for profile in saved_profiles
        ],
        "safety": _safety(),
        "next_action": {
            "title": "Keep touchpoints locked",
            "action": (
                "Use this inventory as the boundary checklist for future real execution work. Do not implement, "
                "register, enable, execute, or persist any listed touchpoint until explicit unlock."
            ),
        },
    }


def runner_real_execution_touchpoint_inventory_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_INVENTORY_SCHEMA_VERSION,
        "inventory_state": {
            "read_only": True,
            "touchpoint_inventory_only": True,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
            "requires_future_unlock": True,
        },
        "touchpoints": [
            _touchpoint("file", "execution_adapter_module", "src/flowtrace/runner_execution_adapter.py"),
            _touchpoint("file", "process_lifecycle_module", "src/flowtrace/runner_process_lifecycle.py"),
            _touchpoint("file", "stream_capture_module", "src/flowtrace/runner_stream_capture.py"),
            _touchpoint("file", "runner_event_writer_module", "src/flowtrace/runner_event_writer.py"),
            _touchpoint("file", "audit_persistence_module", "src/flowtrace/runner_audit_persistence.py"),
            _touchpoint("file", "real_session_store_module", "src/flowtrace/runner_real_session_store.py"),
            _touchpoint("api", "launch_post_api", "POST /api/project/runner/launch"),
            _touchpoint("api", "cancel_post_api", "POST /api/project/runner/cancel"),
            _touchpoint("api", "timeout_post_api", "POST /api/project/runner/timeout"),
            _touchpoint("ui", "launch_button", "Runner workbench launch control"),
            _touchpoint("ui", "cancel_button", "Runner workbench cancel control"),
            _touchpoint("ui", "timeout_button", "Runner workbench timeout control"),
            _touchpoint("ui", "execution_console", "Runner execution console"),
            _touchpoint("state", "session_status", "runner session status transitions"),
            _touchpoint("state", "process_identity", "pid/process-group ownership"),
            _touchpoint("state", "stdout_stderr_tail", "bounded stdout/stderr preview state"),
            _touchpoint("state", "audit_record_id", "real execution audit record linkage"),
            _touchpoint("state", "authorization_snapshot", "human authorization snapshot reference"),
        ],
        "forbidden_actions": [
            "creating listed files as implementation modules",
            "registering listed POST APIs",
            "enabling listed UI controls",
            "creating or mutating listed runtime state",
            "creating or controlling processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events",
            "reading or writing real logs or audit logs",
            "collecting, storing, accepting, or granting authorization",
            "writing user project files",
        ],
    }


def _inventory_report(
    profile: dict[str, Any],
    inventory_schema: dict[str, object],
    development_path_anchor_collection: dict[str, Any],
) -> dict[str, object]:
    touchpoints = inventory_schema["touchpoints"]
    return {
        "id": f"runner_real_execution_touchpoint_inventory:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "touchpoint_inventory_locked",
        "path_anchor_status": development_path_anchor_collection.get("status", "missing"),
        "current_phase": development_path_anchor_collection.get("summary", {}).get("current_phase", "unknown"),
        "touchpoints": touchpoints,
        "checks": [
            _check("path_anchor_present", "pass", "Path anchor is present", "Touchpoint inventory follows the locked development path anchor."),
            _check("touchpoints_declared", "pass", "Touchpoints declared", "Future real execution files, APIs, UI controls, and state fields are explicit."),
            _check("touchpoints_locked", "warn", "Touchpoints remain locked", "Every listed touchpoint requires future explicit unlock before implementation."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer does not create files, register APIs, enable UI, mutate state, execute commands, or write logs."),
        ],
    }


def _touchpoint(kind: str, key: str, target: str) -> dict[str, object]:
    return {
        "kind": kind,
        "key": key,
        "target": target,
        "current_permission": "locked",
        "can_implement_now": False,
        "can_execute_now": False,
        "requires_future_unlock": True,
    }


def _count_kind(touchpoints: list[dict[str, object]], kind: str) -> int:
    return sum(1 for item in touchpoints if item.get("kind") == kind)


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "touchpoint_inventory_only": True,
        "writes_code": False,
        "creates_files": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
        "enables_launch_ui": False,
        "enables_cancel_ui": False,
        "enables_timeout_ui": False,
        "implements_runner": False,
        "implements_adapter": False,
        "imports_adapter": False,
        "calls_execution_adapter": False,
        "creates_session": False,
        "stores_session_state": False,
        "mutates_session_state": False,
        "creates_or_controls_process": False,
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
