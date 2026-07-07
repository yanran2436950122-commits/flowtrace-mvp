from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .context import utc_now


RUN_PROFILE_STORE_VERSION = "run_profile_store.v1"
RUN_PROFILE_STORE_FILENAME = "run_profiles.json"


def load_saved_run_profiles(trace_dir: Path) -> dict[str, object]:
    path = _store_path(trace_dir)
    if not path.exists():
        return _empty_store()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    profiles = [item for item in payload.get("profiles", []) if isinstance(item, dict) and item.get("id")]
    return {
        "schema_version": RUN_PROFILE_STORE_VERSION,
        "updated_at": payload.get("updated_at"),
        "profiles": sorted(profiles, key=lambda item: str(item.get("saved_at") or "")),
        "profile_ids": sorted(str(item["id"]) for item in profiles),
    }


def save_run_profile(trace_dir: Path, profile: dict[str, Any]) -> dict[str, object]:
    profile_id = _profile_id(profile)
    store = load_saved_run_profiles(trace_dir)
    profiles = [item for item in store["profiles"] if item.get("id") != profile_id]
    snapshot = _profile_snapshot(profile)
    snapshot["saved_at"] = utc_now()
    profiles.append(snapshot)
    return _write_store(trace_dir, profiles)


def remove_run_profile(trace_dir: Path, profile_id: str) -> dict[str, object]:
    normalized_id = profile_id.strip()
    store = load_saved_run_profiles(trace_dir)
    profiles = [item for item in store["profiles"] if item.get("id") != normalized_id]
    return _write_store(trace_dir, profiles)


def annotate_run_profiles(collection: dict[str, Any], saved_store: dict[str, object]) -> dict[str, object]:
    saved_profiles = [item for item in saved_store.get("profiles", []) if isinstance(item, dict)]
    saved_by_id = {str(item.get("id")): item for item in saved_profiles if item.get("id")}
    profiles = []
    for profile in collection.get("profiles", []) if isinstance(collection.get("profiles"), list) else []:
        if not isinstance(profile, dict):
            continue
        saved_snapshot = saved_by_id.get(str(profile.get("id")))
        profiles.append(
            {
                **profile,
                "saved": bool(saved_snapshot),
                "saved_at": saved_snapshot.get("saved_at") if saved_snapshot else None,
            }
        )

    summary = collection.get("summary") if isinstance(collection.get("summary"), dict) else {}
    return {
        **collection,
        "summary": {
            **summary,
            "saved_count": len(saved_profiles),
        },
        "profiles": profiles,
        "saved_profiles": saved_profiles,
        "saved_profile_ids": sorted(saved_by_id),
        "storage": {
            "schema_version": RUN_PROFILE_STORE_VERSION,
            "updated_at": saved_store.get("updated_at"),
            "writes_trace_dir": True,
        },
    }


def _store_path(trace_dir: Path) -> Path:
    return trace_dir / RUN_PROFILE_STORE_FILENAME


def _empty_store() -> dict[str, object]:
    return {
        "schema_version": RUN_PROFILE_STORE_VERSION,
        "updated_at": None,
        "profiles": [],
        "profile_ids": [],
    }


def _write_store(trace_dir: Path, profiles: list[dict[str, object]]) -> dict[str, object]:
    trace_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUN_PROFILE_STORE_VERSION,
        "updated_at": utc_now(),
        "profiles": sorted(profiles, key=lambda item: str(item.get("label") or item.get("id") or "")),
    }
    path = _store_path(trace_dir)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temporary_path.replace(path)
    return load_saved_run_profiles(trace_dir)


def _profile_id(profile: dict[str, Any]) -> str:
    value = profile.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("run profile id is required")
    return value.strip()


def _profile_snapshot(profile: dict[str, Any]) -> dict[str, object]:
    return {
        "id": _profile_id(profile),
        "label": profile.get("label"),
        "mode": profile.get("mode"),
        "command": profile.get("command"),
        "args": profile.get("args") if isinstance(profile.get("args"), list) else [],
        "argv": profile.get("argv") if isinstance(profile.get("argv"), list) else [],
        "display_command": profile.get("display_command"),
        "working_directory": profile.get("working_directory"),
        "env": profile.get("env") if isinstance(profile.get("env"), dict) else {},
        "confidence": profile.get("confidence"),
        "requires_confirmation": bool(profile.get("requires_confirmation", True)),
        "preflight": profile.get("preflight") if isinstance(profile.get("preflight"), list) else [],
        "notes": profile.get("notes") if isinstance(profile.get("notes"), list) else [],
        "source_target": profile.get("source_target") if isinstance(profile.get("source_target"), dict) else {},
    }
