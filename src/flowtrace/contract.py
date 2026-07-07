from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .sanitize import safe_snapshot


FieldSpec = type | tuple[Any, ...] | str


@dataclass(frozen=True)
class Contract:
    name: str
    required: dict[str, FieldSpec] = field(default_factory=dict)
    optional: dict[str, FieldSpec] = field(default_factory=dict)
    allow_extra: bool = True
    version: str = "v1"


_input_contracts: dict[str, Contract] = {}
_output_contracts: dict[str, Contract] = {}


def register_contract(node_name: str, contract: Contract) -> None:
    register_output_contract(node_name, contract)


def get_contract(node_name: str) -> Contract | None:
    return get_output_contract(node_name)


def register_input_contract(node_name: str, contract: Contract) -> None:
    _input_contracts[node_name] = contract


def register_output_contract(node_name: str, contract: Contract) -> None:
    _output_contracts[node_name] = contract


def get_input_contract(node_name: str) -> Contract | None:
    return _input_contracts.get(node_name)


def get_output_contract(node_name: str) -> Contract | None:
    return _output_contracts.get(node_name)


def validate_payload(payload: Any, contract: Contract | None) -> dict[str, Any]:
    if contract is None:
        return {"status": "no_contract", "contract": None}

    payload = safe_snapshot(payload)
    if not isinstance(payload, dict):
        return {
            "status": "fail",
            "contract": _contract_summary(contract),
            "missing_fields": list(contract.required),
            "unexpected_fields": [],
            "type_mismatches": [],
            "message": "payload is not an object",
        }

    missing_fields = [field_name for field_name in contract.required if field_name not in payload]
    unexpected_fields: list[str] = []
    if not contract.allow_extra:
        allowed = set(contract.required) | set(contract.optional)
        unexpected_fields = [field_name for field_name in payload if field_name not in allowed]

    type_mismatches = []
    specs = {**contract.required, **contract.optional}
    for field_name, spec in specs.items():
        if field_name not in payload:
            continue
        if not _matches_spec(payload[field_name], spec):
            type_mismatches.append(
                {
                    "field": field_name,
                    "expected": _spec_name(spec),
                    "actual": type(payload[field_name]).__name__,
                    "value": payload[field_name],
                }
            )

    status = "pass"
    if missing_fields or type_mismatches:
        status = "fail"
    elif unexpected_fields:
        status = "warn"

    return {
        "status": status,
        "contract": _contract_summary(contract),
        "missing_fields": missing_fields,
        "unexpected_fields": unexpected_fields,
        "type_mismatches": type_mismatches,
    }


def diff_payloads(before: Any, after: Any) -> dict[str, Any]:
    before = safe_snapshot(before)
    after = safe_snapshot(after)
    if not isinstance(before, dict) or not isinstance(after, dict):
        return {"status": "not_comparable"}

    before_keys = set(before)
    after_keys = set(after)
    changed = []
    for field_name in sorted(before_keys & after_keys):
        before_value = before[field_name]
        after_value = after[field_name]
        if before_value != after_value or type(before_value) is not type(after_value):
            changed.append(
                {
                    "field": field_name,
                    "before": before_value,
                    "after": after_value,
                    "before_type": type(before_value).__name__,
                    "after_type": type(after_value).__name__,
                }
            )

    return {
        "status": "compared",
        "added_fields": sorted(after_keys - before_keys),
        "removed_fields": sorted(before_keys - after_keys),
        "changed_fields": changed,
    }


def _matches_spec(value: Any, spec: FieldSpec) -> bool:
    if isinstance(spec, str):
        return type(value).__name__ == spec
    if isinstance(spec, tuple):
        return any(_matches_spec(value, item) for item in spec)
    return isinstance(value, spec)


def _spec_name(spec: FieldSpec) -> str:
    if isinstance(spec, str):
        return spec
    if isinstance(spec, tuple):
        return " | ".join(_spec_name(item) for item in spec)
    return spec.__name__


def _contract_summary(contract: Contract) -> dict[str, Any]:
    return {
        "name": contract.name,
        "version": contract.version,
        "required": {key: _spec_name(value) for key, value in contract.required.items()},
        "optional": {key: _spec_name(value) for key, value in contract.optional.items()},
        "allow_extra": contract.allow_extra,
    }
