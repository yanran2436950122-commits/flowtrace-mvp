from __future__ import annotations

from typing import Any


RUNNER_SERVICE_FLAG_AUDIT_VERSION = "project_runner_service_flag_audits.v1"
RUNNER_SERVICE_FLAG_AUDIT_SCHEMA_VERSION = "runner_service_flag_audit_schema.v1"


def build_project_runner_service_flag_audits(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    config_checks: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    config_check_by_profile = {
        str(report.get("profile_id")): report
        for report in config_checks.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _service_flag_audit_report(profile, config_check_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_SERVICE_FLAG_AUDIT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "service_flags_required_count": sum(1 for report in reports if report["status"] == "service_flags_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "service_flag_schema": service_flag_audit_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "service_flag_audit_only": True,
            "reads_environment": False,
            "parses_process_args": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def service_flag_audit_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_SERVICE_FLAG_AUDIT_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "audited_inputs": [
            "runner_execution_config_check_report",
        ],
        "not_inspected_inputs": [
            "process.argv",
            "os.environ",
            "shell history",
            "external supervisor state",
        ],
        "required_future_flags": {
            "server_flag": "--allow-real-execution",
            "environment_flag": "FLOWTRACE_ALLOW_REAL_EXECUTION=1",
            "config_flag": "runner.enable_real_execution=true",
            "typed_consent": "RUN TARGET PROJECT",
        },
        "blocked_actions": [
            "process.spawn",
            "shell command execution",
            "launch POST API registration",
            "config file creation",
            "user project writes",
        ],
    }


def _service_flag_audit_report(
    profile: dict[str, Any],
    config_check_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_config_check(config_check_report),
        _check_server_flag_required(),
        _check_environment_flag_required(),
        _check_launch_api_absent(),
        _check_no_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_service_flag_audit:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "config_check_status": config_check_report.get("status") if isinstance(config_check_report, dict) else "missing",
        "checks": checks,
        "required_flags": service_flag_audit_schema()["required_future_flags"],
        "execution_boundary": "当前只审计未来真实执行所需的服务开关条件；不会读取环境、解析进程参数、创建进程或执行命令。",
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "服务开关审计只能基于已保存运行配置。")


def _check_config_check(config_check_report: dict[str, Any] | None) -> dict[str, object]:
    if not config_check_report:
        return _check("config_check", "error", "缺少配置检查报告", "需要先生成 Runner 配置检查报告。")
    if config_check_report.get("status") in {"config_missing", "config_present_but_launch_disabled"}:
        return _check("config_check", "pass", "配置检查报告已生成", str(config_check_report.get("status")))
    return _check("config_check", "error", "配置检查存在阻塞项", str(config_check_report.get("status") or "unknown"))


def _check_server_flag_required() -> dict[str, object]:
    return _check("server_flag_required", "warn", "仍需服务启动参数", "未来真实执行必须由 --allow-real-execution 显式启用。")


def _check_environment_flag_required() -> dict[str, object]:
    return _check("environment_flag_required", "warn", "仍需环境开关", "未来真实执行必须要求 FLOWTRACE_ALLOW_REAL_EXECUTION=1。")


def _check_launch_api_absent() -> dict[str, object]:
    return _check("launch_api_absent", "pass", "真实启动 API 仍不存在", "当前没有注册真实 launch POST。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只输出服务开关审计报告。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "service_flags_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "service_flags_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "服务开关审计存在阻塞项",
        "service_flags_required": "仍需显式服务开关",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成配置检查",
            "action": "保存运行配置并完成 Runner 配置检查后，再审计服务开关条件。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复服务开关审计阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "仍需显式服务开关",
        "action": "当前只确认真实 launch API 不存在；下一步可继续设计日志目录策略，仍不要启动目标项目。",
    }
