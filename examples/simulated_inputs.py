from __future__ import annotations

from flowtrace import SimulatedInputScenario, run_simulated_scenarios
from order_flow import OrderForm, submit_order


def run_order_payload(payload: dict[str, object]) -> dict[str, object]:
    form = OrderForm(
        user_id=int(payload["user_id"]),
        role=str(payload["role"]),
        amount=str(payload["amount"]),
        permissions=list(payload.get("permissions", [])),
        coupon_id=payload.get("coupon_id"),  # type: ignore[arg-type]
    )
    return submit_order(form)


def main() -> None:
    scenarios = [
        SimulatedInputScenario(
            name="管理员带优惠券",
            payload={
                "user_id": 123,
                "role": "admin",
                "amount": "42.50",
                "permissions": ["read", "write"],
                "coupon_id": "WELCOME",
            },
            tags=("happy_path", "admin"),
        ),
        SimulatedInputScenario(
            name="普通用户无优惠券",
            payload={
                "user_id": 456,
                "role": "user",
                "amount": "19.99",
                "permissions": ["read"],
                "coupon_id": None,
            },
            tags=("no_coupon",),
        ),
        SimulatedInputScenario(
            name="缺少用户 ID",
            payload={
                "user_id": 0,
                "role": "admin",
                "amount": "10.00",
                "permissions": ["read", "write"],
                "coupon_id": None,
            },
            tags=("invalid",),
        ),
    ]
    results = run_simulated_scenarios(scenarios, run_order_payload, run_label_prefix="订单模拟输入")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()

