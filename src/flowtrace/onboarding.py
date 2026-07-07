from __future__ import annotations

from typing import Any


ONBOARDING_VERSION = "project_onboarding.v1"
CORE_NAME_HINTS = (
    "submit",
    "create",
    "process",
    "handle",
    "validate",
    "normalize",
    "save",
    "run",
    "execute",
    "main",
    "app",
)


def build_project_onboarding(project_model: dict[str, Any], coverage: dict[str, Any]) -> dict[str, object]:
    functions = project_model.get("functions", [])
    entrypoints = project_model.get("entrypoints", [])
    scan_errors = project_model.get("scan_errors", [])
    covered_methods = set(coverage.get("covered_methods", []))
    uncovered_methods = set(coverage.get("uncovered_methods", []))
    runtime_only_methods = set(coverage.get("runtime_only_methods", []))

    traced_functions = {
        str(item.get("traced_label")): item
        for item in functions
        if isinstance(item, dict) and item.get("traced_label")
    }
    function_by_id = {str(item.get("id")): item for item in functions if isinstance(item, dict)}

    suggestions: list[dict[str, object]] = []
    suggestions.extend(_scan_error_suggestions(scan_errors))
    suggestions.extend(_entrypoint_suggestions(entrypoints, function_by_id))
    suggestions.extend(_uncovered_suggestions(uncovered_methods, traced_functions))
    suggestions.extend(_runtime_only_suggestions(runtime_only_methods))
    suggestions.extend(_core_function_suggestions(functions, traced_functions, covered_methods, uncovered_methods))

    suggestions = _dedupe_suggestions(suggestions)
    suggestions.sort(key=lambda item: (priority_rank(str(item["priority"])), str(item["target"])))

    return {
        "schema_version": ONBOARDING_VERSION,
        "context": project_model.get("context"),
        "summary": {
            "entrypoint_count": len(entrypoints),
            "suggestion_count": len(suggestions),
            "high_priority_count": sum(1 for item in suggestions if item["priority"] == "high"),
            "uncovered_method_count": len(uncovered_methods),
            "runtime_only_method_count": len(runtime_only_methods),
            "scan_error_count": len(scan_errors),
        },
        "steps": [
            "确认目标项目与运行记录目录是否正确。",
            "优先在入口候选和核心流程方法上添加 trace_node。",
            "为跨层传参边界补充 contract，先覆盖输入输出结构最稳定的位置。",
            "运行一次真实或模拟流程，再回到层级流转、问题列表和运行对比页检查结果。",
        ],
        "suggestions": suggestions,
    }


def _scan_error_suggestions(scan_errors: list[dict[str, Any]]) -> list[dict[str, object]]:
    return [
        {
            "id": f"scan-error:{item.get('file')}",
            "priority": "high",
            "kind": "scan_error",
            "target": item.get("file") or "未知文件",
            "file": item.get("file"),
            "line": None,
            "title": "先修复扫描错误",
            "reason": f"{item.get('error')}: {item.get('message')}",
            "action": "修复该文件的语法或编码问题，否则项目结构候选图可能不完整。",
            "code": "",
        }
        for item in scan_errors
    ]


def _entrypoint_suggestions(entrypoints: list[dict[str, Any]], function_by_id: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    result = []
    for entrypoint in entrypoints[:8]:
        function = function_by_id.get(str(entrypoint.get("id"))) or {}
        traced_label = function.get("traced_label")
        target = traced_label or entrypoint.get("label") or entrypoint.get("id")
        is_main_guard = entrypoint.get("kind") == "main_guard"
        result.append(
            {
                "id": f"entrypoint:{entrypoint.get('id')}",
                "priority": "high" if not traced_label else "medium",
                "kind": "entrypoint",
                "target": target,
                "file": entrypoint.get("file"),
                "line": entrypoint.get("line"),
                "title": "主入口文件" if is_main_guard else "入口候选",
                "reason": f"扫描器识别到 {entrypoint.get('kind')}，适合作为一次真实流程的起点。",
                "action": _entrypoint_action(is_main_guard),
                "code": "" if is_main_guard else _trace_code(str(target)),
            }
        )
    return result


def _uncovered_suggestions(uncovered_methods: set[str], traced_functions: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    result = []
    for method in sorted(uncovered_methods):
        function = traced_functions.get(method, {})
        result.append(
            {
                "id": f"uncovered:{method}",
                "priority": "high",
                "kind": "uncovered_method",
                "target": method,
                "file": function.get("file"),
                "line": function.get("line"),
                "title": "声明方法未被运行覆盖",
                "reason": "静态扫描发现该方法已声明为可追踪，但当前运行记录没有覆盖它。",
                "action": "补充真实流程或模拟输入，让该方法至少被执行一次。",
                "code": _trace_code(method),
            }
        )
    return result


def _runtime_only_suggestions(runtime_only_methods: set[str]) -> list[dict[str, object]]:
    return [
        {
            "id": f"runtime-only:{method}",
            "priority": "medium",
            "kind": "runtime_only_method",
            "target": method,
            "file": None,
            "line": None,
            "title": "仅运行时发现的方法",
            "reason": "运行记录中出现该方法，但静态项目扫描没有在目标项目里找到对应声明。",
            "action": "确认目标项目根目录是否正确，或检查该方法是否来自外部包、动态包装、生成代码。",
            "code": "",
        }
        for method in sorted(runtime_only_methods)
    ]


def _core_function_suggestions(
    functions: list[dict[str, Any]],
    traced_functions: dict[str, dict[str, Any]],
    covered_methods: set[str],
    uncovered_methods: set[str],
) -> list[dict[str, object]]:
    known_traced = covered_methods | uncovered_methods | set(traced_functions)
    result = []
    for function in functions:
        if not isinstance(function, dict) or function.get("traced_label"):
            continue
        name = str(function.get("name") or "")
        qualname = str(function.get("qualname") or name)
        if name.startswith("_") or not _looks_core_name(name, qualname, str(function.get("module") or "")):
            continue
        target = _suggested_trace_label(function)
        if target in known_traced:
            continue
        result.append(
            {
                "id": f"core:{function.get('id')}",
                "priority": "medium",
                "kind": "core_candidate",
                "target": target,
                "file": function.get("file"),
                "line": function.get("line"),
                "title": "疑似核心流程方法",
                "reason": "方法名或模块名命中确定性流程关键词，可能是参数流的重要边界。",
                "action": "人工确认它是否属于真实 workflow；确认后再添加 trace_node 和必要 contract。",
                "code": _trace_code(target),
            }
        )
    return result[:12]


def _looks_core_name(name: str, qualname: str, module: str) -> bool:
    text = f"{module}.{qualname}".lower()
    return any(hint in text for hint in CORE_NAME_HINTS)


def _suggested_trace_label(function: dict[str, Any]) -> str:
    module = str(function.get("module") or "")
    qualname = str(function.get("qualname") or function.get("name") or "unknown")
    return f"{module}.{qualname}".strip(".")


def _trace_code(node_name: str) -> str:
    return (
        "from flowtrace import trace_node, contract\n\n"
        f"@trace_node(\"{node_name}\")\n"
        "def your_function(*args, **kwargs):\n"
        "    return original_function(*args, **kwargs)\n\n"
        f"contract(\"{node_name}\", input_required={{}}, required={{}})"
    )


def _entrypoint_action(is_main_guard: bool) -> str:
    if is_main_guard:
        return "该文件是运行入口；不要装饰 if __name__ 分支本身，应优先在它调用的核心函数上接入 trace_node。"
    return "确认该入口是否属于用户真实 workflow；如果是，优先在它或它直接调用的方法上接入 trace_node。"


def _dedupe_suggestions(suggestions: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    seen = set()
    for suggestion in suggestions:
        key = (suggestion.get("kind"), suggestion.get("target"), suggestion.get("file"), suggestion.get("line"))
        if key in seen:
            continue
        seen.add(key)
        result.append(suggestion)
    return result


def priority_rank(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)
