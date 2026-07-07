from __future__ import annotations

from typing import Any


INTEGRATION_PLAN_VERSION = "project_integration_plan.v1"


def build_project_integration_plan(
    project_model: dict[str, Any],
    coverage: dict[str, Any],
    readiness: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, object]:
    """Build a deterministic plan for connecting a target project to FlowTrace."""
    checks = [item for item in readiness.get("checks", []) if isinstance(item, dict)]
    findings = [item for item in audit.get("findings", []) if isinstance(item, dict)]
    blockers = _blockers(checks, findings)
    targets = _execution_targets(project_model, readiness)
    phases = _phases(project_model, coverage, readiness, audit, targets, blockers)

    return {
        "schema_version": INTEGRATION_PLAN_VERSION,
        "context": project_model.get("context"),
        "status": _plan_status(readiness, blockers),
        "summary": {
            "project_name": _project_name(project_model),
            "execution_target_count": len(targets),
            "phase_count": len(phases),
            "blocker_count": len(blockers),
            "readiness_status": readiness.get("status"),
            "audit_status": audit.get("status"),
            "coverage_ratio": _coverage_ratio(coverage),
        },
        "execution_targets": targets,
        "phases": phases,
        "blockers": blockers,
        "validation_gates": _validation_gates(readiness, audit),
        "next_action": _next_action(phases, blockers),
    }


def _project_name(project_model: dict[str, Any]) -> str:
    identity = project_model.get("project_identity")
    if isinstance(identity, dict) and identity.get("name"):
        return str(identity["name"])
    return str(project_model.get("root") or "unknown")


def _coverage_ratio(coverage: dict[str, Any]) -> float:
    summary = coverage.get("summary")
    if not isinstance(summary, dict):
        return 0
    try:
        return float(summary.get("coverage_ratio") or 0)
    except (TypeError, ValueError):
        return 0


def _plan_status(readiness: dict[str, Any], blockers: list[dict[str, object]]) -> str:
    if blockers:
        return "blocked"
    readiness_status = str(readiness.get("status") or "unknown")
    if readiness_status in {"ready", "partial", "risky", "no_runs", "not_connected"}:
        return readiness_status
    return "unknown"


def _execution_targets(project_model: dict[str, Any], readiness: dict[str, Any]) -> list[dict[str, object]]:
    targets: list[dict[str, object]] = []
    for entrypoint in project_model.get("entrypoints", []) if isinstance(project_model.get("entrypoints"), list) else []:
        if not isinstance(entrypoint, dict):
            continue
        targets.append(_target_from_entrypoint(entrypoint))

    for candidate in readiness.get("workflow_candidates", []) if isinstance(readiness.get("workflow_candidates"), list) else []:
        if not isinstance(candidate, dict):
            continue
        targets.append(_target_from_workflow(candidate))

    return _dedupe_targets(targets)[:16]


def _target_from_entrypoint(entrypoint: dict[str, Any]) -> dict[str, object]:
    kind = str(entrypoint.get("kind") or "entrypoint")
    file = str(entrypoint.get("file") or "")
    label = str(entrypoint.get("label") or entrypoint.get("id") or "entrypoint")
    command = _entrypoint_command(kind, file)
    return {
        "id": f"entrypoint:{entrypoint.get('id') or file or label}",
        "kind": "entrypoint",
        "label": label,
        "file": file or None,
        "line": entrypoint.get("line"),
        "confidence": "high" if kind in {"main_guard", "function_name"} else "medium",
        "source": kind,
        "run_hint": command,
        "action": "用真实输入触发该入口，并确认 .flowtrace 下生成运行记录。",
    }


def _entrypoint_command(kind: str, file: str) -> str:
    if kind == "main_guard" and file:
        return f"python {file}"
    if kind == "function_name" and file:
        return f"python {file}"
    if kind == "route_decorator":
        return "启动对应 Web 服务后，通过页面或 HTTP 请求触发该路由。"
    return "按目标项目原有方式启动，并执行一次真实 workflow。"


def _target_from_workflow(candidate: dict[str, Any]) -> dict[str, object]:
    label = str(candidate.get("label") or candidate.get("id") or "workflow")
    return {
        "id": f"workflow:{candidate.get('id') or label}",
        "kind": "workflow",
        "label": label,
        "file": candidate.get("file"),
        "line": candidate.get("line"),
        "confidence": "high" if candidate.get("covered") else "medium",
        "source": candidate.get("source") or "readiness",
        "run_hint": "确保该方法被真实流程调用，而不是只在孤立单测里调用。",
        "action": "把该 workflow 作为主观察对象，优先补齐 trace_node 与 contract。",
    }


def _dedupe_targets(targets: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    seen = set()
    for target in targets:
        key = (target.get("kind"), target.get("label"), target.get("file"), target.get("line"))
        if key in seen:
            continue
        seen.add(key)
        result.append(target)
    return result


def _blockers(checks: list[dict[str, Any]], findings: list[dict[str, Any]]) -> list[dict[str, object]]:
    result = []
    for check in checks:
        if check.get("status") != "error":
            continue
        result.append(
            {
                "id": f"readiness:{check.get('key')}",
                "source": "readiness",
                "title": check.get("title") or check.get("key"),
                "detail": check.get("detail") or "",
                "action": check.get("action") or "",
            }
        )

    for finding in findings:
        if finding.get("severity") not in {"critical", "error"}:
            continue
        result.append(
            {
                "id": f"audit:{finding.get('id')}",
                "source": "audit",
                "title": finding.get("title") or finding.get("kind"),
                "detail": finding.get("detail") or finding.get("message") or "",
                "action": finding.get("action") or "",
            }
        )
    return result[:12]


def _phases(
    project_model: dict[str, Any],
    coverage: dict[str, Any],
    readiness: dict[str, Any],
    audit: dict[str, Any],
    targets: list[dict[str, object]],
    blockers: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [
        {
            "id": "select_project",
            "title": "确认目标项目",
            "status": "done" if project_model.get("context") else "todo",
            "goal": "FlowTrace 读取的是用户选择的目标项目，而不是 viewer 自身。",
            "actions": [_context_action(project_model)],
        },
        {
            "id": "resolve_entry",
            "title": "确认可执行入口",
            "status": "done" if targets else "todo",
            "goal": "找到用户能够真实跑一遍流程的入口。",
            "actions": _target_actions(targets),
        },
        {
            "id": "instrument_boundaries",
            "title": "收敛追踪边界",
            "status": _instrument_status(coverage),
            "goal": "只在 workflow、跨层调用、参数结构变化点接入 trace_node 和 contract。",
            "actions": _instrument_actions(readiness),
        },
        {
            "id": "run_flow",
            "title": "运行真实流程",
            "status": _run_status(readiness),
            "goal": "用真实输入或可复现模拟输入生成运行记录。",
            "actions": ["执行一次完整用户流程；完成后刷新运行记录。"],
        },
        {
            "id": "review_evidence",
            "title": "审查参数流证据",
            "status": "todo" if blockers else _review_status(audit),
            "goal": "通过层级流转、方法数据流、运行对比和问题列表定位参数不同步问题。",
            "actions": _review_actions(audit, blockers),
        },
    ]


def _context_action(project_model: dict[str, Any]) -> str:
    context = project_model.get("context")
    if isinstance(context, dict):
        root = context.get("root") or project_model.get("root")
        trace_dir = context.get("trace_dir")
        return f"当前目标项目：{root}；运行记录目录：{trace_dir}。"
    return "在项目结构页选择目标项目根目录和运行记录目录。"


def _target_actions(targets: list[dict[str, object]]) -> list[str]:
    if not targets:
        return ["当前未识别明确入口；先从 README、pyproject、main 函数或 Web 路由中确认一个可运行入口。"]
    actions = []
    for target in targets[:5]:
        label = target.get("label") or target.get("id")
        hint = target.get("run_hint") or ""
        file = target.get("file")
        location = f"（{file}:{target.get('line')}）" if file and target.get("line") else ""
        actions.append(f"{label}{location}：{hint}")
    return actions


def _instrument_status(coverage: dict[str, Any]) -> str:
    summary = coverage.get("summary") if isinstance(coverage.get("summary"), dict) else {}
    known = int(summary.get("known_method_count") or 0)
    covered = int(summary.get("covered_method_count") or 0)
    if not known:
        return "todo"
    return "done" if covered >= known else "doing"


def _instrument_actions(readiness: dict[str, Any]) -> list[str]:
    groups = readiness.get("method_groups") if isinstance(readiness.get("method_groups"), dict) else {}
    missing_contract = [str(item) for item in groups.get("missing_contract", [])] if isinstance(groups.get("missing_contract"), list) else []
    uncovered = [str(item) for item in groups.get("uncovered", [])] if isinstance(groups.get("uncovered"), list) else []
    actions = []
    if uncovered:
        actions.append(f"优先覆盖未运行方法：{', '.join(uncovered[:6])}。")
    if missing_contract:
        actions.append(f"优先补契约：{', '.join(missing_contract[:6])}。")
    return actions or ["当前追踪边界基本可用；后续只在出现参数风险时补充更细的 contract。"]


def _run_status(readiness: dict[str, Any]) -> str:
    summary = readiness.get("summary") if isinstance(readiness.get("summary"), dict) else {}
    return "done" if int(summary.get("run_count") or 0) > 0 else "todo"


def _review_status(audit: dict[str, Any]) -> str:
    return "done" if audit.get("status") == "pass" else "doing"


def _review_actions(audit: dict[str, Any], blockers: list[dict[str, object]]) -> list[str]:
    if blockers:
        return [str(item.get("action") or item.get("detail") or item.get("title")) for item in blockers[:5]]
    actions = audit.get("next_actions")
    if isinstance(actions, list) and actions:
        return [str(item.get("action") or item.get("title") or item) for item in actions[:5] if isinstance(item, dict)]
    return ["查看问题列表与运行对比；若没有错误，保存当前流程作为基线运行。"]


def _validation_gates(readiness: dict[str, Any], audit: dict[str, Any]) -> list[dict[str, object]]:
    summary = readiness.get("summary") if isinstance(readiness.get("summary"), dict) else {}
    audit_summary = audit.get("summary") if isinstance(audit.get("summary"), dict) else {}
    return [
        {
            "id": "has_target_project",
            "label": "已选择目标项目",
            "passed": bool(readiness.get("context")),
        },
        {
            "id": "has_runs",
            "label": "已有运行记录",
            "passed": int(summary.get("run_count") or 0) > 0,
        },
        {
            "id": "has_coverage",
            "label": "存在方法覆盖",
            "passed": int(summary.get("covered_method_count") or 0) > 0,
        },
        {
            "id": "contracts_usable",
            "label": "契约基本可用",
            "passed": int(summary.get("missing_contract_count") or 0) == 0,
        },
        {
            "id": "no_blocking_audit",
            "label": "无阻断级审查问题",
            "passed": int(audit_summary.get("critical_count") or 0) == 0 and int(audit_summary.get("error_count") or 0) == 0,
        },
    ]


def _next_action(phases: list[dict[str, object]], blockers: list[dict[str, object]]) -> dict[str, object] | None:
    if blockers:
        blocker = blockers[0]
        return {
            "phase": "blocked",
            "title": blocker.get("title"),
            "action": blocker.get("action") or blocker.get("detail"),
        }
    for phase in phases:
        if phase.get("status") != "done":
            actions = phase.get("actions") if isinstance(phase.get("actions"), list) else []
            return {
                "phase": phase.get("id"),
                "title": phase.get("title"),
                "action": actions[0] if actions else phase.get("goal"),
            }
    return {"phase": "complete", "title": "接入计划完成", "action": "保存当前运行记录作为后续对比基线。"}
