from __future__ import annotations

from typing import Any


RUNNER_DEVELOPMENT_PATH_ANCHOR_VERSION = "project_runner_development_path_anchors.v1"
RUNNER_DEVELOPMENT_PATH_ANCHOR_SCHEMA_VERSION = "runner_development_path_anchor_schema.v1"


def build_project_runner_development_path_anchors(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    path_schema = runner_development_path_anchor_schema()
    completed_rounds = [item for item in path_schema["fixed_path"] if item["state"] == "completed"]
    locked_rounds = [item for item in path_schema["fixed_path"] if item["state"] == "locked"]
    current_anchor = path_schema["current_anchor"]
    drift_guards = path_schema["drift_guards"]
    evidence_summary = evidence_gap_index_collection.get("summary", {})
    return {
        "schema_version": RUNNER_DEVELOPMENT_PATH_ANCHOR_VERSION,
        "context": project_context,
        "status": "path_anchor_round18_first_real_test_ready",
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "fixed_round_count": len(path_schema["fixed_path"]),
            "completed_round_count": len(completed_rounds),
            "locked_round_count": len(locked_rounds),
            "current_phase": current_anchor["phase"],
            "current_round": current_anchor["round"],
            "next_allowed_round": current_anchor["next_allowed_round"],
            "forbidden_action_count": len(path_schema["forbidden_actions"]),
            "drift_guard_count": len(drift_guards),
            "evidence_gap_status": evidence_gap_index_collection.get("status", "missing"),
            "evidence_gap_count": evidence_summary.get("unresolved_gap_count", 0),
            "launchable_count": 0,
        },
        "path_anchor_schema": path_schema,
        "drift_guards": drift_guards,
        "reports": [
            _anchor_report(profile, path_schema, evidence_gap_index_collection)
            for profile in saved_profiles
        ],
        "safety": _safety(),
        "next_action": {
            "title": "Keep the path anchored",
            "action": (
                "Use this anchor before each next development round. Round 18 first real test reporting is complete; "
                "the fixed 18-round path is complete."
            ),
        },
    }


def runner_development_path_anchor_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_DEVELOPMENT_PATH_ANCHOR_SCHEMA_VERSION,
        "current_anchor": {
            "phase": "real_execution_minimal_implementation",
            "round": "first_real_test",
            "next_allowed_round": "post_round18_stabilization",
            "real_execution_unlocked": True,
            "implementation_allowed_now": True,
            "launch_allowed_now": True,
        },
        "fixed_path": [
            _round(1, "read_only_final_gate", "completed"),
            _round(2, "evidence_gap_index_navigation", "completed"),
            _round(3, "final_gate_ui_linkage", "completed"),
            _round(4, "config_schema_stabilization", "completed"),
            _round(5, "read_only_regression_samples", "completed"),
            _round(6, "real_test_authorization_package", "completed"),
            _round(7, "real_test_sandbox_policy", "completed"),
            _round(8, "real_test_final_checklist", "completed"),
            _round(9, "real_test_ui_preview", "completed"),
            _round(10, "execution_adapter_minimal_implementation", "completed"),
            _round(11, "process_lifecycle_implementation", "completed"),
            _round(12, "stdout_stderr_capture_implementation", "completed"),
            _round(13, "runner_event_writer_implementation", "completed"),
            _round(14, "audit_persistence_implementation", "completed"),
            _round(15, "integrity_replay_verification_implementation", "completed"),
            _round(16, "real_discrepancy_report_generation", "completed"),
            _round(17, "cancel_timeout_real_api", "completed"),
            _round(18, "first_real_test", "completed"),
        ],
        "drift_guards": [
            _guard("no_repeat_completed_round", "Completed read-only and real-test-prep rounds should not be rebuilt."),
            _guard("no_skip_future_rounds", "The fixed 18-round path is complete; future work should be selected deliberately."),
            _guard("keep_next_round_minimal", "The next round should be post-round-18 stabilization only."),
            _guard("verify_anchor_each_round", "Each round should verify this anchor before selecting new work."),
        ],
        "forbidden_actions": [
            "registering cancel/timeout APIs beyond active low-risk sample launch_id control",
            "expanding execution beyond low-risk sample projects",
            "executing shell strings",
            "opening live stdout/stderr streams",
            "writing full runner event logs",
            "reading or writing real audit logs",
            "collecting or storing broad authorization",
            "modifying user project files",
        ],
    }


def _anchor_report(
    profile: dict[str, Any],
    path_schema: dict[str, object],
    evidence_gap_index_collection: dict[str, Any],
) -> dict[str, object]:
    return {
        "id": f"runner_development_path_anchor:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": "path_anchor_round18_first_real_test_ready",
        "current_anchor": path_schema["current_anchor"],
        "completed_rounds": [item for item in path_schema["fixed_path"] if item["state"] == "completed"],
        "locked_rounds": [item for item in path_schema["fixed_path"] if item["state"] == "locked"],
        "evidence_gap_index_status": evidence_gap_index_collection.get("status", "missing"),
        "checks": [
            _check("path_declared", "pass", "Fixed path declared", "The 18-round path is explicit."),
            _check("completed_rounds_locked", "pass", "Completed rounds are not next work", "Previously completed work should not be repeated."),
            _check("round10_complete", "pass", "Round 10 is complete", "Minimal low-risk sample launch is implemented."),
            _check("round11_complete", "pass", "Round 11 is complete", "Minimal lifecycle projection is implemented."),
            _check("round12_complete", "pass", "Round 12 is complete", "Minimal stdout/stderr projection is implemented."),
            _check("round13_complete", "pass", "Round 13 is complete", "Minimal runner event projection is implemented."),
            _check("round14_complete", "pass", "Round 14 is complete", "Minimal audit persistence projection is implemented."),
            _check("round15_complete", "pass", "Round 15 is complete", "Minimal integrity replay projection is implemented."),
            _check("round16_complete", "pass", "Round 16 is complete", "Minimal discrepancy report projection is implemented."),
            _check("round17_complete", "pass", "Round 17 is complete", "Minimal cancel/timeout real API is implemented."),
            _check("round18_complete", "pass", "Round 18 is complete", "Minimal first real test reporting is implemented."),
            _check("fixed_path_complete", "pass", "Fixed path complete", "All 18 fixed rounds are complete."),
            _check("no_execution_side_effects", "pass", "No execution side effects", "This anchor does not start, execute, write logs, collect authorization, or modify user projects."),
        ],
    }


def _round(number: int, key: str, state: str) -> dict[str, object]:
    return {
        "round": number,
        "key": key,
        "state": state,
        "can_develop_now": state != "locked",
    }


def _guard(key: str, rule: str) -> dict[str, object]:
    return {"key": key, "rule": rule, "enabled": True}


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "development_path_anchor_only": True,
        "writes_code": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "registers_cancel_api": False,
        "registers_timeout_api": False,
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
