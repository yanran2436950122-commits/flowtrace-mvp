from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
}


def safe_snapshot(value: Any, *, max_depth: int = 6, max_string: int = 500) -> Any:
    return _snapshot(value, depth=0, max_depth=max_depth, max_string=max_string)


def _snapshot(value: Any, *, depth: int, max_depth: int, max_string: int) -> Any:
    if depth > max_depth:
        return {"__truncated__": "max_depth"}

    if value is None or isinstance(value, bool | int | float):
        return value

    if isinstance(value, str):
        if len(value) > max_string:
            return value[:max_string] + "...[truncated]"
        return value

    if isinstance(value, bytes):
        return {"__bytes__": len(value)}

    if is_dataclass(value):
        return _snapshot(asdict(value), depth=depth + 1, max_depth=max_depth, max_string=max_string)

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _snapshot(model_dump(), depth=depth + 1, max_depth=max_depth, max_string=max_string)

    dict_method = getattr(value, "dict", None)
    if callable(dict_method):
        try:
            return _snapshot(dict_method(), depth=depth + 1, max_depth=max_depth, max_string=max_string)
        except TypeError:
            pass

    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in SENSITIVE_KEYS:
                result[key_text] = "[redacted]"
            else:
                result[key_text] = _snapshot(item, depth=depth + 1, max_depth=max_depth, max_string=max_string)
        return result

    if isinstance(value, list | tuple | set):
        items = list(value)
        rendered = [_snapshot(item, depth=depth + 1, max_depth=max_depth, max_string=max_string) for item in items[:50]]
        if len(items) > 50:
            rendered.append({"__truncated_items__": len(items) - 50})
        return rendered

    return repr(value)

