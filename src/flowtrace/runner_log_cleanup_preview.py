from __future__ import annotations

from typing import Any


RUNNER_LOG_CLEANUP_PREVIEW_VERSION = "project_runner_log_cleanup_previews.v1"
RUNNER_LOG_CLEANUP_PREVIEW_SCHEMA_VERSION = "runner_log_cleanup_preview_schema.v1"


def build_project_runner_log_cleanup_previews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    log_retention_policies: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    retention_policy_by_profile = {
        str(report.get("profile_id")): report
        for report in log_retention_policies.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _log_cleanup_preview_report(profile, retention_policy_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_CLEANUP_PREVIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "preview_required_count": sum(1 for report in reports if report["status"] == "cleanup_preview_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "previewed_deletion_count": 0,
            "launchable_count": 0,
        },
        "cleanup_preview_schema": log_cleanup_preview_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "cleanup_preview_only": True,
            "scans_log_directory": False,
            "reads_log_files": False,
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


def log_cleanup_preview_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_CLEANUP_PREVIEW_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "preview_inputs": [
            "runner_log_retention_policy_report",
        ],
        "not_inspected_inputs": [
            "runner log directories",
            "stdout.log",
            "stderr.log",
            "runner_events.jsonl",
            "summary.json",
            "filesystem metadata",
        ],
        "future_preview_sections": [
            "candidate_directories",
            "retention_limits",
            "rotation_limits",
            "cleanup_rules",
            "risk_warnings",
            "required_user_confirmation",
        ],
        "required_future_confirmation": {
            "typed_consent": "PREVIEW RUNNER LOG CLEANUP",
            "scope_acknowledgement": "TRACE DIRECTORY ONLY",
        },
        "blocked_actions": [
            "Path.iterdir",
            "Path.stat",
            "Path.unlink",
            "Path.rename",
            "open(log_file)",
            "shutil.rmtree",
            "log cleanup execution",
            "launch POST API registration",
        ],
    }


def _log_cleanup_preview_report(
    profile: dict[str, Any],
    retention_policy_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_log_retention_policy(retention_policy_report),
        _check_preview_inputs_only(),
        _check_required_confirmation(),
        _check_no_filesystem_inspection(),
        _check_no_cleanup_mutation(),
    ]
    status = _report_status(checks)
    schema = log_cleanup_preview_schema()
    return {
        "id": f"runner_log_cleanup_preview:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "log_retention_policy_status": (
            retention_policy_report.get("status") if isinstance(retention_policy_report, dict) else "missing"
        ),
        "candidate_directories": (
            retention_policy_report.get("candidate_directories", [])
            if isinstance(retention_policy_report, dict)
            else []
        ),
        "retention_limits": (
            retention_policy_report.get("retention_limits", {})
            if isinstance(retention_policy_report, dict)
            else {}
        ),
        "rotation_limits": (
            retention_policy_report.get("rotation_limits", {})
            if isinstance(retention_policy_report, dict)
            else {}
        ),
        "cleanup_rules": (
            retention_policy_report.get("cleanup_rules", [])
            if isinstance(retention_policy_report, dict)
            else []
        ),
        "risk_warnings": risk_warnings(),
        "required_future_confirmation": schema["required_future_confirmation"],
        "preview_counts": {
            "candidate_directory_count": len(
                retention_policy_report.get("candidate_directories", [])
                if isinstance(retention_policy_report, dict)
                else []
            ),
            "planned_delete_count": 0,
            "planned_rotate_count": 0,
            "planned_truncate_count": 0,
        },
        "checks": checks,
        "execution_boundary": (
            "当前只生成未来日志清理预览规则；不会扫描真实目录、读取日志文件、删除日志、轮转日志、截断文件、写入日志或执行命令。"
        ),
    }


def risk_warnings() -> list[dict[str, object]]:
    return [
        {
            "id": "preview_without_fs_scan",
            "severity": "info",
            "message": "当前预览不枚举真实文件，因此不会列出实际可删除文件。",
        },
        {
            "id": "future_cleanup_requires_confirmation",
            "severity": "warning",
            "message": "未来真实清理必须先显示候选文件清单并要求用户确认。",
        },
        {
            "id": "trace_dir_only",
            "severity": "warning",
            "message": "未来清理范围必须限制在 FlowTrace trace_dir 下的 runner 日志目录。",
        },
    ]


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "日志清理预览只能基于已保存运行配置。")


def _check_log_retention_policy(retention_policy_report: dict[str, Any] | None) -> dict[str, object]:
    if not retention_policy_report:
        return _check("log_retention_policy", "error", "缺少日志保留策略报告", "需要先生成 Runner 日志保留/轮转策略报告。")
    if retention_policy_report.get("status") == "log_retention_policy_required":
        return _check("log_retention_policy", "pass", "日志保留策略已声明", "清理预览仍只作为未来约束。")
    return _check("log_retention_policy", "error", "日志保留策略存在阻塞项", str(retention_policy_report.get("status") or "unknown"))


def _check_preview_inputs_only() -> dict[str, object]:
    return _check("preview_inputs_only", "pass", "当前只消费保留策略报告", "不读取日志目录、日志文件或文件系统元数据。")


def _check_required_confirmation() -> dict[str, object]:
    return _check("required_confirmation", "pass", "未来清理需要显式确认", "真实清理前必须先展示候选清单和确认短语。")


def _check_no_filesystem_inspection() -> dict[str, object]:
    return _check("no_filesystem_inspection", "pass", "当前不会检查文件系统", "本阶段不枚举目录、不读取文件大小、不读取修改时间。")


def _check_no_cleanup_mutation() -> dict[str, object]:
    return _check("no_cleanup_mutation", "pass", "当前不会清理日志", "删除、轮转、重命名、截断和写入均保持禁用。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "cleanup_preview_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "cleanup_preview_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "日志清理预览存在阻塞项",
        "cleanup_preview_required": "仍需日志清理预览和确认约束",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成日志保留策略",
            "action": "保存运行配置并完成 Runner 日志保留/轮转策略后，再生成日志清理预览。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复日志清理预览阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "日志清理预览规则已声明",
        "action": "下一步可以继续设计清理确认只读层；真实扫描、删除、轮转和写入仍保持禁用。",
    }
