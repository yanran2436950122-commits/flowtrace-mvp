from __future__ import annotations

from typing import Any


RUNNER_LOG_CLEANUP_AUDIT_TRAIL_VERSION = "project_runner_log_cleanup_audit_trails.v1"
RUNNER_LOG_CLEANUP_AUDIT_TRAIL_SCHEMA_VERSION = "runner_log_cleanup_audit_trail_schema.v1"


def build_project_runner_log_cleanup_audit_trails(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    cleanup_confirmations: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    confirmation_by_profile = {
        str(report.get("profile_id")): report
        for report in cleanup_confirmations.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _cleanup_audit_trail_report(profile, confirmation_by_profile.get(str(profile.get("id"))))
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LOG_CLEANUP_AUDIT_TRAIL_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "audit_trail_required_count": sum(1 for report in reports if report["status"] == "cleanup_audit_trail_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stored_audit_event_count": 0,
            "launchable_count": 0,
        },
        "cleanup_audit_trail_schema": log_cleanup_audit_trail_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "cleanup_audit_trail_only": True,
            "stores_audit_events": False,
            "writes_audit_log": False,
            "reads_audit_log": False,
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


def log_cleanup_audit_trail_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LOG_CLEANUP_AUDIT_TRAIL_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "audit_sink": {
            "planned_file": "runner_cleanup_audit.jsonl",
            "write_now": False,
            "read_now": False,
        },
        "required_future_events": [
            "cleanup_preview_rendered",
            "candidate_manifest_rendered",
            "cleanup_confirmation_prompt_rendered",
            "typed_consent_recorded",
            "scope_acknowledgement_recorded",
            "candidate_manifest_acknowledgement_recorded",
            "cleanup_started",
            "cleanup_file_deleted",
            "cleanup_file_rotated",
            "cleanup_completed",
            "cleanup_failed",
        ],
        "required_event_fields": [
            "event_id",
            "event_type",
            "created_at",
            "profile_id",
            "run_profile_fingerprint",
            "trace_dir",
            "candidate_manifest_hash",
            "confirmation_id",
            "actor",
            "result",
        ],
        "not_recorded_now": [
            "audit event id",
            "confirmation id",
            "candidate manifest hash",
            "cleanup result",
            "deleted file path",
            "rotated file path",
        ],
        "blocked_actions": [
            "open(audit_log, append)",
            "Path.write_text",
            "Path.read_text(audit_log)",
            "Path.iterdir",
            "Path.unlink",
            "Path.rename",
            "shutil.rmtree",
            "log cleanup execution",
            "launch POST API registration",
        ],
    }


def _cleanup_audit_trail_report(
    profile: dict[str, Any],
    cleanup_confirmation_report: dict[str, Any] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_cleanup_confirmation(cleanup_confirmation_report),
        _check_audit_schema_declared(),
        _check_event_fields_declared(),
        _check_no_audit_storage(),
        _check_no_audit_read(),
        _check_no_cleanup_mutation(),
    ]
    status = _report_status(checks)
    schema = log_cleanup_audit_trail_schema()
    return {
        "id": f"runner_log_cleanup_audit_trail:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "cleanup_confirmation_status": (
            cleanup_confirmation_report.get("status") if isinstance(cleanup_confirmation_report, dict) else "missing"
        ),
        "audit_sink": schema["audit_sink"],
        "required_future_events": schema["required_future_events"],
        "required_event_fields": schema["required_event_fields"],
        "audit_state": {
            "status": "not_recorded",
            "stored": False,
            "event_count": 0,
            "can_write_now": False,
            "reason": "This layer only declares future cleanup audit trail requirements.",
        },
        "checks": checks,
        "execution_boundary": (
            "当前只声明未来日志清理审计追踪要求；不会写审计日志、读取审计日志、扫描目录、读取日志、"
            "删除日志、轮转日志、重命名日志、截断日志、写入日志或执行命令。"
        ),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "日志清理审计追踪只能基于已保存运行配置。")


def _check_cleanup_confirmation(cleanup_confirmation_report: dict[str, Any] | None) -> dict[str, object]:
    if not cleanup_confirmation_report:
        return _check("cleanup_confirmation", "error", "缺少日志清理确认报告", "需要先生成 Runner 日志清理确认报告。")
    if cleanup_confirmation_report.get("status") == "cleanup_confirmation_required":
        return _check("cleanup_confirmation", "pass", "日志清理确认约束已声明", "审计追踪层继续保持只读。")
    return _check("cleanup_confirmation", "error", "日志清理确认存在阻塞项", str(cleanup_confirmation_report.get("status") or "unknown"))


def _check_audit_schema_declared() -> dict[str, object]:
    return _check("audit_schema", "pass", "审计事件 schema 已声明", "未来真实清理必须写入结构化审计事件。")


def _check_event_fields_declared() -> dict[str, object]:
    return _check("event_fields", "pass", "审计事件字段已声明", "未来事件必须包含确认、候选清单和结果证据。")


def _check_no_audit_storage() -> dict[str, object]:
    return _check("no_audit_storage", "pass", "当前不写审计日志", "本层不追加、创建或修改审计事件文件。")


def _check_no_audit_read() -> dict[str, object]:
    return _check("no_audit_read", "pass", "当前不读审计日志", "本层不读取已有审计事件或日志文件。")


def _check_no_cleanup_mutation() -> dict[str, object]:
    return _check("no_cleanup_mutation", "pass", "当前不会清理日志", "删除、轮转、重命名、截断和写入均保持禁用。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "cleanup_audit_trail_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "cleanup_audit_trail_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "日志清理审计追踪存在阻塞项",
        "cleanup_audit_trail_required": "仍需日志清理审计追踪约束",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成日志清理确认",
            "action": "保存运行配置并完成 Runner 日志清理确认约束后，再声明清理审计追踪要求。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复日志清理审计追踪阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "日志清理审计追踪要求已声明",
        "action": "下一步只能继续细化审计事件查看和报告的只读设计；真实扫描、删除、轮转和写入仍保持禁用。",
    }
