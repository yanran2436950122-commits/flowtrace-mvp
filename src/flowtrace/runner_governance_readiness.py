from __future__ import annotations

from typing import Any


RUNNER_GOVERNANCE_READINESS_VERSION = "project_runner_governance_readiness.v1"
RUNNER_GOVERNANCE_READINESS_SCHEMA_VERSION = "runner_governance_readiness_schema.v1"

LAYER_LABELS = {
    "run_preflight": "执行前安全预检",
    "run_execution_gate": "最终执行确认",
    "runner_plan": "Runner 隔离设计",
    "execution_requests": "执行请求草案",
    "runner_sessions": "Runner 会话草案",
    "runner_launch_snapshots": "启动前快照",
    "runner_dry_runs": "Dry-run Runner",
    "runner_launch_controls": "Runner 启动开关",
    "runner_runtime_policies": "Runner 运行时策略",
    "runner_execution_configs": "Runner 执行配置",
    "runner_execution_config_checks": "Runner 配置检查",
    "runner_config_schema_stabilizations": "Runner 配置 Schema 稳定化",
    "runner_config_compatibility_reports": "Runner 配置兼容性报告",
    "runner_service_flag_audits": "Runner 服务开关审计",
    "runner_log_directory_policies": "Runner 日志目录策略",
    "runner_log_retention_policies": "Runner 日志保留策略",
    "runner_log_cleanup_previews": "Runner 日志清理预览",
    "runner_log_cleanup_confirmations": "Runner 日志清理确认",
    "runner_log_cleanup_audit_trails": "Runner 日志清理审计追踪",
    "runner_log_cleanup_execution_plans": "Runner 日志清理执行计划",
}


LAYER_LABELS["runner_config_remediation_summaries"] = "Runner 配置修复建议汇总"
LAYER_LABELS["runner_config_field_contract_views"] = "Runner 配置字段契约说明"
LAYER_LABELS["runner_config_field_coverage_indexes"] = "Runner config field coverage index"


def build_project_runner_governance_readiness(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    governance_layers: dict[str, dict[str, Any]],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    reports = [_governance_report(profile, governance_layers) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_GOVERNANCE_READINESS_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "governance_required_count": sum(1 for report in reports if report["status"] == "governance_required"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "layer_count": len(LAYER_LABELS),
            "launchable_count": 0,
        },
        "governance_schema": governance_readiness_schema(),
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "governance_readiness_only": True,
            "writes_user_project": False,
            "creates_config_file": False,
            "reads_log_files": False,
            "writes_logs": False,
            "deletes_logs": False,
            "rotates_logs": False,
            "truncates_logs": False,
        },
        "next_action": _next_action(status, reports),
    }


def governance_readiness_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_GOVERNANCE_READINESS_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "required_layers": [
            {"id": key, "label": label}
            for key, label in LAYER_LABELS.items()
        ],
        "blocked_until_future_layers": [
            "real launch API",
            "process execution adapter",
            "live stdout/stderr writer",
            "cancel endpoint",
            "completion refresh worker",
            "audit-log persistence",
        ],
    }


def _governance_report(profile: dict[str, Any], governance_layers: dict[str, dict[str, Any]]) -> dict[str, object]:
    profile_id = str(profile.get("id") or "")
    layer_states = [_layer_state(profile_id, key, collection) for key, collection in governance_layers.items()]
    checks = [
        _check_saved_profile(profile),
        _check_layer_chain(layer_states),
        _check_no_launch_api(),
        _check_no_runner_implementation(),
        _check_no_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_governance_readiness:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "layer_states": layer_states,
        "checks": checks,
        "launch_state": {
            "launchable": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "reason": "所有 Runner 治理层当前只读；真实 runner、启动 API 和进程执行适配器仍未实现。",
        },
        "execution_boundary": "当前只汇总 Runner 治理就绪度；不会启动进程、执行命令、读写日志、清理日志或修改用户项目。",
    }


def _layer_state(profile_id: str, key: str, collection: dict[str, Any]) -> dict[str, object]:
    report = _find_profile_report(collection, profile_id)
    if report is None and key in {"runner_config_field_contract_views", "runner_config_field_coverage_indexes"}:
        report = _first_collection_report(collection)
    return {
        "key": key,
        "label": LAYER_LABELS.get(key, key),
        "collection_status": collection.get("status"),
        "report_status": report.get("status") if report else "missing",
        "schema_version": collection.get("schema_version"),
    }


def _find_profile_report(collection: dict[str, Any], profile_id: str) -> dict[str, Any] | None:
    reports = collection.get("reports")
    if not isinstance(reports, list):
        return None
    for report in reports:
        if isinstance(report, dict) and str(report.get("profile_id")) == profile_id:
            return report
    return None


def _first_collection_report(collection: dict[str, Any]) -> dict[str, Any] | None:
    reports = collection.get("reports")
    if isinstance(reports, list) and reports and isinstance(reports[0], dict):
        return reports[0]
    return None


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "治理就绪度只能基于已保存运行配置。")


def _check_layer_chain(layer_states: list[dict[str, object]]) -> dict[str, object]:
    missing = [item["label"] for item in layer_states if item.get("report_status") == "missing"]
    blocked = [item["label"] for item in layer_states if item.get("report_status") == "blocked"]
    if missing:
        return _check("layer_chain", "error", "治理层报告缺失", "、".join(str(item) for item in missing))
    if blocked:
        return _check("layer_chain", "error", "治理层存在阻塞项", "、".join(str(item) for item in blocked))
    return _check("layer_chain", "pass", "治理层链路完整", f"{len(layer_states)} 个只读层已纳入汇总。")


def _check_no_launch_api() -> dict[str, object]:
    return _check("no_launch_api", "pass", "真实启动 API 不存在", "当前没有注册 launch POST API。")


def _check_no_runner_implementation() -> dict[str, object]:
    return _check("no_runner_implementation", "pass", "真实 runner 未实现", "当前没有进程执行适配器。")


def _check_no_mutation() -> dict[str, object]:
    return _check("no_mutation", "pass", "当前不会修改运行环境", "不执行命令、不读写日志、不清理日志、不写用户项目。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "governance_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "governance_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "Runner 治理链路存在阻塞项",
        "governance_required": "Runner 治理链路已汇总但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并完成上游 Runner 治理链路后，再查看治理就绪度。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复治理链路阻塞项",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "治理链路已汇总",
        "action": "下一步仍只能继续只读治理设计；真实启动 API、进程执行和日志写入仍保持禁用。",
    }
