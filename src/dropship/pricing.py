"""Retail price, margin and break-even metrics.

price = landed x multiplier (4–5, cheaper items get the higher multiplier),
rounded to .99. Shopify fees ~2.9% + $0.30 per order.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import Market, Settings


@dataclass
class Pricing:
    landed_cost: float
    multiplier: float
    price: float  # recommended retail (USD)
    price_low: float  # landed x multiplier_min
    price_high: float  # landed x multiplier_max
    fees: float
    profit: float  # per order before ad spend
    margin_pct: float  # profit / price
    breakeven_cpa: float  # max ad cost per purchase before losing money
    breakeven_roas: float  # revenue / ad spend at break-even
    local_currency: str = "USD"
    local_price: float | None = None
    capped_by_market: bool = False  # price lowered to the Amazon/Shopping median
    market_price: float | None = None


def round_99(x: float) -> float:
    """Round to the nearest X.99 (minimum 0.99)."""
    return max(0.99, round(x) - 0.01) if x >= 1 else 0.99


def multiplier_for(landed: float, settings: Settings) -> float:
    lo, hi = settings.landed_min, settings.landed_max
    if hi <= lo:
        return settings.multiplier_max
    t = min(1.0, max(0.0, (landed - lo) / (hi - lo)))
    return round(settings.multiplier_max - t * (settings.multiplier_max - settings.multiplier_min), 2)


def price_product(landed: float, settings: Settings, market: Market | None = None,
                  market_price: float | None = None) -> Pricing:
    """`market_price` (e.g. Amazon page-1 median) caps the price: Google Shopping shows
    competitors side by side, so pricing above the market median rarely gets clicks."""
    mult = multiplier_for(landed, settings)
    price = round_99(landed * mult)
    capped = False
    if market_price and price > market_price:
        price, capped = round_99(market_price), True
        mult = round(price / landed, 2) if landed else mult
    fees = round(price * settings.fee_pct + settings.fee_fixed, 2)
    profit = round(price - landed - fees, 2)
    be_cpa = max(profit, 0.0)
    pricing = Pricing(
        landed_cost=round(landed, 2), multiplier=mult, price=price,
        price_low=round_99(landed * settings.multiplier_min),
        price_high=round_99(landed * settings.multiplier_max),
        fees=fees, profit=profit, margin_pct=round(profit / price, 3) if price else 0.0,
        breakeven_cpa=round(be_cpa, 2),
        breakeven_roas=round(price / be_cpa, 2) if be_cpa > 0 else math.inf,
        capped_by_market=capped, market_price=market_price,
    )
    if market is not None:
        pricing.local_currency = market.currency
        pricing.local_price = price if market.currency == "USD" else round_99(price * market.usd_rate)
    return pricing
