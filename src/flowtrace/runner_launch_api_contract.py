from __future__ import annotations

from typing import Any


RUNNER_LAUNCH_API_CONTRACT_VERSION = "project_runner_launch_api_contracts.v1"
RUNNER_LAUNCH_API_CONTRACT_SCHEMA_VERSION = "runner_launch_api_contract_schema.v1"


def build_project_runner_launch_api_contracts(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_adapter_contracts: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    contract_schema = runner_launch_api_contract_schema()
    reports = [
        _launch_api_contract_report(profile, execution_adapter_contracts, contract_schema)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_LAUNCH_API_CONTRACT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "launch_api_contract_required_count": sum(
                1 for report in reports if report["status"] == "launch_api_contract_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "registered_endpoint_count": 0,
            "launchable_count": 0,
        },
        "contract_schema": contract_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "launch_api_contract_only": True,
            "registers_post_api": False,
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


def runner_launch_api_contract_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_LAUNCH_API_CONTRACT_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "future_endpoint": {
            "method": "POST",
            "path": "/api/project/runner/launch",
            "registered_now": False,
            "requires_idempotency_key": True,
            "requires_second_confirmation": True,
            "requires_final_human_consent": True,
        },
        "request_contract": {
            "required_fields": [
                "profile_id",
                "execution_request_id",
                "runner_session_id",
                "launch_snapshot_id",
                "idempotency_key",
                "typed_consent",
            ],
            "forbidden_fields": [
                "shell",
                "command_string",
                "cwd_override",
                "env_override",
                "log_path_override",
            ],
        },
        "response_contract": {
            "success_fields": [
                "request_id",
                "session_id",
                "run_id",
                "status",
                "created_at",
                "event_stream",
            ],
            "error_fields": [
                "error",
                "reason",
                "failed_guard",
                "next_action",
            ],
        },
        "required_guards": [
            "service_flag_explicitly_enabled",
            "profile_saved",
            "preflight_confirmed",
            "final_execution_confirmed",
            "execution_request_second_confirmed",
            "runner_session_drafted",
            "launch_snapshot_fresh",
            "dry_run_prepared",
            "runtime_policy_valid",
            "execution_config_checked",
            "service_flag_audited",
            "log_directory_policy_declared",
            "governance_readiness_required",
            "execution_adapter_contract_required",
        ],
        "idempotency_contract": {
            "scope": "profile_id + launch_snapshot_id + idempotency_key",
            "duplicate_request_behavior": "return existing launch session summary",
            "mutation_allowed_now": False,
        },
        "blocked_actions": [
            "registering POST /api/project/runner/launch",
            "starting process from HTTP handler",
            "calling execution adapter",
            "opening stdout/stderr files",
            "writing runner event logs",
            "writing user project files",
        ],
    }


def _launch_api_contract_report(
    profile: dict[str, Any],
    execution_adapter_contracts: dict[str, Any],
    contract_schema: dict[str, object],
) -> dict[str, object]:
    adapter_report = _find_profile_report(execution_adapter_contracts, str(profile.get("id") or ""))
    checks = [
        _check_saved_profile(profile),
        _check_execution_adapter_contract(adapter_report),
        _check_endpoint_not_registered(contract_schema),
        _check_request_contract(contract_schema),
        _check_required_guards(contract_schema),
        _check_idempotency_contract(contract_schema),
        _check_no_execution(),
        _check_no_filesystem_or_log_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_launch_api_contract:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "execution_adapter_contract_status": adapter_report.get("status") if adapter_report else "missing",
        "launch_api_contract": {
            "future_endpoint": contract_schema["future_endpoint"],
            "request_contract": contract_schema["request_contract"],
            "response_contract": contract_schema["response_contract"],
            "required_guards": contract_schema["required_guards"],
            "idempotency_contract": contract_schema["idempotency_contract"],
            "blocked_actions": contract_schema["blocked_actions"],
        },
        "checks": checks,
        "execution_boundary": (
            "当前只定义未来 Runner 启动 API 合约；不会注册 POST 路由、不会从 HTTP handler 启动进程、"
            "不会调用执行适配器、不会写入日志，也不会修改用户项目。"
        ),
    }


def _find_profile_report(collection: dict[str, Any], profile_id: str) -> dict[str, Any] | None:
    reports = collection.get("reports")
    if not isinstance(reports, list):
        return None
    for report in reports:
        if isinstance(report, dict) and str(report.get("profile_id")) == profile_id:
            return report
    return None


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "启动 API 合约只能基于已保存运行配置生成。")


def _check_execution_adapter_contract(adapter_report: dict[str, Any] | None) -> dict[str, object]:
    if not adapter_report:
        return _check("execution_adapter_contract", "error", "缺少执行适配器合约", "需要先完成执行适配器合约报告。")
    if adapter_report.get("status") != "adapter_contract_required":
        return _check(
            "execution_adapter_contract",
            "error",
            "执行适配器合约未通过",
            f"当前状态：{adapter_report.get('status')}",
        )
    return _check("execution_adapter_contract", "pass", "执行适配器合约已声明", "启动 API 合约可以继续保持只读设计。")


def _check_endpoint_not_registered(contract_schema: dict[str, object]) -> dict[str, object]:
    endpoint = contract_schema.get("future_endpoint")
    if isinstance(endpoint, dict) and endpoint.get("registered_now") is False:
        return _check("endpoint_not_registered", "pass", "启动 POST 未注册", "当前仅声明未来端点，不开放真实启动入口。")
    return _check("endpoint_not_registered", "error", "启动 POST 不应注册", "真实启动入口必须继续保持不可用。")


def _check_request_contract(contract_schema: dict[str, object]) -> dict[str, object]:
    request_contract = contract_schema.get("request_contract")
    if not isinstance(request_contract, dict):
        return _check("request_contract", "error", "缺少请求合约", "需要声明请求字段和禁止字段。")
    required_fields = request_contract.get("required_fields")
    forbidden_fields = request_contract.get("forbidden_fields")
    if isinstance(required_fields, list) and isinstance(forbidden_fields, list) and "command_string" in forbidden_fields:
        return _check("request_contract", "pass", "请求合约已声明", "禁止 shell、命令字符串、工作目录覆盖和环境变量覆盖。")
    return _check("request_contract", "error", "请求合约不完整", "必须声明必填字段与危险字段黑名单。")


def _check_required_guards(contract_schema: dict[str, object]) -> dict[str, object]:
    guards = contract_schema.get("required_guards")
    required = {
        "service_flag_explicitly_enabled",
        "final_execution_confirmed",
        "execution_request_second_confirmed",
        "execution_adapter_contract_required",
    }
    if isinstance(guards, list) and required.issubset(set(str(item) for item in guards)):
        return _check("required_guards", "pass", "启动门槛已声明", "未来启动前必须通过服务开关、最终确认、二次确认和适配器合约。")
    return _check("required_guards", "error", "启动门槛不完整", "缺少未来启动前置门槛。")


def _check_idempotency_contract(contract_schema: dict[str, object]) -> dict[str, object]:
    idempotency = contract_schema.get("idempotency_contract")
    if isinstance(idempotency, dict) and idempotency.get("mutation_allowed_now") is False:
        return _check("idempotency_contract", "pass", "幂等合约已声明", "重复请求只能返回既有会话摘要，当前不允许写入。")
    return _check("idempotency_contract", "error", "幂等合约不完整", "必须声明幂等范围和重复请求行为。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不执行命令", "没有真实 POST、没有进程创建、没有调用执行适配器。")


def _check_no_filesystem_or_log_mutation() -> dict[str, object]:
    return _check("no_log_mutation", "pass", "当前不读写日志", "不打开 stdout/stderr 文件，不写 runner 事件日志，不修改用户项目。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "launch_api_contract_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "launch_api_contract_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "启动 API 合约存在阻塞项",
        "launch_api_contract_required": "启动 API 合约已声明但真实启动仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并完成执行适配器合约后，再生成启动 API 合约报告。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复启动 API 合约阻塞项",
                "action": failed.get("detail") or "完成前置合约后再继续。",
            }
    return {
        "title": "启动 API 合约已收敛",
        "action": "下一步仍只能做只读审查；真实 POST 注册、进程创建和日志写入继续保持禁用。",
    }
