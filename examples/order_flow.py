from __future__ import annotations

from dataclasses import dataclass

from flowtrace import contract, record_user_action, start_run, trace_node


@dataclass
class OrderForm:
    user_id: int
    role: str
    amount: str
    permissions: list[str]
    coupon_id: str | None = None


contract(
    "frontend.validate_form",
    input_required={
        "user_id": int,
        "role": str,
        "amount": str,
        "permissions": list,
    },
    input_optional={"coupon_id": (str, "NoneType")},
    input_allow_extra=False,
    required={
        "user_id": int,
        "role": str,
        "amount": str,
        "permissions": list,
    },
    optional={"coupon_id": (str, "NoneType")},
    allow_extra=False,
)

contract(
    "api.create_order",
    input_required={
        "user_id": int,
        "role": str,
        "amount": str,
        "permissions": list,
    },
    input_optional={"coupon_id": (str, "NoneType")},
    input_allow_extra=False,
    required={
        "user_id": int,
        "role": str,
        "amount": str,
        "permissions": list,
    },
    optional={"coupon_id": (str, "NoneType")},
    allow_extra=False,
)

contract(
    "service.normalize_order",
    input_required={
        "user_id": int,
        "role": str,
        "amount": str,
        "permissions": list,
    },
    input_optional={"coupon_id": (str, "NoneType")},
    input_allow_extra=False,
    required={
        "userId": int,
        "role": str,
        "amount": float,
        "permissions": list,
    },
    optional={"coupon_id": (str, "NoneType")},
    allow_extra=False,
)

contract(
    "repository.save_order",
    input_required={
        "userId": int,
        "role": str,
        "amount": float,
        "permissions": list,
    },
    input_optional={"coupon_id": (str, "NoneType")},
    input_allow_extra=False,
    required={
        "order_id": str,
        "status": str,
        "order": dict,
    },
    allow_extra=False,
)


@trace_node("frontend.validate_form", tags=["frontend", "validation"])
def validate_form(form: OrderForm) -> dict[str, object]:
    if not form.user_id:
        raise ValueError("user_id is required")
    return {
        "user_id": form.user_id,
        "role": form.role,
        "amount": form.amount,
        "permissions": form.permissions,
        "coupon_id": form.coupon_id,
    }


@trace_node("api.create_order", tags=["api"])
def create_order_api(payload: dict[str, object]) -> dict[str, object]:
    # MVP 示例：这里故意丢失 permissions 字段，用于验证契约失败提示。
    return {
        "user_id": payload["user_id"],
        "role": payload["role"],
        "amount": payload["amount"],
        "coupon_id": payload.get("coupon_id"),
    }


@trace_node("service.normalize_order", tags=["service"])
def normalize_order(payload: dict[str, object]) -> dict[str, object]:
    # MVP 示例：这里故意覆盖 role 字段，用于验证字段变化提示。
    return {
        "userId": payload["user_id"],
        "role": "user",
        "amount": float(payload["amount"]),
        "coupon_id": payload.get("coupon_id"),
    }


@trace_node("repository.save_order", tags=["repository"])
def save_order(order: dict[str, object]) -> dict[str, object]:
    return {
        "order_id": "ord_1001",
        "status": "created",
        "order": order,
    }


@trace_node("workflow.submit_order", tags=["workflow"])
def submit_order(form: OrderForm) -> dict[str, object]:
    validated = validate_form(form)
    api_payload = create_order_api(validated)
    order = normalize_order(api_payload)
    return save_order(order)


def main() -> None:
    with start_run("示例订单提交"):
        form = OrderForm(
            user_id=123,
            role="admin",
            amount="42.50",
            permissions=["read", "write"],
            coupon_id="WELCOME",
        )
        record_user_action("frontend.submit_order_form", {"form": form})
        result = submit_order(form)
        record_user_action("ui.show_order_confirmation", {"result": result})


if __name__ == "__main__":
    main()
