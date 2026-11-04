"""Small helpers shared by modules."""

from __future__ import annotations

import dataclasses
import hashlib
import html
import random
import re
import statistics
from typing import Any, Iterable


def seeded_rng(*parts: Any) -> random.Random:
    """Deterministic RNG for mock data (same keyword -> same numbers)."""
    digest = hashlib.sha256("|".join(str(p).lower() for p in parts).encode()).hexdigest()
    return random.Random(int(digest[:12], 16))


def to_jsonable(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: to_jsonable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):
        return None  # JSON has no NaN/Infinity
    return obj


def median(values: Iterable[float]) -> float | None:
    vals = [v for v in values if v is not None]
    return round(statistics.median(vals), 2) if vals else None


def to_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"-?\d[\d,]*\.?\d*", str(value).replace(" ", " "))
    if not m:
        return default
    s = m.group(0)
    # "1.234,56" (EU) vs "1,234.56" (US)
    if "," in s and "." in s and s.rfind(",") > s.rfind("."):
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." not in s and len(s.split(",")[-1]) == 2:
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return default


def parse_days(text: Any) -> tuple[int | None, int | None]:
    """'7-12' / '7~12 days' / '5' -> (min, max)."""
    nums = [int(n) for n in re.findall(r"\d+", str(text or ""))]
    if not nums:
        return None, None
    return min(nums[:2]), max(nums[:2])


def html_to_text(markup: str) -> str:
    markup = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|summary|details)>", "\n", markup)
    text = html.unescape(re.sub(r"<[^>]+>", " ", markup))
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))
