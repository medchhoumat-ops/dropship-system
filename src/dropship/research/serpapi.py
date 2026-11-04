"""SerpApi: Google Shopping offers and (optional) Google Trends 12-month interest."""

from __future__ import annotations

import copy
from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse

from ..config import Market
from ..http import ApiError, BaseClient, load_fixture
from ..models import ShoppingOffer, ShoppingSummary
from ..utils import median, seeded_rng, to_float

MARKETPLACES = {"amazon", "walmart", "ebay", "etsy", "target", "temu", "aliexpress", "wish",
                "google", "cdiscount", "otto", "fnac", "argos", "bestbuy", "kaufland", "shein"}


def offer_domain(link: str | None) -> str | None:
    if not link:
        return None
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    if host.endswith("google.com") or ".google." in host:
        target = parse_qs(parsed.query).get("url") or parse_qs(parsed.query).get("q")
        if target and target[0].startswith("http"):
            return offer_domain(target[0])
        return None
    return host.removeprefix("www.") or None


def is_marketplace(domain: str | None, source: str = "") -> bool:
    text = f"{domain or ''} {source}".lower()
    return any(m in text for m in MARKETPLACES)


def monthly_buckets(timeline: list[dict], months: int = 12) -> list[float]:
    """Collapse weekly Google Trends points to `months` equal buckets (0..1)."""
    values = []
    for point in timeline:
        vals = point.get("values") or [{}]
        v = vals[0].get("extracted_value", to_float(vals[0].get("value"), 0))
        values.append(float(v or 0))
    if not values:
        return []
    size = max(1, len(values) / months)
    buckets = []
    for i in range(months):
        chunk = values[int(i * size): int((i + 1) * size)] or values[-1:]
        buckets.append(sum(chunk) / len(chunk))
    peak = max(buckets) or 1
    return [round(b / peak, 2) for b in buckets]


class SerpApiClient(BaseClient):
    source = "serpapi"
    URL = "https://serpapi.com/search.json"

    def has_credentials(self) -> bool:
        return self.settings.has_keys("SERPAPI_KEY")

    def check(self, endpoint, data):
        err = isinstance(data, dict) and data.get("error")
        if err and "hasn't returned any results" not in err:
            raise ApiError(f"serpapi {endpoint}: {err}")

    def _search(self, endpoint: str, params: dict) -> dict:
        return self.call(endpoint, self.URL, params,
                         secret_params={"api_key": self.settings.key("SERPAPI_KEY")})

    def shopping(self, keyword: str, market: Market, limit: int = 40) -> ShoppingSummary:
        data = self._search("google_shopping", {
            "engine": "google_shopping", "q": keyword, "gl": market.google_gl,
            "hl": market.google_hl, "google_domain": market.google_domain, "num": limit,
        })
        offers = []
        for r in (data.get("shopping_results") or [])[:limit]:
            link = r.get("link") or r.get("product_link")
            offers.append(ShoppingOffer(
                title=r.get("title", ""), source=r.get("source", ""),
                price=to_float(r.get("extracted_price"), None) or to_float(r.get("price")),
                rating=to_float(r.get("rating")), reviews=int(r["reviews"]) if r.get("reviews") else None,
                link=link, domain=offer_domain(link),
            ))
        prices = [o.price for o in offers if o.price]
        return ShoppingSummary(
            count=len(offers), sellers=len({o.source.lower() for o in offers if o.source}),
            price_min=min(prices) if prices else None, price_median=median(prices),
            price_max=max(prices) if prices else None, offers=offers,
        )

    def trends(self, keyword: str, market: Market) -> list[float]:
        data = self._search("google_trends", {
            "engine": "google_trends", "q": keyword, "geo": market.trends_geo,
            "date": "today 12-m", "data_type": "TIMESERIES",
        })
        return monthly_buckets((data.get("interest_over_time") or {}).get("timeline_data") or [])

    # ------------------------------------------------------------------ mock
    def mock_response(self, endpoint, params):
        kw = params.get("q", "")
        if endpoint == "google_shopping":
            data = load_fixture("serpapi_google_shopping.json")
            rng = seeded_rng("shopping", kw, params.get("gl"))
            keep = rng.randint(5, len(data["shopping_results"]))
            results = []
            for r in data["shopping_results"][:keep]:
                r = copy.deepcopy(r)
                r["title"] = r["title"].replace("{Keyword}", kw.title())
                factor = rng.uniform(0.7, 1.4)
                r["extracted_price"] = round(r["extracted_price"] * factor, 2)
                r["price"] = f"${r['extracted_price']:.2f}"
                results.append(r)
            data["shopping_results"] = results
            return data
        if endpoint == "google_trends":
            data = load_fixture("serpapi_google_trends.json")
            rng = seeded_rng("trends", kw, params.get("geo"))
            slope = rng.uniform(-0.6, 1.2) / 52
            start = date.today() - timedelta(weeks=52)
            data["interest_over_time"]["timeline_data"] = [
                {"date": (start + timedelta(weeks=w)).isoformat(),
                 "values": [{"query": kw, "extracted_value":
                             max(1, min(100, int(50 * (1 + slope * w) + rng.uniform(-6, 6))))}]}
                for w in range(52)
            ]
            return data
        raise KeyError(endpoint)
