from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RUNNER_EXECUTION_CONFIG_CHECK_VERSION = "project_runner_execution_config_checks.v1"
RUNNER_EXECUTION_CONFIG_CHECK_SCHEMA_VERSION = "runner_execution_config_check_schema.v1"
CONFIG_FILE_NAME = "flowtrace.runner.json"


def build_project_runner_execution_config_checks(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    execution_configs: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    execution_config_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_configs.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    config_file = _read_config_file(project_context)
    reports = [
        _config_check_report(profile, execution_config_by_profile.get(str(profile.get("id"))), config_file)
        for profile in saved_profiles
    ]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_EXECUTION_CONFIG_CHECK_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "config_present_count": sum(1 for report in reports if report["config_file"]["status"] == "present"),
            "valid_config_count": sum(1 for report in reports if report["status"] == "config_present_but_launch_disabled"),
            "missing_config_count": sum(1 for report in reports if report["status"] == "config_missing"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "config_check_schema": config_check_schema(project_context),
        "config_file": config_file,
        "reports": reports,
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "runner_implemented": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "config_check_only": True,
            "writes_user_project": False,
            "creates_config_file": False,
        },
        "next_action": _next_action(status, reports),
    }


def config_check_schema(project_context: dict[str, Any]) -> dict[str, object]:
    return {
        "schema_version": RUNNER_EXECUTION_CONFIG_CHECK_SCHEMA_VERSION,
        "config_file_name": CONFIG_FILE_NAME,
        "candidate_paths": _candidate_paths(project_context),
        "required_fields": [
            "runner.enable_real_execution",
            "runner.typed_consent",
            "process.no_shell_string",
            "process.argv_must_be_tokenized",
            "process.inherit_environment",
            "logs.stdout_chunk_bytes",
            "logs.stderr_chunk_bytes",
            "logs.max_stream_bytes",
            "cancel_timeout.default_timeout_seconds",
        ],
        "launch_enabled": False,
        "launch_api_available": False,
    }


def _config_check_report(
    profile: dict[str, Any],
    execution_config_report: dict[str, Any] | None,
    config_file: dict[str, Any],
) -> dict[str, object]:
    if config_file.get("status") == "present":
        field_checks = _field_checks(config_file.get("data") if isinstance(config_file.get("data"), dict) else {})
    else:
        field_checks = []
    checks = [
        _check_saved_profile(profile),
        _check_execution_config(execution_config_report),
        _check_config_file(config_file),
        *field_checks,
        _check_no_execution(),
    ]
    status = _report_status(checks, config_file)
    return {
        "id": f"runner_execution_config_check:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "execution_config_status": execution_config_report.get("status") if isinstance(execution_config_report, dict) else "missing",
        "config_file": _public_config_file(config_file),
        "checks": checks,
        "execution_boundary": "当前只读取并校验配置文件；不会创建配置、创建进程或执行命令。",
    }


def _read_config_file(project_context: dict[str, Any]) -> dict[str, Any]:
    candidates = _candidate_paths(project_context)
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return {
                "status": "unreadable",
                "path": str(path),
                "candidate_paths": candidates,
                "error": str(exc),
                "data": None,
            }
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return {
                "status": "invalid_json",
                "path": str(path),
                "candidate_paths": candidates,
                "error": str(exc),
                "data": None,
            }
        return {
            "status": "present",
            "path": str(path),
            "candidate_paths": candidates,
            "error": None,
            "data": data if isinstance(data, dict) else None,
        }
    return {
        "status": "missing",
        "path": None,
        "candidate_paths": candidates,
        "error": None,
        "data": None,
    }


def _candidate_paths(project_context: dict[str, Any]) -> list[str]:
    paths = []
    for key in ("root", "trace_dir"):
        raw_path = project_context.get(key)
        if raw_path:
            paths.append(str(Path(str(raw_path)) / CONFIG_FILE_NAME))
    return list(dict.fromkeys(paths))


def _public_config_file(config_file: dict[str, Any]) -> dict[str, object]:
    return {
        "status": config_file.get("status"),
        "path": config_file.get("path"),
        "candidate_paths": config_file.get("candidate_paths") or [],
        "error": config_file.get("error"),
    }


def _field_checks(data: dict[str, Any]) -> list[dict[str, object]]:
    return [
        _required_value("runner.enable_real_execution", _get(data, ["runner", "enable_real_execution"]), True),
        _required_value("runner.typed_consent", _get(data, ["runner", "typed_consent"]), "RUN TARGET PROJECT"),
        _required_value("process.no_shell_string", _get(data, ["process", "no_shell_string"]), True),
        _required_value("process.argv_must_be_tokenized", _get(data, ["process", "argv_must_be_tokenized"]), True),
        _required_value("process.inherit_environment", _get(data, ["process", "inherit_environment"]), False),
        _required_int("logs.stdout_chunk_bytes", _get(data, ["logs", "stdout_chunk_bytes"]), 4096),
        _required_int("logs.stderr_chunk_bytes", _get(data, ["logs", "stderr_chunk_bytes"]), 4096),
        _required_int("logs.max_stream_bytes", _get(data, ["logs", "max_stream_bytes"]), 2 * 1024 * 1024),
        _required_int("cancel_timeout.default_timeout_seconds", _get(data, ["cancel_timeout", "default_timeout_seconds"]), 120),
    ]


def _get(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _required_value(field: str, value: Any, expected: Any) -> dict[str, object]:
    if value == expected:
        return _check(field, "pass", f"{field} 符合要求", f"expected={expected!r}")
    return _check(field, "error", f"{field} 不符合要求", f"expected={expected!r}, actual={value!r}")


def _required_int(field: str, value: Any, minimum: int) -> dict[str, object]:
    if isinstance(value, int) and value >= minimum:
        return _check(field, "pass", f"{field} 符合要求", f"minimum={minimum}")
    return _check(field, "error", f"{field} 不符合要求", f"minimum={minimum}, actual={value!r}")


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "配置检查只能基于已保存运行配置。")


def _check_execution_config(execution_config_report: dict[str, Any] | None) -> dict[str, object]:
    if not execution_config_report:
        return _check("execution_config", "error", "缺少执行配置需求报告", "需要先生成 Runner 执行配置报告。")
    if execution_config_report.get("status") == "configuration_required":
        return _check("execution_config", "pass", "执行配置需求已生成", "可以读取配置文件并做只读校验。")
    return _check("execution_config", "error", "执行配置需求未就绪", str(execution_config_report.get("status") or "unknown"))


def _check_config_file(config_file: dict[str, Any]) -> dict[str, object]:
    status = str(config_file.get("status") or "missing")
    if status == "present":
        return _check("config_file", "pass", "配置文件已读取", str(config_file.get("path") or ""))
    if status == "missing":
        return _check("config_file", "warn", "未发现配置文件", "当前阶段不会自动创建 flowtrace.runner.json。")
    return _check("config_file", "error", "配置文件无法读取或解析", str(config_file.get("error") or status))


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只读取配置并输出校验报告。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], config_file: dict[str, Any]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if config_file.get("status") == "present":
        return "config_present_but_launch_disabled"
    return "config_missing"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "config_present_but_launch_disabled" for report in reports):
        return "config_present_but_launch_disabled"
    return "config_missing"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "配置检查存在阻塞项",
        "config_missing": "未发现真实执行配置文件",
        "config_present_but_launch_disabled": "配置已读取但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先完成执行配置需求报告",
            "action": "保存运行配置并完成上游确认链路后，再检查配置文件。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复配置检查阻塞项",
                "action": failed.get("detail") or "修复配置文件后再继续。",
            }
    if status == "config_missing":
        return {
            "title": "尚未发现配置文件",
            "action": "当前只报告缺失状态，不会自动创建 flowtrace.runner.json。",
        }
    return {
        "title": "配置文件已读取",
        "action": "配置字段合规；真实执行仍需要服务启动开关和独立 launch API，当前保持禁用。",
    }
