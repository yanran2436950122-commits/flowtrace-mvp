from __future__ import annotations

from typing import Any

from .run_final_confirmation_store import final_confirmation


RUN_EXECUTION_GATE_VERSION = "project_run_execution_gate.v1"


def build_project_run_execution_gate(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    run_preflight: dict[str, Any],
    final_confirmation_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    preflight_by_profile = {
        str(report.get("profile_id")): report
        for report in run_preflight.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _gate_report(profile, preflight_by_profile.get(str(profile.get("id"))), final_confirmation_store)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUN_EXECUTION_GATE_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "ready_count": sum(1 for report in reports if report["status"] == "ready_for_final_confirmation"),
            "confirmed_count": sum(1 for report in reports if report["final_confirmation"]["status"] == "confirmed"),
            "blocked_count": sum(1 for report in reports if report["status"].startswith("blocked")),
            "stale_confirmation_count": sum(1 for report in reports if report["final_confirmation"]["status"] == "stale"),
        },
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "requires_preflight_confirmation": True,
            "requires_final_confirmation": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _gate_report(
    profile: dict[str, Any],
    preflight_report: dict[str, Any] | None,
    final_confirmation_store: dict[str, object] | None,
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_preflight_report(preflight_report),
        _check_preflight_status(preflight_report),
        _check_preflight_confirmation(preflight_report),
        _check_no_command_execution(),
    ]
    status = _report_status(checks)
    confirmation = (
        final_confirmation(profile, preflight_report, final_confirmation_store)
        if preflight_report and status == "ready_for_final_confirmation"
        else {"status": "blocked", "confirmed": False, "confirmed_at": None, "stale": False}
    )
    if confirmation["status"] == "confirmed":
        status = "final_confirmed"
    elif confirmation["status"] == "stale":
        status = "ready_for_final_confirmation"
    return {
        "id": f"execution_gate:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "mode": profile.get("mode"),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "status": status,
        "status_label": _status_label(status),
        "preflight_status": preflight_report.get("status") if preflight_report else "missing",
        "preflight_confirmation": preflight_report.get("confirmation") if preflight_report else {"status": "missing"},
        "final_confirmation": confirmation,
        "checks": checks,
        "execution_boundary": "当前只确认最终执行意图；不会启动目标项目命令。",
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "最终确认只能基于已保存的运行配置。")


def _check_preflight_report(preflight_report: dict[str, Any] | None) -> dict[str, object]:
    if preflight_report:
        return _check("preflight_report", "pass", "预检报告存在", str(preflight_report.get("id") or ""))
    return _check("preflight_report", "error", "缺少预检报告", "需要先生成并通过执行前安全预检。")


def _check_preflight_status(preflight_report: dict[str, Any] | None) -> dict[str, object]:
    if not preflight_report:
        return _check("preflight_status", "error", "无法读取预检状态", "缺少预检报告。")
    status = str(preflight_report.get("status") or "")
    if status == "blocked":
        return _check("preflight_status", "error", "预检被阻断", "修复预检错误后再进行最终确认。")
    if status == "review":
        return _check("preflight_status", "warn", "预检需要复核", "存在警告项，最终确认前需要人工复核。")
    return _check("preflight_status", "pass", "预检可进入最终确认", status)


def _check_preflight_confirmation(preflight_report: dict[str, Any] | None) -> dict[str, object]:
    confirmation = preflight_report.get("confirmation") if isinstance(preflight_report, dict) else {}
    status = confirmation.get("status") if isinstance(confirmation, dict) else None
    if status == "confirmed":
        return _check("preflight_confirmation", "pass", "预检已确认", str(confirmation.get("confirmed_at") or ""))
    if status == "stale":
        return _check("preflight_confirmation", "error", "预检确认已失效", "运行配置变化后需要重新确认预检。")
    return _check("preflight_confirmation", "error", "预检尚未确认", "最终确认前必须先确认执行前安全预检。")


def _check_no_command_execution() -> dict[str, object]:
    return _check("no_command_execution", "pass", "当前不会执行命令", "最终确认页只保存确认状态，不启动目标项目。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "ready_for_final_confirmation"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if statuses == {"final_confirmed"}:
        return "final_confirmed"
    return "ready_for_final_confirmation"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "最终确认被阻断",
        "ready_for_final_confirmation": "等待最终确认",
        "final_confirmed": "已最终确认",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置草案",
            "action": "保存运行配置后再进入预检与最终确认。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复最终确认阻断项",
                "action": failed.get("detail") or "完成前置确认后再继续。",
            }
    if status == "final_confirmed":
        return {
            "title": "最终确认已记录",
            "action": "下一阶段才能接入独立 runner；当前仍不会执行命令。",
        }
    return {
        "title": "等待最终执行确认",
        "action": "确认前请复核工作目录、argv、环境变量、运行记录目录和预检确认时间。",
    }
