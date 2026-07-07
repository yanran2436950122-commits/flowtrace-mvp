from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contract import Contract, register_input_contract, register_output_contract
from .context import current_run_id, current_run_label, current_span_id, current_trace_id, new_id
from .instrumentation import format_error
from .model import create_event
from .storage import append_event


def get_current_run_id() -> str | None:
    return current_run_id.get()


@dataclass
class TraceRun:
    label: str | None = None
    run_id: str | None = None
    trace_id: str | None = None

    def __enter__(self) -> "TraceRun":
        self.run_id = self.run_id or new_id("run")
        self.trace_id = self.trace_id or new_id("trace")
        self._run_token = current_run_id.set(self.run_id)
        self._trace_token = current_trace_id.set(self.trace_id)
        self._span_token = current_span_id.set(None)
        self._label_token = current_run_label.set(self.label)
        record_event(
            event_type="run_start",
            action="run.start",
            actor="flowtrace",
            payload={"label": self.label},
        )
        return self

    def __exit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None:
        payload: dict[str, Any] = {"label": self.label}
        if exc is not None:
            payload["error"] = repr(exc)
        record_event(
            event_type="run_end",
            action="run.end",
            actor="flowtrace",
            payload=payload,
            error=format_error(exc) if exc else None,
        )
        current_run_id.reset(self._run_token)
        current_trace_id.reset(self._trace_token)
        current_span_id.reset(self._span_token)
        current_run_label.reset(self._label_token)


def start_run(label: str | None = None) -> TraceRun:
    return TraceRun(label=label)


def record_user_action(action: str, payload: Any | None = None, *, actor: str = "user") -> dict[str, Any]:
    return record_event(
        event_type="user_action",
        action=action,
        actor=actor,
        payload=payload,
    )


def record_event(
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
) -> dict[str, Any]:
    event = create_event(
        event_type=event_type,
        action=action,
        actor=actor,
        payload=payload,
        source_node=source_node,
        target_node=target_node,
        input_payload=input_payload,
        output_payload=output_payload,
        duration_ms=duration_ms,
        error=error,
        tags=tags,
    )
    append_event(event)
    return event


def contract(
    node_name: str,
    *,
    input_required: dict[str, object] | None = None,
    input_optional: dict[str, object] | None = None,
    input_allow_extra: bool = True,
    required: dict[str, object] | None = None,
    optional: dict[str, object] | None = None,
    allow_extra: bool = True,
    version: str = "v1",
) -> None:
    if input_required is not None or input_optional is not None:
        register_input_contract(
            node_name,
            Contract(
                name=f"{node_name}.input",
                required=input_required or {},
                optional=input_optional or {},
                allow_extra=input_allow_extra,
                version=version,
            ),
        )
    if required is not None or optional is not None:
        register_output_contract(
            node_name,
            Contract(
                name=f"{node_name}.output",
                required=required or {},
                optional=optional or {},
                allow_extra=allow_extra,
                version=version,
            ),
        )
