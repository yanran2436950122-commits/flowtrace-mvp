from __future__ import annotations

from collections import defaultdict
from typing import Any


RUNNER_CONFIG_REMEDIATION_SUMMARY_VERSION = "project_runner_config_remediation_summaries.v1"


def build_project_runner_config_remediation_summaries(
    project_context: dict[str, Any],
    compatibility_reports: dict[str, Any],
) -> dict[str, object]:
    reports = [_remediation_report(report, compatibility_reports) for report in compatibility_reports.get("reports", [])]
    recommendations = [item for report in reports for item in report.get("recommendations", [])]
    status = _collection_status(compatibility_reports, recommendations)
    return {
        "schema_version": RUNNER_CONFIG_REMEDIATION_SUMMARY_VERSION,
        "context": project_context,
        "status": status,
        "summary": {
            "report_count": len(reports),
            "recommendation_count": len(recommendations),
            "field_count": len({item["field"] for item in recommendations}),
            "error_code_count": len({item["error_code"] for item in recommendations}),
            "blocked_count": sum(1 for report in reports if report["status"] == "blocked"),
            "launchable_count": 0,
        },
        "reports": reports,
        "safety": _safety(),
        "next_action": _next_action(status, recommendations),
    }


def _remediation_report(report: dict[str, Any], compatibility_reports: dict[str, Any]) -> dict[str, object]:
    issues = [issue for issue in report.get("compatibility_issues", []) if isinstance(issue, dict)]
    recommendations = _recommendations(issues, compatibility_reports)
    status = "remediation_required" if recommendations else str(report.get("status") or "no_recommendations")
    return {
        "id": f"runner_config_remediation_summary:{report.get('profile_id')}",
        "profile_id": report.get("profile_id"),
        "label": report.get("label"),
        "status": status,
        "status_label": _status_label(status),
        "recommendations": recommendations,
        "source_report_id": report.get("id"),
        "source_issue_count": len(issues),
        "execution_boundary": (
            "This layer only summarizes existing compatibility report issues; it does not read or write config files, "
            "execute commands, create processes, or expose launch APIs."
        ),
    }


def _recommendations(
    issues: list[dict[str, Any]],
    compatibility_reports: dict[str, Any],
) -> list[dict[str, object]]:
    contracts = {
        str(item.get("path")): item
        for item in compatibility_reports.get("compatibility_report_schema", {}).get("field_contracts", [])
        if isinstance(item, dict) and item.get("path")
    }
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        grouped[(str(issue.get("field") or ""), str(issue.get("error_code") or ""))].append(issue)

    output: list[dict[str, object]] = []
    for (field, error_code), group in sorted(grouped.items()):
        kind = str(group[0].get("kind") or "compatibility_issue")
        contract = contracts.get(field, {})
        output.append(
            {
                "field": field,
                "error_code": error_code,
                "issue_kind": kind,
                "issue_count": len(group),
                "severity": _max_severity(group),
                "expected_type": contract.get("type") or group[0].get("expected"),
                "default": contract.get("default"),
                "action": _action(kind, field, contract),
                "source_issue_keys": [
                    issue.get("navigation", {}).get("item_key")
                    for issue in group
                    if isinstance(issue.get("navigation"), dict)
                ],
                "navigation": _navigation(group[0]),
            }
        )
    return output


def _navigation(issue: dict[str, Any]) -> dict[str, object]:
    navigation = issue.get("navigation") if isinstance(issue.get("navigation"), dict) else {}
    return {
        "stage_key": navigation.get("stage_key") or "runner_config_compatibility_reports",
        "evidence_group": navigation.get("evidence_group") or "配置问题定位",
        "item_key": navigation.get("item_key") or "",
    }


def _action(kind: str, field: str, contract: dict[str, Any]) -> str:
    expected_type = contract.get("type")
    if kind == "missing_field":
        return f"Add required field `{field}` with type `{expected_type or 'defined by schema'}`."
    if kind == "type_mismatch":
        return f"Change `{field}` to the stable schema type `{expected_type or 'expected type'}`."
    if kind == "unsupported_version":
        return "Use the supported runner config schema version before real testing."
    if kind == "default_violation":
        return f"Restore `{field}` to the safe default `{contract.get('default')}`."
    if kind == "minimum_violation":
        return f"Raise `{field}` to the stable minimum/default value `{contract.get('default')}`."
    return f"Review `{field}` against the stable runner config schema."


def _max_severity(issues: list[dict[str, Any]]) -> str:
    severities = {str(issue.get("severity") or "warn") for issue in issues}
    if "error" in severities:
        return "error"
    if "warn" in severities:
        return "warn"
    return "info"


def _collection_status(compatibility_reports: dict[str, Any], recommendations: list[dict[str, object]]) -> str:
    upstream_status = str(compatibility_reports.get("status") or "")
    if upstream_status == "no_saved_profiles":
        return "no_saved_profiles"
    if upstream_status == "blocked":
        return "blocked"
    if recommendations:
        return "remediation_required"
    return "no_recommendations"


def _status_label(status: str) -> str:
    return {
        "no_saved_profiles": "No saved runner config",
        "blocked": "Remediation summary blocked",
        "remediation_required": "Config remediation required",
        "no_recommendations": "No remediation needed",
    }.get(status, status)


def _next_action(status: str, recommendations: list[dict[str, object]]) -> dict[str, object]:
    if status == "no_saved_profiles":
        return {"title": "Save a runner config first", "action": "Generate compatibility issues before remediation."}
    if status == "blocked":
        return {"title": "Resolve upstream compatibility blockers", "action": "Fix blocked compatibility prerequisites first."}
    if status == "remediation_required":
        first = recommendations[0]
        return {"title": "Apply the first config fix manually", "action": str(first.get("action") or "")}
    return {"title": "No config remediation needed", "action": "Keep launch disabled until later real-run gates pass."}


def _safety() -> dict[str, object]:
    return {
        "executes_commands": False,
        "creates_process": False,
        "runner_implemented": False,
        "launch_enabled": False,
        "launch_api_available": False,
        "config_remediation_summary_only": True,
        "reads_config_file": False,
        "consumes_compatibility_report": True,
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
