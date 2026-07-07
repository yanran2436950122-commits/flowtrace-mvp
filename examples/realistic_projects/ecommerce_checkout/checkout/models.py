from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CheckoutForm:
    user_id: int
    customer_tier: str
    items: list[dict[str, object]]
    coupon_code: str | None = None

