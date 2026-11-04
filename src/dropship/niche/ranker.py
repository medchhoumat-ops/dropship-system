"""Rank niches by demand, trend, competition and price range."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from ..config import Market, Settings
from ..http import ApiError
from ..research.service import trend_change
from ..utils import clamp, median
from .expand import merge_ideas, seed_niches

log = logging.getLogger("dropship")

NICHE_WEIGHTS = {"demand": 35, "trend": 20, "competition": 25, "price": 20}
PRICE_SWEET_SPOT = (20.0, 60.0)  # retail where a $5–15 landed product sells at 4–5x


@dataclass
class ProductIdea:
    keyword: str
    volume: int = 0
    cpc: float = 0.0
    competition: float = 0.0
    trend_change: float = 0.0


@dataclass
class NicheResult:
    name: str
    category: str
    head_term: str
    ideas: list[ProductIdea] = field(default_factory=list)
    demand: int = 0  # total monthly searches across ideas
    trend: float = 0.0  # average 12-month change
    competition: float = 0.0  # average 0..1
    price_min: float | None = None
    price_median: float | None = None
    price_max: float | None = None
    components: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


def price_fit(med: float | None) -> float:
    if med is None:
        return 0.5
    lo, hi = PRICE_SWEET_SPOT
    if lo <= med <= hi:
        return 1.0
    return clamp(med / lo) if med < lo else clamp(1 - (med - hi) / hi)


def _score(n: NicheResult) -> None:
    avg_vol = n.demand / max(len(n.ideas), 1)
    comps = {
        "demand": clamp(math.log10(max(n.demand, 1)) / 5.3) * 0.6 + clamp(math.log10(max(avg_vol, 1)) / 4.5) * 0.4,
        "trend": clamp((n.trend + 0.3) / 0.8),
        "competition": 1 - clamp(n.competition),
        "price": price_fit(n.price_median),
    }
    n.components = {k: round(v, 3) for k, v in comps.items()}
    n.score = round(sum(comps[k] * w for k, w in NICHE_WEIGHTS.items()), 1)
    n.reasons = [
        f"{n.demand:,} monthly searches across {len(n.ideas)} product ideas",
        f"12-month trend {n.trend * 100:+.0f}% (avg)",
        f"Paid competition {n.competition:.2f} (0 = empty, 1 = saturated)",
    ]
    if n.price_median is not None:
        n.reasons.append(f"Google Shopping prices ${n.price_min:.0f}–${n.price_max:.0f} "
                         f"(median ${n.price_median:.0f}; sweet spot ${PRICE_SWEET_SPOT[0]:.0f}–"
                         f"${PRICE_SWEET_SPOT[1]:.0f})")


def deep_search(seeds: list[str], market: Market, settings: Settings, clients) -> list[NicheResult]:
    """Expand seeds into niches, measure each product idea, rank, return top N."""
    niches: list[NicheResult] = []
    for seed in seeds:
        for sub, starters in seed_niches(seed).items():
            head = starters[0] if starters else sub
            related: list[str] = []
            try:
                for probe in starters[:2] or [sub]:  # probe real products, not category names
                    related += [m.keyword for m in clients.semrush.related(probe, market, limit=10)
                                if m.volume >= 100]
            except ApiError as exc:
                log.warning("related keywords for %s: %s", sub, exc)
            ideas_kw = merge_ideas(starters, related, settings.max_ideas_per_niche)
            n = NicheResult(name=sub, category=seed.strip().lower(), head_term=head)
            for kw in ideas_kw:
                try:
                    m = clients.semrush.keyword_overview(kw, market)
                except ApiError as exc:
                    log.warning("semrush %s: %s", kw, exc)
                    m = None
                if m and m.volume > 0:
                    n.ideas.append(ProductIdea(kw, m.volume, m.cpc, m.competition, trend_change(m.trend)))
            n.ideas.sort(key=lambda i: i.volume, reverse=True)
            if len(n.ideas) < settings.min_ideas:
                log.info("niche %s dropped: only %d ideas with volume", sub, len(n.ideas))
                continue
            n.demand = sum(i.volume for i in n.ideas)
            n.trend = round(sum(i.trend_change * i.volume for i in n.ideas) / max(n.demand, 1), 3)
            n.competition = round(sum(i.competition for i in n.ideas) / len(n.ideas), 3)
            _score(n)
            niches.append(n)

    # stage 2: price range from Google Shopping for the best candidates only (saves credits)
    niches.sort(key=lambda n: n.score, reverse=True)
    for n in niches[: settings.enrich_top]:
        prices: list[float] = []
        for idea in n.ideas[:2]:
            try:
                shop = clients.serpapi.shopping(idea.keyword, market, 20)
                prices += [o.price for o in shop.offers if o.price]
            except ApiError as exc:
                log.warning("shopping %s: %s", idea.keyword, exc)
        if prices:
            n.price_min, n.price_median, n.price_max = min(prices), median(prices), max(prices)
        _score(n)
    niches.sort(key=lambda n: n.score, reverse=True)
    return niches[: settings.top_niches]
