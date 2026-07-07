from __future__ import annotations

from flowtrace import contract, trace_node

from .models import CheckoutForm


contract(
    "frontend.validate_cart",
    input_required={"user_id": int, "customer_tier": str, "items": list},
    input_optional={"coupon_code": (str, "NoneType")},
    input_allow_extra=False,
    required={"user_id": int, "customer_tier": str, "items": list},
    optional={"coupon_code": (str, "NoneType")},
    allow_extra=False,
)


@trace_node("frontend.validate_cart", tags=["frontend", "validation"])
def validate_cart(form: CheckoutForm) -> dict[str, object]:
    if not form.user_id:
        raise ValueError("user_id is required")
    if not form.items:
        raise ValueError("items is required")
    return {
        "user_id": form.user_id,
        "customer_tier": form.customer_tier,
        "items": form.items,
        "coupon_code": form.coupon_code,
    }

