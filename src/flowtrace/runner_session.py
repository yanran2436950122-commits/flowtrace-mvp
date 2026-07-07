from __future__ import annotations

from typing import Any

from .runner_session_store import runner_session_state


RUNNER_SESSION_VERSION = "project_runner_sessions.v1"
RUNNER_EVENT_SCHEMA_VERSION = "runner_event_schema.v1"


def build_project_runner_sessions(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_requests: dict[str, Any],
    session_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    request_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_requests.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _runner_session_report(profile, request_by_profile.get(str(profile.get("id"))), session_store)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_SESSION_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_count": sum(1 for report in reports if report["status"] == "ready_to_draft"),
            "drafted_count": sum(1 for report in reports if report["session"]["status"] == "drafted"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stale_count": sum(1 for report in reports if report["session"]["status"] == "stale"),
        },
        "event_schema": runner_event_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "skeleton_only": True,
            "session_store_only": True,
            "requires_second_confirmed_request": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _runner_session_report(
    profile: dict[str, Any],
    execution_report: dict[str, Any] | None,
    session_store: dict[str, object] | None,
) -> dict[str, object]:
    session = runner_session_state(profile, execution_report, session_store)
    checks = [
        _check_saved_profile(profile),
        _check_execution_request(execution_report),
        _check_session_state(session),
        _check_event_schema(),
        _check_no_execution(),
    ]
    status = _report_status(checks, session)
    request = execution_report.get("request") if isinstance(execution_report, dict) and isinstance(execution_report.get("request"), dict) else {}
    return {
        "id": f"runner_session:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "request_id": request.get("request_id"),
        "request_status": request.get("status") or "missing",
        "session": session,
        "checks": checks,
        "can_prepare": request.get("status") == "second_confirmed",
        "can_remove": session.get("status") in {"drafted", "stale"},
        "execution_boundary": "当前只生成 runner 会话草案和事件 schema；不会创建进程或执行命令。",
    }


def runner_event_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EVENT_SCHEMA_VERSION,
        "format": "jsonl",
        "emits_runtime_events_now": False,
        "store_preview_only": True,
        "required_fields": [
            "schema_version",
            "event_id",
            "session_id",
            "profile_id",
            "event_type",
            "created_at",
            "payload",
        ],
        "event_types": [
            {"event_type": "session.created", "phase": "draft", "meaning": "会话草案已创建。"},
            {"event_type": "runner.preflight_snapshotted", "phase": "draft", "meaning": "预检、最终确认和执行请求状态被快照化。"},
            {"event_type": "process.starting", "phase": "future", "meaning": "未来真实 runner 准备启动进程。"},
            {"event_type": "process.running", "phase": "future", "meaning": "未来真实 runner 已进入运行状态。"},
            {"event_type": "stdout.chunk", "phase": "future", "meaning": "未来真实 runner 捕获 stdout 片段。"},
            {"event_type": "stderr.chunk", "phase": "future", "meaning": "未来真实 runner 捕获 stderr 片段。"},
            {"event_type": "process.completed", "phase": "future", "meaning": "未来真实 runner 正常退出。"},
            {"event_type": "process.failed", "phase": "future", "meaning": "未来真实 runner 异常退出。"},
            {"event_type": "process.cancelled", "phase": "future", "meaning": "未来用户取消执行。"},
            {"event_type": "process.timed_out", "phase": "future", "meaning": "未来真实 runner 超时终止。"},
        ],
        "payload_rules": [
            {"id": "argv_array_only", "label": "命令参数必须保留为 argv 数组，不保存 shell 字符串。"},
            {"id": "bounded_output", "label": "stdout/stderr 事件必须截断或分片，避免大日志挤爆前端。"},
            {"id": "trace_dir_only", "label": "runner 自身只写 trace 目录下的 runner 子目录。"},
            {"id": "no_user_source_write", "label": "runner 事件不得写入或修改用户源码。"},
        ],
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "runner 会话草案只能基于已保存运行配置。")


def _check_execution_request(execution_report: dict[str, Any] | None) -> dict[str, object]:
    if not execution_report:
        return _check("execution_request", "error", "缺少执行请求报告", "需要先准备并二次确认执行请求。")
    request = execution_report.get("request") if isinstance(execution_report.get("request"), dict) else {}
    if request.get("status") == "second_confirmed":
        return _check("execution_request", "pass", "执行请求已二次确认", str(request.get("second_confirmed_at") or ""))
    if request.get("status") == "prepared":
        return _check("execution_request", "error", "执行请求尚未二次确认", "生成 runner 会话草案前必须完成二次确认。")
    return _check("execution_request", "error", "执行请求未就绪", "请先完成执行请求草案准备和二次确认。")


def _check_session_state(session: dict[str, object]) -> dict[str, object]:
    status = session.get("status")
    if status == "drafted":
        return _check("session_state", "pass", "runner 会话草案已生成", str(session.get("created_at") or ""))
    if status == "stale":
        return _check("session_state", "error", "runner 会话草案已失效", str(session.get("reason") or ""))
    if status == "blocked":
        return _check("session_state", "error", "runner 会话草案被阻断", str(session.get("reason") or ""))
    return _check("session_state", "warn", "尚未生成 runner 会话草案", "生成草案仍不会创建进程。")


def _check_event_schema() -> dict[str, object]:
    return _check("event_schema", "pass", "runner 事件 schema 已定义", RUNNER_EVENT_SCHEMA_VERSION)


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只保存会话草案和事件 schema 预览。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], session: dict[str, object]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if session.get("status") == "drafted":
        return "drafted"
    return "ready_to_draft"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if statuses == {"drafted"}:
        return "drafted"
    return "ready_to_draft"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "runner 会话草案被阻断",
        "ready_to_draft": "可生成 runner 会话草案",
        "drafted": "runner 会话草案已生成",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成运行配置与执行请求确认",
            "action": "保存运行配置、完成预检、最终确认、执行请求草案和二次确认后，再生成 runner 会话草案。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复 runner 会话阻断项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    if status == "drafted":
        return {
            "title": "runner 会话草案已就绪",
            "action": "下一步可以实现启动前快照和真实 runner API；当前仍不会启动命令。",
        }
    return {
        "title": "可以生成 runner 会话草案",
        "action": "草案只写入 FlowTrace trace 目录，并展示未来 runner 事件结构。",
    }
