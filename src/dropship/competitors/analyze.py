"""Summarise what competitor stores do well and where the gaps are."""

from __future__ import annotations

import logging
import re

from ..models import CompetitorStore, ShoppingSummary
from ..research.serpapi import is_marketplace
from ..utils import html_to_text, median, to_float
from .shopify import ShopifyInspector, detect_theme

log = logging.getLogger("dropship")

FREE_THEMES = {"dawn", "refresh", "sense", "craft", "studio", "taste", "crave", "colorblock",
               "ride", "spotlight", "origin", "publisher", "trade", "debut", "brooklyn", "horizon"}


def competitor_domains(shopping: ShoppingSummary | None, extra: list[str] | None = None,
                       limit: int = 5) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for d in extra or []:
        d = re.sub(r"^https?://", "", d.strip()).strip("/").removeprefix("www.")
        if d:
            seen.setdefault(d, d)
    for offer in (shopping.offers if shopping else []):
        if offer.domain and not is_marketplace(offer.domain, offer.source):
            seen.setdefault(offer.domain, offer.source)
    return list(seen.items())[:limit]


def _keyword_tokens(keyword: str) -> set[str]:
    stop = {"for", "the", "and", "with", "a", "of", "to", "in"}
    return {t for t in re.findall(r"[a-z0-9]+", keyword.lower()) if t not in stop and len(t) > 2}


def _matches(title: str, tokens: set[str]) -> bool:
    words = set(re.findall(r"[a-z0-9]+", title.lower()))
    return bool(tokens) and len(tokens & words) >= max(1, len(tokens) // 2)


def parse_shipping_policy(text: str) -> tuple[tuple[int | None, int | None] | None, float | None, bool]:
    # several ranges usually exist (processing 1-2 days, delivery 5-9 days): keep the longest
    ranges = [(int(a), int(b)) for a, b in re.findall(
        r"(\d{1,2})\s*(?:-|–|to)\s*(\d{1,2})\s*(?:business\s+|working\s+)?days", text, re.I)]
    days = max(ranges, key=lambda r: r[1]) if ranges else None
    threshold = None
    m = re.search(r"free\s+shipping[^.]{0,40}?(?:over|above|from)\s*[$£€]?\s*(\d+(?:[.,]\d+)?)", text, re.I)
    if m:
        threshold = to_float(m.group(1))
    free = bool(re.search(r"free\s+shipping", text, re.I))
    return days, threshold, free


def parse_refund_days(text: str) -> int | None:
    m = re.search(r"(\d{1,3})[\s-]*days?", text, re.I)
    return int(m.group(1)) if m else None


def inspect_store(inspector: ShopifyInspector, domain: str, source_name: str, keyword: str,
                  our_price: float | None = None) -> CompetitorStore:
    store = CompetitorStore(domain=domain, source_name=source_name)
    products = inspector.products(domain)
    if products is None:
        store.errors.append("not a Shopify store or /products.json disabled")
        return store
    store.is_shopify = True
    store.product_count = len(products)
    tokens = _keyword_tokens(keyword)
    matching = [p for p in products if _matches(p.get("title", ""), tokens)] or products
    store.matching_products = len([p for p in products if _matches(p.get("title", ""), tokens)])
    prices = [to_float(v.get("price")) for p in matching for v in (p.get("variants") or [])[:1]]
    prices = [p for p in prices if p]
    if prices:
        store.price_min, store.price_median, store.price_max = min(prices), median(prices), max(prices)
    imgs = [len(p.get("images") or []) for p in matching]
    store.images_avg = round(sum(imgs) / len(imgs), 1) if imgs else None
    compare_at = any((v.get("compare_at_price") or "") not in ("", None)
                     for p in matching for v in (p.get("variants") or []))

    home = inspector.home(domain) or ""
    store.theme = detect_theme(home)

    faq_html = inspector.faq(domain)
    if faq_html:
        faq_text = html_to_text(faq_html)
        store.faq_found = True
        store.faq_questions = sum(1 for ln in faq_text.splitlines() if ln.strip().endswith("?"))

    ship_html = inspector.policy(domain, "shipping")
    if ship_html:
        text = html_to_text(ship_html)
        store.shipping_policy = text[:280]
        store.shipping_days, store.free_shipping_threshold, store.free_shipping = parse_shipping_policy(text)
    refund_html = inspector.policy(domain, "refund")
    if refund_html:
        store.refund_days = parse_refund_days(html_to_text(refund_html))

    # ------------------------------------------------------------ verdicts
    s, g = store.strengths, store.gaps
    if store.images_avg is not None:
        (s if store.images_avg >= 6 else g if store.images_avg <= 3 else []).append(
            f"{store.images_avg:.0f} images per product on average")
    if store.faq_found and store.faq_questions >= 4:
        s.append(f"FAQ page answers {store.faq_questions} questions")
    elif not store.faq_found:
        g.append("No FAQ page – objections are left unanswered")
    if store.refund_days and store.refund_days >= 30:
        s.append(f"{store.refund_days}-day returns")
    elif store.refund_days:
        g.append(f"Short {store.refund_days}-day return window")
    else:
        g.append("No clear refund policy found")
    if store.free_shipping:
        s.append("Free shipping" + (f" over ${store.free_shipping_threshold:.0f}"
                                    if store.free_shipping_threshold else ""))
    else:
        g.append("No free-shipping offer")
    if store.shipping_days and store.shipping_days[1] and store.shipping_days[1] > 10:
        g.append(f"Slow delivery ({store.shipping_days[0]}-{store.shipping_days[1]} days)")
    elif store.shipping_days:
        s.append(f"Delivery promise {store.shipping_days[0]}-{store.shipping_days[1]} days")
    if compare_at:
        s.append("Uses compare-at (anchor) pricing")
    if any("bundle" in (p.get("title") or "").lower() or "pack" in (p.get("title") or "").lower()
           for p in products):
        s.append("Sells bundles / multi-packs")
    else:
        g.append("No bundles or multi-packs – AOV opportunity")
    if store.product_count > 150:
        g.append(f"General store ({store.product_count} products) – weak niche branding")
    elif store.product_count <= 30:
        s.append(f"Focused catalogue ({store.product_count} products)")
    if store.theme and store.theme.lower() in FREE_THEMES:
        g.append(f"Free theme ({store.theme}) – easy to match or beat on design")
    elif store.theme:
        s.append(f"Premium/custom theme ({store.theme})")
    if our_price and store.price_median:
        diff = (our_price - store.price_median) / store.price_median
        (s if diff > 0.1 else g if diff < -0.1 else s).append(
            f"Their median price ${store.price_median:.2f} vs our ${our_price:.2f} ({diff * 100:+.0f}%)")
    return store


def analyze_competitors(inspector: ShopifyInspector, shopping: ShoppingSummary | None, keyword: str,
                        *, our_price: float | None = None, extra_domains: list[str] | None = None,
                        limit: int = 5) -> list[CompetitorStore]:
    stores = []
    for domain, name in competitor_domains(shopping, extra_domains, limit):
        try:
            stores.append(inspect_store(inspector, domain, name, keyword, our_price))
        except Exception as exc:  # network oddities must not kill a run
            log.warning("competitor %s: %s", domain, exc)
            stores.append(CompetitorStore(domain=domain, source_name=name, errors=[str(exc)]))
    return stores
