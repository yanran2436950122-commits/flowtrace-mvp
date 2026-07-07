from __future__ import annotations

from flowtrace import contract, trace_node

from .catalog import read_stock, write_stock


contract(
    "cli.parse_transfer",
    input_required={"source": str, "target": str, "sku": str, "quantity": int},
    input_allow_extra=False,
    required={"source": str, "target": str, "sku": str, "quantity": int},
    allow_extra=False,
)

contract(
    "inventory.validate_transfer",
    input_required={"source": str, "target": str, "sku": str, "quantity": int},
    input_allow_extra=False,
    required={"source": str, "target": str, "sku": str, "quantity": int, "available": int},
    allow_extra=False,
)

contract(
    "inventory.reserve_stock",
    input_required={"source": str, "target": str, "sku": str, "quantity": int, "available": int},
    input_allow_extra=False,
    required={"source": str, "target": str, "sku": str, "quantity": int, "remaining": int},
    allow_extra=False,
)

contract(
    "inventory.commit_transfer",
    input_required={"source": str, "target": str, "sku": str, "quantity": int, "remaining": int},
    input_allow_extra=False,
    required={"transfer_id": str, "status": str, "source_remaining": int, "target_total": int},
    allow_extra=False,
)


@trace_node("cli.parse_transfer", tags=["cli"])
def parse_transfer(raw: dict[str, object]) -> dict[str, object]:
    return {
        "source": str(raw["source"]),
        "target": str(raw["target"]),
        "sku": str(raw["sku"]),
        "quantity": int(raw["quantity"]),
    }


@trace_node("inventory.validate_transfer", tags=["service", "validation"])
def validate_transfer(command: dict[str, object]) -> dict[str, object]:
    available = read_stock(str(command["source"]), str(command["sku"]))
    if available < int(command["quantity"]):
        raise ValueError("not enough stock")
    return {**command, "available": available}


@trace_node("inventory.reserve_stock", tags=["service"])
def reserve_stock(command: dict[str, object]) -> dict[str, object]:
    remaining = int(command["available"]) - int(command["quantity"])
    return {
        "source": command["source"],
        "target": command["target"],
        "sku": command["sku"],
        "quantity": command["quantity"],
        "remaining": remaining,
    }


@trace_node("inventory.commit_transfer", tags=["repository"])
def commit_transfer(reservation: dict[str, object]) -> dict[str, object]:
    source = str(reservation["source"])
    target = str(reservation["target"])
    sku = str(reservation["sku"])
    quantity = int(reservation["quantity"])
    remaining = int(reservation["remaining"])
    target_total = read_stock(target, sku) + quantity
    write_stock(source, sku, remaining)
    write_stock(target, sku, target_total)
    return {
        "transfer_id": "transfer_sample_2001",
        "status": "committed",
        "source_remaining": remaining,
        "target_total": target_total,
    }


@trace_node("workflow.transfer_inventory", tags=["workflow"])
def transfer_inventory(raw: dict[str, object]) -> dict[str, object]:
    command = parse_transfer(raw)
    validated = validate_transfer(command)
    reservation = reserve_stock(validated)
    return commit_transfer(reservation)

