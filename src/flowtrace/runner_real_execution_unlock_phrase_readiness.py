from __future__ import annotations

from typing import Any


RUNNER_REAL_EXECUTION_UNLOCK_PHRASE_READINESS_VERSION = (
    "project_runner_real_execution_unlock_phrase_readiness.v1"
)
RUNNER_REAL_EXECUTION_UNLOCK_PHRASE_READINESS_SCHEMA_VERSION = (
    "runner_real_execution_unlock_phrase_readiness_schema.v1"
)
REQUIRED_UNLOCK_PHRASE = "确认解锁真实执行实现，仅限低风险样例项目，按最小实现推进"


def build_project_runner_real_execution_unlock_phrase_readiness(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    touchpoint_unlock_matrix_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    readiness_schema = runner_real_execution_unlock_phrase_readiness_schema()
    reports = [
        _readiness_report(profile, readiness_schema, touchpoint_unlock_matrix_collection)
        for profile in saved_profiles
    ]
    return {
        "schema_version": RUNNER_REAL_EXECUTION_UNLOCK_PHRASE_READINESS_VERSION,
        "context": project_context,
        "status": "unlock_phrase_readiness_locked",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "required_phrase_count": 1,
            "observed_phrase_count": 0,
            "matching_phrase_count": 0,
            "accepted_phrase_count": 0,
            "implementation_allowed_count": 0,
            "execution_allowed_count": 0,
            "launchable_count": 0,
            "touchpoint_unlock_matrix_status": touchpoint_unlock_matrix_collection.get("status", "missing"),
            "touchpoint_unlock_matrix_entry_count": touchpoint_unlock_matrix_collection.get("summary", {}).get(
                "matrix_entry_count",
                0,
            ),
        },
        "unlock_phrase_readiness_schema": readiness_schema,
        "required_unlock_phrase": _required_unlock_phrase(),
        "reports": reports,
        "safety": _safety(),
        "next_action": {
            "title": "Keep explicit unlock phrase unaccepted",
            "action": (
                "Use this read-only layer to display the exact explicit unlock phrase required before round 10. "
                "Do not collect, store, accept, or act on the phrase in this layer."
            ),
        },
    }


def runner_real_execution_unlock_phrase_readiness_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_REAL_EXECUTION_UNLOCK_PHRASE_READINESS_SCHEMA_VERSION,
        "readiness_state": {
            "read_only": True,
            "unlock_phrase_readiness_only": True,
            "collects_phrase_now": False,
            "stores_phrase_now": False,
            "accepts_phrase_now": False,
            "implementation_allowed_now": False,
            "execution_allowed_now": False,
            "launch_allowed_now": False,
        },
        "required_phrase_contract": _required_unlock_phrase(),
        "blocked_actions": [
            "collecting the explicit unlock phrase",
            "storing the explicit unlock phrase",
            "accepting the explicit unlock phrase",
            "granting implementation permission",
            "granting launch permission",
            "writing runner execution implementation",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch/cancel/timeout UI controls",
            "importing or calling execution adapters",
            "creating sessions or processes",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events, logs, audit logs, authorization records, or user project files",
        ],
    }


def _required_unlock_phrase() -> dict[str, object]:
    return {
        "key": "explicit_real_execution_implementation_unlock_phrase",
        "language": "zh-CN",
        "exact_phrase": REQUIRED_UNLOCK_PHRASE,
        "scope": "low-risk sample project only",
        "minimum_implementation_mode": "minimal implementation",
        "accepted_now": False,
        "stored_now": False,
        "matches_now": False,
        "required_before_round": 10,
    }


def _readiness_report(
    profile: dict[str, Any],
    readiness_schema: dict[str, object],
    touchpoint_unlock_matrix_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_real_execution_unlock_phrase_readiness:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "unlock_phrase_readiness_locked",
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "required_unlock_phrase": readiness_schema["required_phrase_contract"],
        "observed_unlock_phrase": None,
        "phrase_observed_now": False,
        "phrase_matches_now": False,
        "phrase_accepted_now": False,
        "implementation_allowed_now": False,
        "execution_allowed_now": False,
        "touchpoint_unlock_matrix_status": touchpoint_unlock_matrix_collection.get("status", "missing"),
        "touchpoint_unlock_matrix_entry_count": touchpoint_unlock_matrix_collection.get("summary", {}).get(
            "matrix_entry_count",
            0,
        ),
        "checks": [
            _check("required_phrase_declared", "pass", "Required phrase declared", "The exact explicit unlock phrase is visible for review."),
            _check("phrase_not_collected", "pass", "Phrase not collected", "This layer does not collect or store phrase input."),
            _check("phrase_not_accepted", "warn", "Phrase not accepted", "Implementation and execution remain locked."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This layer only reports phrase readiness requirements."),
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
        "unlock_phrase_readiness_only": True,
        "collects_unlock_phrase": False,
        "stores_unlock_phrase": False,
        "accepts_unlock_phrase": False,
        "allows_real_execution_implementation": False,
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
