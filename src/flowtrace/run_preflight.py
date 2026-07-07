from __future__ import annotations

from pathlib import Path
from typing import Any

from .run_confirmation_store import profile_confirmation


RUN_PREFLIGHT_VERSION = "project_run_preflight.v1"


def build_project_run_preflight(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    confirmation_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    reports = [_profile_report(project_context, profile, confirmation_store) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUN_PREFLIGHT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "error_count": sum(1 for report in reports for check in report["checks"] if check["status"] == "error"),
            "warning_count": sum(1 for report in reports for check in report["checks"] if check["status"] == "warn"),
            "pass_count": sum(1 for report in reports for check in report["checks"] if check["status"] == "pass"),
            "confirmed_count": sum(1 for report in reports if report["confirmation"]["status"] == "confirmed"),
            "stale_confirmation_count": sum(1 for report in reports if report["confirmation"]["status"] == "stale"),
        },
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "requires_user_confirmation": True,
            "allows_shell_string": False,
        },
        "next_action": _next_action(status, reports),
    }


def _profile_report(
    project_context: dict[str, Any],
    profile: dict[str, Any],
    confirmation_store: dict[str, object] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_requires_confirmation(profile),
        _check_working_directory(profile),
        _check_argv(profile),
        _check_entry_file(profile),
        _check_trace_dir(project_context, profile),
        _check_no_auto_execute(),
    ]
    status = _report_status(checks)
    return {
        "id": f"preflight:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "mode": profile.get("mode"),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "status": status,
        "status_label": _status_label(status),
        "confirmation": profile_confirmation(profile, confirmation_store),
        "checks": checks,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    return _check(
        "saved_profile",
        "pass" if profile.get("saved_at") else "warn",
        "运行配置已保存" if profile.get("saved_at") else "缺少保存时间",
        str(profile.get("saved_at") or "该配置来自保存区，但缺少 saved_at 元数据。"),
    )


def _check_requires_confirmation(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("requires_confirmation", True):
        return _check("requires_confirmation", "pass", "需要用户确认", "该配置仍处于确认后才能执行的状态。")
    return _check("requires_confirmation", "error", "缺少确认门", "运行配置不得绕过用户确认。")


def _check_working_directory(profile: dict[str, Any]) -> dict[str, object]:
    value = profile.get("working_directory")
    if not isinstance(value, str) or not value.strip():
        return _check("working_directory", "error", "缺少工作目录", "运行命令必须绑定明确工作目录。")
    path = Path(value)
    if path.exists() and path.is_dir():
        return _check("working_directory", "pass", "工作目录存在", str(path))
    return _check("working_directory", "error", "工作目录不存在", str(path))


def _check_argv(profile: dict[str, Any]) -> dict[str, object]:
    mode = profile.get("mode")
    argv = profile.get("argv") if isinstance(profile.get("argv"), list) else []
    if mode == "manual":
        return _check("argv", "warn", "手动触发流程", "该配置需要用户或浏览器录制触发，不应直接执行命令。")
    if not argv:
        return _check("argv", "error", "缺少 argv", "可执行配置必须使用 argv 数组保存命令。")
    if any(not isinstance(item, str) or not item.strip() for item in argv):
        return _check("argv", "error", "argv 包含空参数", "命令参数必须是非空字符串。")
    return _check("argv", "pass", "argv 结构可审查", "命令以参数数组保存，不通过 shell 字符串执行。")


def _check_entry_file(profile: dict[str, Any]) -> dict[str, object]:
    mode = profile.get("mode")
    args = profile.get("args") if isinstance(profile.get("args"), list) else []
    working_directory = profile.get("working_directory")
    if mode != "command" or not args:
        return _check("entry_file", "warn", "无直接入口文件", "该配置不是直接 Python 文件入口。")
    if not isinstance(working_directory, str):
        return _check("entry_file", "error", "无法检查入口文件", "缺少工作目录。")
    entry_file = Path(working_directory) / str(args[0])
    if entry_file.exists() and entry_file.is_file():
        return _check("entry_file", "pass", "入口文件存在", str(entry_file))
    return _check("entry_file", "error", "入口文件不存在", str(entry_file))


def _check_trace_dir(project_context: dict[str, Any], profile: dict[str, Any]) -> dict[str, object]:
    env = profile.get("env") if isinstance(profile.get("env"), dict) else {}
    expected = str(project_context.get("trace_dir") or "")
    actual = str(env.get("FLOWTRACE_DIR") or "")
    if not actual:
        return _check("trace_dir", "error", "缺少 FLOWTRACE_DIR", "运行配置必须显式写入运行记录目录。")
    if expected and Path(actual) != Path(expected):
        return _check("trace_dir", "warn", "运行记录目录与当前上下文不同", f"配置：{actual}；当前：{expected}")
    return _check("trace_dir", "pass", "运行记录目录明确", actual)


def _check_no_auto_execute() -> dict[str, object]:
    return _check("no_auto_execute", "pass", "当前不会自动执行", "预检报告只读，不启动目标项目命令。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if "warn" in statuses:
        return "review"
    return "ready_for_confirmation"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if "review" in statuses:
        return "review"
    return "ready_for_confirmation"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "预检阻断",
        "review": "需要复核",
        "ready_for_confirmation": "可进入用户确认",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置草案",
            "action": "在运行配置草案中选择一个入口并保存，然后再生成执行前预检。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复预检阻断项",
                "action": failed.get("detail") or "修复后重新预检。",
            }
    if status == "review":
        return {
            "title": "人工复核预检警告",
            "action": "确认手动触发流程、trace 目录和入口文件符合预期。",
        }
    return {
        "title": "等待用户确认执行",
        "action": "预检已通过；下一步仍需用户显式确认后才能执行命令。",
    }
