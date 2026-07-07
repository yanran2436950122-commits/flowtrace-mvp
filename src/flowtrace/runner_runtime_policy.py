from __future__ import annotations

from typing import Any


RUNNER_RUNTIME_POLICY_VERSION = "project_runner_runtime_policies.v1"
RUNNER_RUNTIME_POLICY_SCHEMA_VERSION = "runner_runtime_policy_schema.v1"


def build_project_runner_runtime_policies(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    launch_controls: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    control_by_profile = {
        str(report.get("profile_id")): report
        for report in launch_controls.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [_runtime_policy_report(profile, control_by_profile.get(str(profile.get("id")))) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_RUNTIME_POLICY_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_policy_count": sum(1 for report in reports if report["status"] == "ready_but_launch_disabled"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "runtime_schema": runtime_policy_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "runtime_policy_only": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _runtime_policy_report(profile: dict[str, Any], launch_control_report: dict[str, Any] | None) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_launch_control(launch_control_report),
        _check_output_policy(),
        _check_cancellation_policy(),
        _check_completion_policy(),
        _check_no_execution(),
    ]
    status = _report_status(checks, launch_control_report)
    return {
        "id": f"runner_runtime_policy:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "launch_control_status": launch_control_report.get("status") if isinstance(launch_control_report, dict) else "missing",
        "checks": checks,
        "output_policy": output_policy(),
        "cancellation_policy": cancellation_policy(),
        "completion_policy": completion_policy(),
        "execution_boundary": "当前只展示 runner 运行时策略；不会创建进程、文件或执行命令。",
    }


def runtime_policy_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_RUNTIME_POLICY_SCHEMA_VERSION,
        "launch_enabled": False,
        "policy_sections": [
            "output_policy",
            "cancellation_policy",
            "completion_policy",
            "failure_policy",
        ],
    }


def output_policy() -> dict[str, object]:
    return {
        "stdout_chunk_bytes": 4096,
        "stderr_chunk_bytes": 4096,
        "max_stream_bytes": 2 * 1024 * 1024,
        "tail_preview_bytes": 16 * 1024,
        "max_event_payload_bytes": 8192,
        "encoding": "utf-8 with replacement",
        "rules": [
            {"id": "chunk_stdout", "label": "stdout 必须按固定字节块写入事件。"},
            {"id": "chunk_stderr", "label": "stderr 必须按固定字节块写入事件。"},
            {"id": "bounded_stream", "label": "单次运行的 stdout/stderr 总量必须有上限。"},
            {"id": "tail_summary", "label": "前端默认展示尾部摘要，不直接渲染完整日志。"},
            {"id": "no_inline_large_payload", "label": "大型日志不得塞入单个 JSON 事件。"},
        ],
    }


def cancellation_policy() -> dict[str, object]:
    return {
        "default_timeout_seconds": 120,
        "graceful_shutdown_seconds": 5,
        "force_kill_after_seconds": 10,
        "requires_user_cancel_action": True,
        "rules": [
            {"id": "cancel_event", "label": "取消必须写入 runner 事件。"},
            {"id": "timeout_event", "label": "超时必须写入 runner 事件。"},
            {"id": "no_auto_retry", "label": "取消或超时后不得自动重试。"},
            {"id": "preserve_partial_logs", "label": "取消或超时后必须保留已有日志摘要。"},
        ],
    }


def completion_policy() -> dict[str, object]:
    return {
        "refresh_runs_after_completion": True,
        "write_summary_after_completion": True,
        "capture_exit_code": True,
        "capture_duration_ms": True,
        "rules": [
            {"id": "summary_file", "label": "完成、失败、取消和超时都必须写 summary。"},
            {"id": "refresh_run_list", "label": "进程结束后必须刷新运行记录列表。"},
            {"id": "preserve_exit_code", "label": "必须记录退出码或终止原因。"},
            {"id": "no_source_write", "label": "完成刷新不得写用户源码。"},
        ],
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "运行时策略只能基于已保存运行配置。")


def _check_launch_control(launch_control_report: dict[str, Any] | None) -> dict[str, object]:
    if not launch_control_report:
        return _check("launch_control", "error", "缺少启动开关策略", "需要先生成启动开关策略报告。")
    if launch_control_report.get("status") == "disabled_by_policy":
        return _check("launch_control", "pass", "真实执行仍被策略禁用", "运行时策略仅用于未来真实执行审计。")
    return _check("launch_control", "error", "启动开关前置条件未满足", str(launch_control_report.get("status") or "unknown"))


def _check_output_policy() -> dict[str, object]:
    return _check("output_policy", "pass", "输出分片策略已定义", "stdout/stderr 分片、上限和尾部摘要已固定。")


def _check_cancellation_policy() -> dict[str, object]:
    return _check("cancellation_policy", "pass", "取消和超时策略已定义", "取消、超时、强制终止和失败保留日志策略已固定。")


def _check_completion_policy() -> dict[str, object]:
    return _check("completion_policy", "pass", "完成刷新策略已定义", "退出码、耗时、summary 和运行列表刷新策略已固定。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只展示运行时策略。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], launch_control_report: dict[str, Any] | None) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if isinstance(launch_control_report, dict) and launch_control_report.get("status") == "disabled_by_policy":
        return "ready_but_launch_disabled"
    return "blocked"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "ready_but_launch_disabled"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "运行时策略前置条件未满足",
        "ready_but_launch_disabled": "运行时策略已就绪但真实执行禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成启动开关策略",
            "action": "完成 dry-run runner 和启动开关策略后，再查看运行时策略。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复运行时策略阻断项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "运行时策略已就绪",
        "action": "策略已覆盖输出、取消、超时和完成刷新；真实执行仍保持禁用。",
    }
