"""Orchestrates per-keyword research across Semrush, SerpApi and Apify."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ..config import Market, Settings
from ..http import ApiError
from ..models import KeywordResearch
from .amazon import ApifyAmazonClient
from .semrush import SemrushClient
from .serpapi import SerpApiClient

log = logging.getLogger("dropship")


@dataclass
class Clients:
    semrush: SemrushClient
    serpapi: SerpApiClient
    amazon: ApifyAmazonClient
    cj: object = None
    aliexpress: object = None
    shopify: object = None

    def modes(self) -> dict[str, str]:
        return {name: ("mock" if getattr(c, "mock", True) else "live")
                for name, c in vars(self).items() if c is not None}


def make_clients(settings: Settings, mock: bool | None = None) -> Clients:
    from ..competitors.shopify import ShopifyInspector
    from ..sourcing.aliexpress import AliExpressClient
    from ..sourcing.cj import CJClient

    return Clients(
        semrush=SemrushClient(settings, mock),
        serpapi=SerpApiClient(settings, mock),
        amazon=ApifyAmazonClient(settings, mock),
        cj=CJClient(settings, mock),
        aliexpress=AliExpressClient(settings, mock),
        shopify=ShopifyInspector(settings, mock),
    )


def trend_change(trend: list[float]) -> float:
    """Average of the last 3 months vs the first 3 months (0.25 = +25%)."""
    if len(trend) < 6:
        return 0.0
    first, last = sum(trend[:3]) / 3, sum(trend[-3:]) / 3
    return round((last - first) / first, 3) if first else 0.0


def research_keyword(
    keyword: str,
    market: Market,
    settings: Settings,
    clients: Clients,
    *,
    amazon: bool = True,
    shopping: bool = True,
) -> KeywordResearch:
    res = KeywordResearch(keyword=keyword, country=market.code)
    try:
        m = clients.semrush.keyword_overview(keyword, market)
        if m:
            res.volume, res.cpc, res.competition, res.trend = m.volume, m.cpc, m.competition, m.trend
    except ApiError as exc:
        res.errors.append(str(exc))

    if settings.use_google_trends:
        try:
            gt = clients.serpapi.trends(keyword, market)
            if gt:
                res.trend, res.trend_source = gt, "google_trends"
        except ApiError as exc:
            res.errors.append(str(exc))
    res.trend_change = trend_change(res.trend)

    if shopping:
        try:
            res.shopping = clients.serpapi.shopping(keyword, market, settings.shopping_max_items)
        except ApiError as exc:
            res.errors.append(str(exc))
    if amazon:
        try:
            res.amazon = clients.amazon.search(keyword, market, settings.amazon_max_items)
        except ApiError as exc:
            res.errors.append(str(exc))
    for e in res.errors:
        log.warning(e)
    return res
