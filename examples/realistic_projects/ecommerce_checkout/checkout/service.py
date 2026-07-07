from __future__ import annotations

from flowtrace import contract, trace_node


contract(
    "service.price_order",
    input_required={"user_id": int, "items": list},
    input_optional={"coupon_code": (str, "NoneType"), "customer_tier": str},
    input_allow_extra=False,
    required={"user_id": int, "total": float, "discount_rate": float, "line_count": int},
    optional={"coupon_code": (str, "NoneType"), "customer_tier": str},
    allow_extra=False,
)


@trace_node("service.price_order", tags=["service"])
def price_order(payload: dict[str, object]) -> dict[str, object]:
    items = payload["items"]
    subtotal = sum(float(item["price"]) * int(item["quantity"]) for item in items)
    tier = str(payload.get("customer_tier") or "standard")
    discount_rate = 0.15 if tier == "vip" else 0.0
    if payload.get("coupon_code") == "SAVE10":
        discount_rate = max(discount_rate, 0.10)
    return {
        "user_id": payload["user_id"],
        "customer_tier": tier,
        "coupon_code": payload.get("coupon_code"),
        "total": round(subtotal * (1 - discount_rate), 2),
        "discount_rate": discount_rate,
        "line_count": len(items),
    }

