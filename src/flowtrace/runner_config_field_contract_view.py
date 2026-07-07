from __future__ import annotations

from typing import Any

from .runner_config_schema_stabilization import runner_config_schema_stabilization_schema


RUNNER_CONFIG_FIELD_CONTRACT_VIEW_VERSION = "project_runner_config_field_contract_views.v1"
RUNNER_CONFIG_FIELD_CONTRACT_VIEW_SCHEMA_VERSION = "runner_config_field_contract_view_schema.v1"


def build_project_runner_config_field_contract_views(
    project_context: dict[str, Any],
    config_schema_stabilizations: dict[str, Any],
) -> dict[str, object]:
    stable_schema = _stable_schema(project_context, config_schema_stabilizations)
    field_contracts = [
        _field_description(item)
        for item in stable_schema.get("field_contracts", [])
        if isinstance(item, dict) and item.get("path")
    ]
    error_codes = [
        _error_description(item)
        for item in stable_schema.get("error_map", [])
        if isinstance(item, dict) and item.get("code")
    ]
    section_groups = _section_groups(field_contracts)
    status = "contract_view_ready" if field_contracts and error_codes else "blocked"
    return {
        "schema_version": RUNNER_CONFIG_FIELD_CONTRACT_VIEW_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "stable_schema_count": 1 if field_contracts else 0,
            "supported_version_count": len(stable_schema.get("supported_versions", [])),
            "field_contract_count": len(field_contracts),
            "required_field_count": sum(1 for item in field_contracts if item["required"]),
            "default_value_count": sum(1 for item in field_contracts if item.get("default") is not None),
            "error_code_count": len(error_codes),
            "section_count": len(section_groups),
            "launchable_count": 0,
        },
        "field_contract_view_schema": {
            "schema_version": RUNNER_CONFIG_FIELD_CONTRACT_VIEW_SCHEMA_VERSION,
            "stable_config_schema_version": stable_schema.get("config_file_schema_version"),
            "source_schema_version": stable_schema.get("schema_version"),
            "supported_versions": stable_schema.get("supported_versions", []),
            "config_file_name": stable_schema.get("config_file_name"),
            "read_only_purpose": (
                "Present stable Runner config fields, JSON types, defaults, and error codes for manual repair."
            ),
            "blocked_actions": _blocked_actions(),
        },
        "sections": section_groups,
        "field_contracts": field_contracts,
        "error_codes": error_codes,
        "reports": [_view_report(stable_schema, field_contracts, error_codes, section_groups, status)],
        "safety": _safety(),
        "next_action": _next_action(status, field_contracts),
    }


def _stable_schema(project_context: dict[str, Any], config_schema_stabilizations: dict[str, Any]) -> dict[str, Any]:
    schema = config_schema_stabilizations.get("config_schema_stabilization_schema")
    if isinstance(schema, dict):
        return schema
    return runner_config_schema_stabilization_schema(project_context)


def _field_description(contract: dict[str, Any]) -> dict[str, object]:
    path = str(contract.get("path") or "")
    section = path.split(".", 1)[0] if "." in path else "root"
    default = contract.get("default")
    return {
        "path": path,
        "section": section,
        "type": str(contract.get("type") or "unknown"),
        "default": default,
        "default_display": _display_value(default),
        "required": bool(contract.get("required")),
        "error_code": str(contract.get("error_code") or ""),
        "manual_repair_hint": _manual_repair_hint(contract),
        "navigation": {
            "stage_key": "runner_config_field_contract_views",
            "evidence_group": "Field contracts",
            "item_key": _item_key("field", path),
        },
    }


def _error_description(error: dict[str, Any]) -> dict[str, object]:
    code = str(error.get("code") or "")
    field = str(error.get("field") or "")
    return {
        "code": code,
        "field": field,
        "message": str(error.get("message") or ""),
        "manual_repair_hint": _error_repair_hint(code, field),
        "navigation": {
            "stage_key": "runner_config_field_contract_views",
            "evidence_group": "Error codes",
            "item_key": _item_key("error", code),
        },
    }


def _section_groups(field_contracts: list[dict[str, object]]) -> list[dict[str, object]]:
    sections: dict[str, list[dict[str, object]]] = {}
    for contract in field_contracts:
        sections.setdefault(str(contract.get("section") or "root"), []).append(contract)
    return [
        {
            "key": section,
            "title": _section_title(section),
            "field_count": len(items),
            "required_field_count": sum(1 for item in items if item["required"]),
            "fields": [item["path"] for item in items],
            "navigation": {
                "stage_key": "runner_config_field_contract_views",
                "evidence_group": "Sections",
                "item_key": _item_key("section", section),
            },
        }
        for section, items in sorted(sections.items())
    ]


def _view_report(
    stable_schema: dict[str, Any],
    field_contracts: list[dict[str, object]],
    error_codes: list[dict[str, object]],
    sections: list[dict[str, object]],
    status: str,
) -> dict[str, object]:
    return {
        "id": "runner_config_field_contract_view:stable_schema",
        "status": status,
        "status_label": "Runner config field contract view ready" if status == "contract_view_ready" else "Field contract view blocked",
        "stable_config_schema_version": stable_schema.get("config_file_schema_version"),
        "field_contract_count": len(field_contracts),
        "error_code_count": len(error_codes),
        "section_count": len(sections),
        "index_entries": _index_entries(field_contracts, error_codes, sections),
        "execution_boundary": (
            "This layer only describes stable Runner config field contracts for manual repair; it does not read, "
            "create, or write config files, execute commands, create processes, or expose launch APIs."
        ),
    }


def _index_entries(
    field_contracts: list[dict[str, object]],
    error_codes: list[dict[str, object]],
    sections: list[dict[str, object]],
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in field_contracts:
        entries.append(
            _index_entry(
                item.get("navigation"),
                "config_field_contract",
                str(item.get("path") or ""),
                f"type={item.get('type')} default={item.get('default_display')} error={item.get('error_code')}",
                "info",
            )
        )
    for item in error_codes:
        entries.append(
            _index_entry(
                item.get("navigation"),
                "config_error_code",
                str(item.get("code") or ""),
                f"{item.get('field')}: {item.get('message')}",
                "info",
            )
        )
    for item in sections:
        entries.append(
            _index_entry(
                item.get("navigation"),
                "config_contract_section",
                str(item.get("title") or item.get("key") or ""),
                f"{item.get('field_count')} fields",
                "info",
            )
        )
    return entries


def _index_entry(
    navigation: object,
    kind: str,
    title: str,
    detail: str,
    status: str,
) -> dict[str, object]:
    nav = navigation if isinstance(navigation, dict) else {}
    return {
        "key": nav.get("item_key") or _item_key(kind, title),
        "kind": kind,
        "title": title,
        "detail": detail,
        "status": status,
        "navigation": {
            "stage_key": nav.get("stage_key") or "runner_config_field_contract_views",
            "evidence_group": nav.get("evidence_group") or "Field contracts",
            "item_key": nav.get("item_key") or _item_key(kind, title),
        },
    }


def _manual_repair_hint(contract: dict[str, Any]) -> str:
    path = str(contract.get("path") or "")
    field_type = str(contract.get("type") or "the documented type")
    default = _display_value(contract.get("default"))
    if contract.get("required"):
        return f"Ensure `{path}` exists as JSON {field_type}; use `{default}` as the stable default/minimum."
    return f"If `{path}` is present, keep it as JSON {field_type}; omitted values resolve to `{default}`."


def _error_repair_hint(code: str, field: str) -> str:
    if field == "*":
        return "Find the field reported with this code, then compare it with the field contract table."
    if field == "launch":
        return "Keep launch disabled; this code documents that launch APIs are unavailable in this phase."
    return f"Repair `{field}` according to the stable field contract mapped to `{code}`."


def _section_title(section: str) -> str:
    return {
        "root": "Root",
        "runner": "Runner",
        "process": "Process",
        "logs": "Logs",
        "cancel_timeout": "Cancel timeout",
        "completion_refresh": "Completion refresh",
    }.get(section, section)


def _display_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def _item_key(kind: str, value: str) -> str:
    raw = f"{kind}:{value}"
    slug = "".join(char.lower() if char.isalnum() else "_" for char in raw)
    return "config_contract:" + "_".join(part for part in slug.split("_") if part)


def _blocked_actions() -> list[str]:
    return [
        "reading config files directly in this layer",
        "creating flowtrace.runner.json",
        "modifying flowtrace.runner.json",
        "executing commands",
        "creating processes",
        "registering launch/cancel/timeout POST APIs",
        "enabling launch UI",
        "calling execution adapters",
        "creating or mutating runner sessions",
        "writing user project files",
    ]


def _next_action(status: str, field_contracts: list[dict[str, object]]) -> dict[str, object]:
    if status != "contract_view_ready":
        return {
            "title": "Stabilize Runner config schema first",
            "action": "Generate the stable schema layer before showing field contract descriptions.",
        }
    first = field_contracts[0] if field_contracts else {}
    return {
        "title": "Use field contracts for manual config repair",
        "action": f"Start with `{first.get('path') or 'schema_version'}` and keep real execution disabled.",
    }


def _safety() -> dict[str, object]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "config_field_contract_view_only": True,
        "reads_config_file": False,
        "describes_stable_schema_only": True,
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
