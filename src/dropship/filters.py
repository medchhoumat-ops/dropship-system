"""Hard filters a product must pass before it can be a pick.

1. single variant (no size / colour options)
2. stock in a warehouse inside or near the target market
3. a shipping method from that warehouse with delivery <= max_delivery_days
4. landed cost (item + shipping) between landed_min and landed_max USD
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import Market, Settings
from .models import ShippingOption, SourcedProduct

@dataclass
class FilterResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    warehouse: str | None = None
    shipping: ShippingOption | None = None
    item_cost: float | None = None  # unit cost from the chosen warehouse
    landed_cost: float | None = None


def is_single_variant(product: SourcedProduct) -> bool:
    """True when the customer has nothing to choose (no size/colour/style options)."""
    if len(product.variants) <= 1:
        return True
    distinct = {tuple(sorted(v.attributes.items())) if v.attributes else v.name.strip().lower()
                for v in product.variants}
    return len(distinct) == 1


def evaluate(product: SourcedProduct, market: Market, settings: Settings) -> FilterResult:
    res = FilterResult(passed=False)

    # 1. variants
    if settings.single_variant_only and not is_single_variant(product):
        opts = sorted({k for v in product.variants for k in v.attributes}) or ["options"]
        res.failures.append(f"{len(product.variants)} variants ({', '.join(opts)}) – need a single variant")
        if not product.stock and not product.shipping:  # lookups were skipped; nothing else to judge
            return res

    # 2. stock near the market
    eligible = [s for s in product.stock if s.quantity > 0 and s.country in market.warehouse_countries]
    if not eligible:
        where = ", ".join(f"{s.country}:{s.quantity}" for s in product.stock) or "unknown"
        res.failures.append(f"no stock in/near {market.code} (stock: {where})")
    else:
        local = [s for s in eligible if s.country == market.iso]
        best_wh = max(local or eligible, key=lambda s: s.quantity)
        res.notes.append(f"stock {best_wh.quantity} in {best_wh.name or best_wh.country}")
        if best_wh.quantity < 20:
            res.notes.append("low stock – risk of selling out")

    # 3. shipping speed from an eligible warehouse
    eligible_countries = {s.country for s in eligible}
    fast = [o for o in product.shipping
            if o.from_country in eligible_countries and o.max_days is not None
            and o.max_days <= settings.max_delivery_days]
    if fast:
        res.shipping = min(fast, key=lambda o: (o.cost, o.max_days or 99))
        res.warehouse = res.shipping.from_country
    else:
        if product.shipping:
            quickest = min(product.shipping, key=lambda o: o.max_days or 99)
            res.failures.append(
                f"no method <= {settings.max_delivery_days} days from a local warehouse "
                f"(fastest: {quickest.method} from {quickest.from_country}, "
                f"{quickest.min_days}-{quickest.max_days} days)")
        else:
            res.failures.append("no shipping quote available")

    # 4. landed cost
    ship = res.shipping or (min(product.shipping, key=lambda o: o.cost) if product.shipping else None)
    item_price = product.price_from(ship.from_country) if ship else product.price
    if item_price is None:
        res.failures.append("no item price")
    elif ship is not None:
        res.item_cost = item_price
        res.landed_cost = round(item_price + ship.cost, 2)
        if not settings.landed_min <= res.landed_cost <= settings.landed_max:
            res.failures.append(
                f"landed cost ${res.landed_cost:.2f} outside ${settings.landed_min:.0f}–${settings.landed_max:.0f}")

    res.passed = not res.failures
    return res
