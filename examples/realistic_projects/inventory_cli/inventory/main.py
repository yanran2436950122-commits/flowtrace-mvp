from __future__ import annotations

from flowtrace import record_user_action, start_run

from inventory.workflow import transfer_inventory


def main() -> None:
    with start_run("样本库存调拨 - CLI"):
        raw_command = {
            "source": "warehouse-a",
            "target": "warehouse-b",
            "sku": "sku-100",
            "quantity": "5",
        }
        record_user_action("cli.submit_transfer_command", raw_command)
        result = transfer_inventory(raw_command)
        record_user_action("cli.print_transfer_result", {"result": result})


if __name__ == "__main__":
    main()

