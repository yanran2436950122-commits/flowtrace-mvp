from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TicketRequest:
    user_id: int
    subject: str
    message: str
    severity: str

