from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now
from .run_confirmation_store import profile_fingerprint


EXECUTION_REQUEST_STORE_VERSION = "execution_request_store.v1"
EXECUTION_REQUEST_STORE_FILENAME = "execution_requests.json"


def load_execution_requests(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    requests = [item for item in payload.get("requests", []) if isinstance(item, dict) and item.get("profile_id")]
    return {
        "schema_version": EXECUTION_REQUEST_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "requests": sorted(requests, key=lambda item: str(item.get("created_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in requests),
    }


def prepare_execution_request(trace_dir: Path, profile: dict[str, Any], runner_report: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_execution_requests(trace_dir)
    requests = [item for item in store["requests"] if item.get("profile_id") != profile_id]
    requests.append(
        {
            "request_id": execution_request_id(profile_id),
            "profile_id": profile_id,
            "request_fingerprint": execution_request_fingerprint(profile, runner_report),
            "created_at": utc_now(),
            "second_confirmed_at": None,
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "runner_plan_status": runner_report.get("status"),
            "executes_commands": False,
        }
    )
    return _write_store(trace_dir, requests)


def confirm_execution_request(trace_dir: Path, profile: dict[str, Any], runner_report: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_execution_requests(trace_dir)
    requests = []
    matched = False
    current_fingerprint = execution_request_fingerprint(profile, runner_report)
    for item in store["requests"]:
        if item.get("profile_id") != profile_id:
            requests.append(item)
            continue
        matched = True
        if item.get("request_fingerprint") != current_fingerprint:
            raise ValueError("execution request is stale")
        requests.append({**item, "second_confirmed_at": utc_now(), "executes_commands": False})
    if not matched:
        raise ValueError("execution request must be prepared before second confirmation")
    return _write_store(trace_dir, requests)


def revoke_execution_request_confirmation(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_execution_requests(trace_dir)
    requests = [
        {**item, "second_confirmed_at": None}
        if item.get("profile_id") == normalized_id
        else item
        for item in store["requests"]
    ]
    return _write_store(trace_dir, requests)


def remove_execution_request(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_execution_requests(trace_dir)
    requests = [item for item in store["requests"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, requests)


def execution_request_state(
    profile: dict[str, Any],
    runner_report: dict[str, Any] | None,
    request_store: dict[str, object] | None,
) -> dict[str, object]:
    if not runner_report:
        return {"status": "blocked", "prepared": False, "second_confirmed": False, "stale": False}
    requests = request_store.get("requests", []) if isinstance(request_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in requests if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not match:
        return {"status": "none", "prepared": False, "second_confirmed": False, "stale": False}
    current_fingerprint = execution_request_fingerprint(profile, runner_report)
    if match.get("request_fingerprint") != current_fingerprint:
        return {
            "status": "stale",
            "request_id": match.get("request_id"),
            "prepared": False,
            "second_confirmed": False,
            "created_at": match.get("created_at"),
            "second_confirmed_at": match.get("second_confirmed_at"),
            "stale": True,
            "reason": "运行配置或 runner 计划已变化，需要重新准备执行请求。",
        }
    if match.get("second_confirmed_at"):
        return {
            "status": "second_confirmed",
            "request_id": match.get("request_id"),
            "prepared": True,
            "second_confirmed": True,
            "created_at": match.get("created_at"),
            "second_confirmed_at": match.get("second_confirmed_at"),
            "stale": False,
        }
    return {
        "status": "prepared",
        "request_id": match.get("request_id"),
        "prepared": True,
        "second_confirmed": False,
        "created_at": match.get("created_at"),
        "second_confirmed_at": None,
        "stale": False,
    }


def execution_request_fingerprint(profile: dict[str, Any], runner_report: dict[str, Any]) -> str:
    checks = runner_report.get("checks") if isinstance(runner_report.get("checks"), list) else []
    payload = {
        "profile_fingerprint": profile_fingerprint(profile),
        "runner_status": runner_report.get("status"),
        "log_plan": runner_report.get("log_plan") if isinstance(runner_report.get("log_plan"), dict) else {},
        "checks": [
            {
                "key": check.get("key"),
                "status": check.get("status"),
                "title": check.get("title"),
            }
            for check in checks
            if isinstance(check, dict)
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def execution_request_id(profile_id: str) -> str:
    return f"execution_request:{profile_id.strip()}"


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / EXECUTION_REQUEST_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": EXECUTION_REQUEST_STORE_VERSION,
        "updated_at": None,
        "requests": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, requests: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": EXECUTION_REQUEST_STORE_VERSION,
        "updated_at": utc_now(),
        "requests": sorted(requests, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_execution_requests(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
