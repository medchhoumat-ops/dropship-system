"""Read public Shopify storefront data: /products.json, theme, FAQ and policy pages."""

from __future__ import annotations

import json
import re

from ..http import ApiError, BaseClient, load_fixture

FAQ_PATHS = ("/pages/faq", "/pages/faqs", "/pages/frequently-asked-questions", "/pages/help")
POLICY_PATHS = {"shipping": "/policies/shipping-policy", "refund": "/policies/refund-policy"}


def detect_theme(html: str) -> str | None:
    m = re.search(r"Shopify\.theme\s*=\s*(\{.*?\})\s*;", html or "", re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            return data.get("schema_name") or data.get("name")
        except json.JSONDecodeError:
            pass
    m = re.search(r'"schema_name"\s*:\s*"([^"]+)"', html or "")
    return m.group(1) if m else None


class ShopifyInspector(BaseClient):
    """No API key needed; mock mode only when DROPSHIP_MOCK is set (or forced)."""

    source = "shopify"
    min_interval = 1.0  # be polite to storefronts
    timeout = 20.0
    max_retries = 2

    def __init__(self, settings, mock=None, http=None):
        super().__init__(settings, settings.force_mock if mock is None else mock, http)

    def _get(self, domain: str, path: str, parse: str = "text"):
        url = f"https://{domain}{path}"
        try:
            return self.call(f"{domain}{path}", url, parse=parse)
        except (ApiError, ValueError):
            return None

    def products(self, domain: str) -> list[dict] | None:
        data = self._get(domain, "/products.json?limit=250", parse="json")
        if isinstance(data, dict) and isinstance(data.get("products"), list):
            return data["products"]
        return None

    def home(self, domain: str) -> str | None:
        return self._get(domain, "/")

    def faq(self, domain: str) -> str | None:
        for path in FAQ_PATHS:
            html = self._get(domain, path)
            if html and len(html) > 200 and "404" not in html[:500]:
                return html
        return None

    def policy(self, domain: str, kind: str) -> str | None:
        return self._get(domain, POLICY_PATHS[kind])

    def mock_response(self, endpoint, params):
        domain, _, path = endpoint.partition("/")
        path = "/" + path
        if "amazon" in domain or "walmart" in domain:
            return None
        if path.startswith("/products.json"):
            return load_fixture("shopify_products.json")
        if path == "/":
            return load_fixture("shopify_home.html")
        if path == "/pages/faq":
            return load_fixture("shopify_faq.html")
        if path.startswith("/pages/"):
            return None
        if path == POLICY_PATHS["shipping"]:
            return load_fixture("shopify_shipping.html")
        if path == POLICY_PATHS["refund"]:
            return load_fixture("shopify_refund.html")
        return None
