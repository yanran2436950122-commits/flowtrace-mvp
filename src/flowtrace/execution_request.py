from __future__ import annotations

from typing import Any

from .execution_request_store import execution_request_state


EXECUTION_REQUEST_VERSION = "project_execution_requests.v1"


def build_project_execution_requests(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    runner_plan: dict[str, Any],
    request_store: dict[str, object] | None = None,
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    runner_by_profile = {
        str(report.get("profile_id")): report
        for report in runner_plan.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    reports = [
        _execution_request_report(profile, runner_by_profile.get(str(profile.get("id"))), request_store)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": EXECUTION_REQUEST_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "prepared_count": sum(1 for report in reports if report["request"]["status"] in {"prepared", "second_confirmed"}),
            "second_confirmed_count": sum(1 for report in reports if report["request"]["status"] == "second_confirmed"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stale_count": sum(1 for report in reports if report["request"]["status"] == "stale"),
        },
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "runner_implemented": False,
            "request_store_only": True,
            "requires_second_confirmation": True,
            "writes_user_project": False,
        },
        "next_action": _next_action(status, reports),
    }


def _execution_request_report(
    profile: dict[str, Any],
    runner_report: dict[str, Any] | None,
    request_store: dict[str, object] | None,
) -> dict[str, object]:
    request = execution_request_state(profile, runner_report, request_store)
    checks = [
        _check_saved_profile(profile),
        _check_runner_plan(runner_report),
        _check_request_state(request),
        _check_no_execution(),
    ]
    status = _report_status(checks, request)
    return {
        "id": f"execution_request:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "runner_status": runner_report.get("status") if runner_report else "missing",
        "request": request,
        "checks": checks,
        "can_prepare": runner_report is not None and runner_report.get("status") == "ready_for_runner_implementation",
        "can_confirm": request.get("status") == "prepared",
        "can_revoke": request.get("status") == "second_confirmed",
        "can_remove": request.get("status") in {"prepared", "second_confirmed", "stale"},
        "execution_boundary": "当前只保存执行请求草案和二次确认状态；不会启动目标项目命令。",
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "执行请求只能基于已保存运行配置。")


def _check_runner_plan(runner_report: dict[str, Any] | None) -> dict[str, object]:
    if not runner_report:
        return _check("runner_plan", "error", "缺少 runner 设计报告", "需要先生成 runner 隔离设计报告。")
    if runner_report.get("status") == "ready_for_runner_implementation":
        return _check("runner_plan", "pass", "runner 前置设计已就绪", str(runner_report.get("status")))
    return _check("runner_plan", "error", "runner 前置条件未满足", "执行请求草案只能在 runner plan 就绪后准备。")


def _check_request_state(request: dict[str, object]) -> dict[str, object]:
    status = request.get("status")
    if status == "second_confirmed":
        return _check("request_state", "pass", "执行请求已二次确认", str(request.get("second_confirmed_at") or ""))
    if status == "prepared":
        return _check("request_state", "warn", "执行请求草案已准备", "仍需要二次确认；当前不会执行命令。")
    if status == "stale":
        return _check("request_state", "error", "执行请求草案已失效", str(request.get("reason") or ""))
    if status == "blocked":
        return _check("request_state", "error", "执行请求被阻断", "缺少 runner 前置报告。")
    return _check("request_state", "warn", "尚未准备执行请求", "准备请求只会保存草案，不会执行命令。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只保存请求草案和二次确认状态。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], request: dict[str, object]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if request.get("status") == "second_confirmed":
        return "second_confirmed"
    if request.get("status") == "prepared":
        return "prepared"
    return "ready_to_prepare"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    statuses = {str(report.get("status")) for report in reports}
    if "blocked" in statuses:
        return "blocked"
    if statuses == {"second_confirmed"}:
        return "second_confirmed"
    if "prepared" in statuses:
        return "prepared"
    return "ready_to_prepare"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "执行请求被阻断",
        "ready_to_prepare": "可准备执行请求草案",
        "prepared": "执行请求草案已准备",
        "second_confirmed": "执行请求已二次确认",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存并确认运行配置",
            "action": "完成运行配置、预检、最终确认和 runner plan 后，再准备执行请求草案。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复执行请求阻断项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    if status == "second_confirmed":
        return {
            "title": "二次确认已记录",
            "action": "当前仍不会执行命令；后续接入 runner 后还需要单独执行动作。",
        }
    if status == "prepared":
        return {
            "title": "等待二次确认",
            "action": "请复核执行请求草案；二次确认仍只保存状态，不启动命令。",
        }
    return {
        "title": "可以准备执行请求草案",
        "action": "准备请求会写入 FlowTrace trace 目录，不会启动目标项目。",
    }
