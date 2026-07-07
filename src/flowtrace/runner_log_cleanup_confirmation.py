from __future__ import annotations

from typing import Any


RUNNER_LOG_CLEANUP_CONFIRMATION_VERSION = "project_runner_log_cleanup_confirmations.v1"
RUNNER_LOG_CLEANUP_CONFIRMATION_SCHEMA_VERSION = "runner_log_cleanup_confirmation_schema.v1"


def build_project_runner_log_cleanup_confirmations(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    cleanup_previews: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    preview_by_profile = {
        str(report.get("profile_id")): report
        for report in cleanup_previews.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _cleanup_confirmation_report(profile, preview_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_CLEANUP_CONFIRMATION_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "confirmation_required_count": sum(
                1 for report in reports if report["status"] == "cleanup_confirmation_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "confirmed_cleanup_count": 0,
            "launchable_count": 0,
        },
        "cleanup_confirmation_schema": log_cleanup_confirmation_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "cleanup_confirmation_only": True,
            "stores_confirmation": False,
            "scans_log_directory": False,
            "reads_log_files": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "renames_logs": False,
            "truncates_logs": False,
            "writes_logs": False,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def log_cleanup_confirmation_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_CLEANUP_CONFIRMATION_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "confirmation_inputs": [
            "runner_log_cleanup_preview_report",
            "future_candidate_file_manifest",
            "future_user_typed_consent",
        ],
        "not_collected_now": [
            "typed cleanup consent",
            "candidate file acknowledgement",
            "cleanup scope acknowledgement",
            "confirmation persistence record",
        ],
        "required_future_confirmation": {
            "typed_consent": "CONFIRM RUNNER LOG CLEANUP",
            "scope_acknowledgement": "TRACE DIRECTORY ONLY",
            "candidate_manifest_acknowledgement": "I REVIEWED THE CANDIDATE LOG MANIFEST",
            "irreversible_action_acknowledgement": "DELETE OR ROTATE ONLY LISTED RUNNER LOGS",
        },
        "confirmation_gates": [
            "show_candidate_manifest",
            "show_retention_limits",
            "show_rotation_limits",
            "show_risk_warnings",
            "require_typed_consent",
            "require_scope_acknowledgement",
            "require_manifest_acknowledgement",
            "write_confirmation_record_before_cleanup",
        ],
        "blocked_actions": [
            "Path.iterdir",
            "Path.stat",
            "Path.unlink",
            "Path.rename",
            "Path.write_text",
            "open(log_file)",
            "shutil.rmtree",
            "log cleanup execution",
            "launch POST API registration",
        ],
    }


def _cleanup_confirmation_report(
    profile: dict[str, Any],
    cleanup_preview_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_cleanup_preview(cleanup_preview_report),
        _check_confirmation_schema_declared(),
        _check_manifest_required(),
        _check_no_confirmation_storage(),
        _check_no_filesystem_inspection(),
        _check_no_cleanup_mutation(),
    ]
    status = _report_status(checks)
    schema = log_cleanup_confirmation_schema()
    preview_counts = (
        cleanup_preview_report.get("preview_counts", {})
        if isinstance(cleanup_preview_report, dict) and isinstance(cleanup_preview_report.get("preview_counts"), dict)
        else {}
    )
    return {
        "id": f"runner_log_cleanup_confirmation:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "cleanup_preview_status": (
            cleanup_preview_report.get("status") if isinstance(cleanup_preview_report, dict) else "missing"
        ),
        "preview_counts": {
            "candidate_directory_count": preview_counts.get("candidate_directory_count", 0),
            "planned_delete_count": 0,
            "planned_rotate_count": 0,
            "planned_truncate_count": 0,
        },
        "required_future_confirmation": schema["required_future_confirmation"],
        "confirmation_gates": schema["confirmation_gates"],
        "confirmation_state": {
            "status": "not_collected",
            "confirmed": False,
            "stored": False,
            "can_confirm_now": False,
            "reason": "This layer only declares future cleanup confirmation gates.",
        },
        "checks": checks,
        "execution_boundary": (
            "当前只声明未来日志清理确认门槛；不会收集确认、写入确认记录、扫描目录、读取日志、删除日志、"
            "轮转日志、重命名日志、截断日志、写入日志或执行命令。"
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "日志清理确认只能基于已保存运行配置。")


def _check_cleanup_preview(cleanup_preview_report: dict[str, Any] | None) -> dict[str, object]:
    if not cleanup_preview_report:
        return _check("cleanup_preview", "error", "缺少日志清理预览报告", "需要先生成 Runner 日志清理预览报告。")
    if cleanup_preview_report.get("status") == "cleanup_preview_required":
        return _check("cleanup_preview", "pass", "日志清理预览约束已声明", "确认层继续保持只读。")
    return _check("cleanup_preview", "error", "日志清理预览存在阻塞项", str(cleanup_preview_report.get("status") or "unknown"))


def _check_confirmation_schema_declared() -> dict[str, object]:
    return _check("confirmation_schema", "pass", "确认 schema 已声明", "未来真实清理前必须逐项展示确认门槛。")


def _check_manifest_required() -> dict[str, object]:
    return _check("candidate_manifest_required", "pass", "未来必须确认候选清单", "当前不会生成或读取真实候选文件清单。")


def _check_no_confirmation_storage() -> dict[str, object]:
    return _check("no_confirmation_storage", "pass", "当前不保存清理确认", "本层不写入确认记录或任何状态文件。")


def _check_no_filesystem_inspection() -> dict[str, object]:
    return _check("no_filesystem_inspection", "pass", "当前不检查文件系统", "不枚举目录、不读取文件大小、不读取修改时间。")


def _check_no_cleanup_mutation() -> dict[str, object]:
    return _check("no_cleanup_mutation", "pass", "当前不会清理日志", "删除、轮转、重命名、截断和写入均保持禁用。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "cleanup_confirmation_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "cleanup_confirmation_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "日志清理确认存在阻塞项",
        "cleanup_confirmation_required": "仍需日志清理确认约束",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成日志清理预览",
            "action": "保存运行配置并完成 Runner 日志清理预览后，再声明清理确认门槛。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复日志清理确认阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "日志清理确认门槛已声明",
        "action": "下一步只能继续细化确认记录和审计追踪的只读设计；真实扫描、删除、轮转和写入仍保持禁用。",
    }
