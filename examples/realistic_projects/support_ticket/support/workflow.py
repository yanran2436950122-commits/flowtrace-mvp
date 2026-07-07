from __future__ import annotations

import asyncio

from flowtrace import contract, trace_node

from .classifier import keyword_topic
from .models import TicketRequest


contract(
    "api.receive_ticket",
    input_required={"user_id": int, "subject": str, "message": str, "severity": str},
    input_allow_extra=False,
    required={"user_id": int, "subject": str, "message": str, "severity": str},
    allow_extra=False,
)

contract(
    "service.classify_ticket",
    input_required={"user_id": int, "subject": str, "message": str, "severity": str},
    input_allow_extra=False,
    required={"user_id": int, "subject": str, "topic": str, "priority": str},
    allow_extra=False,
)

contract(
    "service.assign_ticket",
    input_required={"user_id": int, "subject": str, "topic": str, "priority": str},
    input_allow_extra=False,
    required={"ticket_id": str, "queue": str, "priority": str},
    allow_extra=False,
)


@trace_node("api.receive_ticket", tags=["api"])
async def receive_ticket(request: TicketRequest) -> dict[str, object]:
    await asyncio.sleep(0)
    return {
        "user_id": request.user_id,
        "subject": request.subject,
        "message": request.message,
        "severity": request.severity,
    }


@trace_node("service.classify_ticket", tags=["service"])
async def classify_ticket(payload: dict[str, object]) -> dict[str, object]:
    await asyncio.sleep(0)
    severity = str(payload["severity"])
    return {
        "user_id": payload["user_id"],
        "subject": payload["subject"],
        "topic": keyword_topic(str(payload["message"])),
        "priority": "high" if severity in {"urgent", "high"} else "normal",
    }


@trace_node("service.assign_ticket", tags=["service"])
async def assign_ticket(ticket: dict[str, object]) -> dict[str, object]:
    await asyncio.sleep(0)
    queue = f"{ticket['topic']}-support"
    return {
        "ticket_id": "ticket_sample_3001",
        "queue": queue,
        "priority": ticket["priority"],
    }


@trace_node("workflow.handle_ticket", tags=["workflow"])
async def handle_ticket(request: TicketRequest) -> dict[str, object]:
    payload = await receive_ticket(request)
    classified = await classify_ticket(payload)
    return await assign_ticket(classified)

