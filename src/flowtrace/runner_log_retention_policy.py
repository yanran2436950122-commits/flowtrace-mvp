from __future__ import annotations

from typing import Any


RUNNER_LOG_RETENTION_POLICY_VERSION = "project_runner_log_retention_policies.v1"
RUNNER_LOG_RETENTION_POLICY_SCHEMA_VERSION = "runner_log_retention_policy_schema.v1"


def build_project_runner_log_retention_policies(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    log_directory_policies: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    directory_policy_by_profile = {
        str(report.get("profile_id")): report
        for report in log_directory_policies.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _log_retention_policy_report(profile, directory_policy_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_RETENTION_POLICY_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "policy_required_count": sum(1 for report in reports if report["status"] == "log_retention_policy_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "log_retention_schema": log_retention_policy_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "log_retention_policy_only": True,
            "scans_log_directory": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "renames_logs": False,
            "truncates_logs": False,
            "writes_logs": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def log_retention_policy_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_RETENTION_POLICY_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "retention_limits": {
            "max_retained_runs_per_profile": 20,
            "max_total_profile_log_bytes": 256 * 1024 * 1024,
            "max_single_run_log_bytes": 32 * 1024 * 1024,
            "retain_days": 14,
        },
        "rotation_limits": {
            "stdout_rotate_bytes": 8 * 1024 * 1024,
            "stderr_rotate_bytes": 8 * 1024 * 1024,
            "runner_events_rotate_bytes": 16 * 1024 * 1024,
            "max_rotated_files_per_stream": 4,
        },
        "cleanup_rules": [
            "cleanup must be a future explicit user action",
            "cleanup must stay under runner log candidate directories",
            "cleanup must never touch user source directories",
            "cleanup must preserve latest summary.json per retained run",
            "cleanup must report planned deletions before deleting anything",
        ],
        "blocked_actions": [
            "Path.iterdir",
            "Path.unlink",
            "Path.rename",
            "open(log_file, truncate_mode)",
            "shutil.rmtree",
            "log file deletion",
            "log file rotation",
            "launch POST API registration",
        ],
    }


def _log_retention_policy_report(
    profile: dict[str, Any],
    directory_policy_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_log_directory_policy(directory_policy_report),
        _check_retention_limits(),
        _check_rotation_limits(),
        _check_no_directory_scan(),
        _check_no_cleanup_mutation(),
    ]
    status = _report_status(checks)
    schema = log_retention_policy_schema()
    return {
        "id": f"runner_log_retention_policy:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "log_directory_policy_status": (
            directory_policy_report.get("status") if isinstance(directory_policy_report, dict) else "missing"
        ),
        "candidate_directories": (
            directory_policy_report.get("candidate_directories", [])
            if isinstance(directory_policy_report, dict)
            else []
        ),
        "retention_limits": schema["retention_limits"],
        "rotation_limits": schema["rotation_limits"],
        "cleanup_rules": schema["cleanup_rules"],
        "checks": checks,
        "execution_boundary": (
            "当前只声明未来日志保留和轮转策略；不会扫描目录、删除日志、重命名日志、截断文件、写入日志或执行命令。"
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "日志保留策略只能基于已保存运行配置。")


def _check_log_directory_policy(directory_policy_report: dict[str, Any] | None) -> dict[str, object]:
    if not directory_policy_report:
        return _check("log_directory_policy", "error", "缺少日志目录策略报告", "需要先生成 Runner 日志目录策略报告。")
    if directory_policy_report.get("status") == "log_directory_policy_required":
        return _check("log_directory_policy", "pass", "日志目录策略已声明", "保留和轮转策略仍只作为未来约束。")
    return _check("log_directory_policy", "error", "日志目录策略存在阻塞项", str(directory_policy_report.get("status") or "unknown"))


def _check_retention_limits() -> dict[str, object]:
    return _check("retention_limits", "pass", "保留上限已声明", "保留天数、单次运行大小和每 profile 总量均已固定。")


def _check_rotation_limits() -> dict[str, object]:
    return _check("rotation_limits", "pass", "轮转上限已声明", "stdout/stderr/events 的未来轮转阈值已固定。")


def _check_no_directory_scan() -> dict[str, object]:
    return _check("no_directory_scan", "pass", "当前不会扫描日志目录", "本阶段不枚举目录，也不读取已有日志文件。")


def _check_no_cleanup_mutation() -> dict[str, object]:
    return _check("no_cleanup_mutation", "pass", "当前不会清理或轮转日志", "删除、重命名、截断和写入均保持禁用。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "log_retention_policy_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "log_retention_policy_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "日志保留策略存在阻塞项",
        "log_retention_policy_required": "仍需日志保留和轮转策略约束",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成日志目录策略",
            "action": "保存运行配置并完成 Runner 日志目录策略后，再生成日志保留和轮转策略。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复日志保留策略阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "日志保留和轮转策略已声明",
        "action": "下一步可以继续设计日志清理预览只读层；真实清理、轮转、删除和写入仍保持禁用。",
    }
