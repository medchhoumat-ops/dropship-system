"""Seed -> sub-niches -> keyword ideas (curated taxonomy + Semrush related keywords)."""

from __future__ import annotations

import json
import re
from importlib import resources

BLOCKLIST = ("amazon", "walmart", "target", "ebay", "temu", "aliexpress", "shein", "near me", "diy",
             "how to", "reddit", "review", "reviews", "vs", "free", "used", "repair", "manual",
             "meaning", "wiki", "youtube", "tiktok", "ikea", "costco")


def load_taxonomy() -> dict[str, dict[str, list[str]]]:
    text = resources.files("dropship.niche").joinpath("taxonomy.json").read_text(encoding="utf-8")
    return json.loads(text)


def seed_niches(seed: str) -> dict[str, list[str]]:
    """Sub-niches with starter keywords for a seed (falls back to the seed itself)."""
    tax = load_taxonomy()
    key = seed.strip().lower()
    if key in tax:
        return tax[key]
    for cat, subs in tax.items():  # seed matches a sub-niche name
        if key in subs:
            return {key: subs[key]}
        if key.rstrip("s") == cat.rstrip("s"):
            return subs
    return {key: [key]}


LEADING_FILLER = re.compile(r"^(best|top|cheap|good|new|buy)\s+", re.I)


def normalise(kw: str) -> str:
    return LEADING_FILLER.sub("", " ".join(kw.lower().split()))


def is_product_keyword(kw: str) -> bool:
    k = kw.lower()
    return not any(re.search(rf"\b{re.escape(b)}\b", k) for b in BLOCKLIST) and 1 <= len(k.split()) <= 6


def merge_ideas(base: list[str], related: list[str], limit: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for kw in [*base, *related]:
        norm = normalise(kw)
        if norm in seen or not is_product_keyword(norm):
            continue
        seen.add(norm)
        out.append(norm)
        if len(out) >= limit:
            break
    return out
