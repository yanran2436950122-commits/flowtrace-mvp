from __future__ import annotations

from typing import Any

from .runner_dry_run_store import runner_dry_run_state


RUNNER_DRY_RUN_VERSION = "project_runner_dry_runs.v1"
RUNNER_DRY_RUN_SCHEMA_VERSION = "runner_dry_run_schema.v1"


def build_project_runner_dry_runs(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    launch_snapshots: dict[str, Any],
    dry_run_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    snapshot_by_profile = {
        str(report.get("profile_id")): report
        for report in launch_snapshots.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _dry_run_report(profile, snapshot_by_profile.get(str(profile.get("id"))), dry_run_store)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_DRY_RUN_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_count": sum(1 for report in reports if report["status"] == "ready_to_prepare"),
            "prepared_count": sum(1 for report in reports if report["dry_run"]["status"] == "prepared"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stale_count": sum(1 for report in reports if report["dry_run"]["status"] == "stale"),
        },
        "dry_run_schema": dry_run_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "dry_run_only": True,
            "launch_enabled": False,
            "dry_run_store_only": True,
            "requires_launch_snapshot": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _dry_run_report(
    profile: dict[str, Any],
    launch_snapshot_report: dict[str, Any] | None,
    dry_run_store: dict[str, object] | None,
) -> dict[str, object]:
    dry_run = runner_dry_run_state(profile, launch_snapshot_report, dry_run_store)
    checks = [
        _check_saved_profile(profile),
        _check_launch_snapshot(launch_snapshot_report),
        _check_dry_run_state(dry_run),
        _check_dry_run_schema(),
        _check_no_execution(),
    ]
    status = _report_status(checks, dry_run)
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report, dict) and isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    return {
        "id": f"runner_dry_run:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_status": snapshot.get("status") or "missing",
        "dry_run": dry_run,
        "checks": checks,
        "preview": _preview(profile, launch_snapshot_report, dry_run),
        "can_prepare": snapshot.get("status") == "snapshotted",
        "can_remove": dry_run.get("status") in {"prepared", "stale"},
        "execution_boundary": "当前只生成 dry-run runner 记录；不会创建进程或执行命令。",
    }


def dry_run_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_DRY_RUN_SCHEMA_VERSION,
        "store_preview_only": True,
        "launch_enabled": False,
        "required_sections": [
            "snapshot",
            "argv_preview",
            "planned_logs",
            "lifecycle_policy",
            "output_policy",
            "safety",
        ],
        "lifecycle_policy": [
            {"state": "created", "meaning": "dry-run 记录已创建，但没有进程。"},
            {"state": "would_start", "meaning": "未来真实 runner 会在这里尝试启动进程。"},
            {"state": "would_stream_output", "meaning": "未来真实 runner 会分片采集 stdout/stderr。"},
            {"state": "would_complete", "meaning": "未来真实 runner 会写 summary 并刷新运行记录。"},
        ],
        "output_policy": [
            {"id": "chunk_stdout", "label": "stdout 必须分片写入，不直接塞入单个事件。"},
            {"id": "chunk_stderr", "label": "stderr 必须分片写入，不直接塞入单个事件。"},
            {"id": "bounded_preview", "label": "前端只展示摘要和尾部预览。"},
            {"id": "no_output_now", "label": "dry-run 阶段不创建 stdout/stderr 文件。"},
        ],
    }


def _preview(
    profile: dict[str, Any],
    launch_snapshot_report: dict[str, Any] | None,
    dry_run: dict[str, object],
) -> dict[str, object]:
    argv = profile.get("argv") if isinstance(profile.get("argv"), list) else []
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report, dict) and isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    return {
        "snapshot_id": snapshot.get("snapshot_id"),
        "argv_count": len(argv),
        "argv_preview": argv[:8],
        "working_directory": profile.get("working_directory"),
        "planned_logs": dry_run.get("planned_logs") if isinstance(dry_run.get("planned_logs"), dict) else {},
        "creates_files_now": False,
        "creates_process_now": False,
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "dry-run runner 只能基于已保存运行配置。")


def _check_launch_snapshot(launch_snapshot_report: dict[str, Any] | None) -> dict[str, object]:
    if not launch_snapshot_report:
        return _check("launch_snapshot", "error", "缺少启动前快照报告", "需要先生成启动前快照。")
    snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
    if snapshot.get("status") == "snapshotted":
        return _check("launch_snapshot", "pass", "启动前快照已生成", str(snapshot.get("created_at") or ""))
    if snapshot.get("status") == "stale":
        return _check("launch_snapshot", "error", "启动前快照已失效", str(snapshot.get("reason") or ""))
    return _check("launch_snapshot", "error", "启动前快照未就绪", "请先生成启动前快照。")


def _check_dry_run_state(dry_run: dict[str, object]) -> dict[str, object]:
    status = dry_run.get("status")
    if status == "prepared":
        return _check("dry_run_state", "pass", "dry-run runner 记录已生成", str(dry_run.get("created_at") or ""))
    if status == "stale":
        return _check("dry_run_state", "error", "dry-run runner 记录已失效", str(dry_run.get("reason") or ""))
    if status == "blocked":
        return _check("dry_run_state", "error", "dry-run runner 被阻断", str(dry_run.get("reason") or ""))
    return _check("dry_run_state", "warn", "尚未生成 dry-run runner 记录", "生成记录仍不会创建进程。")


def _check_dry_run_schema() -> dict[str, object]:
    return _check("dry_run_schema", "pass", "dry-run runner schema 已定义", RUNNER_DRY_RUN_SCHEMA_VERSION)


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只保存 dry-run runner 记录。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], dry_run: dict[str, object]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if dry_run.get("status") == "prepared":
        return "prepared"
    return "ready_to_prepare"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if statuses == {"prepared"}:
        return "prepared"
    return "ready_to_prepare"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "dry-run runner 被阻断",
        "ready_to_prepare": "可生成 dry-run runner 记录",
        "prepared": "dry-run runner 记录已生成",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成启动前快照",
            "action": "完成确认链路、runner 会话草案和启动前快照后，再生成 dry-run runner 记录。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复 dry-run runner 阻断项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    if status == "prepared":
        return {
            "title": "dry-run runner 记录已就绪",
            "action": "下一步可以设计真实 runner 的显式开关；当前仍不会启动命令。",
        }
    return {
        "title": "可以生成 dry-run runner 记录",
        "action": "记录只写入 FlowTrace trace 目录，用于验证 runner 边界和日志策略。",
    }
