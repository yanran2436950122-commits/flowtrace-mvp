from __future__ import annotations

from pathlib import Path
from typing import Any


RUNNER_PLAN_VERSION = "project_runner_plan.v1"


def build_project_runner_plan(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_gate: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    gate_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_gate.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [_profile_runner_plan(project_context, profile, gate_by_profile.get(str(profile.get("id")))) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_PLAN_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_count": sum(1 for report in reports if report["status"] == "ready_for_runner_implementation"),
            "blocked_count": sum(1 for report in reports if report["status"].startswith("blocked")),
        },
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "runner_implemented": False,
            "requires_preflight_confirmation": True,
            "requires_final_confirmation": True,
            "writes_user_project": False,
            "planned_trace_writes_only": True,
        },
        "next_action": _next_action(status, reports),
    }


def _profile_runner_plan(
    project_context: dict[str, Any],
    profile: dict[str, Any],
    gate_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_final_gate(gate_report),
        _check_argv(profile),
        _check_working_directory(profile),
        _check_trace_dir(project_context, profile),
        _check_no_runner(),
    ]
    status = _report_status(checks)
    trace_dir = Path(str(project_context.get("trace_dir") or ".flowtrace"))
    return {
        "id": f"runner_plan:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "checks": checks,
        "isolation": _isolation_policy(),
        "lifecycle": _lifecycle_policy(),
        "log_plan": _log_plan(trace_dir, profile),
        "failure_recovery": _failure_recovery_policy(),
        "execution_boundary": "当前只生成 runner 设计报告；不会启动目标项目命令。",
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "runner 只能消费已保存的运行配置。")


def _check_final_gate(gate_report: dict[str, Any] | None) -> dict[str, object]:
    if not gate_report:
        return _check("final_gate", "error", "缺少最终执行确认门", "需要先生成最终执行门报告。")
    confirmation = gate_report.get("final_confirmation") if isinstance(gate_report.get("final_confirmation"), dict) else {}
    if gate_report.get("status") == "final_confirmed" and confirmation.get("status") == "confirmed":
        return _check("final_gate", "pass", "最终执行确认已完成", str(confirmation.get("confirmed_at") or ""))
    return _check("final_gate", "error", "最终执行确认未完成", "runner 实现前必须保留最终确认门。")


def _check_argv(profile: dict[str, Any]) -> dict[str, object]:
    mode = profile.get("mode")
    argv = profile.get("argv") if isinstance(profile.get("argv"), list) else []
    if mode == "manual":
        return _check("argv", "warn", "手动触发流程", "该入口需要浏览器录制或用户操作触发，不能由命令 runner 直接执行。")
    if argv and all(isinstance(item, str) and item.strip() for item in argv):
        return _check("argv", "pass", "argv 可结构化执行", "后续 runner 必须使用 argv 数组，不允许 shell 字符串。")
    return _check("argv", "error", "缺少 argv", "命令 runner 必须只消费结构化 argv。")


def _check_working_directory(profile: dict[str, Any]) -> dict[str, object]:
    value = profile.get("working_directory")
    if not isinstance(value, str) or not value.strip():
        return _check("working_directory", "error", "缺少工作目录", "runner 必须显式绑定工作目录。")
    return _check("working_directory", "pass", "工作目录已绑定", value)


def _check_trace_dir(project_context: dict[str, Any], profile: dict[str, Any]) -> dict[str, object]:
    env = profile.get("env") if isinstance(profile.get("env"), dict) else {}
    expected = str(project_context.get("trace_dir") or "")
    actual = str(env.get("FLOWTRACE_DIR") or "")
    if not actual:
        return _check("trace_dir", "error", "缺少 FLOWTRACE_DIR", "runner 必须把运行日志写入 FlowTrace trace 目录。")
    if expected and Path(actual) != Path(expected):
        return _check("trace_dir", "warn", "运行记录目录不一致", f"配置：{actual}；当前：{expected}")
    return _check("trace_dir", "pass", "运行记录目录已绑定", actual)


def _check_no_runner() -> dict[str, object]:
    return _check("no_runner", "pass", "runner 尚未实现", "当前报告只描述 runner 边界，不创建进程。")


def _isolation_policy() -> list[dict[str, object]]:
    return [
        {"id": "argv_only", "label": "只允许 argv 数组", "required": True},
        {"id": "no_shell_string", "label": "禁止 shell 字符串执行", "required": True},
        {"id": "fixed_cwd", "label": "必须绑定工作目录", "required": True},
        {"id": "trace_dir_only", "label": "FlowTrace 只写运行记录目录", "required": True},
        {"id": "no_source_write", "label": "不得写入用户源码", "required": True},
        {"id": "explicit_timeout", "label": "必须配置超时和取消策略", "required": True},
    ]


def _lifecycle_policy() -> list[dict[str, object]]:
    return [
        {"state": "created", "meaning": "执行请求已创建，但尚未启动进程。"},
        {"state": "starting", "meaning": "进程启动中，尚未产生业务事件。"},
        {"state": "running", "meaning": "目标流程正在运行，持续写入 runner 日志。"},
        {"state": "completed", "meaning": "进程正常退出，并触发运行记录刷新。"},
        {"state": "failed", "meaning": "进程异常退出，保留 stderr/stdout 摘要和退出码。"},
        {"state": "cancelled", "meaning": "用户主动取消，记录取消时间和清理结果。"},
        {"state": "timed_out", "meaning": "超时中断，记录超时阈值和清理结果。"},
    ]


def _log_plan(trace_dir: Path, profile: dict[str, Any]) -> dict[str, object]:
    future_run_id = "<future-run-id>"
    run_dir = trace_dir / "runner" / future_run_id
    return {
        "run_directory": str(run_dir),
        "event_log": str(run_dir / "runner_events.jsonl"),
        "stdout_log": str(run_dir / "stdout.log"),
        "stderr_log": str(run_dir / "stderr.log"),
        "summary_file": str(run_dir / "summary.json"),
        "profile_id": profile.get("id"),
        "creates_files_now": False,
    }


def _failure_recovery_policy() -> list[dict[str, object]]:
    return [
        {"id": "preserve_logs", "label": "失败时保留 runner 日志和退出码。"},
        {"id": "refresh_runs", "label": "执行结束后刷新运行记录列表。"},
        {"id": "no_retry", "label": "失败后不自动重试，必须由用户再次确认。"},
        {"id": "revoke_on_change", "label": "配置变化后最终确认和 runner 计划需要重新生成。"},
    ]


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "ready_for_runner_implementation"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "ready_for_runner_implementation"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "runner 设计前置条件未满足",
        "ready_for_runner_implementation": "可进入 runner 实现设计",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存并确认运行配置",
            "action": "完成运行配置保存、预检确认和最终确认后，再生成 runner 实现计划。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复 runner 前置条件",
                "action": failed.get("detail") or "完成前置确认后再继续。",
            }
    return {
        "title": "可以设计独立 runner",
        "action": "下一步实现 runner 时必须沿用本报告的隔离、日志、生命周期和失败回收策略。",
    }
