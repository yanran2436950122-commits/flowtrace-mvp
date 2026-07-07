from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .context import utc_now


RUN_CONFIRMATION_STORE_VERSION = "run_confirmation_store.v1"
RUN_CONFIRMATION_STORE_FILENAME = "run_profile_confirmations.json"


def load_run_confirmations(trace_dir: Path) -> dict[str, object]:
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
        "schema_version": RUN_CONFIRMATION_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "confirmations": sorted(confirmations, key=lambda item: str(item.get("confirmed_at") or "")),
        "profile_ids": sorted(str(item["profile_id"]) for item in confirmations),
    }


def confirm_run_profile(trace_dir: Path, profile: dict[str, Any], report: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_run_confirmations(trace_dir)
    confirmations = [item for item in store["confirmations"] if item.get("profile_id") != profile_id]
    confirmations.append(
        {
            "profile_id": profile_id,
            "profile_fingerprint": profile_fingerprint(profile),
            "confirmed_at": utc_now(),
            "label": profile.get("label"),
            "display_command": profile.get("display_command"),
            "preflight_status": report.get("status"),
        }
    )
    return _write_store(trace_dir, confirmations)


def revoke_run_confirmation(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_run_confirmations(trace_dir)
    confirmations = [item for item in store["confirmations"] if item.get("profile_id") != normalized_id]
    return _write_store(trace_dir, confirmations)


def profile_confirmation(profile: dict[str, Any], confirmation_store: dict[str, object] | None) -> dict[str, object]:
    confirmations = confirmation_store.get("confirmations", []) if isinstance(confirmation_store, dict) else []
    profile_id = str(profile.get("id") or "")
    match = next((item for item in confirmations if isinstance(item, dict) and item.get("profile_id") == profile_id), None)
    if not match:
        return {"status": "none", "confirmed": False, "confirmed_at": None, "stale": False}
    current_fingerprint = profile_fingerprint(profile)
    if match.get("profile_fingerprint") != current_fingerprint:
        return {
            "status": "stale",
            "confirmed": False,
            "confirmed_at": match.get("confirmed_at"),
            "stale": True,
            "reason": "运行配置草案已变化，需要重新确认。",
        }
    return {
        "status": "confirmed",
        "confirmed": True,
        "confirmed_at": match.get("confirmed_at"),
        "stale": False,
    }


def profile_fingerprint(profile: dict[str, Any]) -> str:
    payload = {
        "id": profile.get("id"),
        "mode": profile.get("mode"),
        "command": profile.get("command"),
        "args": profile.get("args") if isinstance(profile.get("args"), list) else [],
        "argv": profile.get("argv") if isinstance(profile.get("argv"), list) else [],
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "env": profile.get("env") if isinstance(profile.get("env"), dict) else {},
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUN_CONFIRMATION_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUN_CONFIRMATION_STORE_VERSION,
        "updated_at": None,
        "confirmations": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, confirmations: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUN_CONFIRMATION_STORE_VERSION,
        "updated_at": utc_now(),
        "confirmations": sorted(confirmations, key=lambda item: str(item.get("profile_id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_run_confirmations(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()
