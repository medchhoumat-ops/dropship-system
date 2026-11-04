"""Rule-based write-up for each pick: why, risks, how to scale."""

from __future__ import annotations

from ..config import MARKETS, Market
from ..filters import FilterResult
from ..models import CompetitorStore, KeywordResearch, SourcedProduct
from ..pricing import Pricing
from .score import ScoreBreakdown


def _pct(x: float) -> str:
    return f"{x * 100:+.0f}%"


def write_pick(
    product: SourcedProduct,
    research: KeywordResearch | None,
    pricing: Pricing | None,
    score: ScoreBreakdown,
    filt: FilterResult,
    market: Market,
    competitors: list[CompetitorStore] | None = None,
) -> dict[str, list[str]]:
    why: list[str] = []
    risks: list[str] = []
    scale: list[str] = []
    c = score.components

    # ------------------------------------------------------------------ why
    if research:
        if research.volume:
            why.append(f"~{research.volume:,} monthly searches for “{research.keyword}” in {market.name}.")
        if research.trend_change > 0.1:
            why.append(f"Search interest is rising ({_pct(research.trend_change)} over 12 months).")
        elif research.trend_change > -0.05:
            why.append("Stable, non-seasonal demand over the last 12 months.")
        if research.amazon and research.amazon.price_median:
            why.append(f"Amazon page-1 median price ${research.amazon.price_median:.2f} "
                       f"anchors buyer expectations.")
    if pricing:
        why.append(f"Landed ${pricing.landed_cost:.2f} → retail ${pricing.price:.2f} "
                   f"({pricing.margin_pct * 100:.0f}% margin, break-even CPA ${pricing.breakeven_cpa:.2f}, "
                   f"break-even ROAS {pricing.breakeven_roas:.2f}).")
    if filt.shipping:
        why.append(f"Ships from {filt.shipping.from_country} via {filt.shipping.method} in "
                   f"{filt.shipping.min_days}-{filt.shipping.max_days} days.")
    if len(product.variants) <= 1:
        why.append("Single variant: no size/colour returns, simple listing and ads.")

    # ------------------------------------------------------------------ risks
    risks.extend(f"Filter: {f}" for f in filt.failures)
    if research:
        if research.trend_change < -0.1:
            risks.append(f"Declining interest ({_pct(research.trend_change)}); validate before scaling.")
        if research.competition > 0.75:
            risks.append("High paid-search competition: Shopping CPCs may be expensive "
                         f"(Semrush CPC ${research.cpc:.2f}).")
        if research.amazon and (research.amazon.reviews_median or 0) > 2000:
            risks.append("Amazon listings have thousands of reviews – shoppers may just buy there; "
                         "differentiate with bundle, guarantee and content.")
        if research.shopping and research.amazon and research.amazon.price_median and pricing \
                and pricing.price > research.amazon.price_median * 1.6:
            risks.append(f"Our price ${pricing.price:.2f} is well above Amazon's median "
                         f"${research.amazon.price_median:.2f}; consider a bundle to justify it.")
    if pricing and pricing.breakeven_cpa < 12:
        risks.append(f"Thin ad budget per sale (break-even CPA ${pricing.breakeven_cpa:.2f}); "
                     "needs high CTR creatives or bundles to raise AOV.")
    risks.extend(n for n in filt.notes if "risk" in n)
    if product.supplier and product.platform == "aliexpress":
        risks.append("AliExpress seller: order a sample and confirm the local-warehouse stock with the "
                     "seller before running ads.")
    risks.append("Check trademarks/patents and product-safety rules (CE/UKCA/CPSC) before listing.")
    if competitors:
        strong = [s for s in competitors if len(s.strengths) > len(s.gaps)]
        if strong:
            risks.append(f"{len(strong)} competitor store(s) look well-run: "
                         + ", ".join(s.domain for s in strong[:3]) + ".")

    # ------------------------------------------------------------------ scale
    kw = research.keyword if research else product.title
    scale.append(f"Bundle: 2-pack / 3-pack at ~1.6x / 2.2x price to lift AOV above ${pricing.price * 1.6:.0f}."
                 if pricing else "Bundle: 2-pack / 3-pack to lift AOV.")
    scale.append("Upsells: post-purchase one-click add-on of a related store product, "
                 "plus a low-cost complementary accessory at checkout.")
    others = [m.code for m in MARKETS.values() if m.code != market.code]
    scale.append(f"More markets: once ROAS is stable, re-run `dropship source` for {', '.join(others)} "
                 "and list where local stock exists.")
    scale.append(f"Ad angles: (1) problem/solution demo for “{kw}”, (2) before/after in daily use, "
                 "(3) gift angle for the buyer's partner/parent, (4) comparison vs the usual alternative.")
    if c.get("trend", 0) > 0.6:
        scale.append("Trend is up: scale Google Shopping budgets 20% every 3 days while ROAS holds.")
    if c.get("competition", 0) > 0.6:
        scale.append("Low competition: test broad Performance Max early, then add search campaigns.")
    return {"why": why, "risks": risks, "scale": scale}
