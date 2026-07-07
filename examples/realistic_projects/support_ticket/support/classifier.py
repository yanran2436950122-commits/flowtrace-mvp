from __future__ import annotations


def keyword_topic(message: str) -> str:
    text = message.lower()
    if "refund" in text or "invoice" in text:
        return "billing"
    if "login" in text or "password" in text:
        return "account"
    return "general"

