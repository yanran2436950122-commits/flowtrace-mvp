from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_TOUCHPOINT_UNLOCK_MATRIX_VERSION = (
    "project_runner_real_execution_touchpoint_unlock_matrices.v1"
)
RUNNER_REAL_EXECUTION_TOUCHPOINT_UNLOCK_MATRIX_SCHEMA_VERSION = (
    "runner_real_execution_touchpoint_unlock_matrix_schema.v1"
)


def build_project_runner_real_execution_touchpoint_unlock_matrices(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    touchpoint_gap_link_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    matrix_schema = runner_real_execution_touchpoint_unlock_matrix_schema()
    matrix_entries = _matrix_entries(touchpoint_gap_link_collection)
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_UNLOCK_MATRIX_VERSION,
        "context": project_context,
        "status": "touchpoint_unlock_matrix_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(saved_profiles),
            "matrix_entry_count": len(matrix_entries),
            "locked_matrix_count": sum(1 for item in matrix_entries if item["current_permission"] == "locked"),
            "implementation_allowed_count": sum(1 for item in matrix_entries if item["can_implement_now"]),
            "execution_allowed_count": sum(1 for item in matrix_entries if item["can_execute_now"]),
            "launchable_count": 0,
            "gap_link_status": touchpoint_gap_link_collection.get("status", "missing"),
        },
        "touchpoint_unlock_matrix_schema": matrix_schema,
        "matrix_entries": matrix_entries,
        "reports": [_matrix_report(profile, matrix_entries, touchpoint_gap_link_collection) for profile in saved_profiles],
        "safety": _safety(),
        "next_action": {
            "title": "Keep unlock matrix locked",
            "action": (
                "Use this matrix to review the exact material and safety conditions required before real execution "
                "implementation. Do not implement, register, enable, execute, or persist any touchpoint before explicit unlock."
            ),
        },
    }


def runner_real_execution_touchpoint_unlock_matrix_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_TOUCHPOINT_UNLOCK_MATRIX_SCHEMA_VERSION,
        "matrix_state": {
            "read_only": True,
            "touchpoint_unlock_matrix_only": True,
            "implementation_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_material_columns": [
            "explicit real-execution unlock statement",
            "accepted low-risk sample project scope",
            "touchpoint-specific implementation plan",
            "touchpoint-specific evidence gap resolution",
            "rollback and audit trail expectation",
        ],
        "required_safety_columns": [
            "no command execution before implementation unlock",
            "no process creation before implementation unlock",
            "no launch/cancel/timeout POST registration before implementation unlock",
            "no adapter import or call before implementation unlock",
            "no stdout/stderr open before implementation unlock",
            "no Runner event, log, audit log, authorization, permission, or user-project write before implementation unlock",
        ],
    }


def _matrix_entries(touchpoint_gap_link_collection: dict[str, Any]) -> list[dict[str, object]]:
    entries = [
        item
        for item in touchpoint_gap_link_collection.get("link_entries", [])
        if isinstance(item, dict) and item.get("key")
    ]
    return [_matrix_entry(item) for item in entries]


def _matrix_entry(touchpoint: dict[str, Any]) -> dict[str, object]:
    key = str(touchpoint.get("key") or "")
    kind = str(touchpoint.get("kind") or "unknown")
    return {
        "key": key,
        "kind": kind,
        "target": touchpoint.get("target"),
        "owner_stage_key": touchpoint.get("owner_stage_key"),
        "fixed_round": touchpoint.get("fixed_round"),
        "blocker_key": touchpoint.get("blocker_key"),
        "required_unlock_materials": _required_unlock_materials(kind, key, touchpoint),
        "required_safety_conditions": _required_safety_conditions(kind, key),
        "current_permission": "locked",
        "can_implement_now": False,
        "can_execute_now": False,
        "requires_future_unlock": True,
        "linked_gap_count": touchpoint.get("linked_gap_count", 0),
        "navigation": touchpoint.get("navigation"),
    }


def _required_unlock_materials(kind: str, key: str, touchpoint: dict[str, Any]) -> list[str]:
    base = [
        "explicit user unlock for real execution implementation",
        "low-risk sample project scope remains accepted",
        "touchpoint evidence gap is resolved or formally accepted",
    ]
    if kind == "file":
        base.append(f"minimal implementation contract for {key}")
    elif kind == "api":
        base.append(f"request, response, idempotency, and error contract for {key}")
    elif kind == "ui":
        base.append(f"disabled-to-enabled UI state transition review for {key}")
    elif kind == "state":
        base.append(f"runtime state ownership and persistence boundary for {key}")
    else:
        base.append(f"touchpoint-specific implementation notes for {key}")
    if int(touchpoint.get("linked_gap_count") or 0) > 0:
        base.append("linked gap evidence reviewed from the touchpoint gap link layer")
    return base


def _required_safety_conditions(kind: str, key: str) -> list[str]:
    common = [
        "implementation_allowed_now is false until explicit unlock",
        "execution_allowed_now is false until explicit unlock",
        "launchable_count remains zero",
        "no command execution, process creation, adapter call, stream open, event write, log write, audit write, authorization acceptance, permission grant, or user-project write",
    ]
    if kind == "api":
        common.append(f"{key} must not be registered as a POST endpoint before unlock")
    if kind == "ui":
        common.append(f"{key} must remain a read-only preview or disabled control before unlock")
    if kind == "file":
        common.append(f"{key} must not create a real execution module before unlock")
    if kind == "state":
        common.append(f"{key} must not mutate runtime session state before unlock")
    return common


def _matrix_report(
    profile: dict[str, Any],
    matrix_entries: list[dict[str, object]],
    touchpoint_gap_link_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_touchpoint_unlock_matrix:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "touchpoint_unlock_matrix_locked",
        "touchpoint_gap_link_status": touchpoint_gap_link_collection.get("status", "missing"),
        "matrix_entries": matrix_entries,
        "checks": [
            _check("matrix_entries_declared", "pass", "Matrix entries declared", "Known touchpoints have unlock materials and safety conditions."),
            _check("implementation_still_locked", "warn", "Implementation remains locked", "The matrix does not unlock implementation or execution."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only derives in-memory unlock requirements."),
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
        "touchpoint_unlock_matrix_only": True,
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
