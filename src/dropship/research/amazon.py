"""Amazon search results via an Apify actor (default: junglee~amazon-crawler)."""

from __future__ import annotations

import copy
from urllib.parse import quote_plus

from ..config import Market
from ..http import BaseClient, load_fixture
from ..models import AmazonProduct, AmazonSummary
from ..utils import median, seeded_rng, to_float


def _first(item: dict, *keys):
    for k in keys:
        if item.get(k) not in (None, "", []):
            return item[k]
    return None


def parse_amazon_item(item: dict) -> AmazonProduct:
    price = item.get("price")
    if isinstance(price, dict):
        price = price.get("value")
    ranks = _first(item, "bestsellerRanks", "bestSellersRank", "bsr")
    bsr, bsr_cat = None, None
    if isinstance(ranks, list) and ranks:
        r0 = min(ranks, key=lambda r: to_float(r.get("rank"), 1e12) if isinstance(r, dict) else 1e12)
        if isinstance(r0, dict):
            bsr, bsr_cat = to_float(r0.get("rank")), r0.get("category")
    elif ranks is not None:
        bsr = to_float(ranks)
    seller = item.get("seller")
    if isinstance(seller, dict):
        seller = seller.get("name")
    seller = seller or _first(item, "sellerName", "brand", "manufacturer")
    reviews = _first(item, "reviewsCount", "reviewCount", "ratingsCount")
    offers = _first(item, "numberOfOffers", "offersCount", "sellersCount")
    return AmazonProduct(
        title=item.get("title") or "",
        asin=_first(item, "asin", "ASIN"),
        price=to_float(price),
        rating=to_float(_first(item, "stars", "rating")),
        reviews=int(to_float(reviews, 0)) if reviews is not None else None,
        bsr=int(bsr) if bsr else None,
        bsr_category=bsr_cat,
        seller=seller,
        offers=int(to_float(offers, 0)) if offers is not None else None,
        url=item.get("url"),
    )


def summarise(products: list[AmazonProduct], domain: str) -> AmazonSummary:
    prices = [p.price for p in products if p.price]
    ratings = [p.rating for p in products if p.rating]
    reviews = [p.reviews for p in products if p.reviews is not None]
    bsrs = [p.bsr for p in products if p.bsr]
    return AmazonSummary(
        domain=domain, count=len(products),
        price_min=min(prices) if prices else None, price_median=median(prices),
        price_max=max(prices) if prices else None,
        rating_avg=round(sum(ratings) / len(ratings), 2) if ratings else None,
        reviews_median=median(reviews), reviews_total=sum(reviews),
        best_bsr=min(bsrs) if bsrs else None,
        sellers=len({p.seller.lower() for p in products if p.seller}),
        offers_total=sum(p.offers or 1 for p in products),
        products=products,
    )


class ApifyAmazonClient(BaseClient):
    source = "apify"
    URL = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
    timeout = 300.0

    def has_credentials(self) -> bool:
        return self.settings.has_keys("APIFY_TOKEN")

    def search(self, keyword: str, market: Market, max_items: int = 20) -> AmazonSummary:
        actor = self.settings.apify_amazon_actor
        search_url = f"https://www.{market.amazon_domain}/s?k={quote_plus(keyword)}"
        body = {
            "categoryOrProductUrls": [{"url": search_url}],
            "maxItemsPerStartUrl": max_items,
            "proxyCountry": "AUTO_SELECT_PROXY_COUNTRY",
        }
        items = self.call(f"amazon_{actor}", self.URL.format(actor=actor), method="POST",
                          json_body=body,
                          headers={"Authorization": f"Bearer {self.settings.key('APIFY_TOKEN')}"})
        products = [parse_amazon_item(i) for i in (items or []) if isinstance(i, dict)]
        return summarise(products[:max_items], market.amazon_domain)

    def mock_response(self, endpoint, params):
        url = params["body"]["categoryOrProductUrls"][0]["url"]
        kw = url.split("k=", 1)[-1].replace("+", " ")
        rng = seeded_rng("amazon", url)
        items = []
        for raw in load_fixture("apify_amazon.json"):
            item = copy.deepcopy(raw)
            item["title"] = item["title"].replace("{Keyword}", kw.title())
            item["price"]["value"] = round(item["price"]["value"] * rng.uniform(0.75, 1.5), 2)
            item["reviewsCount"] = int(item["reviewsCount"] * rng.uniform(0.1, 2.5))
            item["bestsellerRanks"][0]["rank"] = int(item["bestsellerRanks"][0]["rank"] * rng.uniform(0.3, 4))
            items.append(item)
        return items
