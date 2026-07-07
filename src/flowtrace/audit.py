from __future__ import annotations

from typing import Any


AUDIT_VERSION = "project_audit.v1"


def build_project_audit(
    project_model: dict[str, Any],
    readiness: dict[str, Any],
    coverage: dict[str, Any],
    runs: list[dict[str, Any]],
    issues_by_run: list[dict[str, Any]],
) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    findings.extend(_scan_findings(project_model))
    findings.extend(_readiness_findings(readiness))
    findings.extend(_coverage_findings(coverage, project_model))
    findings.extend(_issue_findings(issues_by_run))
    findings = _dedupe_findings(findings)
    findings.sort(key=lambda item: (_severity_rank(str(item["severity"])), str(item["layer"]), str(item["target"])))

    return {
        "schema_version": AUDIT_VERSION,
        "context": project_model.get("context"),
        "status": _audit_status(findings),
        "summary": {
            "finding_count": len(findings),
            "critical_count": sum(1 for item in findings if item["severity"] == "critical"),
            "error_count": sum(1 for item in findings if item["severity"] == "error"),
            "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
            "info_count": sum(1 for item in findings if item["severity"] == "info"),
            "run_count": len(runs),
        },
        "findings": findings,
        "next_actions": _next_actions(findings),
    }


def _scan_findings(project_model: dict[str, Any]) -> list[dict[str, object]]:
    result = []
    for item in project_model.get("scan_errors", []) if isinstance(project_model.get("scan_errors"), list) else []:
        if not isinstance(item, dict):
            continue
        result.append(
            _finding(
                "scan_error",
                "critical",
                "Project Scanner",
                item.get("file") or "未知文件",
                "项目文件无法扫描",
                f"{item.get('error')}: {item.get('message')}",
                "修复该文件的语法或编码问题，否则项目结构与接入状态可能不完整。",
                evidence={"file": item.get("file"), "line": item.get("line")},
                location={"kind": "file", "file": item.get("file"), "line": item.get("line")},
            )
        )
    return result


def _readiness_findings(readiness: dict[str, Any]) -> list[dict[str, object]]:
    result = []
    for check in readiness.get("checks", []) if isinstance(readiness.get("checks"), list) else []:
        if not isinstance(check, dict) or check.get("status") == "pass":
            continue
        severity = "error" if check.get("status") == "error" else "warning"
        result.append(
            _finding(
                f"readiness:{check.get('key')}",
                severity,
                _layer_for_check(str(check.get("key") or "")),
                check.get("key") or "readiness",
                check.get("title") or "接入状态检查未通过",
                check.get("detail") or "",
                check.get("action") or "按接入状态建议处理。",
                evidence={"check": check.get("key")},
                location={"kind": "check", "check": check.get("key")},
            )
        )
    return result


def _coverage_findings(coverage: dict[str, Any], project_model: dict[str, Any]) -> list[dict[str, object]]:
    result = []
    uncovered = _strings(coverage.get("uncovered_methods", []))
    runtime_only = _strings(coverage.get("runtime_only_methods", []))
    traced_methods = set(_strings(project_model.get("traced_methods", [])))
    contract_methods = set(_strings(project_model.get("contract_methods", [])))
    missing_contract = sorted(traced_methods - contract_methods)

    for method in uncovered:
        result.append(
            _finding(
                f"coverage:uncovered:{method}",
                "warning",
                "Analysis",
                method,
                "声明方法未被运行覆盖",
                "该方法已出现在 trace/contract 声明中，但当前运行记录没有覆盖它。",
                "补充真实流程或模拟输入，让该方法至少被执行一次。",
                evidence={"method": method},
                location={"kind": "method", "method": method},
            )
        )
    for method in runtime_only:
        result.append(
            _finding(
                f"coverage:runtime_only:{method}",
                "warning",
                "Project Scanner",
                method,
                "运行方法无法对齐静态项目",
                "运行记录中出现该方法，但静态扫描没有在目标项目中找到对应声明。",
                "确认目标项目根目录是否正确，或检查该方法是否来自外部包、动态包装、生成代码。",
                evidence={"method": method},
                location={"kind": "method", "method": method},
            )
        )
    for method in missing_contract:
        result.append(
            _finding(
                f"contract:missing:{method}",
                "warning",
                "Contract",
                method,
                "追踪方法缺少 contract",
                "该方法已接入 trace_node，但没有声明输入/输出契约，无法稳定判断参数结构变化。",
                "为该方法补充 contract，优先覆盖跨层传参边界的输入和输出字段。",
                evidence={"method": method},
                location={"kind": "method", "method": method},
            )
        )
    return result


def _issue_findings(issues_by_run: list[dict[str, Any]]) -> list[dict[str, object]]:
    result = []
    for run_report in issues_by_run:
        run_id = run_report.get("run_id")
        label = run_report.get("label")
        report = run_report.get("issues") if isinstance(run_report.get("issues"), dict) else {}
        issues = report.get("issues", []) if isinstance(report.get("issues"), list) else []
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            result.append(_finding_from_issue(issue, run_id, label))
    return result


def _finding_from_issue(issue: dict[str, Any], run_id: object, label: object) -> dict[str, object]:
    kind = str(issue.get("kind") or "runtime_issue")
    severity = "error" if issue.get("severity") == "error" else "warning"
    if kind == "runtime_error":
        layer = "Instrumentation"
        title = "运行异常"
        action = "先打开问题列表查看异常堆栈，确认参数缺失、类型错误或业务异常来源。"
    elif kind in {"input_contract_failure", "output_contract_failure"}:
        layer = "Contract"
        title = issue.get("title") or "契约失败"
        action = "检查该边的上级输出和下级输入，确认字段是否缺失、额外或类型不匹配。"
    elif kind == "handoff_diff":
        layer = "Analysis"
        title = "参数交接发生变化"
        action = "检查数据流边，确认字段变化是否符合业务预期；若不符合，优先修复上游输出。"
    else:
        layer = "Analysis"
        title = issue.get("title") or "运行问题"
        action = "查看关联运行记录和数据流边。"
    target = issue.get("edge") or issue.get("node") or issue.get("id") or kind
    return _finding(
        f"issue:{run_id}:{issue.get('id') or kind}",
        severity,
        layer,
        target,
        title,
        issue.get("message") or "",
        action,
        evidence={
            "run_id": run_id,
            "run_label": label,
            "issue_kind": kind,
            "node": issue.get("node"),
            "edge": issue.get("edge"),
        },
        location={
            "kind": "runtime_issue",
            "run_id": run_id,
            "node": issue.get("node"),
            "edge": issue.get("edge"),
        },
    )


def _finding(
    finding_id: str,
    severity: str,
    layer: str,
    target: object,
    title: object,
    detail: object,
    action: object,
    *,
    evidence: dict[str, object] | None = None,
    location: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "severity": severity,
        "layer": layer,
        "target": str(target),
        "title": str(title),
        "detail": str(detail),
        "action": str(action),
        "evidence": evidence or {},
        "location": location or {},
    }


def _layer_for_check(key: str) -> str:
    return {
        "scan_errors": "Project Scanner",
        "declared_methods": "Instrumentation",
        "runs": "Storage",
        "coverage": "Analysis",
        "runtime_only": "Project Scanner",
        "contracts": "Contract",
        "runtime_issues": "Analysis",
        "workflow_candidates": "Analysis",
    }.get(key, "Analysis")


def _audit_status(findings: list[dict[str, object]]) -> str:
    severities = {item["severity"] for item in findings}
    if "critical" in severities:
        return "blocked"
    if "error" in severities:
        return "fail"
    if "warning" in severities:
        return "warn"
    return "pass"


def _next_actions(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "finding_id": item["id"],
            "priority": "high" if item["severity"] in {"critical", "error"} else "medium",
            "title": item["title"],
            "target": item["target"],
            "action": item["action"],
        }
        for item in findings[:8]
    ]


def _dedupe_findings(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    seen = set()
    for item in findings:
        key = (item.get("layer"), item.get("target"), item.get("title"), item.get("detail"))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _severity_rank(severity: str) -> int:
    return {"critical": 0, "error": 1, "warning": 2, "info": 3}.get(severity, 4)


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]
