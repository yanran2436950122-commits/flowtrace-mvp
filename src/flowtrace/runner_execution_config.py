from __future__ import annotations

from typing import Any


RUNNER_EXECUTION_CONFIG_VERSION = "project_runner_execution_configs.v1"
RUNNER_EXECUTION_CONFIG_SCHEMA_VERSION = "runner_execution_config_schema.v1"


def build_project_runner_execution_configs(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runtime_policies: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    policy_by_profile = {
        str(report.get("profile_id")): report
        for report in runtime_policies.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [_execution_config_report(profile, policy_by_profile.get(str(profile.get("id")))) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EXECUTION_CONFIG_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "configuration_required_count": sum(1 for report in reports if report["status"] == "configuration_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "execution_config_schema": execution_config_schema(project_context),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "execution_config_only": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _execution_config_report(profile: dict[str, Any], runtime_policy_report: dict[str, Any] | None) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_runtime_policy(runtime_policy_report),
        _check_required_config_file(),
        _check_required_server_switch(),
        _check_required_typed_consent(),
        _check_no_execution(),
    ]
    status = _report_status(checks, runtime_policy_report)
    return {
        "id": f"runner_execution_config:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "runtime_policy_status": runtime_policy_report.get("status") if isinstance(runtime_policy_report, dict) else "missing",
        "checks": checks,
        "required_config": execution_requirements(),
        "execution_boundary": "当前只展示未来真实执行所需的显式配置；不会创建进程、写配置文件或执行命令。",
    }


def execution_config_schema(project_context: dict[str, Any]) -> dict[str, object]:
    trace_dir = str(project_context.get("trace_dir") or "")
    return {
        "schema_version": RUNNER_EXECUTION_CONFIG_SCHEMA_VERSION,
        "config_file_name": "flowtrace.runner.json",
        "config_file_location": "目标项目根目录或 FlowTrace trace 目录；当前阶段不自动创建。",
        "suggested_trace_dir": trace_dir,
        "launch_enabled": False,
        "launch_api_available": False,
        "required_sections": [
            "real_execution",
            "process_isolation",
            "log_limits",
            "cancel_timeout",
            "completion_refresh",
        ],
    }


def execution_requirements() -> dict[str, object]:
    return {
        "real_execution": {
            "config_flag": "runner.enable_real_execution=true",
            "server_flag": "--allow-real-execution",
            "environment_flag": "FLOWTRACE_ALLOW_REAL_EXECUTION=1",
            "typed_consent": "RUN TARGET PROJECT",
        },
        "process_isolation": {
            "working_directory_must_match_profile": True,
            "no_shell_string": True,
            "argv_must_be_tokenized": True,
            "inherit_environment": False,
        },
        "log_limits": {
            "stdout_chunk_bytes": 4096,
            "stderr_chunk_bytes": 4096,
            "max_stream_bytes": 2 * 1024 * 1024,
            "tail_preview_bytes": 16 * 1024,
        },
        "cancel_timeout": {
            "default_timeout_seconds": 120,
            "graceful_shutdown_seconds": 5,
            "force_kill_after_seconds": 10,
        },
        "completion_refresh": {
            "refresh_runs_after_completion": True,
            "write_summary_after_completion": True,
            "capture_exit_code": True,
        },
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "执行配置只能基于已保存运行配置。")


def _check_runtime_policy(runtime_policy_report: dict[str, Any] | None) -> dict[str, object]:
    if not runtime_policy_report:
        return _check("runtime_policy", "error", "缺少运行时策略", "需要先生成 Runner 运行时策略。")
    if runtime_policy_report.get("status") == "ready_but_launch_disabled":
        return _check("runtime_policy", "pass", "运行时策略已就绪", "输出、取消、超时和完成刷新策略已定义。")
    return _check("runtime_policy", "error", "运行时策略未就绪", str(runtime_policy_report.get("status") or "unknown"))


def _check_required_config_file() -> dict[str, object]:
    return _check("config_file_required", "warn", "仍需显式配置文件", "未来真实执行必须读取 flowtrace.runner.json。")


def _check_required_server_switch() -> dict[str, object]:
    return _check("server_switch_required", "warn", "仍需服务启动开关", "未来真实执行必须通过服务启动参数显式允许。")


def _check_required_typed_consent() -> dict[str, object]:
    return _check("typed_consent_required", "warn", "仍需输入确认短语", "未来真实执行不能只靠单击按钮触发。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只展示真实执行配置需求。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], runtime_policy_report: dict[str, Any] | None) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if isinstance(runtime_policy_report, dict) and runtime_policy_report.get("status") == "ready_but_launch_disabled":
        return "configuration_required"
    return "blocked"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "configuration_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "执行配置前置条件未满足",
        "configuration_required": "真实执行配置待显式启用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成运行时策略",
            "action": "保存运行配置并完成 dry-run、启动开关和运行时策略后，再查看执行配置需求。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复执行配置前置条件",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "真实执行配置仍需显式启用",
        "action": "配置需求已固化；当前没有写配置、启动进程或开放真实执行 API。",
    }
