from __future__ import annotations

import functools
import inspect
import time
import traceback
from collections.abc import Callable
from typing import Any, TypeVar

from .contract import diff_payloads, get_input_contract, get_output_contract, validate_payload
from .context import current_span_id, new_id
from .model import create_event
from .storage import append_event


F = TypeVar("F", bound=Callable[..., Any])


def trace_node(name: str | None = None, *, tags: list[str] | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        signature = inspect.signature(func)
        node_name = name or f"{func.__module__}.{func.__qualname__}"

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await _call_async(func, signature, node_name, tags or [], args, kwargs)

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _call_sync(func, signature, node_name, tags or [], args, kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def format_error(exc: BaseException | None) -> dict[str, Any] | None:
    if exc is None:
        return None
    return {
        "type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }


def _bind_arguments(signature: inspect.Signature, args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    bound = signature.bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return dict(bound.arguments)


def _start_span(node_name: str, arguments: dict[str, Any], tags: list[str]) -> tuple[str, object, float, str | None]:
    parent_span_id = current_span_id.get()
    span_id = new_id("span")
    token = current_span_id.set(span_id)
    started = time.perf_counter()
    input_validation = validate_payload(_primary_payload(arguments), get_input_contract(node_name))
    append_event(
        create_event(
            event_type="function_start",
            action="call.start",
            actor="function",
            source_node=parent_span_id,
            target_node=node_name,
            input_payload=arguments,
            tags=tags,
            validation=input_validation,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )
    )
    return span_id, token, started, parent_span_id


def _finish_span(
    *,
    span_id: str,
    parent_span_id: str | None,
    node_name: str,
    started: float,
    output: Any = None,
    error: dict[str, Any] | None = None,
    tags: list[str],
    validation: dict[str, Any] | None = None,
    diff: dict[str, Any] | None = None,
) -> None:
    append_event(
        create_event(
            event_type="function_end",
            action="call.end",
            actor="function",
            source_node=node_name,
            target_node=parent_span_id,
            output_payload=output,
            duration_ms=round((time.perf_counter() - started) * 1000, 3),
            error=error,
            tags=tags,
            validation=validation,
            diff=diff,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )
    )


def _call_sync(
    func: Callable[..., Any],
    signature: inspect.Signature,
    node_name: str,
    tags: list[str],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    arguments = _bind_arguments(signature, args, kwargs)
    span_id, token, started, parent_span_id = _start_span(node_name, arguments, tags)
    try:
        result = func(*args, **kwargs)
    except BaseException as exc:
        _finish_span(
            span_id=span_id,
            parent_span_id=parent_span_id,
            node_name=node_name,
            started=started,
            error=format_error(exc),
            tags=tags,
        )
        raise
    else:
        validation = validate_payload(result, get_output_contract(node_name))
        diff = diff_payloads(_primary_payload(arguments), result)
        _finish_span(
            span_id=span_id,
            parent_span_id=parent_span_id,
            node_name=node_name,
            started=started,
            output=result,
            validation=validation,
            diff=diff,
            tags=tags,
        )
        return result
    finally:
        current_span_id.reset(token)


async def _call_async(
    func: Callable[..., Any],
    signature: inspect.Signature,
    node_name: str,
    tags: list[str],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    arguments = _bind_arguments(signature, args, kwargs)
    span_id, token, started, parent_span_id = _start_span(node_name, arguments, tags)
    try:
        result = await func(*args, **kwargs)
    except BaseException as exc:
        _finish_span(
            span_id=span_id,
            parent_span_id=parent_span_id,
            node_name=node_name,
            started=started,
            error=format_error(exc),
            tags=tags,
        )
        raise
    else:
        validation = validate_payload(result, get_output_contract(node_name))
        diff = diff_payloads(_primary_payload(arguments), result)
        _finish_span(
            span_id=span_id,
            parent_span_id=parent_span_id,
            node_name=node_name,
            started=started,
            output=result,
            validation=validation,
            diff=diff,
            tags=tags,
        )
        return result
    finally:
        current_span_id.reset(token)


def _primary_payload(arguments: dict[str, Any]) -> Any:
    if len(arguments) == 1:
        return next(iter(arguments.values()))
    return arguments
