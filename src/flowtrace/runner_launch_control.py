from __future__ import annotations

from typing import Any


RUNNER_LAUNCH_CONTROL_VERSION = "project_runner_launch_controls.v1"
RUNNER_LAUNCH_CONTROL_SCHEMA_VERSION = "runner_launch_control_schema.v1"


def build_project_runner_launch_controls(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_dry_runs: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    dry_run_by_profile = {
        str(report.get("profile_id")): report
        for report in runner_dry_runs.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [_launch_control_report(profile, dry_run_by_profile.get(str(profile.get("id")))) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LAUNCH_CONTROL_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "disabled_count": sum(1 for report in reports if report["status"] == "disabled_by_policy"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "control_schema": launch_control_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "requires_dry_run": True,
            "requires_future_explicit_enablement": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _launch_control_report(profile: dict[str, Any], dry_run_report: dict[str, Any] | None) -> dict[str, object]:
    dry_run = dry_run_report.get("dry_run") if isinstance(dry_run_report, dict) and isinstance(dry_run_report.get("dry_run"), dict) else {}
    checks = [
        _check_saved_profile(profile),
        _check_dry_run(dry_run_report),
        _check_launch_disabled(),
        _check_future_switches(),
        _check_no_execution(),
    ]
    status = _report_status(checks, dry_run)
    return {
        "id": f"runner_launch_control:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "dry_run_id": dry_run.get("dry_run_id"),
        "dry_run_status": dry_run.get("status") or "missing",
        "switch": {
            "state": "disabled",
            "launch_enabled": False,
            "launch_api_available": False,
            "reason": "真实 runner 启动开关尚未实现；当前阶段只允许审计 dry-run 记录。",
        },
        "checks": checks,
        "future_enablement": launch_control_schema()["future_enablement"],
        "execution_boundary": "当前只展示 runner 启动开关策略；不会创建进程或执行命令。",
    }


def launch_control_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LAUNCH_CONTROL_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "future_enablement": [
            {"id": "config_flag", "label": "配置文件必须显式启用 runner.enable_real_execution=true。"},
            {"id": "server_flag", "label": "服务启动参数必须显式允许真实执行。"},
            {"id": "fresh_dry_run", "label": "必须存在未失效的 dry-run runner 记录。"},
            {"id": "fresh_snapshot", "label": "必须存在未失效的启动前快照。"},
            {"id": "typed_consent", "label": "用户必须输入确认短语，而不是单击按钮。"},
            {"id": "bounded_logs", "label": "stdout/stderr 分片与大小上限必须通过审计。"},
            {"id": "cancel_timeout", "label": "取消、超时和失败清理策略必须通过审计。"},
        ],
        "blocked_actions": [
            "process.spawn",
            "shell command execution",
            "stdout/stderr file creation",
            "user project writes",
        ],
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "启动开关策略只能基于已保存运行配置。")


def _check_dry_run(dry_run_report: dict[str, Any] | None) -> dict[str, object]:
    if not dry_run_report:
        return _check("dry_run", "error", "缺少 dry-run runner 报告", "需要先生成 dry-run runner 记录。")
    dry_run = dry_run_report.get("dry_run") if isinstance(dry_run_report.get("dry_run"), dict) else {}
    if dry_run.get("status") == "prepared":
        return _check("dry_run", "pass", "dry-run runner 记录已生成", str(dry_run.get("created_at") or ""))
    if dry_run.get("status") == "stale":
        return _check("dry_run", "error", "dry-run runner 记录已失效", str(dry_run.get("reason") or ""))
    return _check("dry_run", "error", "dry-run runner 未就绪", "请先生成 dry-run runner 记录。")


def _check_launch_disabled() -> dict[str, object]:
    return _check("launch_disabled", "pass", "真实执行开关保持禁用", "当前没有可调用的真实启动 API。")


def _check_future_switches() -> dict[str, object]:
    return _check("future_switches", "warn", "真实执行仍需额外显式开关", "后续必须实现配置开关、服务开关和输入确认短语。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只展示启动开关策略。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], dry_run: dict[str, object]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if dry_run.get("status") == "prepared":
        return "disabled_by_policy"
    return "blocked"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "disabled_by_policy"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "启动开关前置条件未满足",
        "disabled_by_policy": "真实执行被策略禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成 dry-run runner",
            "action": "完成确认链路、启动前快照和 dry-run runner 后，再查看启动开关策略。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复启动开关前置条件",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "真实执行仍被禁用",
        "action": "下一步只能继续细化日志、取消、超时和显式开关策略；不要直接启动目标项目命令。",
    }
