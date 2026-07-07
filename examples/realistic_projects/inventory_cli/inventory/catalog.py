from __future__ import annotations


STOCK = {
    "warehouse-a": {"sku-100": 12, "sku-200": 3},
    "warehouse-b": {"sku-100": 4, "sku-200": 9},
}


def read_stock(location: str, sku: str) -> int:
    return int(STOCK.get(location, {}).get(sku, 0))


def write_stock(location: str, sku: str, quantity: int) -> None:
    STOCK.setdefault(location, {})[sku] = quantity

