from __future__ import annotations

from typing import Any

from .runner_launch_snapshot_store import runner_launch_snapshot_state


RUNNER_LAUNCH_SNAPSHOT_VERSION = "project_runner_launch_snapshots.v1"
RUNNER_LAUNCH_SNAPSHOT_SCHEMA_VERSION = "runner_launch_snapshot_schema.v1"


def build_project_runner_launch_snapshots(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_sessions: dict[str, Any],
    snapshot_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    session_by_profile = {
        str(report.get("profile_id")): report
        for report in runner_sessions.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _launch_snapshot_report(profile, session_by_profile.get(str(profile.get("id"))), snapshot_store)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LAUNCH_SNAPSHOT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_count": sum(1 for report in reports if report["status"] == "ready_to_snapshot"),
            "snapshotted_count": sum(1 for report in reports if report["snapshot"]["status"] == "snapshotted"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stale_count": sum(1 for report in reports if report["snapshot"]["status"] == "stale"),
        },
        "snapshot_schema": launch_snapshot_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "snapshot_store_only": True,
            "requires_runner_session_drafted": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _launch_snapshot_report(
    profile: dict[str, Any],
    runner_session_report: dict[str, Any] | None,
    snapshot_store: dict[str, object] | None,
) -> dict[str, object]:
    snapshot = runner_launch_snapshot_state(profile, runner_session_report, snapshot_store)
    checks = [
        _check_saved_profile(profile),
        _check_runner_session(runner_session_report),
        _check_snapshot_state(snapshot),
        _check_snapshot_schema(),
        _check_no_execution(),
    ]
    status = _report_status(checks, snapshot)
    session = runner_session_report.get("session") if isinstance(runner_session_report, dict) and isinstance(runner_session_report.get("session"), dict) else {}
    return {
        "id": f"runner_launch_snapshot:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "session_id": session.get("session_id"),
        "session_status": session.get("status") or "missing",
        "request_id": runner_session_report.get("request_id") if isinstance(runner_session_report, dict) else None,
        "snapshot": snapshot,
        "checks": checks,
        "evidence": _evidence(profile, runner_session_report),
        "can_prepare": session.get("status") == "drafted",
        "can_remove": snapshot.get("status") in {"snapshotted", "stale"},
        "execution_boundary": "当前只生成启动前快照；不会创建进程或执行命令。",
    }


def launch_snapshot_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LAUNCH_SNAPSHOT_SCHEMA_VERSION,
        "store_preview_only": True,
        "required_sections": [
            "profile",
            "runner_session",
            "execution_request",
            "event_schema",
            "safety",
        ],
        "rules": [
            {"id": "bind_profile", "label": "快照必须绑定已保存运行配置。"},
            {"id": "bind_session", "label": "快照必须绑定已生成 runner 会话草案。"},
            {"id": "bind_request", "label": "快照必须绑定已二次确认的执行请求。"},
            {"id": "freeze_schema", "label": "快照必须记录当前 runner 事件 schema 版本。"},
            {"id": "no_launch", "label": "快照阶段禁止启动目标项目命令。"},
        ],
    }


def _evidence(profile: dict[str, Any], runner_session_report: dict[str, Any] | None) -> dict[str, object]:
    session = runner_session_report.get("session") if isinstance(runner_session_report, dict) and isinstance(runner_session_report.get("session"), dict) else {}
    return {
        "profile": {
            "id": profile.get("id"),
            "label": profile.get("label"),
            "saved_at": profile.get("saved_at"),
            "mode": profile.get("mode"),
            "display_command": profile.get("display_command"),
            "working_directory": profile.get("working_directory"),
            "argv_count": len(profile.get("argv") if isinstance(profile.get("argv"), list) else []),
        },
        "runner_session": {
            "status": session.get("status"),
            "session_id": session.get("session_id"),
            "request_id": session.get("request_id") or (runner_session_report or {}).get("request_id"),
            "created_at": session.get("created_at"),
        },
        "event_schema": {
            "schema_version": "runner_event_schema.v1",
        },
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "launch_enabled": False,
        },
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "启动前快照只能基于已保存运行配置。")


def _check_runner_session(runner_session_report: dict[str, Any] | None) -> dict[str, object]:
    if not runner_session_report:
        return _check("runner_session", "error", "缺少 runner 会话报告", "需要先生成 runner 会话草案。")
    session = runner_session_report.get("session") if isinstance(runner_session_report.get("session"), dict) else {}
    if session.get("status") == "drafted":
        return _check("runner_session", "pass", "runner 会话草案已生成", str(session.get("created_at") or ""))
    if session.get("status") == "stale":
        return _check("runner_session", "error", "runner 会话草案已失效", str(session.get("reason") or ""))
    return _check("runner_session", "error", "runner 会话草案未就绪", "请先生成 runner 会话草案。")


def _check_snapshot_state(snapshot: dict[str, object]) -> dict[str, object]:
    status = snapshot.get("status")
    if status == "snapshotted":
        return _check("snapshot_state", "pass", "启动前快照已生成", str(snapshot.get("created_at") or ""))
    if status == "stale":
        return _check("snapshot_state", "error", "启动前快照已失效", str(snapshot.get("reason") or ""))
    if status == "blocked":
        return _check("snapshot_state", "error", "启动前快照被阻断", str(snapshot.get("reason") or ""))
    return _check("snapshot_state", "warn", "尚未生成启动前快照", "生成快照仍不会创建进程。")


def _check_snapshot_schema() -> dict[str, object]:
    return _check("snapshot_schema", "pass", "启动前快照 schema 已定义", RUNNER_LAUNCH_SNAPSHOT_SCHEMA_VERSION)


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只保存启动前快照。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], snapshot: dict[str, object]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if snapshot.get("status") == "snapshotted":
        return "snapshotted"
    return "ready_to_snapshot"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if statuses == {"snapshotted"}:
        return "snapshotted"
    return "ready_to_snapshot"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "启动前快照被阻断",
        "ready_to_snapshot": "可生成启动前快照",
        "snapshotted": "启动前快照已生成",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成 runner 会话草案",
            "action": "完成运行配置、确认链路、执行请求和 runner 会话草案后，再生成启动前快照。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复启动前快照阻断项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    if status == "snapshotted":
        return {
            "title": "启动前快照已就绪",
            "action": "下一步可以设计 dry-run runner API；当前仍不会启动命令。",
        }
    return {
        "title": "可以生成启动前快照",
        "action": "快照只写入 FlowTrace trace 目录，用于启动前一致性审计。",
    }
