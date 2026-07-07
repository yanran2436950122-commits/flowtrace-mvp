from __future__ import annotations

from flowtrace import contract, trace_node


contract(
    "api.submit_checkout",
    input_required={"user_id": int, "customer_tier": str, "items": list},
    input_optional={"coupon_code": (str, "NoneType")},
    input_allow_extra=False,
    required={"user_id": int, "items": list},
    optional={"coupon_code": (str, "NoneType")},
    allow_extra=False,
)


@trace_node("api.submit_checkout", tags=["api"])
def submit_checkout(payload: dict[str, object]) -> dict[str, object]:
    # 故意丢失 customer_tier，用于验证字段丢失和默认策略问题。
    return {
        "user_id": payload["user_id"],
        "items": payload["items"],
        "coupon_code": payload.get("coupon_code"),
    }

