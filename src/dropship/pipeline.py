"""High-level flows used by the CLI: research, source, niche."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

from . import __version__
from .competitors import analyze_competitors
from .config import Market, Settings
from .creative import creative_pack
from .filters import evaluate
from .models import KeywordResearch, SourcedProduct
from .niche import deep_search
from .pricing import price_product
from .research import Clients, research_keyword
from .scoring import score_product, write_pick
from .sourcing import detect_query, source_products
from .utils import to_jsonable

log = logging.getLogger("dropship")


def new_run(command: str, market: Market, settings: Settings, clients: Clients, params: dict) -> dict:
    now = datetime.now(UTC)
    return {
        "id": f"{now:%Y%m%d-%H%M%S}-{command}",
        "command": command,
        "created_at": now.isoformat(timespec="seconds"),
        "version": __version__,
        "country": market.code,
        "market": to_jsonable(market),
        "params": params,
        "modes": clients.modes(),
        "rules": {
            "landed_usd": [settings.landed_min, settings.landed_max],
            "max_delivery_days": settings.max_delivery_days,
            "single_variant_only": settings.single_variant_only,
            "multiplier": [settings.multiplier_min, settings.multiplier_max],
            "fees": f"{settings.fee_pct * 100:.1f}% + ${settings.fee_fixed:.2f}",
            "warehouses": list(market.warehouse_countries),
        },
        "research": [],
        "competitors": [],
        "niches": [],
        "picks": [],
        "rejected": [],
    }


def keyword_from_title(title: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", title)
    return " ".join(words[:4]).lower() or title


def run_research(keyword: str, market: Market, settings: Settings, clients: Clients, *,
                 amazon: bool = True, competitors: bool = True,
                 extra_domains: list[str] | None = None) -> dict:
    run = new_run("research", market, settings, clients,
                  {"keyword": keyword, "amazon": amazon, "competitors": competitors})
    res = research_keyword(keyword, market, settings, clients, amazon=amazon)
    run["research"].append(to_jsonable(res))
    if competitors:
        stores = analyze_competitors(clients.shopify, res.shopping, keyword,
                                     extra_domains=extra_domains, limit=settings.max_competitor_stores)
        run["competitors"] = to_jsonable(stores)
    return run


def evaluate_products(products: list[SourcedProduct], research: KeywordResearch | None, market: Market,
                      settings: Settings, niche: str = "") -> tuple[list[dict], list[dict]]:
    picks, rejected = [], []
    for p in products:
        filt = evaluate(p, market, settings)
        pricing = price_product(filt.landed_cost, settings, market) if filt.landed_cost else None
        score = score_product(research, pricing, filt)
        entry = {
            "keyword": research.keyword if research else keyword_from_title(p.title),
            "product": p, "filter": filt, "pricing": pricing, "score": score,
        }
        if filt.passed:
            entry["narrative"] = write_pick(p, research, pricing, score, filt, market)
            entry["creative"] = creative_pack(p.title, entry["keyword"], niche, market)
            picks.append(entry)
        else:
            rejected.append(entry)
    picks.sort(key=lambda e: e["score"].total, reverse=True)
    rejected.sort(key=lambda e: e["score"].total, reverse=True)
    return picks, rejected


def run_source(query: str, market: Market, settings: Settings, clients: Clients, *,
               limit: int = 5, keyword: str | None = None, platforms: tuple[str, ...] = ("cj", "aliexpress"),
               amazon: bool = True, competitors: bool = True, niche: str = "") -> dict:
    run = new_run("source", market, settings, clients,
                  {"query": query, "limit": limit, "platforms": list(platforms), "keyword": keyword})
    products = source_products(query, market, clients, limit=limit, platforms=platforms)
    kind, value = detect_query(query)
    kw = keyword or (value if kind == "keyword" else keyword_from_title(products[0].title if products else value))
    research = research_keyword(kw, market, settings, clients, amazon=amazon)
    run["research"].append(to_jsonable(research))
    picks, rejected = evaluate_products(products, research, market, settings, niche)
    if competitors:
        our_price = picks[0]["pricing"].price if picks and picks[0]["pricing"] else None
        stores = analyze_competitors(clients.shopify, research.shopping, kw, our_price=our_price,
                                     limit=settings.max_competitor_stores)
        run["competitors"] = to_jsonable(stores)
        for e in picks:
            e["narrative"] = write_pick(e["product"], research, e["pricing"], e["score"], e["filter"],
                                        market, stores)
    run["picks"] = to_jsonable(picks)
    run["rejected"] = to_jsonable(rejected)
    return run


def run_niche(seeds: list[str], market: Market, settings: Settings, clients: Clients, *,
              source: bool = False, per_idea: int = 3) -> dict:
    run = new_run("niche", market, settings, clients, {"seeds": seeds, "source": source})
    niches = deep_search(seeds, market, settings, clients)
    run["niches"] = to_jsonable(niches)
    if source and niches:
        best = niches[0]
        all_picks, all_rejected = [], []
        for idea in best.ideas[: max(settings.min_ideas, 4)]:
            products = source_products(idea.keyword, market, clients, limit=per_idea)
            research = research_keyword(idea.keyword, market, settings, clients, amazon=False)
            run["research"].append(to_jsonable(research))
            picks, rejected = evaluate_products(products, research, market, settings, best.name)
            all_picks.extend(picks[:1])  # best product per idea -> a 4-product store
            all_rejected.extend(rejected)
        all_picks.sort(key=lambda e: e["score"].total, reverse=True)
        run["picks"] = to_jsonable(all_picks)
        run["rejected"] = to_jsonable(all_rejected[:20])
    return run
