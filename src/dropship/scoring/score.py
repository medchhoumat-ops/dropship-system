"""Winner score 0–100.

Components (each 0..1, then weighted):
  demand            monthly search volume (log scale, 100k+ = 1)
  trend             12-month momentum (-30% -> 0, +50% -> 1)
  competition       Semrush paid competition + Amazon review moat
  margin            profit margin after fees (40% -> 0, 75% -> 1)
  shipping          delivery speed (<=4 days = 1, 10+ days = 0)
  competitor_stores distinct sellers on Google Shopping (few = good, but 0 = unvalidated)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..filters import FilterResult
from ..models import KeywordResearch
from ..pricing import Pricing
from ..utils import clamp

WEIGHTS = {
    "demand": 25,
    "trend": 15,
    "competition": 15,
    "margin": 20,
    "shipping": 15,
    "competitor_stores": 10,
}


@dataclass
class ScoreBreakdown:
    components: dict[str, float] = field(default_factory=dict)  # 0..1
    points: dict[str, float] = field(default_factory=dict)  # weighted
    total: float = 0.0
    grade: str = "D"


def demand_score(volume: int) -> float:
    return clamp(math.log10(max(volume, 1)) / 5) if volume else 0.0


def trend_score(change: float) -> float:
    return clamp((change + 0.3) / 0.8)


def competition_score(research: KeywordResearch | None) -> float:
    if research is None:
        return 0.5
    paid = 1 - clamp(research.competition)
    amz = research.amazon
    if amz and amz.reviews_median is not None:
        # median page-1 reviews: 50 -> easy (1.0), 5000+ -> entrenched (0.0)
        moat = 1 - clamp((math.log10(max(amz.reviews_median, 1)) - 1.7) / 2.0)
        return round(0.5 * paid + 0.5 * moat, 3)
    return round(paid, 3)


def margin_score(pricing: Pricing | None) -> float:
    return clamp((pricing.margin_pct - 0.40) / 0.35) if pricing else 0.0


def shipping_score(filt: FilterResult | None) -> float:
    if not filt or not filt.shipping or filt.shipping.max_days is None:
        return 0.0
    return clamp((10 - filt.shipping.max_days) / 6)


def competitor_store_score(n: int | None) -> float:
    if n is None:
        return 0.5
    if n == 0:
        return 0.4  # nobody sells it: unvalidated demand
    return clamp(1 - (n - 3) / 27) if n > 3 else 1.0


def grade(total: float) -> str:
    return "A" if total >= 75 else "B" if total >= 60 else "C" if total >= 45 else "D"


def score_product(
    research: KeywordResearch | None,
    pricing: Pricing | None,
    filt: FilterResult | None,
    competitor_stores: int | None = None,
) -> ScoreBreakdown:
    if competitor_stores is None and research and research.shopping:
        competitor_stores = research.shopping.sellers
    comps = {
        "demand": demand_score(research.volume if research else 0),
        "trend": trend_score(research.trend_change if research else 0.0),
        "competition": competition_score(research),
        "margin": margin_score(pricing),
        "shipping": shipping_score(filt),
        "competitor_stores": competitor_store_score(competitor_stores),
    }
    comps = {k: round(v, 3) for k, v in comps.items()}
    points = {k: round(comps[k] * WEIGHTS[k], 1) for k in WEIGHTS}
    total = round(sum(points.values()), 1)
    if filt is not None and not filt.passed:
        total = round(total * 0.5, 1)  # failed hard filters: never a winner
    return ScoreBreakdown(components=comps, points=points, total=total, grade=grade(total))
