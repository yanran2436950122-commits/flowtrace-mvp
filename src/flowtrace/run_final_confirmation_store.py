from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now
from .run_confirmation_store import profile_fingerprint


RUN_FINAL_CONFIRMATION_STORE_VERSION = "run_final_confirmation_store.v1"
RUN_FINAL_CONFIRMATION_STORE_FILENAME = "run_final_confirmations.json"


def load_run_final_confirmations(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    confirmations = [item for item in payload.get("confirmations", []) if isinstance(item, dict) and item.get("profile_id")]
    return {
        "schema_version": RUN_FINAL_CONFIRMATION_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "confirmations": sorted(confirmations, key=lambda item: str(item.get("confirmed_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in confirmations),
    }


def confirm_run_final_execution(trace_dir: Path, profile: dict[str, Any], preflight_report: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_run_final_confirmations(trace_dir)
    confirmations = [item for item in store["confirmations"] if item.get("profile_id") != profile_id]
    confirmations.append(
        {
            "profile_id": profile_id,
            "gate_fingerprint": final_gate_fingerprint(profile, preflight_report),
            "confirmed_at": utc_now(),
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "preflight_status": preflight_report.get("status"),
            "preflight_confirmed_at": (preflight_report.get("confirmation") or {}).get("confirmed_at"),
            "executes_commands": False,
        }
    )
    return _write_store(trace_dir, confirmations)


def revoke_run_final_confirmation(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_run_final_confirmations(trace_dir)
    confirmations = [item for item in store["confirmations"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, confirmations)


def final_confirmation(
    profile: dict[str, Any],
    preflight_report: dict[str, Any],
    final_confirmation_store: dict[str, object] | None,
) -> dict[str, object]:
    confirmations = final_confirmation_store.get("confirmations", []) if isinstance(final_confirmation_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in confirmations if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not match:
        return {"status": "none", "confirmed": False, "confirmed_at": None, "stale": False}
    current_fingerprint = final_gate_fingerprint(profile, preflight_report)
    if match.get("gate_fingerprint") != current_fingerprint:
        return {
            "status": "stale",
            "confirmed": False,
            "confirmed_at": match.get("confirmed_at"),
            "stale": True,
            "reason": "运行配置或预检确认已变化，需要重新进行最终确认。",
        }
    return {
        "status": "confirmed",
        "confirmed": True,
        "confirmed_at": match.get("confirmed_at"),
        "stale": False,
    }


def final_gate_fingerprint(profile: dict[str, Any], preflight_report: dict[str, Any]) -> str:
    confirmation = preflight_report.get("confirmation") if isinstance(preflight_report.get("confirmation"), dict) else {}
    checks = preflight_report.get("checks") if isinstance(preflight_report.get("checks"), list) else []
    payload = {
        "profile_fingerprint": profile_fingerprint(profile),
        "preflight_status": preflight_report.get("status"),
        "preflight_confirmation_status": confirmation.get("status"),
        "preflight_confirmed_at": confirmation.get("confirmed_at"),
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


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUN_FINAL_CONFIRMATION_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUN_FINAL_CONFIRMATION_STORE_VERSION,
        "updated_at": None,
        "confirmations": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, confirmations: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUN_FINAL_CONFIRMATION_STORE_VERSION,
        "updated_at": utc_now(),
        "confirmations": sorted(confirmations, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_run_final_confirmations(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
