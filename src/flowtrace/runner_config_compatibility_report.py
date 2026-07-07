from __future__ import annotations

from typing import Any

from .runner_config_schema_stabilization import runner_config_schema_stabilization_schema


RUNNER_CONFIG_COMPATIBILITY_REPORT_VERSION = "project_runner_config_compatibility_reports.v1"
RUNNER_CONFIG_COMPATIBILITY_REPORT_SCHEMA_VERSION = "runner_config_compatibility_report_schema.v1"


def build_project_runner_config_compatibility_reports(
    project_context: dict[str, Any],
    run_profile_collection: dict[str, Any],
    config_schema_stabilizations: dict[str, Any],
    execution_config_checks: dict[str, Any],
) -> dict[str, object]:
    saved_profiles = [
        item for item in run_profile_collection.get("saved_profiles", []) if isinstance(item, dict) and item.get("id")
    ]
    schema_report_by_profile = {
        str(report.get("profile_id")): report
        for report in config_schema_stabilizations.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    check_report_by_profile = {
        str(report.get("profile_id")): report
        for report in execution_config_checks.get("reports", [])
        if isinstance(report, dict) and report.get("profile_id")
    }
    compatibility_schema = runner_config_compatibility_report_schema(project_context)
    config_file = execution_config_checks.get("config_file") if isinstance(execution_config_checks.get("config_file"), dict) else {}
    reports = [
        _compatibility_report(
            profile,
            schema_report_by_profile.get(str(profile.get("id"))),
            check_report_by_profile.get(str(profile.get("id"))),
            config_file,
            compatibility_schema,
        )
        for profile in saved_profiles
    ]
    issues = [issue for report in reports for issue in report.get("compatibility_issues", [])]
    index_entries = [entry for report in reports for entry in report.get("index_entries", [])]
    status = _collection_status(reports, saved_profiles)
    return {
        "schema_version": RUNNER_CONFIG_COMPATIBILITY_REPORT_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "saved_profile_count": len(saved_profiles),
            "report_count": len(reports),
            "config_present_count": sum(1 for report in reports if report["config_file_status"] == "present"),
            "compatibility_report_required_count": sum(
                1 for report in reports if report["status"] == "compatibility_report_required"
            ),
            "config_missing_count": sum(1 for report in reports if report["status"] == "config_missing"),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "compatibility_issue_count": len(issues),
            "missing_field_count": sum(1 for issue in issues if issue["kind"] == "missing_field"),
            "type_mismatch_count": sum(1 for issue in issues if issue["kind"] == "type_mismatch"),
            "unsupported_version_count": sum(1 for issue in issues if issue["kind"] == "unsupported_version"),
            "default_violation_count": sum(1 for issue in issues if issue["kind"] == "default_violation"),
            "issue_navigation_target_count": len(index_entries),
            "launchable_count": 0,
        },
        "compatibility_report_schema": compatibility_schema,
        "config_file": _public_config_file(config_file),
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, reports),
    }


def runner_config_compatibility_report_schema(project_context: dict[str, Any]) -> dict[str, object]:
    stable_schema = runner_config_schema_stabilization_schema(project_context)
    return {
        "schema_version": RUNNER_CONFIG_COMPATIBILITY_REPORT_SCHEMA_VERSION,
        "stable_config_schema_version": stable_schema["config_file_schema_version"],
        "supported_versions": stable_schema["supported_versions"],
        "field_contracts": stable_schema["field_contracts"],
        "compatibility_rules": stable_schema["compatibility_rules"],
        "error_map": stable_schema["error_map"],
        "issue_kinds": [
            "config_missing",
            "missing_field",
            "type_mismatch",
            "unsupported_version",
            "minimum_violation",
            "default_violation",
        ],
        "blocked_actions": [
            "reading config files directly in this layer",
            "creating or modifying config files",
            "executing commands",
            "creating processes",
            "registering launch/cancel/timeout POST APIs",
            "enabling launch UI",
            "calling execution adapters",
            "creating or mutating runner sessions",
            "collecting or storing authorization",
            "writing user project files",
        ],
    }


def _compatibility_report(
    profile: dict[str, Any],
    schema_report: dict[str, Any] | None,
    config_check_report: dict[str, Any] | None,
    config_file: dict[str, Any],
    compatibility_schema: dict[str, object],
) -> dict[str, object]:
    config_data = config_file.get("data") if isinstance(config_file.get("data"), dict) else None
    issues = _compatibility_issues(config_data, config_file, compatibility_schema)
    index_entries = _issue_index_entries(profile, issues)
    checks = [
        _check_saved_profile(profile),
        _check_schema_stabilization(schema_report),
        _check_config_check(config_check_report),
        _check_config_presence(config_file),
        _check_issue_map(issues),
        _check_no_execution(),
    ]
    status = _report_status(checks, config_file)
    return {
        "id": f"runner_config_compatibility_report:{profile.get('id')}",
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "schema_stabilization_status": schema_report.get("status") if isinstance(schema_report, dict) else "missing",
        "config_check_status": config_check_report.get("status") if isinstance(config_check_report, dict) else "missing",
        "config_file_status": str(config_file.get("status") or "missing"),
        "config_file": _public_config_file(config_file),
        "stable_config_schema_version": compatibility_schema["stable_config_schema_version"],
        "compatibility_issues": issues,
        "index_entries": index_entries,
        "checks": checks,
        "execution_boundary": (
            "当前只基于上游配置检查载入的内存 payload 生成兼容性报告；不会直接读取配置文件、不会写配置、"
            "不会执行命令、创建进程、开放真实启动 API 或修改用户项目。"
        ),
    }


def _compatibility_issues(
    data: dict[str, Any] | None,
    config_file: dict[str, Any],
    compatibility_schema: dict[str, object],
) -> list[dict[str, object]]:
    if config_file.get("status") != "present":
        return [
            _issue(
                "config_missing",
                "flowtrace.runner.json",
                "FTRCFG_REQUIRED_FIELD_MISSING",
                "未发现候选配置文件，无法进行字段兼容性判断。",
                "warn",
                None,
                "present config",
            )
        ]
    if data is None:
        return [
            _issue(
                "type_mismatch",
                "flowtrace.runner.json",
                "FTRCFG_TYPE_MISMATCH",
                "配置根节点必须是 JSON object。",
                "error",
                type(data).__name__,
                "object",
            )
        ]

    issues: list[dict[str, object]] = []
    supported_versions = set(str(item) for item in compatibility_schema.get("supported_versions", []))
    schema_version = _get(data, ["schema_version"])
    if schema_version not in supported_versions:
        kind = "missing_field" if schema_version is None else "unsupported_version"
        issues.append(
            _issue(
                kind,
                "schema_version",
                "FTRCFG_SCHEMA_VERSION_REQUIRED" if schema_version is None else "FTRCFG_UNSUPPORTED_SCHEMA_VERSION",
                "配置 schema_version 缺失或不受支持。",
                "error",
                schema_version,
                ", ".join(sorted(supported_versions)),
            )
        )

    for contract in compatibility_schema.get("field_contracts", []):
        if not isinstance(contract, dict):
            continue
        path = str(contract.get("path") or "")
        if path == "schema_version":
            continue
        value = _get(data, path.split("."))
        expected_type = str(contract.get("type") or "")
        if value is None:
            issues.append(
                _issue(
                    "missing_field",
                    path,
                    str(contract.get("error_code") or "FTRCFG_REQUIRED_FIELD_MISSING"),
                    "缺少必需配置字段。",
                    "error",
                    None,
                    expected_type,
                )
            )
            continue
        if not _matches_type(value, expected_type):
            issues.append(
                _issue(
                    "type_mismatch",
                    path,
                    "FTRCFG_TYPE_MISMATCH",
                    "配置字段类型不匹配。",
                    "error",
                    type(value).__name__,
                    expected_type,
                )
            )
            continue
        if expected_type == "integer" and isinstance(contract.get("default"), int) and value < contract["default"]:
            issues.append(
                _issue(
                    "minimum_violation",
                    path,
                    str(contract.get("error_code") or "FTRCFG_STREAM_LIMIT_TOO_LOW"),
                    "数值低于稳定 schema 允许的最小值。",
                    "error",
                    value,
                    contract["default"],
                )
            )
        if path in {"process.no_shell_string", "process.argv_must_be_tokenized"} and value is not True:
            issues.append(
                _issue(
                    "default_violation",
                    path,
                    str(contract.get("error_code") or "FTRCFG_TYPE_MISMATCH"),
                    "安全默认值必须保持为 true。",
                    "error",
                    value,
                    True,
                )
            )
        if path == "process.inherit_environment" and value is not False:
            issues.append(
                _issue(
                    "default_violation",
                    path,
                    "FTRCFG_ENV_INHERITANCE_DISABLED",
                    "默认禁止继承外部环境变量。",
                    "error",
                    value,
                    False,
                )
            )
    return issues


def _get(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return True


def _issue(
    kind: str,
    field: str,
    error_code: str,
    message: str,
    severity: str,
    actual: object,
    expected: object,
) -> dict[str, object]:
    item_key = _issue_key(error_code, field)
    return {
        "kind": kind,
        "field": field,
        "error_code": error_code,
        "message": message,
        "severity": severity,
        "actual": actual,
        "expected": expected,
        "navigation": {
            "stage_key": "runner_config_compatibility_reports",
            "evidence_group": "配置问题定位",
            "item_key": item_key,
        },
    }


def _issue_index_entries(profile: dict[str, Any], issues: list[dict[str, object]]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for issue in issues:
        navigation = issue.get("navigation") if isinstance(issue.get("navigation"), dict) else {}
        item_key = str(navigation.get("item_key") or _issue_key(issue.get("error_code"), issue.get("field")))
        field = str(issue.get("field") or "")
        message = str(issue.get("message") or "")
        entries.append(
            {
                "key": item_key,
                "kind": "config_compatibility_issue",
                "title": str(issue.get("error_code") or issue.get("kind") or "config_issue"),
                "detail": f"{field}: {message}" if field else message,
                "status": str(issue.get("severity") or "warn"),
                "profile_id": profile.get("id"),
                "profile_label": profile.get("label"),
                "field": field,
                "error_code": issue.get("error_code"),
                "issue_kind": issue.get("kind"),
                "navigation": {
                    "stage_key": "runner_config_compatibility_reports",
                    "evidence_group": "配置问题定位",
                    "item_key": item_key,
                },
            }
        )
    return entries


def _issue_key(error_code: object, field: object) -> str:
    raw = f"{error_code or 'issue'}:{field or 'config'}"
    slug = "".join(char.lower() if char.isalnum() else "_" for char in raw)
    return "config_issue:" + "_".join(part for part in slug.split("_") if part)


def _public_config_file(config_file: dict[str, Any]) -> dict[str, object]:
    return {
        "status": config_file.get("status") or "missing",
        "path": config_file.get("path"),
        "candidate_paths": config_file.get("candidate_paths") or [],
        "error": config_file.get("error"),
    }


def _check_saved_profile(profile: dict[str, Any]) -> dict[str, object]:
    if profile.get("saved_at"):
        return _check("saved_profile", "pass", "运行配置已保存", str(profile.get("saved_at")))
    return _check("saved_profile", "error", "缺少保存记录", "兼容性报告只能基于已保存运行配置。")


def _check_schema_stabilization(schema_report: dict[str, Any] | None) -> dict[str, object]:
    if not schema_report:
        return _check("schema_stabilization", "error", "缺少配置 schema 稳定化报告", "需要先生成 schema 稳定化报告。")
    if schema_report.get("status") == "schema_stabilization_required":
        return _check("schema_stabilization", "pass", "配置 schema 已稳定", str(schema_report.get("stable_config_schema_version") or ""))
    return _check("schema_stabilization", "error", "配置 schema 稳定化未就绪", str(schema_report.get("status") or "unknown"))


def _check_config_check(config_check_report: dict[str, Any] | None) -> dict[str, object]:
    if not config_check_report:
        return _check("config_check", "error", "缺少配置检查报告", "需要先完成配置检查。")
    if config_check_report.get("status") in {"config_missing", "config_present_but_launch_disabled"}:
        return _check("config_check", "pass", "配置检查报告可用", str(config_check_report.get("status")))
    return _check("config_check", "error", "配置检查报告阻塞", str(config_check_report.get("status") or "unknown"))


def _check_config_presence(config_file: dict[str, Any]) -> dict[str, object]:
    status = str(config_file.get("status") or "missing")
    if status == "present":
        return _check("config_file", "pass", "候选配置 payload 可用", str(config_file.get("path") or ""))
    if status == "missing":
        return _check("config_file", "warn", "未发现候选配置", "当前只报告缺失，不会创建 flowtrace.runner.json。")
    return _check("config_file", "error", "候选配置不可用", str(config_file.get("error") or status))


def _check_issue_map(issues: list[dict[str, object]]) -> dict[str, object]:
    if not issues:
        return _check("compatibility_issues", "pass", "未发现兼容性问题", "候选配置字段符合稳定 schema。")
    error_count = sum(1 for issue in issues if issue.get("severity") == "error")
    status = "warn" if error_count else "pass"
    return _check("compatibility_issues", status, "已生成兼容性问题映射", f"{len(issues)} 项问题，{error_count} 项错误。")


def _check_no_execution() -> dict[str, object]:
    return _check("no_execution", "pass", "当前不会执行命令", "本阶段只生成配置兼容性报告。")


def _check(key: str, status: str, title: str, detail: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail}


def _report_status(checks: list[dict[str, object]], config_file: dict[str, Any]) -> str:
    statuses = {str(check.get("status")) for check in checks}
    if "error" in statuses:
        return "blocked"
    if config_file.get("status") == "present":
        return "compatibility_report_required"
    return "config_missing"


def _collection_status(reports: list[dict[str, object]], saved_profiles: list[dict[str, Any]]) -> str:
    if not saved_profiles:
        return "no_saved_profiles"
    if any(report.get("status") == "blocked" for report in reports):
        return "blocked"
    if any(report.get("status") == "compatibility_report_required" for report in reports):
        return "compatibility_report_required"
    return "config_missing"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "暂无保存配置",
        "blocked": "配置兼容性报告存在阻塞项",
        "config_missing": "未发现候选配置",
        "compatibility_report_required": "配置兼容性报告已生成但真实执行仍禁用",
    }.get(status, status)


def _next_action(status: str, reports: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {
            "title": "先保存运行配置",
            "action": "保存运行配置并完成配置 schema 稳定化后，再生成兼容性报告。",
        }
    for report in reports:
        if report.get("status") == "blocked":
            failed = next((check for check in report["checks"] if check["status"] == "error"), {})
            return {
                "title": failed.get("title") or "修复配置兼容性阻塞项",
                "action": failed.get("detail") or "修复前置条件后再继续。",
            }
    if status == "config_missing":
        return {
            "title": "等待候选配置",
            "action": "当前只报告配置缺失，不会创建 flowtrace.runner.json。",
        }
    return {
        "title": "兼容性报告已生成",
        "action": "请按稳定错误码修复候选配置；真实执行仍保持禁用且没有启动 API。",
    }


def _safety() -> dict[str, object]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "config_compatibility_report_only": True,
        "reads_config_file": False,
        "uses_in_memory_config_payload": True,
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
