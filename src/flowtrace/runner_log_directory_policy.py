from __future__ import annotations

from pathlib import Path
from typing import Any


RUNNER_LOG_DIRECTORY_POLICY_VERSION = "project_runner_log_directory_policies.v1"
RUNNER_LOG_DIRECTORY_POLICY_SCHEMA_VERSION = "runner_log_directory_policy_schema.v1"


def build_project_runner_log_directory_policies(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    service_flag_audits: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    service_audit_by_profile = {
        str(report.get("profile_id")): report
        for report in service_flag_audits.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _log_directory_policy_report(profile, project_context, service_audit_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_DIRECTORY_POLICY_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "policy_required_count": sum(1 for report in reports if report["status"] == "log_directory_policy_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "log_directory_schema": log_directory_policy_schema(project_context),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "log_directory_policy_only": True,
            "creates_log_directory": False,
            "opens_log_files": False,
            "writes_logs": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def log_directory_policy_schema(project_context: dict[str, Any]) -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_DIRECTORY_POLICY_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "candidate_root": str(Path(str(project_context.get("trace_dir") or "")) / "runner-logs"),
        "directory_template": "{trace_dir}/runner-logs/{profile_id}/{run_id}",
        "required_future_files": [
            "stdout.log",
            "stderr.log",
            "runner_events.jsonl",
            "summary.json",
        ],
        "path_rules": [
            "logs must stay under trace_dir",
            "profile_id and run_id must be path-segment sanitized",
            "runner must not write logs into user source directories",
            "large stdout and stderr streams must remain bounded by runtime policy",
        ],
        "blocked_actions": [
            "Path.mkdir",
            "open(log_file, write_mode)",
            "event log append",
            "process.spawn",
            "launch POST API registration",
        ],
    }


def _log_directory_policy_report(
    profile: dict[str, Any],
    project_context: dict[str, Any],
    service_audit_report: dict[str, Any] | None,
) -> dict[str, object]:
    candidate = _candidate_directory(project_context, str(profile.get("id") or "unknown-profile"))
    checks = [
        _check_saved_profile(profile),
        _check_service_flag_audit(service_audit_report),
        _check_trace_dir(project_context),
        _check_candidate_under_trace_dir(project_context, candidate),
        _check_no_directory_creation(),
        _check_no_log_writes(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_log_directory_policy:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "service_flag_audit_status": service_audit_report.get("status") if isinstance(service_audit_report, dict) else "missing",
        "candidate_directories": [candidate],
        "required_future_files": log_directory_policy_schema(project_context)["required_future_files"],
        "checks": checks,
        "execution_boundary": (
            "当前只声明未来 runner 日志目录策略；不会创建目录、打开日志文件、写入日志、创建进程或执行命令。"
        ),
    }


def _candidate_directory(project_context: dict[str, Any], profile_id: str) -> str:
    trace_dir = Path(str(project_context.get("trace_dir") or ""))
    return str(trace_dir / "runner-logs" / _sanitize_segment(profile_id) / "{run_id}")


def _sanitize_segment(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("._") or "unknown"


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "日志目录策略只能基于已保存运行配置。")


def _check_service_flag_audit(service_audit_report: dict[str, Any] | None) -> dict[str, object]:
    if not service_audit_report:
        return _check("service_flag_audit", "error", "缺少服务开关审计报告", "需要先生成 Runner 服务开关审计报告。")
    if service_audit_report.get("status") == "service_flags_required":
        return _check("service_flag_audit", "pass", "服务开关审计已生成", "真实执行仍未启用。")
    return _check("service_flag_audit", "error", "服务开关审计存在阻塞项", str(service_audit_report.get("status") or "unknown"))


def _check_trace_dir(project_context: dict[str, Any]) -> dict[str, object]:
    if project_context.get("trace_dir"):
        return _check("trace_dir", "pass", "trace_dir 已声明", str(project_context.get("trace_dir")))
    return _check("trace_dir", "error", "缺少 trace_dir", "日志目录候选位置必须位于 FlowTrace trace_dir 下。")


def _check_candidate_under_trace_dir(project_context: dict[str, Any], candidate: str) -> dict[str, object]:
    trace_dir = str(Path(str(project_context.get("trace_dir") or "")))
    if trace_dir and candidate.startswith(str(Path(trace_dir) / "runner-logs")):
        return _check("candidate_under_trace_dir", "pass", "候选目录位于 trace_dir 下", candidate)
    return _check("candidate_under_trace_dir", "error", "候选目录越界", candidate)


def _check_no_directory_creation() -> dict[str, object]:
    return _check("no_directory_creation", "pass", "当前不会创建日志目录", "本阶段只输出目录策略报告。")


def _check_no_log_writes() -> dict[str, object]:
    return _check("no_log_writes", "pass", "当前不会写入日志", "stdout/stderr/events/summary 均只作为未来文件名要求。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "log_directory_policy_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "log_directory_policy_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "日志目录策略存在阻塞项",
        "log_directory_policy_required": "仍需日志目录策略约束",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成服务开关审计",
            "action": "保存运行配置并完成 Runner 服务开关审计后，再生成日志目录策略。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复日志目录策略阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "日志目录策略已声明",
        "action": "下一步可以继续做日志保留/轮转只读策略；真实执行、目录创建和日志写入仍保持禁用。",
    }
