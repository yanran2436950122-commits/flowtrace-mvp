from __future__ import annotations

from collections.abc import Iterable

from .contract import diff_payloads


def build_graph(events: list[dict[str, object]]) -> dict[str, object]:
    nodes = []
    edges = []

    for event in events:
        if event.get("event_type") == "function_start" and event.get("span_id"):
            nodes.append(
                {
                    "id": event["span_id"],
                    "label": event.get("target_node"),
                    "event_id": event.get("event_id"),
                    "kind": "function",
                    "timestamp": event.get("timestamp"),
                    "input": event.get("input"),
                    "tags": event.get("tags"),
                }
            )
            parent_span = event.get("parent_span_id")
            if parent_span:
                edges.append(
                    {
                        "id": f"{parent_span}->{event['span_id']}",
                        "from": parent_span,
                        "to": event["span_id"],
                        "relation_type": "call",
                        "source": "runtime",
                    }
                )

    for event in events:
        if event.get("event_type") == "function_end" and event.get("span_id"):
            span_id = str(event["span_id"])
            for node in nodes:
                if node["id"] == span_id:
                    node["output"] = event.get("output")
                    node["duration_ms"] = event.get("duration_ms")
                    node["error"] = event.get("error")
                    node["validation"] = event.get("validation")
                    node["diff"] = event.get("diff")
                    break

    user_events = [event for event in events if event.get("event_type") == "user_action"]
    for index, event in enumerate(user_events):
        node_id = str(event.get("event_id"))
        nodes.append(
            {
                "id": node_id,
                "label": event.get("action"),
                "event_id": event.get("event_id"),
                "kind": "user_action",
                "timestamp": event.get("timestamp"),
                "payload": event.get("payload"),
            }
        )
        if index + 1 < len(user_events):
            edges.append(
                {
                    "id": f"{node_id}->{user_events[index + 1].get('event_id')}",
                    "from": node_id,
                    "to": user_events[index + 1].get("event_id"),
                    "relation_type": "user_sequence",
                    "source": "runtime",
                }
            )

    return {"nodes": nodes, "edges": edges}


def build_dataflow(events: list[dict[str, object]]) -> dict[str, object]:
    starts = _events_by_span(events, "function_start")
    ends = _events_by_span(events, "function_end")

    nodes = []
    edges = []

    for span_id, start in starts.items():
        end = ends.get(span_id, {})
        nodes.append(
            {
                "id": span_id,
                "label": start.get("target_node"),
                "kind": "function",
                "timestamp": start.get("timestamp"),
                "tags": start.get("tags"),
                "input_validation": start.get("validation"),
                "validation": end.get("validation"),
                "error": end.get("error"),
            }
        )

    edges.extend(_sequential_data_edges(events, starts, ends))
    edges.extend(_user_to_root_edges(events, starts))
    return {"nodes": nodes, "edges": edges}


def build_layer_flow(
    events: list[dict[str, object]],
    method_catalog: Iterable[str] | None = None,
) -> dict[str, object]:
    dataflow = build_dataflow(events)
    catalog = set(method_catalog or [])
    called_methods = _called_methods(events)
    layer_nodes = _layer_nodes(catalog, called_methods, dataflow)
    layer_edges = _layer_edges(dataflow["edges"])
    return {"nodes": layer_nodes, "edges": layer_edges}


def collect_method_catalog(events_by_run: Iterable[list[dict[str, object]]]) -> list[str]:
    methods = set()
    for events in events_by_run:
        for event in events:
            if event.get("event_type") == "function_start" and event.get("target_node"):
                methods.add(str(event["target_node"]))
    return sorted(methods)


def build_project_coverage(
    project_model: dict[str, object],
    events_by_run: Iterable[list[dict[str, object]]],
) -> dict[str, object]:
    declared_methods = set(str(item) for item in project_model.get("declared_methods", []) if item)
    traced_functions = {
        str(function["traced_label"])
        for function in project_model.get("functions", [])
        if isinstance(function, dict) and function.get("traced_label")
    }
    known_methods = declared_methods | traced_functions
    runtime_methods = set(collect_method_catalog(events_by_run))
    covered = sorted(known_methods & runtime_methods)
    uncovered = sorted(known_methods - runtime_methods)
    runtime_only = sorted(runtime_methods - known_methods)

    return {
        "schema_version": "project_coverage.v1",
        "summary": {
            "known_method_count": len(known_methods),
            "runtime_method_count": len(runtime_methods),
            "covered_method_count": len(covered),
            "uncovered_method_count": len(uncovered),
            "runtime_only_method_count": len(runtime_only),
            "coverage_ratio": round(len(covered) / len(known_methods), 4) if known_methods else 0,
        },
        "covered_methods": covered,
        "uncovered_methods": uncovered,
        "runtime_only_methods": runtime_only,
    }


def build_run_comparison(
    target_events: list[dict[str, object]],
    base_events: list[dict[str, object]],
) -> dict[str, object]:
    target_dataflow = build_dataflow(target_events)
    base_dataflow = build_dataflow(base_events)
    target_edges = {_edge_key(edge): edge for edge in target_dataflow["edges"]}
    base_edges = {_edge_key(edge): edge for edge in base_dataflow["edges"]}

    comparisons = []
    for edge_key in sorted(set(target_edges) | set(base_edges)):
        target_edge = target_edges.get(edge_key)
        base_edge = base_edges.get(edge_key)
        comparisons.append(_compare_edges(edge_key, target_edge, base_edge))

    return {
        "target": {"nodes": target_dataflow["nodes"], "edges": target_dataflow["edges"]},
        "base": {"nodes": base_dataflow["nodes"], "edges": base_dataflow["edges"]},
        "comparisons": comparisons,
    }


def build_run_issues(events: list[dict[str, object]]) -> dict[str, object]:
    dataflow = build_dataflow(events)
    issues = []

    for event in events:
        if event.get("error"):
            issues.append(
                {
                    "id": event.get("event_id"),
                    "severity": "error",
                    "kind": "runtime_error",
                    "title": "运行异常",
                    "node": event.get("source_node") or event.get("target_node") or event.get("action"),
                    "message": _error_message(event.get("error")),
                    "event": event,
                }
            )

    for edge in dataflow["edges"]:
        input_validation = edge.get("downstream_input_validation")
        output_validation = edge.get("validation")
        if _validation_failed(input_validation):
            issues.append(
                {
                    "id": f"{edge.get('id')}:input",
                    "severity": "error",
                    "kind": "input_contract_failure",
                    "title": "下级输入契约失败",
                    "node": edge.get("to_label"),
                    "edge": _edge_title(edge),
                    "message": _validation_message(input_validation),
                    "edge_data": edge,
                }
            )
        if _validation_failed(output_validation):
            issues.append(
                {
                    "id": f"{edge.get('id')}:output",
                    "severity": "error",
                    "kind": "output_contract_failure",
                    "title": "下级输出契约失败",
                    "node": edge.get("to_label"),
                    "edge": _edge_title(edge),
                    "message": _validation_message(output_validation),
                    "edge_data": edge,
                }
            )
        if _has_payload_changes(edge.get("handoff_diff") or {}):
            issues.append(
                {
                    "id": f"{edge.get('id')}:handoff_diff",
                    "severity": "warn",
                    "kind": "handoff_diff",
                    "title": "交接数据发生变化",
                    "node": edge.get("to_label"),
                    "edge": _edge_title(edge),
                    "message": _diff_message(edge.get("handoff_diff") or {}),
                    "edge_data": edge,
                }
            )

    return {
        "summary": {
            "total": len(issues),
            "errors": sum(1 for issue in issues if issue["severity"] == "error"),
            "warnings": sum(1 for issue in issues if issue["severity"] == "warn"),
        },
        "issues": issues,
    }


def build_run_summary(
    events: list[dict[str, object]],
    method_catalog: Iterable[str] | None = None,
) -> dict[str, object]:
    dataflow = build_dataflow(events)
    layer_flow = build_layer_flow(events, method_catalog)
    issue_report = build_run_issues(events)
    issues = issue_report["issues"]
    contract_failures = [
        issue for issue in issues if issue.get("kind") in {"input_contract_failure", "output_contract_failure"}
    ]
    error_count = sum(1 for issue in issues if issue.get("severity") == "error")
    warning_count = sum(1 for issue in issues if issue.get("severity") == "warn")

    if error_count:
        status = "error"
    elif warning_count:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "event_count": len(events),
        "node_count": len(dataflow["nodes"]),
        "edge_count": len(dataflow["edges"]),
        "layer_count": len(layer_flow["nodes"]),
        "layer_edge_count": len(layer_flow["edges"]),
        "issue_count": len(issues),
        "error_count": error_count,
        "warning_count": warning_count,
        "contract_failure_count": len(contract_failures),
        "runtime_error_count": sum(1 for issue in issues if issue.get("kind") == "runtime_error"),
    }


def _called_methods(events: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    starts = _events_by_span(events, "function_start")
    ends = _events_by_span(events, "function_end")
    result = {}
    for span_id, start in starts.items():
        label = str(start.get("target_node") or span_id)
        end = ends.get(span_id, {})
        result[label] = {
            "id": span_id,
            "label": label,
            "short_label": _method_name(label),
            "layer": _layer_name(label),
            "called": True,
            "timestamp": start.get("timestamp"),
            "input": start.get("input"),
            "output": end.get("output"),
            "input_validation": start.get("validation"),
            "validation": end.get("validation"),
            "diff": end.get("diff"),
            "error": end.get("error"),
            "duration_ms": end.get("duration_ms"),
        }
    return result


def _layer_nodes(
    catalog: set[str],
    called_methods: dict[str, dict[str, object]],
    dataflow: dict[str, object],
) -> list[dict[str, object]]:
    methods_by_layer: dict[str, dict[str, dict[str, object]]] = {}
    for label in catalog | set(called_methods):
        layer = _layer_name(label)
        methods_by_layer.setdefault(layer, {})
        if label in called_methods:
            methods_by_layer[layer][label] = called_methods[label]
        else:
            methods_by_layer[layer][label] = {
                "id": f"catalog:{label}",
                "label": label,
                "short_label": _method_name(label),
                "layer": layer,
                "called": False,
            }

    for edge in dataflow["edges"]:
        for key in ("from_label", "to_label"):
            label = edge.get(key)
            if not label:
                continue
            layer = _layer_name(str(label))
            methods_by_layer.setdefault(layer, {})

    nodes = []
    for layer in sorted(methods_by_layer):
        methods = sorted(methods_by_layer[layer].values(), key=lambda item: (not item.get("called"), str(item.get("label"))))
        called = [method for method in methods if method.get("called")]
        has_error = any(method.get("error") for method in called)
        has_failure = any(
            _validation_failed(method.get("input_validation")) or _validation_failed(method.get("validation"))
            for method in called
        )
        nodes.append(
            {
                "id": f"layer:{layer}",
                "label": layer,
                "kind": "layer",
                "called_method_count": len(called),
                "uncalled_method_count": len(methods) - len(called),
                "methods": methods,
                "error": has_error,
                "validation": {"status": "fail"} if has_failure else {"status": "pass"},
            }
        )
    return nodes


def _layer_edges(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for edge in edges:
        from_layer = _layer_name(str(edge.get("from_label") or edge.get("from") or "unknown"))
        to_layer = _layer_name(str(edge.get("to_label") or edge.get("to") or "unknown"))
        key = (from_layer, to_layer)
        grouped.setdefault(
            key,
            {
                "id": f"layer:{from_layer}->layer:{to_layer}",
                "from": f"layer:{from_layer}",
                "to": f"layer:{to_layer}",
                "from_label": from_layer,
                "to_label": to_layer,
                "relation_type": "layer_data_flow",
                "source": "runtime",
                "method_edges": [],
            },
        )
        grouped[key]["method_edges"].append(edge)

    result = []
    for item in grouped.values():
        method_edges = item["method_edges"]
        item["transfer_count"] = len(method_edges)
        item["upstream_output"] = method_edges[0].get("upstream_output")
        item["downstream_input"] = method_edges[0].get("downstream_input")
        item["downstream_input_validation"] = _worst_validation(edge.get("downstream_input_validation") for edge in method_edges)
        item["validation"] = _worst_validation(edge.get("validation") for edge in method_edges)
        item["handoff_diff"] = _first_changed_diff(edge.get("handoff_diff") for edge in method_edges)
        item["error"] = next((edge.get("error") for edge in method_edges if edge.get("error")), None)
        result.append(item)
    return sorted(result, key=lambda edge: (str(edge["from_label"]), str(edge["to_label"])))


def _compare_edges(
    edge_key: str,
    target_edge: dict[str, object] | None,
    base_edge: dict[str, object] | None,
) -> dict[str, object]:
    if target_edge is None:
        return {
            "edge_key": edge_key,
            "status": "removed",
            "base_edge": base_edge,
            "target_edge": None,
        }
    if base_edge is None:
        return {
            "edge_key": edge_key,
            "status": "added",
            "base_edge": None,
            "target_edge": target_edge,
        }

    upstream_output_diff = diff_payloads(base_edge.get("upstream_output"), target_edge.get("upstream_output"))
    downstream_input_diff = diff_payloads(base_edge.get("downstream_input"), target_edge.get("downstream_input"))
    downstream_output_diff = diff_payloads(base_edge.get("downstream_output"), target_edge.get("downstream_output"))
    validation_change = {
        "base_input_status": _validation_status(base_edge.get("downstream_input_validation")),
        "target_input_status": _validation_status(target_edge.get("downstream_input_validation")),
        "base_output_status": _validation_status(base_edge.get("validation")),
        "target_output_status": _validation_status(target_edge.get("validation")),
    }
    status = "same"
    if (
        _has_payload_changes(upstream_output_diff)
        or _has_payload_changes(downstream_input_diff)
        or _has_payload_changes(downstream_output_diff)
        or validation_change["base_input_status"] != validation_change["target_input_status"]
        or validation_change["base_output_status"] != validation_change["target_output_status"]
    ):
        status = "changed"

    return {
        "edge_key": edge_key,
        "status": status,
        "from_label": target_edge.get("from_label"),
        "to_label": target_edge.get("to_label"),
        "relation_type": target_edge.get("relation_type"),
        "upstream_output_diff": upstream_output_diff,
        "downstream_input_diff": downstream_input_diff,
        "downstream_output_diff": downstream_output_diff,
        "validation_change": validation_change,
        "base_edge": base_edge,
        "target_edge": target_edge,
    }


def _edge_key(edge: dict[str, object]) -> str:
    return "|".join(
        [
            str(edge.get("relation_type") or ""),
            str(edge.get("from_label") or ""),
            str(edge.get("to_label") or ""),
        ]
    )


def _validation_status(validation: object) -> object:
    if isinstance(validation, dict):
        return validation.get("status")
    return None


def _validation_failed(validation: object) -> bool:
    return _validation_status(validation) == "fail"


def _validation_message(validation: object) -> str:
    if not isinstance(validation, dict):
        return "无校验详情"
    parts = []
    missing = validation.get("missing_fields") or []
    unexpected = validation.get("unexpected_fields") or []
    mismatches = validation.get("type_mismatches") or []
    if missing:
        parts.append(f"缺失字段: {', '.join(str(item) for item in missing)}")
    if unexpected:
        parts.append(f"额外字段: {', '.join(str(item) for item in unexpected)}")
    if mismatches:
        fields = [str(item.get("field")) for item in mismatches if isinstance(item, dict)]
        parts.append(f"类型不匹配: {', '.join(fields)}")
    return "；".join(parts) if parts else "契约失败"


def _diff_message(diff: dict[str, object]) -> str:
    added = diff.get("added_fields") or []
    removed = diff.get("removed_fields") or []
    changed = diff.get("changed_fields") or []
    parts = []
    if added:
        parts.append(f"新增字段: {', '.join(str(item) for item in added)}")
    if removed:
        parts.append(f"移除字段: {', '.join(str(item) for item in removed)}")
    if changed:
        fields = [str(item.get("field")) for item in changed if isinstance(item, dict)]
        parts.append(f"变化字段: {', '.join(fields)}")
    return "；".join(parts) if parts else "字段发生变化"


def _error_message(error: object) -> str:
    if isinstance(error, dict):
        message = error.get("message")
        error_type = error.get("type")
        if error_type and message:
            return f"{error_type}: {message}"
        if message:
            return str(message)
    return str(error)


def _edge_title(edge: dict[str, object]) -> str:
    return f"{edge.get('from_label')} -> {edge.get('to_label')}"


def _has_payload_changes(diff: dict[str, object]) -> bool:
    if diff.get("status") != "compared":
        return False
    return bool(diff.get("added_fields") or diff.get("removed_fields") or diff.get("changed_fields"))


def _sequential_data_edges(
    events: list[dict[str, object]],
    starts: dict[str, dict[str, object]],
    ends: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for event in events:
        if event.get("event_type") != "function_start" or not event.get("span_id"):
            continue
        parent_key = str(event.get("parent_span_id") or "__root__")
        grouped.setdefault(parent_key, []).append(event)

    edges = []
    for siblings in grouped.values():
        parent_span = siblings[0].get("parent_span_id")
        if parent_span and str(parent_span) in starts:
            parent_start = starts[str(parent_span)]
            first_child = siblings[0]
            parent_input = parent_start.get("input")
            child_input = first_child.get("input")
            child_span = str(first_child["span_id"])
            child_end = ends.get(child_span, {})
            edges.append(
                {
                    "id": f"{parent_span}->{child_span}:entry",
                    "from": str(parent_span),
                    "to": child_span,
                    "from_label": parent_start.get("target_node"),
                    "to_label": first_child.get("target_node"),
                    "relation_type": "entry_data_flow",
                    "source": "runtime",
                    "upstream_output": parent_input,
                    "downstream_input": child_input,
                    "downstream_input_validation": first_child.get("validation"),
                    "downstream_output": child_end.get("output"),
                    "validation": child_end.get("validation"),
                    "diff": child_end.get("diff"),
                    "handoff_diff": diff_payloads(_primary_payload(parent_input), _primary_payload(child_input)),
                    "error": child_end.get("error"),
                    "timestamp": first_child.get("timestamp"),
                    "duration_ms": child_end.get("duration_ms"),
                }
            )
        if len(siblings) < 2:
            continue
        for upstream_start, downstream_start in zip(siblings, siblings[1:]):
            upstream_span = str(upstream_start["span_id"])
            downstream_span = str(downstream_start["span_id"])
            upstream_end = ends.get(upstream_span, {})
            downstream_end = ends.get(downstream_span, {})
            upstream_output = upstream_end.get("output")
            downstream_input = downstream_start.get("input")
            edges.append(
                {
                    "id": f"{upstream_span}->{downstream_span}",
                    "from": upstream_span,
                    "to": downstream_span,
                    "from_label": upstream_start.get("target_node"),
                    "to_label": downstream_start.get("target_node"),
                    "relation_type": "sequential_data_flow",
                    "source": "runtime",
                    "upstream_output": upstream_output,
                    "downstream_input": downstream_input,
                    "downstream_input_validation": downstream_start.get("validation"),
                    "downstream_output": downstream_end.get("output"),
                    "validation": downstream_end.get("validation"),
                    "diff": downstream_end.get("diff"),
                    "handoff_diff": diff_payloads(_primary_payload(upstream_output), _primary_payload(downstream_input)),
                    "error": downstream_end.get("error"),
                    "timestamp": downstream_start.get("timestamp"),
                    "duration_ms": downstream_end.get("duration_ms"),
                }
            )
    return edges


def _events_by_span(events: list[dict[str, object]], event_type: str) -> dict[str, dict[str, object]]:
    result = {}
    for event in events:
        span_id = event.get("span_id")
        if event.get("event_type") == event_type and span_id:
            result[str(span_id)] = event
    return result


def _user_to_root_edges(events: list[dict[str, object]], starts: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    user_events = [event for event in events if event.get("event_type") == "user_action"]
    root_starts = [event for event in starts.values() if not event.get("parent_span_id")]
    if not user_events or not root_starts:
        return []

    first_user_event = user_events[0]
    edges = []
    for root in root_starts:
        root_end = next(
            (
                event
                for event in events
                if event.get("event_type") == "function_end" and event.get("span_id") == root.get("span_id")
            ),
            {},
        )
        edges.append(
            {
                "id": f"{first_user_event.get('event_id')}->{root.get('span_id')}",
                "from": first_user_event.get("event_id"),
                "to": root.get("span_id"),
                "from_label": first_user_event.get("action"),
                "to_label": root.get("target_node"),
                "relation_type": "user_input",
                "source": "runtime",
                "upstream_output": first_user_event.get("payload"),
                "downstream_input": root.get("input"),
                "downstream_input_validation": root.get("validation"),
                "downstream_output": root_end.get("output"),
                "validation": None,
                "diff": None,
                "handoff_diff": diff_payloads(_primary_payload(first_user_event.get("payload")), _primary_payload(root.get("input"))),
                "error": None,
                "timestamp": root.get("timestamp"),
                "duration_ms": None,
            }
        )
    return edges


def _primary_payload(payload: object) -> object:
    if isinstance(payload, dict) and len(payload) == 1:
        return next(iter(payload.values()))
    return payload


def _layer_name(label: str) -> str:
    return label.split(".", 1)[0] if "." in label else label


def _method_name(label: str) -> str:
    return label.split(".", 1)[1] if "." in label else label


def _worst_validation(validations: Iterable[object]) -> dict[str, object]:
    statuses = [_validation_status(validation) for validation in validations if validation]
    if "fail" in statuses:
        return {"status": "fail"}
    if "warn" in statuses:
        return {"status": "warn"}
    if "pass" in statuses:
        return {"status": "pass"}
    return {"status": "no_contract"}


def _first_changed_diff(diffs: Iterable[object]) -> object:
    for diff in diffs:
        if isinstance(diff, dict) and _has_payload_changes(diff):
            return diff
    return None
