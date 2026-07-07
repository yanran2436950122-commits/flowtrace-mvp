from __future__ import annotations

import contextvars
import uuid
from datetime import datetime, timezone


current_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("flowtrace_run_id", default=None)
current_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("flowtrace_trace_id", default=None)
current_span_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("flowtrace_span_id", default=None)
current_run_label: contextvars.ContextVar[str | None] = contextvars.ContextVar("flowtrace_run_label", default=None)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"

