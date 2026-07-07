from __future__ import annotations

from typing import Any


RUNNER_EXECUTION_ADAPTER_REVIEW_VERSION = "project_runner_execution_adapter_reviews.v1"
RUNNER_EXECUTION_ADAPTER_REVIEW_SCHEMA_VERSION = "runner_execution_adapter_review_schema.v1"


def build_project_runner_execution_adapter_reviews(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    launch_api_contracts: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    review_schema = runner_execution_adapter_review_schema()
    reports = [_adapter_review_report(profile, launch_api_contracts, review_schema) for profile in saved_profiles]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_REVIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "adapter_review_required_count": sum(
                1 for report in reports if report["status"] == "adapter_review_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "implemented_adapter_count": 0,
            "violation_count": 0,
            "launchable_count": 0,
        },
        "review_schema": review_schema,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "adapter_review_only": True,
            "scans_code": False,
            "imports_adapter": False,
            "registers_post_api": False,
            "calls_execution_adapter": False,
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


def runner_execution_adapter_review_schema() -> dict[str, object]:
    return {
        "schema_version": RUNNER_EXECUTION_ADAPTER_REVIEW_SCHEMA_VERSION,
        "launch_enabled": False,
        "launch_api_available": False,
        "implementation_state": {
            "adapter_expected_in_future": True,
            "adapter_loaded_now": False,
            "adapter_invoked_now": False,
            "review_is_preimplementation": True,
        },
        "required_review_gates": [
            "http_handler_must_not_spawn_process",
            "adapter_must_accept_tokenized_argv_only",
            "adapter_must_reject_shell_strings",
            "working_directory_must_match_launch_snapshot",
            "environment_must_use_allowlist",
            "stdout_stderr_must_stream_through_hooks",
            "runner_event_log_writes_must_be_audited",
            "cancel_must_be_idempotent",
            "timeout_must_finalize_session",
            "completion_must_refresh_runs",
            "failure_must_return_structured_summary",
            "user_project_must_remain_readonly",
        ],
        "required_evidence": [
            "launch_api_contract",
            "execution_adapter_contract",
            "launch_snapshot",
            "execution_request",
            "runner_session",
            "runtime_policy",
            "execution_config_check",
            "log_directory_policy",
        ],
        "blocked_actions": [
            "loading adapter implementation during review",
            "calling adapter from review layer",
            "creating subprocess during review",
            "registering launch POST during review",
            "opening stdout/stderr files during review",
            "writing logs during review",
            "writing user project files during review",
        ],
    }


def _adapter_review_report(
    profile: dict[str, Any],
    launch_api_contracts: dict[str, Any],
    review_schema: dict[str, object],
) -> dict[str, object]:
    launch_api_report = _find_profile_report(launch_api_contracts, str(profile.get("id") or ""))
    checks = [
        _check_saved_profile(profile),
        _check_launch_api_contract(launch_api_report),
        _check_preimplementation_state(review_schema),
        _check_review_gates(review_schema),
        _check_required_evidence(review_schema),
        _check_no_adapter_loading(),
        _check_no_execution(),
        _check_no_filesystem_or_log_mutation(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_execution_adapter_review:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "launch_api_contract_status": launch_api_report.get("status") if launch_api_report else "missing",
        "adapter_review": {
            "implementation_state": review_schema["implementation_state"],
            "required_review_gates": review_schema["required_review_gates"],
            "required_evidence": review_schema["required_evidence"],
            "blocked_actions": review_schema["blocked_actions"],
        },
        "checks": checks,
        "execution_boundary": (
            "当前只生成执行适配器预实现审查矩阵；不会加载适配器、不会调用适配器、不会注册启动 POST、"
            "不会创建进程、不会执行命令、不会读写日志，也不会修改用户项目。"
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
    return _check("saved_profile", "error", "缺少保存记录", "执行适配器审查只能基于已保存运行配置生成。")


def _check_launch_api_contract(launch_api_report: dict[str, Any] | None) -> dict[str, object]:
    if not launch_api_report:
        return _check("launch_api_contract", "error", "缺少启动 API 合约", "需要先完成启动 API 合约报告。")
    if launch_api_report.get("status") != "launch_api_contract_required":
        return _check(
            "launch_api_contract",
            "error",
            "启动 API 合约未通过",
            f"当前状态：{launch_api_report.get('status')}",
        )
    return _check("launch_api_contract", "pass", "启动 API 合约已声明", "适配器审查可以继续保持只读设计。")


def _check_preimplementation_state(review_schema: dict[str, object]) -> dict[str, object]:
    state = review_schema.get("implementation_state")
    if (
        isinstance(state, dict)
        and state.get("review_is_preimplementation")
        and state.get("adapter_loaded_now") is False
        and state.get("adapter_invoked_now") is False
    ):
        return _check("preimplementation_state", "pass", "审查保持预实现状态", "当前不加载也不调用执行适配器。")
    return _check("preimplementation_state", "error", "审查状态不安全", "审查层必须保持预实现、只读、不可调用。")


def _check_review_gates(review_schema: dict[str, object]) -> dict[str, object]:
    gates = review_schema.get("required_review_gates")
    required = {
        "http_handler_must_not_spawn_process",
        "adapter_must_accept_tokenized_argv_only",
        "adapter_must_reject_shell_strings",
        "completion_must_refresh_runs",
        "user_project_must_remain_readonly",
    }
    if isinstance(gates, list) and required.issubset(set(str(item) for item in gates)):
        return _check("review_gates", "pass", "审查门槛已声明", "覆盖 HTTP、argv、shell、完成刷新和用户项目只读边界。")
    return _check("review_gates", "error", "审查门槛不完整", "需要补齐未来适配器必须通过的审查门槛。")


def _check_required_evidence(review_schema: dict[str, object]) -> dict[str, object]:
    evidence = review_schema.get("required_evidence")
    required = {"launch_api_contract", "execution_adapter_contract", "launch_snapshot", "runtime_policy"}
    if isinstance(evidence, list) and required.issubset(set(str(item) for item in evidence)):
        return _check("required_evidence", "pass", "审查证据已声明", "未来真实适配器必须绑定合约、快照和运行时策略。")
    return _check("required_evidence", "error", "审查证据不完整", "需要声明未来审查必须读取的证据集合。")


def _check_no_adapter_loading() -> dict[str, object]:
    return _check("no_adapter_loading", "pass", "当前不加载适配器", "审查层不 import、不实例化、不调用未来适配器。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不执行命令", "没有真实 POST、没有进程创建、没有执行适配器调用。")


def _check_no_filesystem_or_log_mutation() -> dict[str, object]:
    return _check("no_log_mutation", "pass", "当前不读写日志", "不打开 stdout/stderr 文件，不写 runner 事件日志，不修改用户项目。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "adapter_review_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "adapter_review_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "执行适配器审查存在阻塞项",
        "adapter_review_required": "执行适配器审查矩阵已声明但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并完成启动 API 合约后，再生成执行适配器审查报告。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复执行适配器审查阻塞项",
                "action": failed.get("detail") or "完成前置合约后再继续。",
            }
    return {
        "title": "执行适配器审查矩阵已收敛",
        "action": "下一步仍只能继续只读阻断设计；真实适配器加载、POST 注册、进程创建和日志写入继续保持禁用。",
    }
