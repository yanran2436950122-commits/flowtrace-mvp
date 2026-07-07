from __future__ import annotations

from typing import Any

from .context import current_run_label, current_run_id, current_span_id, current_trace_id, new_id, utc_now
from .sanitize import safe_snapshot


def create_event(
    *,
    event_type: str,
    action: str,
    actor: str,
    payload: Any | None = None,
    source_node: str | None = None,
    target_node: str | None = None,
    input_payload: Any | None = None,
    output_payload: Any | None = None,
    duration_ms: float | None = None,
    error: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    validation: dict[str, Any] | None = None,
    diff: dict[str, Any] | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
) -> dict[str, Any]:
    return {
        "event_id": new_id("evt"),
        "run_id": current_run_id.get() or new_id("run"),
        "trace_id": current_trace_id.get() or new_id("trace"),
        "span_id": current_span_id.get() if span_id is None else span_id,
        "parent_span_id": parent_span_id,
        "timestamp": utc_now(),
        "actor": actor,
        "action": action,
        "event_type": event_type,
        "source_node": source_node,
        "target_node": target_node,
        "payload": safe_snapshot(payload),
        "input": safe_snapshot(input_payload),
        "output": safe_snapshot(output_payload),
        "duration_ms": duration_ms,
        "error": error,
        "validation": validation,
        "diff": diff,
        "tags": tags or [],
        "source": "runtime",
        "confidence": 1.0,
        "run_label": current_run_label.get(),
    }
