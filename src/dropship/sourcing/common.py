"""Shared sourcing helpers and mock freight rules."""

from __future__ import annotations

from ..config import EU_WAREHOUSES

COUNTRY_NAMES = {
    "china": "CN", "china mainland": "CN", "united states": "US", "usa": "US", "spain": "ES",
    "france": "FR", "germany": "DE", "united kingdom": "GB", "uk": "GB", "poland": "PL",
    "czech republic": "CZ", "italy": "IT", "belgium": "BE", "netherlands": "NL", "canada": "CA",
    "russian federation": "RU", "australia": "AU", "brazil": "BR", "turkey": "TR", "mexico": "MX",
    "saudi arabia": "SA", "korea": "KR", "vietnam": "VN", "united arab emirates": "AE",
}

SHIP_FROM_NAMES = {"ships from", "ship from", "shipping from", "origin", "warehouse"}


def country_iso(name: str | None) -> str:
    if not name:
        return "CN"
    n = name.strip()
    if len(n) == 2:
        return n.upper().replace("UK", "GB")
    return COUNTRY_NAMES.get(n.lower(), n[:2].upper())


def mock_shipping(start: str, end: str) -> list[dict]:
    """Deterministic fake freight table: (method, cost USD, min days, max days)."""
    region = {"US": "NA", "CA": "NA", "MX": "NA", "GB": "EU", **{c: "EU" for c in EU_WAREHOUSES}}
    if start == end:
        return [{"method": "Local Express", "cost": 3.80, "min": 2, "max": 5},
                {"method": "Local Economy", "cost": 2.90, "min": 4, "max": 8}]
    if region.get(start) and region.get(start) == region.get(end):
        return [{"method": "Regional Post", "cost": 5.20, "min": 4, "max": 9}]
    if start == "CN":
        return [{"method": "Economy Post", "cost": 2.40, "min": 12, "max": 25},
                {"method": "Packet Plus", "cost": 4.10, "min": 8, "max": 15}]
    return [{"method": "International Express", "cost": 9.80, "min": 6, "max": 12}]
