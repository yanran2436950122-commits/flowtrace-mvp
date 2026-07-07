from __future__ import annotations

from typing import Any


READINESS_VERSION = "project_readiness.v1"


def build_project_readiness(
    project_model: dict[str, Any],
    coverage: dict[str, Any],
    runs: list[dict[str, Any]],
    issues_by_run: list[dict[str, Any]],
) -> dict[str, object]:
    summary = coverage.get("summary", {}) if isinstance(coverage.get("summary"), dict) else {}
    scan_errors = [item for item in project_model.get("scan_errors", []) if isinstance(item, dict)]
    traced_methods = set(_strings(project_model.get("traced_methods", [])))
    contract_methods = set(_strings(project_model.get("contract_methods", [])))
    declared_methods = set(_strings(project_model.get("declared_methods", [])))
    known_methods = declared_methods | traced_methods | contract_methods
    covered_methods = set(_strings(coverage.get("covered_methods", [])))
    uncovered_methods = set(_strings(coverage.get("uncovered_methods", [])))
    runtime_only_methods = set(_strings(coverage.get("runtime_only_methods", [])))
    missing_contract_methods = sorted((traced_methods | covered_methods) - contract_methods)
    aggregate_issues = _aggregate_issues(issues_by_run)
    workflow_candidates = _workflow_candidates(project_model, covered_methods)
    checks = [
        _check_scan_errors(scan_errors),
        _check_declared_methods(known_methods),
        _check_runs(runs),
        _check_coverage(summary, uncovered_methods),
        _check_runtime_only(runtime_only_methods),
        _check_contracts(missing_contract_methods),
        _check_runtime_issues(aggregate_issues),
        _check_workflow_candidates(workflow_candidates),
    ]
    status = _readiness_status(checks)

    return {
        "schema_version": READINESS_VERSION,
        "context": project_model.get("context"),
        "status": status,
        "status_label": _status_label(status),
        "summary": {
            "run_count": len(runs),
            "known_method_count": summary.get("known_method_count", len(known_methods)),
            "covered_method_count": summary.get("covered_method_count", len(covered_methods)),
            "coverage_ratio": summary.get("coverage_ratio", 0),
            "missing_contract_count": len(missing_contract_methods),
            "runtime_only_method_count": len(runtime_only_methods),
            "issue_count": aggregate_issues["total"],
            "error_count": aggregate_issues["errors"],
            "warning_count": aggregate_issues["warnings"],
            "workflow_candidate_count": len(workflow_candidates),
            "scan_error_count": len(scan_errors),
        },
        "checks": checks,
        "workflow_candidates": workflow_candidates,
        "method_groups": {
            "covered": sorted(covered_methods),
            "uncovered": sorted(uncovered_methods),
            "runtime_only": sorted(runtime_only_methods),
            "missing_contract": missing_contract_methods,
        },
        "risk_edges": aggregate_issues["risk_edges"],
        "next_actions": _next_actions(checks),
    }


def _check_scan_errors(scan_errors: list[dict[str, Any]]) -> dict[str, object]:
    if scan_errors:
        return _check(
            "scan_errors",
            "error",
            "项目扫描存在错误",
            f"{len(scan_errors)} 个文件无法扫描，静态结构可能不完整。",
            "先修复语法或编码问题，再判断接入完整度。",
        )
    return _check("scan_errors", "pass", "项目扫描正常", "未发现扫描错误。", "")


def _check_declared_methods(known_methods: set[str]) -> dict[str, object]:
    if not known_methods:
        return _check(
            "declared_methods",
            "error",
            "尚未发现可追踪方法",
            "项目内没有 trace_node 或 contract 声明。",
            "先在真实 workflow 的关键方法上添加 trace_node。",
        )
    return _check(
        "declared_methods",
        "pass",
        "已发现可追踪方法",
        f"当前识别到 {len(known_methods)} 个声明方法。",
        "",
    )


def _check_runs(runs: list[dict[str, Any]]) -> dict[str, object]:
    if not runs:
        return _check(
            "runs",
            "error",
            "尚无运行记录",
            "没有 .flowtrace 运行数据，无法判断真实流程覆盖。",
            "运行一次真实流程或仿真流程，然后刷新运行记录。",
        )
    event_count = sum(int(run.get("event_count") or 0) for run in runs)
    return _check("runs", "pass", "已发现运行记录", f"{len(runs)} 次运行，{event_count} 条事件。", "")


def _check_coverage(summary: dict[str, Any], uncovered_methods: set[str]) -> dict[str, object]:
    known = int(summary.get("known_method_count") or 0)
    covered = int(summary.get("covered_method_count") or 0)
    if not known:
        return _check("coverage", "error", "无法计算覆盖", "没有声明方法可供覆盖对齐。", "先添加 trace_node。")
    if uncovered_methods:
        return _check(
            "coverage",
            "warn",
            "存在未覆盖声明方法",
            f"{covered}/{known} 个方法已被运行覆盖，{len(uncovered_methods)} 个声明方法未跑到。",
            "补充真实流程或模拟输入，优先覆盖核心 workflow。",
        )
    return _check("coverage", "pass", "运行覆盖完整", f"{covered}/{known} 个声明方法已覆盖。", "")


def _check_runtime_only(runtime_only_methods: set[str]) -> dict[str, object]:
    if runtime_only_methods:
        return _check(
            "runtime_only",
            "warn",
            "存在运行时孤儿方法",
            f"{len(runtime_only_methods)} 个运行时方法没有在目标项目静态结构中找到。",
            "确认目标项目根目录是否正确，或检查动态包装/外部包来源。",
        )
    return _check("runtime_only", "pass", "运行方法均可对齐", "没有运行时孤儿方法。", "")


def _check_contracts(missing_contract_methods: list[str]) -> dict[str, object]:
    if missing_contract_methods:
        return _check(
            "contracts",
            "warn",
            "部分追踪方法缺少 contract",
            f"{len(missing_contract_methods)} 个已追踪方法缺少输入/输出契约。",
            "优先为跨层传参边界补充 contract。",
        )
    return _check("contracts", "pass", "契约声明完整", "已追踪方法均存在 contract 声明。", "")


def _check_runtime_issues(aggregate_issues: dict[str, Any]) -> dict[str, object]:
    if aggregate_issues["errors"]:
        return _check(
            "runtime_issues",
            "error",
            "运行存在错误",
            f"{aggregate_issues['errors']} 个错误，{aggregate_issues['warnings']} 个警告。",
            "先查看问题列表中的运行异常和契约失败。",
        )
    if aggregate_issues["warnings"]:
        return _check(
            "runtime_issues",
            "warn",
            "运行存在参数风险",
            f"{aggregate_issues['warnings']} 个警告，多数来自字段变化或交接差异。",
            "检查数据流边，确认字段变化是否符合预期。",
        )
    return _check("runtime_issues", "pass", "运行问题清洁", "当前运行记录没有错误或警告。", "")


def _check_workflow_candidates(workflow_candidates: list[dict[str, object]]) -> dict[str, object]:
    if not workflow_candidates:
        return _check(
            "workflow_candidates",
            "warn",
            "workflow 候选不明确",
            "未识别到明确 workflow 候选。",
            "确认入口候选和核心方法命名，必要时在 workflow 方法上添加 trace_node。",
        )
    return _check("workflow_candidates", "pass", "workflow 候选明确", f"识别到 {len(workflow_candidates)} 个候选。", "")


def _check(key: str, status: str, title: str, detail: str, action: str) -> dict[str, object]:
    return {"key": key, "status": status, "title": title, "detail": detail, "action": action}


def _readiness_status(checks: list[dict[str, object]]) -> str:
    error_keys = {str(check["key"]) for check in checks if check.get("status") == "error"}
    warn_keys = {str(check["key"]) for check in checks if check.get("status") == "warn"}
    if "scan_errors" in error_keys:
        return "blocked"
    if "declared_methods" in error_keys:
        return "not_connected"
    if "runs" in error_keys:
        return "no_runs"
    if "runtime_issues" in error_keys:
        return "risky"
    if error_keys or warn_keys:
        return "partial"
    return "ready"


def _status_label(status: str) -> str:
    return {
        "blocked": "扫描受阻",
        "not_connected": "未接入",
        "no_runs": "缺少运行",
        "partial": "部分接入",
        "risky": "存在风险",
        "ready": "可用于排查",
    }.get(status, status)


def _next_actions(checks: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for check in checks:
        if check.get("status") == "pass" or not check.get("action"):
            continue
        result.append(
            {
                "check": check["key"],
                "priority": "high" if check.get("status") == "error" else "medium",
                "title": check["title"],
                "action": check["action"],
            }
        )
    return result


def _workflow_candidates(project_model: dict[str, Any], covered_methods: set[str]) -> list[dict[str, object]]:
    result = []
    for method in _strings(project_model.get("declared_methods", [])):
        lower = method.lower()
        if method in covered_methods and ("workflow" in lower or "process" in lower or "handle" in lower or "submit" in lower):
            result.append({"id": method, "label": method, "source": "covered_method", "covered": True})
    for entrypoint in project_model.get("entrypoints", []):
        if not isinstance(entrypoint, dict):
            continue
        label = str(entrypoint.get("label") or entrypoint.get("id") or "")
        result.append(
            {
                "id": str(entrypoint.get("id") or label),
                "label": label,
                "source": str(entrypoint.get("kind") or "entrypoint"),
                "file": entrypoint.get("file"),
                "line": entrypoint.get("line"),
                "covered": False,
            }
        )
    return _dedupe_candidates(result)[:12]


def _dedupe_candidates(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    seen = set()
    for candidate in candidates:
        key = candidate.get("id")
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def _aggregate_issues(issues_by_run: list[dict[str, Any]]) -> dict[str, Any]:
    total = 0
    errors = 0
    warnings = 0
    risk_edges = []
    for run_report in issues_by_run:
        run_id = run_report.get("run_id")
        report = run_report.get("issues") if isinstance(run_report.get("issues"), dict) else {}
        summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
        total += int(summary.get("total") or 0)
        errors += int(summary.get("errors") or 0)
        warnings += int(summary.get("warnings") or 0)
        for issue in report.get("issues", []) if isinstance(report.get("issues"), list) else []:
            if not isinstance(issue, dict):
                continue
            if issue.get("kind") in {"handoff_diff", "input_contract_failure", "output_contract_failure", "runtime_error"}:
                risk_edges.append(
                    {
                        "run_id": run_id,
                        "severity": issue.get("severity"),
                        "kind": issue.get("kind"),
                        "title": issue.get("title"),
                        "node": issue.get("node"),
                        "edge": issue.get("edge"),
                        "message": issue.get("message"),
                    }
                )
    return {"total": total, "errors": errors, "warnings": warnings, "risk_edges": risk_edges[:20]}


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]
