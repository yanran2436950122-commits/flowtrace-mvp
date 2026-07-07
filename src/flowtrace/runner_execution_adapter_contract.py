from __future__ import annotations

from typing import Any


RUNNER_EXECUTION_ADAPTER_CONTRACT_VERSION = "project_runner_execution_adapter_contracts.v1"
RUNNER_EXECUTION_ADAPTER_CONTRACT_SCHEMA_VERSION = "runner_execution_adapter_contract_schema.v1"


def build_project_runner_execution_adapter_contracts(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    governance_readiness: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    contract_schema = runner_execution_adapter_contract_schema()
    reports = [_adapter_contract_report(profile, governance_readiness, contract_schema) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_CONTRACT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "adapter_contract_required_count": sum(
                1 for report in reports if report["status"] == "adapter_contract_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
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
            "execution_adapter_contract_only": True,
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


def runner_execution_adapter_contract_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_CONTRACT_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "adapter_interface": [
            "create_session(snapshot)",
            "spawn_process(argv, cwd, env, stdout_sink, stderr_sink)",
            "cancel(session_id, reason)",
            "timeout(session_id)",
            "finalize(session_id, exit_code, duration_ms)",
        ],
        "required_inputs": [
            "launch_snapshot",
            "execution_request",
            "runner_session",
            "runtime_policy",
            "execution_config_check",
            "service_flag_audit",
            "log_directory_policy",
            "governance_readiness",
        ],
        "required_outputs": [
            "runner_events.jsonl events (future)",
            "stdout/stderr chunks (future)",
            "summary.json (future)",
        ],
        "argv_contract": {
            "argv_must_be_tokenized": True,
            "shell_string_allowed": False,
            "working_directory_locked": True,
            "inherit_environment": False,
        },
        "hooks": [
            "stdout_chunk_hook",
            "stderr_chunk_hook",
            "cancellation_hook",
            "timeout_hook",
            "completion_hook",
            "audit_hook",
        ],
        "blocked_actions": [
            "subprocess.Popen",
            "os.system",
            "shell=True",
            "launch POST API registration",
            "opening stdout/stderr files",
            "writing runner event logs",
            "user project writes",
        ],
    }


def _adapter_contract_report(
    profile: dict[str, Any],
    governance_readiness: dict[str, Any],
    contract_schema: dict[str, object],
) -> dict[str, object]:
    governance_report = _find_profile_report(governance_readiness, str(profile.get("id") or ""))
    checks = [
        _check_saved_profile(profile),
        _check_governance_readiness(governance_readiness, governance_report),
        _check_interface_declared(contract_schema),
        _check_argv_env_contract(contract_schema),
        _check_hooks_declared(contract_schema),
        _check_no_execution(),
        _check_no_filesystem_or_log_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_execution_adapter_contract:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "governance_status": governance_report.get("status") if governance_report else "missing",
        "adapter_contract": {
            "interface": contract_schema["adapter_interface"],
            "required_inputs": contract_schema["required_inputs"],
            "required_outputs": contract_schema["required_outputs"],
            "argv_contract": contract_schema["argv_contract"],
            "hooks": contract_schema["hooks"],
            "blocked_actions": contract_schema["blocked_actions"],
        },
        "checks": checks,
        "execution_boundary": (
            "当前只定义未来 Runner 执行适配器合约；不会注册启动接口、不会创建进程、不会执行命令、"
            "不会打开 stdout/stderr 文件、不会写入 runner 事件日志，也不会修改用户项目。"
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
    return _check("saved_profile", "error", "缺少保存记录", "执行适配器合约只能基于已保存运行配置生成。")


def _check_governance_readiness(
    governance_readiness: dict[str, Any],
    governance_report: dict[str, Any] | None,
) -> dict[str, object]:
    if not governance_report:
        return _check("governance_readiness", "error", "缺少治理就绪度报告", "需要先完成 Runner 治理就绪度汇总。")
    if governance_report.get("status") != "governance_required":
        return _check(
            "governance_readiness",
            "error",
            "治理就绪度未通过",
            f"当前状态：{governance_report.get('status') or governance_readiness.get('status')}",
        )
    return _check("governance_readiness", "pass", "治理链路已汇总", "执行适配器合约可继续保持只读设计。")


def _check_interface_declared(contract_schema: dict[str, object]) -> dict[str, object]:
    adapter_interface = contract_schema.get("adapter_interface")
    if isinstance(adapter_interface, list) and len(adapter_interface) >= 5:
        return _check("interface_declared", "pass", "适配器接口已声明", "包含会话、启动、取消、超时、收尾接口。")
    return _check("interface_declared", "error", "适配器接口不完整", "缺少未来执行适配器接口定义。")


def _check_argv_env_contract(contract_schema: dict[str, object]) -> dict[str, object]:
    argv_contract = contract_schema.get("argv_contract")
    if not isinstance(argv_contract, dict):
        return _check("argv_env_contract", "error", "缺少 argv/env 合约", "需要先声明命令参数与环境变量边界。")
    if argv_contract.get("argv_must_be_tokenized") and not argv_contract.get("shell_string_allowed"):
        return _check("argv_env_contract", "pass", "argv/env 合约已锁定", "禁止 shell 字符串，工作目录固定，环境变量不默认继承。")
    return _check("argv_env_contract", "error", "argv/env 合约不安全", "必须使用 tokenized argv，并禁止 shell 字符串。")


def _check_hooks_declared(contract_schema: dict[str, object]) -> dict[str, object]:
    hooks = contract_schema.get("hooks")
    required = {"stdout_chunk_hook", "stderr_chunk_hook", "cancellation_hook", "timeout_hook", "completion_hook"}
    if isinstance(hooks, list) and required.issubset(set(str(item) for item in hooks)):
        return _check("hooks_declared", "pass", "生命周期钩子已声明", "未来可承接输出、取消、超时、完成和审计。")
    return _check("hooks_declared", "error", "生命周期钩子不完整", "需要补齐输出、取消、超时和完成钩子。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不执行命令", "没有 subprocess、os.system、shell=True 或启动 POST API。")


def _check_no_filesystem_or_log_mutation() -> dict[str, object]:
    return _check("no_log_mutation", "pass", "当前不读写日志", "不打开 stdout/stderr 文件，不写 runner 事件日志，不修改用户项目。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "adapter_contract_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "adapter_contract_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "执行适配器合约存在阻塞项",
        "adapter_contract_required": "执行适配器合约已声明但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并完成 Runner 治理链路后，再生成执行适配器合约报告。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复执行适配器合约阻塞项",
                "action": failed.get("detail") or "完成前置治理条件后再继续。",
            }
    return {
        "title": "执行适配器合约已收敛",
        "action": "下一步仍应先做只读适配器设计审查；真实启动 API、进程创建和日志写入继续保持禁用。",
    }
