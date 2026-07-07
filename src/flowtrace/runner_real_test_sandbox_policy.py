from __future__ import annotations

from typing import Any


RUNNER_REAL_TEST_SANDBOX_POLICY_VERSION = "project_runner_real_test_sandbox_policies.v1"
RUNNER_REAL_TEST_SANDBOX_POLICY_SCHEMA_VERSION = "runner_real_test_sandbox_policy_schema.v1"


def build_project_runner_real_test_sandbox_policies(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    real_test_authorization_packages: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    package_by_profile = {
        str(report.get("profile_id")): report
        for report in real_test_authorization_packages.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    policy_schema = runner_real_test_sandbox_policy_schema(project_context)
    reports = [
        _sandbox_policy_report(
            profile,
            package_by_profile.get(str(profile.get("id"))),
            policy_schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_REAL_TEST_SANDBOX_POLICY_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "sandbox_policy_required_count": sum(1 for report in reports if report["status"] == "sandbox_policy_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "workspace_rule_count": sum(len(report.get("workspace_rules", [])) for report in reports),
            "environment_rule_count": sum(len(report.get("environment_rules", [])) for report in reports),
            "timeout_rule_count": sum(len(report.get("timeout_rules", [])) for report in reports),
            "log_rule_count": sum(len(report.get("log_rules", [])) for report in reports),
            "permission_rule_count": sum(len(report.get("permission_rules", [])) for report in reports),
            "launchable_count": 0,
        },
        "sandbox_policy_schema": policy_schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_real_test_sandbox_policy_schema(project_context: dict[str, Any]) -> dict[str, object]:
    root = str(project_context.get("root") or "")
    trace_dir = str(project_context.get("trace_dir") or "")
    return {
        "schema_version": RUNNER_REAL_TEST_SANDBOX_POLICY_SCHEMA_VERSION,
        "policy_state": {
            "read_only": True,
            "policy_applied_now": False,
            "environment_written_now": False,
            "process_limit_applied_now": False,
            "log_directory_created_now": False,
            "can_launch_now": False,
            "requires_future_explicit_authorization": True,
        },
        "workspace_rules": [
            _rule("working_directory_scope", "Working directory must resolve inside the selected project root.", root),
            _rule("project_root_readonly", "User project files remain read-only until a future authorized execution round.", root),
            _rule("trace_directory_scope", "Runner artifacts must stay inside the configured trace directory.", trace_dir),
        ],
        "environment_rules": [
            _rule("environment_allowlist", "Only explicit allowlisted environment variables may be passed to a target process.", ""),
            _rule("secret_redaction", "Future stdout/stderr and audit payloads must redact configured secret keys.", ""),
            _rule("no_shell_string_expansion", "Future execution requests must use structured argv, not shell-expanded command strings.", ""),
        ],
        "timeout_rules": [
            _rule("startup_timeout", "Future process startup requires a bounded startup timeout.", "30s"),
            _rule("idle_timeout", "Future process output inactivity requires an operator-visible idle timeout.", "120s"),
            _rule("max_runtime", "Future real tests require a maximum runtime before forced terminal handling.", "300s"),
        ],
        "log_rules": [
            _rule("log_directory", "Future runner logs must be written below the trace directory.", trace_dir),
            _rule("append_only_events", "Future runner events must be append-only and schema-versioned.", ""),
            _rule("retention_policy_required", "Future logs require retention and cleanup policy approval before execution.", ""),
        ],
        "permission_rules": [
            _rule("no_network_grant", "No network permission is granted by this policy layer.", ""),
            _rule("no_user_project_write_grant", "No user-project write permission is granted by this policy layer.", ""),
            _rule("no_process_permission_grant", "No process creation permission is granted by this policy layer.", ""),
        ],
        "blocked_actions": [
            "applying sandbox policy",
            "writing environment files",
            "creating log directories",
            "changing filesystem permissions",
            "granting process permissions",
            "starting a target project process",
            "executing commands",
            "opening stdout/stderr streams",
            "writing runner events",
            "writing audit logs",
            "reading or writing log files",
            "writing user project files",
        ],
    }


def _sandbox_policy_report(
    profile: dict[str, Any],
    authorization_package: dict[str, Any] | None,
    policy_schema: dict[str, object],
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_authorization_package(authorization_package),
        _check_policy_sections(policy_schema),
        _check_policy_not_applied(policy_schema),
        _check_no_execution_or_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_real_test_sandbox_policy:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "authorization_package_status": (
            authorization_package.get("status") if isinstance(authorization_package, dict) else "missing"
        ),
        "authorization_checklist_status": (
            authorization_package.get("authorization_checklist_status")
            if isinstance(authorization_package, dict)
            else "missing"
        ),
        "policy_state": policy_schema["policy_state"],
        "workspace_rules": policy_schema["workspace_rules"],
        "environment_rules": policy_schema["environment_rules"],
        "timeout_rules": policy_schema["timeout_rules"],
        "log_rules": policy_schema["log_rules"],
        "permission_rules": policy_schema["permission_rules"],
        "blocked_actions": policy_schema["blocked_actions"],
        "checks": checks,
        "execution_boundary": (
            "Current layer only defines the future real-test sandbox policy. It does not apply filesystem permissions, "
            "write environment files, create log directories, grant process permission, execute commands, start "
            "processes, open stdout/stderr, write runner events, read/write logs, write audit logs, or modify the user "
            "project."
        ),
    }


def _rule(key: str, title: str, value: str) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "value": value,
        "status": "declared",
        "applied_now": False,
        "required_before_real_test": True,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "Saved run profile present", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "Missing saved run profile", "Sandbox policy requires a saved run profile.")


def _check_authorization_package(authorization_package: dict[str, Any] | None) -> dict[str, object]:
    if not authorization_package:
        return _check(
            "authorization_package",
            "error",
            "Missing authorization package",
            "Generate the authorization package before declaring the sandbox policy.",
        )
    if authorization_package.get("status") == "authorization_package_required":
        return _check(
            "authorization_package",
            "pass",
            "Authorization package declared",
            "Sandbox policy can now describe the future authorized execution boundary.",
        )
    return _check(
        "authorization_package",
        "error",
        "Authorization package status is unexpected",
        str(authorization_package.get("status") or "unknown"),
    )


def _check_policy_sections(policy_schema: dict[str, object]) -> dict[str, object]:
    required = {
        "workspace_rules",
        "environment_rules",
        "timeout_rules",
        "log_rules",
        "permission_rules",
    }
    present = {key for key in required if isinstance(policy_schema.get(key), list) and policy_schema.get(key)}
    if required == present:
        return _check("policy_sections_declared", "pass", "Sandbox policy sections declared", "Workspace, environment, timeout, log, and permission rules are explicit.")
    return _check("policy_sections_declared", "error", "Sandbox policy incomplete", "Missing minimum sandbox policy sections.")


def _check_policy_not_applied(policy_schema: dict[str, object]) -> dict[str, object]:
    state = policy_schema.get("policy_state")
    if isinstance(state, dict) and not state.get("policy_applied_now") and not state.get("can_launch_now"):
        return _check("policy_not_applied", "pass", "Sandbox policy is read-only", "No policy, permission, environment, or log directory change is applied.")
    return _check("policy_not_applied", "error", "Sandbox policy was applied", "This layer must remain read-only.")


def _check_no_execution_or_mutation() -> dict[str, object]:
    return _check(
        "no_execution_or_mutation",
        "pass",
        "No execution or mutation",
        "No command execution, subprocess, permission grant, environment write, log directory creation, stream open, runner event write, audit persistence, log access, or user project write occurs.",
    )


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "sandbox_policy_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "sandbox_policy_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved profiles",
        "blocked": "Real-test sandbox policy is blocked",
        "sandbox_policy_required": "Real-test sandbox policy is required",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "Save a run profile first",
            "action": "Save a run profile and prepare the authorization package before reviewing sandbox policy.",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "Fix sandbox policy blocker",
                "action": failed.get("detail") or "Complete the authorization package first.",
            }
    return {
        "title": "Sandbox policy remains read-only",
        "action": "Use these rules as the future real-test isolation contract; no sandbox policy is applied now.",
    }


def _safety() -> dict[str, bool]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "sandbox_policy_only": True,
        "applies_sandbox_policy": False,
        "writes_environment": False,
        "creates_log_directory": False,
        "changes_permissions": False,
        "grants_process_permission": False,
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
        "deletes_logs": False,
        "rotates_logs": False,
        "renames_logs": False,
        "truncates_logs": False,
        "writes_audit_log": False,
        "reads_audit_log": False,
        "collects_human_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
        "writes_user_project": False,
        "creates_config_file": False,
    }
