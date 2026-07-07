from __future__ import annotations

import subprocess
import threading
from typing import Any

from .context import utc_now


RUNNER_CANCEL_TIMEOUT_TYPED_CONSENT = "CONTROL TARGET PROJECT"


class RunnerProcessRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._processes: dict[str, dict[str, Any]] = {}

    def register(self, launch_id: str, process: subprocess.Popen[str], profile: dict[str, Any]) -> None:
        with self._lock:
            self._processes[launch_id] = {
                "launch_id": launch_id,
                "profile_id": profile.get("id"),
                "label": profile.get("label"),
                "process": process,
                "registered_at": utc_now(),
                "requested_terminal_state": None,
                "control_reason": None,
                "controlled_at": None,
            }

    def unregister(self, launch_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._processes.pop(launch_id, None)

    def active(self) -> list[dict[str, object]]:
        with self._lock:
            return [_public_state(item) for item in self._processes.values()]

    def request_control(self, launch_id: str, action: str, reason: str | None = None) -> dict[str, object]:
        if action not in {"cancelled", "timed_out"}:
            raise ValueError("action must be cancelled or timed_out")
        with self._lock:
            item = self._processes.get(launch_id)
            if not item:
                return {
                    "accepted": False,
                    "status": "not_running",
                    "launch_id": launch_id,
                    "detail": "No active runner process exists for this launch_id.",
                }
            process = item["process"]
            if process.poll() is not None:
                return {
                    "accepted": False,
                    "status": "already_finished",
                    "launch_id": launch_id,
                    "detail": "Runner process has already exited.",
                }
            item["requested_terminal_state"] = action
            item["control_reason"] = reason or action
            item["controlled_at"] = utc_now()
            process.terminate()
            return {
                "accepted": True,
                "status": action,
                "launch_id": launch_id,
                "profile_id": item.get("profile_id"),
                "detail": "Termination requested for active low-risk sample runner process.",
            }


def _public_state(item: dict[str, Any]) -> dict[str, object]:
    process = item.get("process")
    return {
        "launch_id": item.get("launch_id"),
        "profile_id": item.get("profile_id"),
        "label": item.get("label"),
        "registered_at": item.get("registered_at"),
        "requested_terminal_state": item.get("requested_terminal_state"),
        "controlled_at": item.get("controlled_at"),
        "running": isinstance(process, subprocess.Popen) and process.poll() is None,
    }
