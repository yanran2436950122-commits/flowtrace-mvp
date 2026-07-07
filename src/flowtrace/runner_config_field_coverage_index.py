from __future__ import annotations

from typing import Any


RUNNER_CONFIG_FIELD_COVERAGE_INDEX_VERSION = "project_runner_config_field_coverage_indexes.v1"


def build_project_runner_config_field_coverage_indexes(
    project_context: dict[str, Any],
    field_contract_views: dict[str, Any],
    compatibility_reports: dict[str, Any],
    remediation_summaries: dict[str, Any],
) -> dict[str, object]:
    field_contracts = [
        item for item in field_contract_views.get("field_contracts", []) if isinstance(item, dict) and item.get("path")
    ]
    compatibility_issues = _compatibility_issues(compatibility_reports)
    recommendations = _recommendations(remediation_summaries)
    entries = [
        _field_entry(contract, compatibility_issues.get(str(contract.get("path") or ""), []), recommendations.get(str(contract.get("path") or ""), []))
        for contract in field_contracts
    ]
    indexed_issue_count = sum(len(item["compatibility_issue_keys"]) for item in entries)
    indexed_recommendation_count = sum(len(item["recommendation_keys"]) for item in entries)
    status = _status(field_contract_views, compatibility_reports, remediation_summaries)
    return {
        "schema_version": RUNNER_CONFIG_FIELD_COVERAGE_INDEX_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "field_count": len(entries),
            "covered_field_count": sum(1 for item in entries if item["has_contract"]),
            "field_with_issue_count": sum(1 for item in entries if item["compatibility_issue_count"]),
            "field_with_recommendation_count": sum(1 for item in entries if item["recommendation_count"]),
            "indexed_issue_count": indexed_issue_count,
            "indexed_recommendation_count": indexed_recommendation_count,
            "target_group_count": len(_target_groups()),
            "filter_group_count": len(_filter_groups(entries)),
            "launchable_count": 0,
        },
        "target_groups": _target_groups(),
        "filter_groups": _filter_groups(entries),
        "field_indexes": entries,
        "reports": [_report(status, entries, indexed_issue_count, indexed_recommendation_count)],
        "safety": _safety(),
        "next_action": _next_action(status, entries),
    }


def _compatibility_issues(compatibility_reports: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for report in compatibility_reports.get("reports", []):
        if not isinstance(report, dict):
            continue
        for issue in report.get("compatibility_issues", []):
            if isinstance(issue, dict) and issue.get("field"):
                output.setdefault(str(issue["field"]), []).append(issue)
    return output


def _recommendations(remediation_summaries: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for report in remediation_summaries.get("reports", []):
        if not isinstance(report, dict):
            continue
        for recommendation in report.get("recommendations", []):
            if isinstance(recommendation, dict) and recommendation.get("field"):
                output.setdefault(str(recommendation["field"]), []).append(recommendation)
    return output


def _field_entry(
    contract: dict[str, Any],
    issues: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
) -> dict[str, object]:
    path = str(contract.get("path") or "")
    coverage_key = _slug("field", path)
    issue_keys = [_item_key(issue, f"compatibility:{path}:{index}") for index, issue in enumerate(issues)]
    recommendation_keys = [
        _item_key(recommendation, f"remediation:{path}:{index}")
        for index, recommendation in enumerate(recommendations)
    ]
    coverage_navigation = _navigation(path)
    contract_navigation = contract.get("navigation") if isinstance(contract.get("navigation"), dict) else coverage_navigation
    return {
        "key": coverage_key,
        "field": path,
        "section": str(contract.get("section") or "root"),
        "type": contract.get("type") or "unknown",
        "required": bool(contract.get("required")),
        "default": contract.get("default"),
        "error_code": contract.get("error_code") or "",
        "has_contract": True,
        "compatibility_issue_count": len(issues),
        "recommendation_count": len(recommendations),
        "compatibility_issue_keys": issue_keys,
        "recommendation_keys": recommendation_keys,
        "navigation": coverage_navigation,
        "field_contract_navigation": contract_navigation,
        "compatibility_issue_targets": _target_list("compatibility_issue", issues),
        "remediation_targets": _target_list("remediation", recommendations),
        "filter_tags": _filter_tags(contract, issues, recommendations),
    }


def _report(
    status: str,
    entries: list[dict[str, object]],
    indexed_issue_count: int,
    indexed_recommendation_count: int,
) -> dict[str, object]:
    return {
        "id": "runner_config_field_coverage_index:stable_schema",
        "status": status,
        "status_label": "Config field coverage index ready",
        "field_count": len(entries),
        "indexed_issue_count": indexed_issue_count,
        "indexed_recommendation_count": indexed_recommendation_count,
        "index_entries": _index_entries(entries),
        "execution_boundary": (
            "This layer only indexes in-memory field contracts, compatibility issues, and remediation suggestions; "
            "it does not read or write config files, execute commands, create processes, or expose launch APIs."
        ),
    }


def _status(
    field_contract_views: dict[str, Any],
    compatibility_reports: dict[str, Any],
    remediation_summaries: dict[str, Any],
) -> str:
    if field_contract_views.get("status") != "contract_view_ready":
        return "blocked"
    if compatibility_reports.get("status") == "blocked" or remediation_summaries.get("status") == "blocked":
        return "blocked"
    if compatibility_reports.get("status") == "no_saved_profiles":
        return "no_saved_profiles"
    return "coverage_index_ready"


def _index_entries(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for item in entries:
        field = str(item.get("field") or "")
        output.append(
            _index_entry(
                key=_slug("config_field_coverage", field),
                kind="config_field_coverage",
                title=field,
                detail=(
                    f"issues={item['compatibility_issue_count']} "
                    f"recommendations={item['recommendation_count']} type={item['type']}"
                ),
                status="warn" if item["compatibility_issue_count"] else "info",
                navigation=item.get("navigation"),
            )
        )
        output.append(
            _index_entry(
                key=_slug("config_field_contract", field),
                kind="config_field_contract",
                title=field,
                detail="open stable field contract",
                status="info",
                navigation=item.get("field_contract_navigation"),
            )
        )
        for target in item.get("compatibility_issue_targets", []):
            if isinstance(target, dict):
                output.append(
                    _index_entry(
                        key=str(target.get("key") or _slug("config_field_issue", field)),
                        kind="config_field_issue",
                        title=field,
                        detail=str(target.get("detail") or "open compatibility issue"),
                        status="warn",
                        navigation=target.get("navigation"),
                    )
                )
        for target in item.get("remediation_targets", []):
            if isinstance(target, dict):
                output.append(
                    _index_entry(
                        key=str(target.get("key") or _slug("config_field_remediation", field)),
                        kind="config_field_remediation",
                        title=field,
                        detail=str(target.get("detail") or "open remediation suggestion"),
                        status="warn",
                        navigation=target.get("navigation"),
                    )
                )
    return output


def _target_groups() -> list[dict[str, object]]:
    return [
        {
            "key": "config_field_coverage",
            "title": "Field coverage",
            "purpose": "Open the field coverage index entry for the selected config field.",
            "effect": "UI navigation only; no config read, write, or repair is performed.",
        },
        {
            "key": "config_field_contract",
            "title": "Field contract",
            "purpose": "Open the stable schema contract that defines type, default, and required state.",
            "effect": "UI navigation only; the stable contract remains read-only.",
        },
        {
            "key": "config_field_issue",
            "title": "Compatibility issue",
            "purpose": "Open the compatibility report issue tied to this field.",
            "effect": "UI navigation only; no compatibility repair is applied.",
        },
        {
            "key": "config_field_remediation",
            "title": "Remediation suggestion",
            "purpose": "Open the manual remediation suggestion tied to this field.",
            "effect": "UI navigation only; no config file is created or modified.",
        },
    ]


def _filter_groups(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        _filter_group("all", "All fields", len(entries)),
        _filter_group("with_issues", "With issues", sum(1 for item in entries if item["compatibility_issue_count"])),
        _filter_group(
            "with_recommendations",
            "With remediation",
            sum(1 for item in entries if item["recommendation_count"]),
        ),
        _filter_group("required", "Required fields", sum(1 for item in entries if item["required"])),
        *[
            _filter_group(f"section:{section}", f"Section: {section}", count)
            for section, count in sorted(_section_counts(entries).items())
        ],
    ]


def _filter_group(key: str, title: str, count: int) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "count": count,
        "effect": "UI filtering only; no config read, write, repair, or execution is performed.",
    }


def _section_counts(entries: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in entries:
        section = str(item.get("section") or "root")
        counts[section] = counts.get(section, 0) + 1
    return counts


def _filter_tags(contract: dict[str, Any], issues: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> list[str]:
    section = str(contract.get("section") or "root")
    return [
        "all",
        "required" if contract.get("required") else "optional",
        "with_issues" if issues else "no_issues",
        "with_recommendations" if recommendations else "no_recommendations",
        f"section:{section}",
    ]


def _index_entry(
    key: str,
    kind: str,
    title: str,
    detail: str,
    status: str,
    navigation: object,
) -> dict[str, object]:
    return {
        "key": key,
        "kind": kind,
        "title": title,
        "detail": detail,
        "status": status,
        "navigation": navigation if isinstance(navigation, dict) else {},
    }


def _target_list(kind: str, items: list[dict[str, Any]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for index, item in enumerate(items):
        navigation = item.get("navigation") if isinstance(item.get("navigation"), dict) else {}
        output.append(
            {
                "key": str(navigation.get("item_key") or f"{kind}:{index}"),
                "kind": kind,
                "detail": str(item.get("error_code") or item.get("action") or item.get("kind") or kind),
                "navigation": navigation,
            }
        )
    return output


def _next_action(status: str, entries: list[dict[str, object]]) -> dict[str, object]:
    if status == "blocked":
        return {"title": "Repair upstream config analysis", "action": "Build field contracts before indexing coverage."}
    if status == "no_saved_profiles":
        return {"title": "Save a runner config first", "action": "The index is ready, but no saved config issues exist yet."}
    first = next((item for item in entries if item["compatibility_issue_count"]), entries[0] if entries else {})
    return {"title": "Review indexed config fields", "action": f"Start with `{first.get('field', 'schema_version')}`."}


def _item_key(item: dict[str, Any], fallback: str) -> str:
    navigation = item.get("navigation") if isinstance(item.get("navigation"), dict) else {}
    return str(navigation.get("item_key") or fallback)


def _navigation(path: str) -> dict[str, object]:
    return {
        "stage_key": "runner_config_field_coverage_indexes",
        "evidence_group": "Field coverage",
        "item_key": _slug("field", path),
    }


def _slug(kind: str, value: str) -> str:
    raw = f"{kind}:{value}"
    slug = "".join(char.lower() if char.isalnum() else "_" for char in raw)
    return "config_field_coverage:" + "_".join(part for part in slug.split("_") if part)


def _safety() -> dict[str, object]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "config_field_coverage_index_only": True,
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
