from __future__ import annotations

from typing import Any


RUNNER_CONFIG_SCHEMA_STABILIZATION_VERSION = "project_runner_config_schema_stabilizations.v1"
RUNNER_CONFIG_SCHEMA_STABILIZATION_SCHEMA_VERSION = "runner_config_schema_stabilization_schema.v1"
RUNNER_CONFIG_FILE_SCHEMA_VERSION = "flowtrace_runner_config.v1"


def build_project_runner_config_schema_stabilizations(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_configs: dict[str, Any],
    execution_config_checks: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    execution_config_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_configs.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    config_check_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_config_checks.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    schema = runner_config_schema_stabilization_schema(project_context)
    reports = [
        _schema_stabilization_report(
            profile,
            execution_config_by_profile.get(str(profile.get("id"))),
            config_check_by_profile.get(str(profile.get("id"))),
            schema,
        )
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_CONFIG_SCHEMA_STABILIZATION_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "schema_stabilization_required_count": sum(
                1 for report in reports if report["status"] == "schema_stabilization_required"
            ),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "stable_schema_count": 1,
            "supported_version_count": len(schema["supported_versions"]),
            "field_contract_count": len(schema["field_contracts"]),
            "compatibility_rule_count": len(schema["compatibility_rules"]),
            "error_code_count": len(schema["error_map"]),
            "launchable_count": 0,
        },
        "config_schema_stabilization_schema": schema,
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_config_schema_stabilization_schema(project_context: dict[str, Any]) -> dict[str, object]:
    return {
        "schema_version": RUNNER_CONFIG_SCHEMA_STABILIZATION_SCHEMA_VERSION,
        "config_file_name": "flowtrace.runner.json",
        "config_file_schema_version": RUNNER_CONFIG_FILE_SCHEMA_VERSION,
        "supported_versions": [RUNNER_CONFIG_FILE_SCHEMA_VERSION],
        "minimum_supported_version": RUNNER_CONFIG_FILE_SCHEMA_VERSION,
        "suggested_trace_dir": str(project_context.get("trace_dir") or ""),
        "default_policy": {
            "runner.enable_real_execution": False,
            "runner.require_server_flag": True,
            "runner.require_environment_flag": True,
            "runner.require_typed_consent": True,
            "process.no_shell_string": True,
            "process.argv_must_be_tokenized": True,
            "process.inherit_environment": False,
            "launch_api_available": False,
            "launch_enabled": False,
        },
        "required_sections": [
            "schema_version",
            "runner",
            "process",
            "logs",
            "cancel_timeout",
            "completion_refresh",
        ],
        "field_contracts": _field_contracts(),
        "compatibility_rules": _compatibility_rules(),
        "error_map": _error_map(),
        "blocked_actions": [
            "creating flowtrace.runner.json",
            "modifying flowtrace.runner.json",
            "writing user project files",
            "executing commands",
            "creating processes",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch UI",
            "importing or calling execution adapters",
            "creating or mutating runner sessions",
            "opening stdout/stderr",
            "reading or writing runner events",
            "reading or writing audit logs",
            "collecting or storing authorization",
        ],
    }


def _schema_stabilization_report(
    profile: dict[str, Any],
    execution_config_report: dict[str, Any] | None,
    config_check_report: dict[str, Any] | None,
    schema: dict[str, object],
) -> dict[str, object]:
    checks = [
        _check_saved_profile(profile),
        _check_execution_config(execution_config_report),
        _check_config_check(config_check_report),
        _check_version_contract(schema),
        _check_default_disabled(schema),
        _check_compatibility_rules(schema),
        _check_error_map(schema),
        _check_no_execution(),
    ]
    status = _report_status(checks)
    return {
        "id": f"runner_config_schema_stabilization:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "execution_config_status": (
            execution_config_report.get("status") if isinstance(execution_config_report, dict) else "missing"
        ),
        "config_check_status": config_check_report.get("status") if isinstance(config_check_report, dict) else "missing",
        "stable_config_schema_version": schema["config_file_schema_version"],
        "supported_versions": schema["supported_versions"],
        "compatibility_rules": schema["compatibility_rules"],
        "error_map": schema["error_map"],
        "checks": checks,
        "execution_boundary": (
            "当前只稳定未来 flowtrace.runner.json 的 schema、兼容性规则和错误码；不会创建或修改配置文件，"
            "不会创建进程、执行命令、开放真实启动 API 或修改用户项目。"
        ),
    }


def _field_contracts() -> list[dict[str, object]]:
    return [
        _field("schema_version", "string", RUNNER_CONFIG_FILE_SCHEMA_VERSION, True, "FTRCFG_SCHEMA_VERSION_REQUIRED"),
        _field("runner.enable_real_execution", "boolean", False, True, "FTRCFG_REAL_EXECUTION_DEFAULT_DISABLED"),
        _field("runner.typed_consent", "string", "RUN TARGET PROJECT", True, "FTRCFG_CONSENT_MISMATCH"),
        _field("runner.require_server_flag", "boolean", True, True, "FTRCFG_SERVER_FLAG_REQUIRED"),
        _field("runner.require_environment_flag", "boolean", True, True, "FTRCFG_ENV_FLAG_REQUIRED"),
        _field("process.no_shell_string", "boolean", True, True, "FTRCFG_SHELL_STRING_FORBIDDEN"),
        _field("process.argv_must_be_tokenized", "boolean", True, True, "FTRCFG_ARGV_TOKENIZATION_REQUIRED"),
        _field("process.inherit_environment", "boolean", False, True, "FTRCFG_ENV_INHERITANCE_DISABLED"),
        _field("logs.stdout_chunk_bytes", "integer", 4096, True, "FTRCFG_STDOUT_CHUNK_TOO_LOW"),
        _field("logs.stderr_chunk_bytes", "integer", 4096, True, "FTRCFG_STDERR_CHUNK_TOO_LOW"),
        _field("logs.max_stream_bytes", "integer", 2 * 1024 * 1024, True, "FTRCFG_STREAM_LIMIT_TOO_LOW"),
        _field("cancel_timeout.default_timeout_seconds", "integer", 120, True, "FTRCFG_TIMEOUT_TOO_LOW"),
        _field("completion_refresh.refresh_runs_after_completion", "boolean", True, True, "FTRCFG_REFRESH_REQUIRED"),
    ]


def _field(path: str, field_type: str, default: object, required: bool, error_code: str) -> dict[str, object]:
    return {
        "path": path,
        "type": field_type,
        "default": default,
        "required": required,
        "error_code": error_code,
    }


def _compatibility_rules() -> list[dict[str, object]]:
    return [
        _rule("exact_schema_version", "Only flowtrace_runner_config.v1 is accepted in this phase."),
        _rule("unknown_major_version_blocks", "Unknown major versions must be rejected before any launch decision."),
        _rule("missing_required_field_blocks", "Required fields cannot be inferred silently."),
        _rule("optional_defaults_are_safe", "Optional fields may only default to disabled or stricter behavior."),
        _rule("booleans_are_strict", "Boolean fields must be JSON booleans, not strings or numbers."),
        _rule("numeric_limits_are_minimums", "Numeric stream and timeout limits must meet or exceed the schema minimum."),
        _rule("typed_consent_is_exact", "Typed consent must exactly match RUN TARGET PROJECT."),
        _rule("launch_remains_disabled", "A schema-valid config is still not launchable without future APIs and authorization."),
    ]


def _rule(key: str, detail: str) -> dict[str, object]:
    return {"key": key, "detail": detail}


def _error_map() -> list[dict[str, object]]:
    return [
        _error("FTRCFG_SCHEMA_VERSION_REQUIRED", "schema_version", "schema_version is missing or not v1."),
        _error("FTRCFG_UNSUPPORTED_SCHEMA_VERSION", "schema_version", "schema_version is not supported."),
        _error("FTRCFG_REQUIRED_FIELD_MISSING", "*", "A required field is missing."),
        _error("FTRCFG_TYPE_MISMATCH", "*", "A field has the wrong JSON type."),
        _error("FTRCFG_REAL_EXECUTION_DEFAULT_DISABLED", "runner.enable_real_execution", "Real execution defaults to disabled."),
        _error("FTRCFG_CONSENT_MISMATCH", "runner.typed_consent", "Typed consent does not match."),
        _error("FTRCFG_SHELL_STRING_FORBIDDEN", "process.no_shell_string", "Shell-string execution is forbidden."),
        _error("FTRCFG_ARGV_TOKENIZATION_REQUIRED", "process.argv_must_be_tokenized", "argv must be tokenized."),
        _error("FTRCFG_STREAM_LIMIT_TOO_LOW", "logs.max_stream_bytes", "Stream limit is below minimum."),
        _error("FTRCFG_TIMEOUT_TOO_LOW", "cancel_timeout.default_timeout_seconds", "Timeout is below minimum."),
        _error("FTRCFG_LAUNCH_API_UNAVAILABLE", "launch", "Launch API is not registered in this phase."),
    ]


def _error(code: str, field: str, message: str) -> dict[str, object]:
    return {"code": code, "field": field, "message": message}


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "schema 稳定化只能基于已保存运行配置。")


def _check_execution_config(execution_config_report: dict[str, Any] | None) -> dict[str, object]:
    if not execution_config_report:
        return _check("execution_config", "error", "缺少执行配置需求报告", "需要先生成 Runner 执行配置报告。")
    if execution_config_report.get("status") == "configuration_required":
        return _check("execution_config", "pass", "执行配置需求已生成", "可以稳定配置 schema。")
    return _check("execution_config", "error", "执行配置需求未就绪", str(execution_config_report.get("status") or "unknown"))


def _check_config_check(config_check_report: dict[str, Any] | None) -> dict[str, object]:
    if not config_check_report:
        return _check("config_check", "error", "缺少配置检查报告", "需要先生成配置检查报告。")
    if config_check_report.get("status") in {"config_missing", "config_present_but_launch_disabled"}:
        return _check("config_check", "pass", "配置检查链路已就绪", str(config_check_report.get("status")))
    return _check("config_check", "error", "配置检查存在阻塞项", str(config_check_report.get("status") or "unknown"))


def _check_version_contract(schema: dict[str, object]) -> dict[str, object]:
    versions = schema.get("supported_versions")
    if isinstance(versions, list) and RUNNER_CONFIG_FILE_SCHEMA_VERSION in versions:
        return _check("version_contract", "pass", "配置版本已固定", RUNNER_CONFIG_FILE_SCHEMA_VERSION)
    return _check("version_contract", "error", "配置版本未固定", "缺少 flowtrace_runner_config.v1。")


def _check_default_disabled(schema: dict[str, object]) -> dict[str, object]:
    default_policy = schema.get("default_policy") if isinstance(schema.get("default_policy"), dict) else {}
    if default_policy.get("runner.enable_real_execution") is False and default_policy.get("launch_enabled") is False:
        return _check("default_disabled", "pass", "默认保持禁用", "schema 合规也不会自动启用真实执行。")
    return _check("default_disabled", "error", "默认禁用策略缺失", "真实执行必须默认关闭。")


def _check_compatibility_rules(schema: dict[str, object]) -> dict[str, object]:
    rules = schema.get("compatibility_rules")
    if isinstance(rules, list) and len(rules) >= 6:
        return _check("compatibility_rules", "pass", "兼容性规则已固定", f"{len(rules)} 条规则。")
    return _check("compatibility_rules", "error", "兼容性规则不足", "需要明确版本、字段和默认值兼容策略。")


def _check_error_map(schema: dict[str, object]) -> dict[str, object]:
    error_map = schema.get("error_map")
    if isinstance(error_map, list) and len(error_map) >= 8:
        return _check("error_map", "pass", "错误码映射已固定", f"{len(error_map)} 个错误码。")
    return _check("error_map", "error", "错误码映射不足", "需要稳定错误码以供 UI 和真实测试复用。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只输出 schema 稳定化报告。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    return "schema_stabilization_required"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    return "schema_stabilization_required"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "配置 schema 稳定化前置条件未满足",
        "schema_stabilization_required": "配置 schema 已稳定但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并生成执行配置与配置检查报告后，再查看 schema 稳定化结果。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复 schema 稳定化前置条件",
                "action": failed.get("detail") or "完成前置条件后再继续。",
            }
    return {
        "title": "配置 schema 已稳定",
        "action": "字段版本、兼容性规则和错误码已固定；真实执行仍保持禁用且没有启动 API。",
    }


def _safety() -> dict[str, object]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "config_schema_stabilization_only": True,
        "reads_config_file": False,
        "creates_config_file": False,
        "writes_config_file": False,
        "writes_user_project": False,
        "registers_post_api": False,
        "registers_launch_api": False,
        "imports_adapter": False,
        "calls_execution_adapter": False,
        "creates_session": False,
        "mutates_session_state": False,
        "opens_stdout_stderr": False,
        "reads_runner_events": False,
        "writes_runner_events": False,
        "reads_audit_log": False,
        "writes_audit_log": False,
        "collects_authorization": False,
        "stores_authorization": False,
        "grants_permission": False,
    }
