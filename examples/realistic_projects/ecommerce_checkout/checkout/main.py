from __future__ import annotations

from flowtrace import record_user_action, start_run, trace_node

from checkout.api import submit_checkout
from checkout.frontend import validate_cart
from checkout.models import CheckoutForm
from checkout.repository import save_order
from checkout.service import price_order


@trace_node("workflow.checkout_order", tags=["workflow"])
def checkout_order(form: CheckoutForm) -> dict[str, object]:
    validated = validate_cart(form)
    api_payload = submit_checkout(validated)
    priced_order = price_order(api_payload)
    return save_order(priced_order)


def main() -> None:
    with start_run("样本订单提交 - 字段丢失"):
        form = CheckoutForm(
            user_id=501,
            customer_tier="vip",
            coupon_code="SAVE10",
            items=[
                {"sku": "keyboard", "price": "199.00", "quantity": 1},
                {"sku": "mouse", "price": "79.00", "quantity": 2},
            ],
        )
        record_user_action("ui.submit_checkout_form", {"form": form})
        result = checkout_order(form)
        record_user_action("ui.show_checkout_result", {"result": result})


if __name__ == "__main__":
    main()

