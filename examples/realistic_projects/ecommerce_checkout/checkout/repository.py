from __future__ import annotations

from flowtrace import contract, trace_node


contract(
    "repository.save_order",
    input_required={"user_id": int, "total": float, "discount_rate": float, "line_count": int},
    input_optional={"coupon_code": (str, "NoneType"), "customer_tier": str},
    input_allow_extra=False,
    required={"order_id": str, "status": str, "stored_order": dict},
    allow_extra=False,
)


@trace_node("repository.save_order", tags=["repository"])
def save_order(order: dict[str, object]) -> dict[str, object]:
    return {
        "order_id": "order_sample_1001",
        "status": "created",
        "stored_order": order,
    }

