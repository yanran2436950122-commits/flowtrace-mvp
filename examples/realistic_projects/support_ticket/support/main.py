from __future__ import annotations

import asyncio

from flowtrace import record_user_action, start_run

from support.models import TicketRequest
from support.workflow import handle_ticket


async def run_ticket_flow() -> None:
    with start_run("样本客服工单 - 异步"):
        request = TicketRequest(
            user_id=808,
            subject="Refund request",
            message="I need a refund for the invoice from yesterday.",
            severity="urgent",
        )
        record_user_action("web.submit_support_ticket", {"ticket": request})
        result = await handle_ticket(request)
        record_user_action("web.show_ticket_result", {"result": result})


def main() -> None:
    asyncio.run(run_ticket_flow())


if __name__ == "__main__":
    main()

