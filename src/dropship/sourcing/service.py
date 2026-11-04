"""Resolve a query (keyword, CJ pid or AliExpress id) into SourcedProducts."""

from __future__ import annotations

import logging
import re

from ..config import Market
from ..http import ApiError
from ..models import SourcedProduct

log = logging.getLogger("dropship")

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def detect_query(query: str) -> tuple[str, str]:
    """Return (kind, value) with kind in {'cj', 'aliexpress', 'keyword'}.

    Accepts explicit prefixes ``cj:``/``ae:``, product URLs, CJ pids (UUID or
    18+ digit numbers) and AliExpress ids (10–17 digits, e.g. 1005…).
    """
    q = query.strip()
    low = q.lower()
    if low.startswith("cj:"):
        return "cj", q[3:].strip()
    if low.startswith(("ae:", "aliexpress:")):
        return "aliexpress", q.split(":", 1)[1].strip()
    m = re.search(r"aliexpress\.[a-z.]+/item/(\d+)", low)
    if m:
        return "aliexpress", m.group(1)
    m = re.search(r"cjdropshipping\.com/.*-p-([0-9a-fA-F-]{10,})\.html", q)
    if m:
        return "cj", m.group(1)
    if UUID_RE.match(q):
        return "cj", q
    if q.isdigit():
        return ("cj", q) if len(q) >= 18 else ("aliexpress", q)
    return "keyword", q


def source_products(
    query: str,
    market: Market,
    clients,
    *,
    limit: int = 5,
    platforms: tuple[str, ...] = ("cj", "aliexpress"),
) -> list[SourcedProduct]:
    kind, value = detect_query(query)
    if kind == "cj":
        return [clients.cj.sourced_product(value, market)]
    if kind == "aliexpress":
        return [clients.aliexpress.sourced_product(value, market)]

    products: list[SourcedProduct] = []
    if "cj" in platforms:
        try:
            for hit in clients.cj.search(value, size=limit, warehouse=market.iso):
                try:
                    p = clients.cj.sourced_product(hit["pid"], market)
                    if hit.get("title") and clients.cj.mock:
                        p.title = hit["title"]
                    products.append(p)
                except ApiError as exc:
                    log.warning("cj %s: %s", hit.get("pid"), exc)
        except ApiError as exc:
            log.warning("cj search failed: %s", exc)
    if "aliexpress" in platforms:
        try:
            for hit in clients.aliexpress.search(value, market, size=limit):
                try:
                    p = clients.aliexpress.sourced_product(hit["pid"], market)
                    if hit.get("title") and clients.aliexpress.mock:
                        p.title = hit["title"]
                    products.append(p)
                except ApiError as exc:
                    log.warning("aliexpress %s: %s", hit.get("pid"), exc)
        except ApiError as exc:
            log.warning("aliexpress search failed: %s", exc)
    return products
